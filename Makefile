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
	./report.py

run:
	./run.sh