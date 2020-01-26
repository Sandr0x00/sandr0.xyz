kill:
	@kill `cat pid`
	@ps -ef | grep "server"

nohup:
	@nohup ./run.sh &
	@printf ""
	@tail -n 2 nohup.out
	@cat pid
	@printf "\n"

build:
	go build -o server -v server.go

rebuild: build run

run:
	./run.sh