SHELL   = /bin/sh
PC      = python3 -m cython
PFLAGS  = -3 --embed
CC      = gcc
CFLAGS  = -O3 -fPIE $(shell python3-config --cflags)
LDFLAGS = -lpython3 $(shell python3-config --ldflags)

PythonSource = examples.py
CSource      = examples.c
Binary       = examples


.PHONY: comp exec run


comp:
	$(PC) $(PFLAGS) -o $(CSource) $(PythonSource)
	$(CC) $(CFLAGS) -o $(Binary) $(CSource) $(LDFLAGS)

exec:
	./$(Binary)

run: comp exec

