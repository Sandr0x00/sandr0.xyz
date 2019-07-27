build:
	sassc sass/style.scss static/style.css
	go build -o server -v server.go

rebuild: build run

run:
	./server