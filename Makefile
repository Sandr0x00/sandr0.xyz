build:
	go build -o server -v server.go

rebuild: build run

run:
	./server