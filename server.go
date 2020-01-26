package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"html"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"

	"io/ioutil"
	"sort"
	"strings"

	"github.com/gorilla/mux"
	"github.com/unrolled/secure"
	"golang.org/x/crypto/acme/autocert"
)

type Users struct {
	Users []User `json:"users"`
}

type User struct {
	Name     string   `json:"name"`
	Password string   `json:"password"`
	Files    []string `json:"files"`
}

var lastHead = ""

func logRequest(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		urlString := fmt.Sprintf("%s", r.URL)
		if strings.HasPrefix(urlString, "/?") {
			head := ""
			for k, v := range r.Header {
				head += fmt.Sprintf("\n    %s %s", k, strings.Join(v, ", "))
			}
			log.Printf("%s %s %s %s%s\n", r.RemoteAddr, r.Method, r.Proto, r.URL, head)
		} else if !strings.HasSuffix(urlString, ".jpg") && !strings.HasSuffix(urlString, ".png") && !strings.HasSuffix(urlString, ".css") && !strings.HasSuffix(urlString, ".svg") && !strings.HasSuffix(urlString, ".ico") && !strings.HasSuffix(urlString, ".js") {
			head := ""
			var keys []string
			for k := range r.Header {
				if k == "If-None-Match" || k == "If-Modified-Since" || k == "Upgrade-Insecure-Requests" || k == "Accept" {
					continue
				}
				keys = append(keys, k)
			}
			sort.Strings(keys)

			for _, k := range keys {
				head += fmt.Sprintf("\n    %s %s", k, strings.Join(r.Header[k], ", "))
			}
			if lastHead == head {
				head = ""
			} else {
				lastHead = head
			}
			log.Printf("%s %s %s %s%s\n", r.RemoteAddr, r.Method, r.Proto, r.URL, head)
		}
		handler.ServeHTTP(w, r)
	})
}

// Serve a reverse proxy for a given url
var recipeProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	// parse the url
	url, _ := url.Parse("http://localhost:8082")

	// create the reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(url)

	// Update the headers to allow for SSL redirection
	r.URL.Host = url.Host
	r.URL.Scheme = url.Scheme
	r.Header.Set("X-Forwarded-Host", r.Header.Get("Host"))
	r.Host = url.Host

	// Note that ServeHttp is non blocking and uses a go routine under the hood
	proxy.ServeHTTP(w, r)
})

// Serve a reverse proxy for a given url
var seriesProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	// parse the url
	url, _ := url.Parse("http://localhost:8083")

	// create the reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(url)

	// Update the headers to allow for SSL redirection
	r.URL.Host = url.Host
	r.URL.Scheme = url.Scheme
	r.Header.Set("X-Forwarded-Host", r.Header.Get("Host"))
	r.Host = url.Host

	// Note that ServeHttp is non blocking and uses a go routine under the hood
	proxy.ServeHTTP(w, r)
})

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
			log.Fatal(err)
		}
		body, err := ioutil.ReadAll(res.Body)
		res.Body.Close()
		w.Header().Add("Content-Type", "text/html; charset=UTF-8")
		w.Header().Add("Connection", "close")
		fmt.Fprint(w, fmt.Sprintf("%s", body))
	} else {
		w.WriteHeader(http.StatusBadRequest)
	}
})

func auth(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		// Authenticated users
		jsonFile, err := os.Open("secured.json")
		// if we os.Open returns an error then handle it
		if err != nil {
			fmt.Println(err)
		}
		// defer the closing of our jsonFile so that we can parse it later on
		defer jsonFile.Close()

		// read our opened jsonFile as a byte array.
		byteValue, _ := ioutil.ReadAll(jsonFile)

		// we initialize our Users array
		var users Users

		// we unmarshal our byteArray which contains our
		// jsonFile's content into 'users' which we defined above
		json.Unmarshal(byteValue, &users)

		user, pass, _ := r.BasicAuth()

		// we iterate through every user within our users array and
		// print out the user Type, their name, and their facebook url
		// as just an example
		for _, valid := range users.Users {
			if valid.Name == user && valid.Password == pass {
				requestFile := html.EscapeString(r.URL.Path)
				for _, curFile := range valid.Files {
					if requestFile == curFile {
						w.Header().Set("Content-Type", "application/octet-stream; charset=utf-8")
						w.Header().Set("Content-Disposition", "attachment;")
						handler.ServeHTTP(w, r)
					}
				}
				for _, curFile := range valid.Files {
					fmt.Fprintf(w, `<a href="%v">%v</a><br>`, curFile, curFile)
				}
				return
			}
		}

		w.Header().Set("WWW-Authenticate", `Basic`)
		http.Error(w, "Unauthorized.", 401)
		return
	})
}

