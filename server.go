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
	"github.com/go-http-utils/logger"
	"github.com/gorilla/mux"
	"github.com/unrolled/secure"
	"golang.org/x/crypto/acme/autocert"
)

type Config struct {
	Users      []User            `json:"users"`
	Subdomains map[string]string `json:"subdomains"`
}

var config Config

type User struct {
	Name     string   `json:"name"`
	Password string   `json:"password"`
	Files    []string `json:"files"`
}

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
	name = strings.Replace(name, "\x00", "", -1)
	f, err := fs.base.Open(name)
	if err != nil {
		return nil, err
	}
	return NoListFile{f}, nil
}

// Serve a reverse proxy for a given url
var proxyHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	target, ok := config.Subdomains[r.Host]
	if !ok {
		return
	}

	// parse the url
	url, _ := url.Parse(target)

	// create the reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(url)

	// Update the headers to allow for SSL redirection
	r.URL.Host = url.Host
	r.URL.Scheme = url.Scheme
	r.Header.Set("X-Forwarded-Host", r.Host)
	r.Host = url.Host

	// Note that ServeHttp is non blocking and uses a go routine under the hood
	proxy.ServeHTTP(w, r)
})

// Redirect paths correctly
func Redirect(target string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, target, http.StatusMovedPermanently)
	})
}

var calProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	cal, ok := r.URL.Query()["cal"]
	if !ok {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	if os.Getenv("CAL_UUID") == cal[0] {
		res, err := http.Get(fmt.Sprintf("https://%s:%s@cal.hxp.io/", os.Getenv("CAL_USER"), os.Getenv("CAL_PW")))
		if err != nil {
			fmt.Println(err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		body, err := io.ReadAll(res.Body)
		res.Body.Close()
		w.Header().Add("Content-Type", "text/html; charset=UTF-8")
		w.Header().Add("Connection", "close")
		fmt.Fprint(w, fmt.Sprintf("%s", body))
	} else {
		w.WriteHeader(http.StatusBadRequest)
	}
})

var mijiaProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	res, err := http.Get(os.Getenv("MIJIA"))
	if err != nil {
		fmt.Println(err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	body, err := io.ReadAll(res.Body)
	res.Body.Close()
	w.Header().Add("Content-Type", "application/json; charset=UTF-8")
	w.Header().Add("Connection", "close")
	fmt.Fprint(w, fmt.Sprintf("%s", body))
})

func reloadConfig() {
	// config file
	jsonFile, err := os.Open("config.json")
	// handle errors
	if err != nil {
		fmt.Println(err)
		return
	}
	// defer the closing of our jsonFile so that we can parse it later on
	defer jsonFile.Close()

	// read our opened jsonFile as a byte array.
	byteValue, _ := io.ReadAll(jsonFile)

	// unmarshal array into 'config'
	err = json.Unmarshal(byteValue, &config)
	if err != nil {
		fmt.Println(err)
		return
	}
}

var reloadConfigHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	reloadConfig()

	w.Header().Add("Content-Type", "text/plain; charset=UTF-8")
	w.Header().Add("Connection", "close")
	fmt.Fprint(w, "reloaded")
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
		http.Error(w, "Unauthorized.", 401)
		return
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

func main() {
	reloadConfig()
	secureMiddleware := secure.New(secure.Options{
		AllowedHosts:         []string{"sandr0\\.xyz", ".*\\.sandr0\\.xyz"},
		AllowedHostsAreRegex: true,
		// HostsProxyHeaders:    []string{"X-Forwarded-Host"},
		SSLRedirect: true,
		SSLHost:     "sandr0.xyz",
		// SSLProxyHeaders:       map[string]string{"X-Forwarded-Proto": "https"},
		STSSeconds:           31536000,
		STSIncludeSubdomains: true,
		STSPreload:           true,
		ForceSTSHeader:       true,
		FrameDeny:            true,
		ContentTypeNosniff:   true,
		BrowserXssFilter:     true,
		// https://developer.mozilla.org/en-US/docs/Web/HTTP/Permissions_Policy
		PermissionsPolicy:     "camera=(), display-capture=(), fullscreen=(), geolocation=(), microphone=(), web-share=()",
		ContentSecurityPolicy: "default-src 'self'; font-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none';",
		ReferrerPolicy:        "strict-origin",
		IsDevelopment:         os.Getenv("DEV") == "true",
	})

	var err error
	accessLog, err := os.OpenFile("access.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	must(err)
	defer accessLog.Close()

	r := mux.NewRouter()

	// subdomains
	for key, _ := range config.Subdomains {
		r.Host(key).Handler(proxyHandler)
	}

	// paths
	r.Handle("/secured", Redirect("/secured/"))
	r.PathPrefix("/secured/").Handler(http.StripPrefix("/secured/", auth(cacheZipMiddleware(http.FileServer(http.Dir("secured"))))))
	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", cacheZipMiddleware(http.FileServer(NoListFileSystem{http.Dir("shared")}))))
	r.Handle("/config", reloadConfigHandler)
	r.Handle("/cal", calProxy)
	r.Handle("/mijia", mijiaProxy)
	r.PathPrefix("/").Handler(secureMiddleware.Handler(cacheZipMiddleware(http.FileServer(NoListFileSystem{http.Dir("static")}))))
	// logger logs also subdomains
	http.Handle("/", logger.Handler(r, accessLog, logger.CombineLoggerType))

	if os.Getenv("DEV") != "true" {
		// start production
		m := autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist("sandr0.xyz", "www.sandr0.xyz", "series-tracker.sandr0.xyz", "recipes.sandr0.xyz"),
			Cache:      autocert.DirCache("certs"),
		}
		server := &http.Server{
			Addr: ":443",
			TLSConfig: &tls.Config{
				GetCertificate: m.GetCertificate,
			},
		}
		log.Printf("Serving http/https on https://sandr0.xyz")
		go func() {
			// serve HTTP, which will redirect automatically to HTTPS
			h := m.HTTPHandler(nil)
			log.Fatal(http.ListenAndServe(":80", h))
		}()

		// serve HTTPS
		log.Fatal(server.ListenAndServeTLS("", ""))
	} else {
		// start locally
		hostname, _ := os.Hostname()
		fmt.Printf("Starting server on http://%s:8081\n", hostname)
		log.Fatal(http.ListenAndServe(":8081", nil))
	}

}
