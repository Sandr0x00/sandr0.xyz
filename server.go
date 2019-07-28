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
	secureMiddleware := secure.New(secure.Options{
		// AllowedHosts:         []string{"sandr0\\.tk"},
		AllowedHostsAreRegex: false,
		// HostsProxyHeaders:    []string{"X-Forwarded-Host"},
		SSLRedirect: false,
		SSLHost:     "sandro.tk",
		// SSLProxyHeaders:       map[string]string{"X-Forwarded-Proto": "https"},
		STSSeconds:            31536000,
		STSIncludeSubdomains:  true,
		STSPreload:            true,
		ForceSTSHeader:        true,
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

	// no securemiddleware in shared
	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))
	r.PathPrefix("/").Handler(secureMiddleware.Handler(http.FileServer(http.Dir("static"))))
	http.Handle("/", r)

	if !development {
		m := autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist("sandr0.tk"),
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
	fmt.Printf("Starting server on http://%s\n", hostname)
	var err error
	err = http.ListenAndServe(":8081", nil)
	if err != nil {
		log.Fatal(err)
	}
}
