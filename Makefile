SHELL   = /bin/sh
PC      = python3.8 -m cython
PFLAGS  = -3 --embed
CC      = gcc
CFLAGS  = -O3 -fPIE $(shell python3.8-config --cflags)
LDFLAGS = -lpython3.8 $(shell python3.8-config --ldflags)

PythonSource = customplot.py
CSource      = customplot.c
Binary       = customplot


.PHONY: comp exec run


comp:
	$(PC) $(PFLAGS) -o $(CSource) $(PythonSource)
	$(CC) $(CFLAGS) -o $(Binary) $(CSource) $(LDFLAGS)

exec:
	./$(Binary)

run: comp exec

