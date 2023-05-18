kill:
	@kill `pidof server`
	@ps -ef | grep "serve[r]"

nohup:
	@nohup ./run.sh &

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