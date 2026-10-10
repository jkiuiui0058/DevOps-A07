CC ?= cc
CFLAGS ?= -O0

.PHONY: all clean

all: app

app: main.o
	$(CC) main.o -o app

# config.h is included by main.c but intentionally omitted: this is the MD fixture.
# unused.h is declared but not included by main.c: this is the RD fixture.
main.o: main.c unused.h
	$(CC) $(CFLAGS) -c main.c -o main.o

clean:
	rm -f *.o app
