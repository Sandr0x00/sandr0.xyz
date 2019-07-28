package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
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
		fmt.Printf("%s %s %s\n", r.RemoteAddr, r.Method, r.URL)
		handler.ServeHTTP(w, r)
	})
}

func main() {
	var m *autocert.Manager

	secureMiddleware := secure.New(secure.Options{
		// AllowedHosts:         []string{"sandr0\\.tk"},
		AllowedHostsAreRegex: false,
		// HostsProxyHeaders:    []string{"X-Forwarded-Host"},
		SSLRedirect: false,
		// SSLHost:               "ssl.example.com",
		// SSLProxyHeaders:       map[string]string{"X-Forwarded-Proto": "https"},
		STSSeconds:            31536000,
		STSIncludeSubdomains:  true,
		STSPreload:            true,
		FrameDeny:             true,
		ContentTypeNosniff:    true,
		BrowserXssFilter:      true,
		ContentSecurityPolicy: "default-src 'self' use.fontawesome.com; font-src 'self' use.fontawesome.com; img-src 'self'; style-src 'self' use.fontawesome.com stackpath.bootstrapcdn.com; script-src 'self' stackpath.bootstrapcdn.com; base-uri 'none'; form-action 'self';",
		// PublicKey:             `pin-sha256="base64+primary=="; pin-sha256="base64+backup=="; max-age=5184000; includeSubdomains; report-uri="https://www.example.com/hpkp-report"`,
		ReferrerPolicy: "same-origin",
		FeaturePolicy:  "vibrate 'none'; geolocation 'none'; speaker 'none'; camera 'none'; microphone 'none'; notifications 'none';",
		IsDevelopment:  development,
	})

	r := mux.NewRouter()

	r.Use(logRequest)
	// r.Use(secureMiddleware.Handler)

	// shared := r.PathPrefix("/shared").Subrouter()
	// shared.Handle("/", http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))

	// static := r.PathPrefix("/").Subrouter()
	// static.Handle("/", http.StripPrefix("/", http.FileServer(http.Dir("static"))))

	// no securemiddleware in shared
	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))
	r.PathPrefix("/").Handler(secureMiddleware.Handler(http.FileServer(http.Dir("static"))))
	http.Handle("/", r)

	if !development {
		m = &autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist("sandr0.tk"), //Your domain here
			Cache:      autocert.DirCache("certs"),          //Folder for storing certificates
		}
		server := &http.Server{
			Addr: ":https",
			TLSConfig: &tls.Config{
				GetCertificate: m.GetCertificate,
			},
		}
		server.ListenAndServeTLS("", "")
	}

	hostname, _ := os.Hostname()
	fmt.Printf("Starting server on http://%s\n", hostname)
	var err error
	if m != nil {
		err = http.ListenAndServe(":8081", m.HTTPHandler(nil))
	} else {
		err = http.ListenAndServe(":8081", nil)
	}
	if err != nil {
		log.Fatal(err)
	}
}
