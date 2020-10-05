kill:
	@kill `cat pid`
	@ps -ef | grep "server"

nohup:
	@nohup ./run.sh &
	@printf ""
	@tail -n 2 nohup.out
	@cat pid
	@printf "\n"

install:
	go get github.com/gorilla/mux
	go get github.com/unrolled/secure
	go get github.com/go-http-utils/logger
	go get golang.org/x/crypto/acme/autocert

build:
	go build -o server -v server.go

rebuild: build run

report:
	goaccess access.log -a -o secured/report.html

run:
	./run.sh