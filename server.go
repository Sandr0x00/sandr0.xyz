package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"

	"github.com/gorilla/mux"
	"github.com/unrolled/secure"
	"golang.org/x/crypto/acme/autocert"
)

const (
	development = false
)

func logRequest(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%s %s %s\n", r.RemoteAddr, r.Method, r.URL)
		handler.ServeHTTP(w, r)
	})
}

// Serve a reverse proxy for a given url
var serveReverseProxy = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
	// parse the url
	url, _ := url.Parse("http://localhost:8082")

	log.Printf("%s %s %s\n", url, r.Method, r.URL)

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

func main() {
	secureMiddleware := secure.New(secure.Options{
		// AllowedHosts:         []string{"sandr0\\.tk"},
		AllowedHostsAreRegex: false,
		// HostsProxyHeaders:    []string{"X-Forwarded-Host"},
		SSLRedirect: false,
		SSLHost:     "sandro.tk",
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
			style-src 'self' 'unsafe-inline' use.fontawesome.com stackpath.bootstrapcdn.com;
			script-src 'self' 'unsafe-inline' unpkg.com stackpath.bootstrapcdn.com;
			base-uri 'none'; form-action 'self';
		`,
		// PublicKey:             `pin-sha256="base64+primary=="; pin-sha256="base64+backup=="; max-age=5184000; includeSubdomains; report-uri="https://www.example.com/hpkp-report"`,
		ReferrerPolicy: "same-origin",
		FeaturePolicy:  "vibrate 'none'; geolocation 'none'; speaker 'none'; camera 'none'; microphone 'none'; notifications 'none';",
		IsDevelopment:  development,
	})

	r := mux.NewRouter()

	r.Use(logRequest)

	// no securemiddleware in shared
	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))
	r.PathPrefix("/recipes/").Handler(secureMiddleware.Handler(serveReverseProxy))
	r.PathPrefix("/").Handler(secureMiddleware.Handler(http.FileServer(http.Dir("static"))))
	http.Handle("/", r)

	if !development {
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
