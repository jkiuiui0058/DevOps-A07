CFLAGS = -O0 -DMODE=7

app: main.o
	cc main.o -o app

main.o: main.c config.h
	cc $(CFLAGS) -c main.c -o main.o

clean:
	rm -f *.o app