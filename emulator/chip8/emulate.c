#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "display.c"

#define RAMSIZE 4 * 1024
#define DISPLAY_WIDTH 64
#define DISPLAY_HEIGHT 32

#define MEMORY_OFFSET 0x1FF
#define FONT_OFFSET 0x050

#define MAX_STACK_SIZE 100

typedef struct node {
    uint16_t addr;
    struct node *prev;
} node_t;
node_t *stack = NULL;
size_t stack_length = 0;

int push(uint16_t addr) {
    if (stack_length >= MAX_STACK_SIZE) {
        return 1;
    }

    node_t *node = malloc(sizeof(node_t));
    if (!node) {
        return 2;
    }

    node->addr = addr;
    node->prev = stack;
    stack = node;

    stack_length++;
    return 0;
}

int pop(uint16_t *addr) {
    if (!stack) {
        return 1;
    }

    node_t *top = stack;
    *addr = top->addr;
    stack = top->prev;

    free(top);
    stack_length--;
    return 0;
}

uint8_t font[] = {
    0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
    0x20, 0x60, 0x20, 0x20, 0x70, // 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
    0x90, 0x90, 0xF0, 0x10, 0x10, // 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
    0xF0, 0x10, 0x20, 0x40, 0x40, // 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, // A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
    0xF0, 0x80, 0x80, 0x80, 0xF0, // C
    0xE0, 0x90, 0x90, 0x90, 0xE0, // D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
    0xF0, 0x80, 0xF0, 0x80, 0x80  // F
};

uint8_t memory[RAMSIZE] = { 0 };
uint16_t pc, index_reg;
uint8_t delay_timer, sound_timer;
uint8_t general_reg[16];

void initialize() {
    memcpy(&memory[FONT_OFFSET], font, sizeof(font));
}

void run() {

    while (1) {
        // fetch

    }
    return;
}