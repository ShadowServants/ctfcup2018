CC=g++ --std=c++11 -O2

main: auth sha256 user command requests main.cc auth.h settings.h command.h
	$(CC) main.cc auth.o sha256.o command.o user.o requests.o -o server

sha256: sha256.c sha256.h
	$(CC) sha256.c -c -o sha256.o

auth: auth.cc auth.h sha256.h settings.h
	$(CC) auth.cc -c -o auth.o

command: command.h command.cc auth.h settings.h requests.h
	$(CC) command.cc -c -o command.o

user: user.h user.cc settings.h
	$(CC) user.cc -c -o user.o

requests: requests.h requests.cc
	$(CC) requests.cc -c -o requests.o

.PHONY: clean purge init run
clean:
	-rm  *.o server 

purge: clean
	-rm -r user_data user_count.txt

init:
	bash init.sh

run: init main
	socat -T20 TCP-LISTEN:7777,reuseaddr,fork,ignoreeof EXEC:"./server"
