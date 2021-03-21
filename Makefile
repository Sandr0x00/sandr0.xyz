kill:
	@kill `cat pid`
	@ps -ef | grep "server"

nohup:
	@nohup ./run.sh &
	@printf ""
	@tail -n 2 nohup.out
	@cat pid
	@printf "\n"


build-html:
	./builder.py

build-server:
	go build -o server -v server.go

build: build-server build-html

rebuild: build run

report:
	goaccess access.log -a -o secured/report.html

run:
	./run.sh