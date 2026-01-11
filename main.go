package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"html"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/NYTimes/gziphandler"
	"go.uber.org/zap"
	"golang.org/x/crypto/acme/autocert"
)

type User struct {
	Name     string   `json:"name"`
	Password string   `json:"password"`
	Files    []string `json:"files"`
}

type Subdomain struct {
	Host  string  `json:"host"`
	Proxy *string `json:"proxy,omitempty"`
}

type Config struct {
	Users      []User      `json:"users"`
	Subdomains []Subdomain `json:"subdomains"`
	CodeStyle  string      `json:"codeStyle"`
	Dev        bool        `json:"dev"`
	CalUser    string      `json:"calUser"`
	CalPw      string      `json:"calPw"`
	CalUuid    string      `json:"calUuid"`
}

var config Config

func must(err error) {
	if err != nil {
		panic(err)
	}
}

type NoListFile struct {
	http.File
}

func (f NoListFile) Readdir(count int) ([]os.FileInfo, error) {
	return nil, nil
}

type NoListFileSystem struct {
	base http.FileSystem
}

// fix file listing and null bytes in paths causing 500 - server error
func (fs NoListFileSystem) Open(name string) (http.File, error) {
	name = strings.ReplaceAll(name, "\x00", "")
	f, err := fs.base.Open(name)
	if err != nil {
		return nil, err
	}
	return NoListFile{f}, nil
}

// Serve a reverse proxy for a given url
func proxyHandler(target string) http.Handler {
	url, _ := url.Parse(target)

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		proxy := httputil.NewSingleHostReverseProxy(url)

		// Update the headers to allow for SSL redirection
		r.URL.Host = url.Host
		r.URL.Scheme = url.Scheme
		r.Header.Set("X-Forwarded-Host", r.Host)
		r.Host = url.Host

		// non blocking, uses a go routine under the hood
		proxy.ServeHTTP(w, r)
	})
}

var calProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	cal, ok := r.URL.Query()["cal"]
	if !ok {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	if config.CalUuid == cal[0] {
		res, err := http.Get(fmt.Sprintf("https://%s:%s@cal.hxp.io/", config.CalUser, config.CalPw))
		if err != nil {
			fmt.Println(err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		body, err := io.ReadAll(res.Body)
		if err != nil {
			fmt.Println(err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		err = res.Body.Close()
		if err != nil {
			fmt.Println(err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		w.Header().Add("Content-Type", "text/html; charset=UTF-8")
		w.Header().Add("Connection", "close")
		fmt.Fprint(w, fmt.Sprintf("%s", body))
	} else {
		w.WriteHeader(http.StatusBadRequest)
	}
})

func reloadConfig() {
	jsonFile, err := os.Open("config.json")
	if err != nil {
		log.Fatal(err)
	}
	defer jsonFile.Close()

	byteValue, err := io.ReadAll(jsonFile)
	if err != nil {
		log.Fatal(err)
	}

	err = json.Unmarshal(byteValue, &config)
	if err != nil {
		log.Fatal(err)
	}
}

var reloadConfigHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	reloadConfig()

	w.Header().Add("Content-Type", "text/plain; charset=UTF-8")
	w.Header().Add("Connection", "close")
	fmt.Fprint(w, "reloaded")
	w.WriteHeader(http.StatusOK)
})

func filteredSearchOfDirectoryTree(re *regexp.Regexp, dir string, w http.ResponseWriter) error {
	walk := func(fn string, fi os.FileInfo, err error) error {
		if !re.MatchString(fn) {
			return nil
		}

		fmt.Fprintf(w, `<a href="/%v">%v</a><br>`, fn, fn)
		return nil
	}
	filepath.Walk(dir, walk)
	return nil
}

func auth(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		user, pass, _ := r.BasicAuth()

		for _, valid := range config.Users {
			if valid.Name != user || valid.Password != pass {
				// wrong user
				continue
			}

			requestFile := html.EscapeString(r.URL.Path)
			if requestFile != "" {
				for _, curFile := range valid.Files {
					re := regexp.MustCompile(curFile)
					if re.MatchString(requestFile) {
						fmt.Printf("matched: %v", requestFile)
						if !strings.HasSuffix(requestFile, "html") {
							w.Header().Set("Content-Type", "application/octet-stream; charset=utf-8")
							w.Header().Set("Content-Disposition", "attachment;")
						}
						handler.ServeHTTP(w, r)
						return
					}
				}
			}
			for _, curFile := range valid.Files {
				filteredSearchOfDirectoryTree(regexp.MustCompile(curFile), "secured", w)
			}
			return
		}

		w.Header().Set("WWW-Authenticate", `Basic`)
		http.Error(w, "Unauthorized.", http.StatusUnauthorized)
	})
}

var (
	cacheSince = time.Now().Format(http.TimeFormat)
)

func cacheZipMiddleware(next http.Handler) http.Handler {
	return gziphandler.GzipHandler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "max-age:604800")
		w.Header().Set("Last-Modified", cacheSince)
		w.Header().Set("Expires", time.Now().AddDate(0, 0, 7).Format(http.TimeFormat))
		next.ServeHTTP(w, r)
	}))
}

func securityHeaderMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Cross-Origin-Embedder-Policy", `require-corp; report-to="default"`)
		w.Header().Set("Cross-Origin-Opener-Policy", `same-origin; report-to="default"`)
		w.Header().Set("Cross-Origin-Resource-Policy", "same-site")
		w.Header().Set("Referrer-Policy", "strict-origin")
		// ignored by modern browsers
		w.Header().Set("X-XSS-Protection", "1; mode=block")
		w.Header().Set("Permissions-Policy", "accelerometer=(), autoplay=(), camera=(), clipboard-read=(), clipboard-write=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()")
		w.Header().Set("Content-Security-Policy",
			"default-src 'self'; "+
				"script-src 'self'; "+
				"style-src 'self' 'unsafe-inline'; "+
				"img-src 'self' data:; "+
				"font-src 'self'; "+
				"connect-src 'self'; "+
				"frame-ancestors 'none'; "+
				"base-uri 'none'; "+
				"form-action 'self'",
		)
		if r.TLS != nil {
			w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
		}

		next.ServeHTTP(w, r)
	})
}

type responseRecorder struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (rw *responseRecorder) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseRecorder) Write(p []byte) (int, error) {
	if rw.status == 0 {
		rw.status = http.StatusOK
	}
	n, err := rw.ResponseWriter.Write(p)
	rw.bytes += n
	return n, err
}

func requestTarget(r *http.Request) string {
	// Prefer RequestURI when present (keeps query string)
	if r.RequestURI != "" {
		return r.RequestURI
	}
	if r.URL != nil {
		if r.URL.RawQuery != "" {
			return r.URL.Path + "?" + r.URL.RawQuery
		}
		return r.URL.Path
	}
	return "/"
}

func escapeQuotes(s string) string {
	// Minimal escaping for combined log fields
	s = strings.ReplaceAll(s, `\`, `\\`)
	s = strings.ReplaceAll(s, `"`, `\"`)
	return s
}

// CombinedLogger logs in "combined" format:
//
//	<ip> - - [02/Jan/2006:15:04:05 -0700] "GET /path HTTP/1.1" 200 1234 "referer" "user-agent"
func combinedLogger(out io.Writer) func(http.Handler) http.Handler {
	if out == nil {
		out = io.Discard
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			rr := &responseRecorder{ResponseWriter: w}
			next.ServeHTTP(rr, r)

			// If handler never wrote anything:
			if rr.status == 0 {
				rr.status = http.StatusOK
			}

			// Combined format components
			ip := r.RemoteAddr
			ts := start.Format("02/Jan/2006:15:04:05 -0700")
			reqLine := fmt.Sprintf("%s %s %s", r.Method, requestTarget(r), r.Proto)

			referer := r.Referer()
			if referer == "" {
				referer = "-"
			}
			ua := r.UserAgent()
			if ua == "" {
				ua = "-"
			}

			// Escape quotes to keep a valid log line
			referer = escapeQuotes(referer)
			ua = escapeQuotes(ua)

			fmt.Fprintf(out, `%s - - [%s] "%s" %d %d "%s" "%s"%s`,
				ip, ts, reqLine, rr.status, rr.bytes, referer, ua, "\n",
			)
		})
	}
}

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	reloadConfig()
	var err error
	accessLog, err := os.OpenFile("access.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	must(err)
	defer accessLog.Close()

	mux := http.NewServeMux()

	subdomains := make([]string, 0, len(config.Subdomains))
	for _, subdomain := range config.Subdomains {
		subdomains = append(subdomains, subdomain.Host)
		if subdomain.Proxy != nil {
			mux.Handle(subdomain.Host+"/", proxyHandler(*subdomain.Proxy))
		}
	}

	mux.Handle("GET /secured/", http.StripPrefix("/secured/", auth(cacheZipMiddleware(http.FileServer(http.Dir("secured"))))))
	mux.Handle("GET /shared/", http.StripPrefix("/shared/", cacheZipMiddleware(http.FileServer(NoListFileSystem{http.Dir("shared")}))))
	mux.Handle("GET /config", reloadConfigHandler)
	mux.Handle("GET /cal", calProxy)
	mux.Handle("/log", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		fields := make([]zap.Field, 0, len(r.Header)+5)
		fields = append(fields,
			zap.String("ip", r.RemoteAddr),
			zap.String("method", r.Method),
			zap.String("path", r.URL.RawPath),
			zap.String("query", r.URL.RawQuery),
			zap.String("proto", r.Proto),
			zap.ByteString("body", body),
		)
		for k, v := range r.Header {
			fields = append(fields, zap.Strings(k, v))
		}
		logger.Info("log", fields...)
		w.WriteHeader(http.StatusOK)
	}))
	mux.Handle("/", securityHeaderMiddleware(cacheZipMiddleware(http.FileServer(NoListFileSystem{http.Dir("static")}))))

	if !config.Dev {
		// start production
		m := autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist(subdomains...),
			Cache:      autocert.DirCache("certs"),
		}
		server := &http.Server{
			Addr: ":443",
			TLSConfig: &tls.Config{
				GetCertificate: m.GetCertificate,
			},
			Handler: combinedLogger(accessLog)(mux),
		}
		logger.Info("Serving http/https on https://sandr0.xyz")
		go func() {
			// serve HTTP, which will redirect automatically to HTTPS
			h := m.HTTPHandler(nil)
			err = http.ListenAndServe(":80", h)
			if err != http.ErrServerClosed {
				logger.Fatal("http redirect server failed", zap.Error(err))
			}

		}()

		// serve HTTPS
		err = server.ListenAndServeTLS("", "")
	} else {
		// start locally
		hostname, _ := os.Hostname()
		fmt.Printf("Starting server on http://%s:8081\n", hostname)
		err = http.ListenAndServe(":8081", mux)
	}
	if err != http.ErrServerClosed {
		logger.Fatal("server failed", zap.Error(err))
	}

}
