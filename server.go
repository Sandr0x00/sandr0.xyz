package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
)

func logRequest(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("%s %s %s\n", r.RemoteAddr, r.Method, r.URL)
		handler.ServeHTTP(w, r)
	})
}

func main() {
	port := 8081

	r := mux.NewRouter()

	r.PathPrefix("/shared/").Handler(http.StripPrefix("/shared/", http.FileServer(http.Dir("shared"))))
	r.PathPrefix("/").Handler(http.FileServer(http.Dir("static")))
	http.Handle("/", r)

	hostname, _ := os.Hostname()
	fmt.Printf("Starting server on http://%s:%d\n", hostname, port)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), logRequest(r)); err != nil {
		log.Fatal(err)
	}
}
