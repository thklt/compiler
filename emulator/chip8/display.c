#include <SDL2/SDL.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct display {
    int width, height, pixel_size;
    uint8_t *data;
    SDL_Window *window;
    SDL_Renderer *renderer;
    SDL_Event event;
} display_t;

display_t *create_display(size_t width, size_t height, size_t pixel_size) {
    
    display_t *display = malloc(sizeof(display_t));
    if (!display) {
        perror("malloc display_t");
        exit(1);
    }
    display->width = width;
    display->height = height;
    display->pixel_size = pixel_size;
    display->data = calloc(width * height, sizeof(bool));
    if (!display->data) {
        perror("malloc display->data");
        exit(1);
    }

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        free(display->data);
        free(display);
        exit(1);
    }

    display->window = SDL_CreateWindow(
        "CHIP-8 Emulator",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        display->width * pixel_size,
        display->height * pixel_size,
        SDL_WINDOW_SHOWN
    );

    if (!display->window) {
        fprintf(stderr, "Window creation failed: %s\n", SDL_GetError());
        SDL_Quit();
        free(display->data);
        free(display);
        exit(1);
    }

    display->renderer = SDL_CreateRenderer(display->window, -1, SDL_RENDERER_ACCELERATED);

    return display;
}

void destroy_display(display_t *display) {
    SDL_DestroyWindow(display->window);
    SDL_Quit();
    free(display->data);
    free(display);
}

int get_pos(display_t *display, int x, int y) {
    return display->width * y + x;
}

#define WHITE 255, 255, 255, 255
#define BLACK 0, 0, 0, 255
void render_display(display_t *display) {
    int size = display->pixel_size;

    SDL_SetRenderDrawColor(display->renderer, BLACK);
    SDL_RenderClear(display->renderer);

    SDL_SetRenderDrawColor(display->renderer, WHITE);

    for (int row = 0; row < display->height; row++)
    {
        int y = size * row;

        for (int col = 0; col < display->width; col++) {
            int x = size * col;
            int pos = display->width * row + col;

            if (display->data[pos]) {
                SDL_Rect pixel = { x, y, size, size };

                SDL_RenderFillRect(display->renderer, &pixel);
            }

            //printf("%b", display->data[pos]);
        }
        //printf("\n");
    }
    //printf("\n\n\n");

    SDL_RenderPresent(display->renderer);
}

void clear_display(display_t *display) {
    for (int i = 0; i < display->height; i++) {
        for (int j = 0; j < display->width; j++) {
            display->data[get_pos(display, j, i)] = false;
        }
    }

    SDL_SetRenderDrawColor(display->renderer, 0, 0, 0, 255);

    SDL_RenderClear(display->renderer);
    SDL_RenderPresent(display->renderer);
}

// int main() {

//     display_t *display = init_display(64, 32, 10);
//     if (!display) {
//         return 1;
//     }

//     display->active = true;
//     clear_display(display);

//     while (display->active) {
//         while (SDL_PollEvent(&display->event)) {
//             if (display->event.type == SDL_QUIT) {
//                 display->active = false;
//             } else if (display->event.type == SDL_KEYDOWN) {
//                 printf("test\n");
//                 display->data[600] = true;
//             }
//         }
//         render_display(display);
//     }

//     destroy_display(display);

//     return 0;
// }