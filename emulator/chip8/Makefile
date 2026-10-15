CC      = gcc
CFLAGS  = -Wall -Wextra -Werror -std=c11 $(shell pkg-config --cflags sdl2 SDL2_ttf)
LDLIBS  = $(shell pkg-config --libs sdl2 SDL2_ttf)
TARGET  = emulate_chip_8
SRCS    = main.c emulate.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(SRCS) -o $@ $(LDLIBS)
	@echo "Build complete: $(TARGET)"

clean:
	rm -f $(TARGET) *.o