import pygame
from path_creator import PathCreator
from constants import SCREEN_SIZE, BACKGROUND_FILE
from helpers import toggle_help

pygame.init()

# Pygame setup
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Path Generator")
clock = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load(BACKGROUND_FILE), SCREEN_SIZE)

path_creator = PathCreator(screen, clock, background)

def main():
    drawing = True
    while drawing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    toggle_help(path_creator)

        path_creator.update()

    pygame.quit()

if __name__ == "__main__":
    main()
