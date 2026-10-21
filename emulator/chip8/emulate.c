#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "display.c"

#define MEMORY_SIZE 4 * 1024
#define MEMORY_OFFSET 0x1FF
#define FONT_OFFSET 0x050
#define PROGRAM_START 0x200
#define MAX_PROGRAM_SIZE MEMORY_SIZE - MEMORY_OFFSET

#define DISPLAY_WIDTH 64
#define DISPLAY_HEIGHT 32
#define PIXEL_SIZE 10

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

uint8_t memory[MEMORY_SIZE] = { 0 };
uint16_t pc, index_reg;
uint8_t delay_timer, sound_timer;
uint8_t general_reg[16];
display_t *display;

void initialize() {
    memcpy(&memory[FONT_OFFSET], font, sizeof(font));
    display = create_display(
        DISPLAY_WIDTH,
        DISPLAY_HEIGHT,
        PIXEL_SIZE
    );
}

unsigned char *get_address(uint16_t addr) {
    if (addr >= MAX_PROGRAM_SIZE) {
        fprintf(stderr, "Invalid address: 0x%X\n", addr);
        exit(1);
    }

    return &memory[addr];
}

void fetch_decode_execute() {
    uint16_t word = (memory[pc] << 8) | memory[pc + 1];
    pc += 2;

    uint8_t op = (word >> 12) & 0xF;
    uint8_t x = (word >> 8) & 0xF;
    uint8_t y = (word >> 4) & 0xF;
    uint8_t n = word & 0xF;
    uint8_t nn = word & 0xFF;
    uint16_t nnn = word & 0xFFF;



    switch (op) {
        case 0x0:
            if (word == 0x00E0) // clear screen
                clear_display(display);
            break;
        case 0x1: // jump
            pc = nnn;
            break;
        case 0x6: // set register
            general_reg[x] = nn;
            break;
        case 0x7: // add register
            general_reg[x] += nn;
            break;
        case 0xA: // set index register
            index_reg = nnn;
            break;
        case 0xd: // draw display
            uint8_t x_cord = general_reg[x] % DISPLAY_WIDTH;
            uint8_t y_cord = general_reg[y] % DISPLAY_HEIGHT;
            general_reg[15] = 0;

            for (int row = 0; row < n; row++) {
                if (y_cord + row >= DISPLAY_HEIGHT) 
                    break;

                uint8_t byte = memory[index_reg + row];

                for (int col = 0; col < 8; col++) {

                    if (x_cord + col >= DISPLAY_WIDTH) 
                        break;

                    int shift = 7 - col;
                    int pos = get_pos(display, x_cord + col, y_cord + row);

                    bool sprite_px = (byte >> shift) & 0b1;
                    bool display_px = display->data[pos];

                    display->data[pos] ^= sprite_px;

                    if (sprite_px && display_px) {
                        general_reg[15] = 1;
                    }
                }
            }

            render_display(display);
            break;

        default :
            printf("Unknown op code 0x%04X.\n", word);
            break;
    }

}

void synchronize_timers() {

}

size_t load_program(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }

    size_t len = fread(
        &memory[PROGRAM_START],
        1,
        MEMORY_SIZE - PROGRAM_START,
        file
    );

    if (ferror(file)) {
        perror("fread");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    fclose(file);

    printf("Loaded %zu bytes.\n", len);

    pc = PROGRAM_START;
    return len;
}

void run() {

    //int cycles = 100;
    bool running = true;
    while (running) {

        while (SDL_PollEvent(&display->event)) {
            if (display->event.type == SDL_QUIT) {
                running = false;
            } else if (display->event.type == SDL_KEYDOWN) {
                display->data[600] = true;
            }
        }

        fetch_decode_execute();

        render_display(display);

        // fetch
    }

    destroy_display(display);
}

char *read_file(const char *filename) {
    // If a program is too long, it is cut off and later the user is notified.
    char *string = malloc(MEMORY_SIZE);
    size_t offset = 0;

    // Inefficient, but it does the job.
    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("fopen file");
        exit(1);
    }

    int c;
    while ((c = fgetc(file)) != EOF) {
        string[offset++] = (char)c;
    }
    string[offset] = '\0';

    fclose(file);
    return string;
}

int main() {

    initialize();
    //char *program = read_file("IBM_logo.ch8");
    load_program("roms/IBM_logo.ch8");
    run();

    return 0;
}