func main() {
	secureMiddleware := secure.New(secure.Options{
		// AllowedHosts:         []string{"sandr0\\.tk"},
		AllowedHostsAreRegex: false,
		// HostsProxyHeaders:    []string{"X-Forwarded-Host"},
		SSLRedirect: false,
		SSLHost:     "sandr0.tk",
		// SSLProxyHeaders:       map[string]string{"X-Forwarded-Proto": "https"},
		STSSeconds:           31536000,
		STSIncludeSubdomains: true,
		STSPreload:           true,
		ForceSTSHeader:       true,
		FrameDeny:            true,
		ContentTypeNosniff:   true,
		BrowserXssFilter:     true,
		ContentSecurityPolicy: `
			default-src 'self' use.fontawesome.com;
			font-src 'self' use.fontawesome.com;
			img-src 'self';
			style-src 'self' 'unsafe-inline' use.fontawesome.com;
			script-src 'self' 'unsafe-inline';
			base-uri 'none';
			form-action 'self';
			frame-ancestors: 'none';
		`,
		// PublicKey:             `pin-sha256="base64+primary=="; pin-sha256="base64+backup=="; max-age=5184000; includeSubdomains; report-uri="https://www.example.com/hpkp-report"`,
		ReferrerPolicy: "same-origin",
		FeaturePolicy:  "vibrate 'none'; geolocation 'none'; speaker 'none'; camera 'none'; microphone 'none'; notifications 'none';",
		IsDevelopment:  os.Getenv("DEV") == "true",
	})

	r := mux.NewRouter()

	r.Use(logRequest)

	// no securemiddleware in shared
	// r.HandlerFunc
	r.Handle("/secured", Redirect("/secured/"))
	r.PathPrefix("/secured/").Handler(http.StripPrefix("/secured/", secureMiddleware.Handler(auth(http.FileServer(http.Dir("secured"))))))
	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))
	r.Handle("/recipes", Redirect("/recipes/"))
	r.PathPrefix("/recipes/").Handler(http.StripPrefix("/recipes/", secureMiddleware.Handler(recipeProxy)))
	r.Handle("/series", Redirect("/series/"))
	r.Handle("/cal", calProxy)
	r.PathPrefix("/series/").Handler(http.StripPrefix("/series/", secureMiddleware.Handler(seriesProxy)))
	r.PathPrefix("/").Handler(secureMiddleware.Handler(http.FileServer(http.Dir("static"))))
	http.Handle("/", r)

	if os.Getenv("DEV") != "true" {
		m := autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist("sandr0.tk", "www.sandr0.tk"),
			Cache:      autocert.DirCache("certs"),
		}
		server := &http.Server{
			Addr: ":8443",
			TLSConfig: &tls.Config{
				GetCertificate: m.GetCertificate,
			},
		}
		log.Printf("Serving http/https on https://sandr0.tk")
		go func() {
			// serve HTTP, which will redirect automatically to HTTPS
			h := m.HTTPHandler(nil)
			log.Fatal(http.ListenAndServe(":8080", h))
		}()

		// serve HTTPS!
		log.Fatal(server.ListenAndServeTLS("", ""))
	}

	hostname, _ := os.Hostname()
	fmt.Printf("Starting server on http://%s:8081\n", hostname)
	var err error
	err = http.ListenAndServe(":8081", nil)
	if err != nil {
		log.Fatal(err)
	}
}
