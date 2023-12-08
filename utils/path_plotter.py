import math
import time

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Path plotter")
clock = pygame.time.Clock()

log_contents = open("Drivetrain_Position.log", "r").readlines()

print([eval(x) for x in log_contents])

points = [eval(x) for x in log_contents]

start_time = time.monotonic()


def main():
    screen.fill("black")
    for time_, point, rot in points:
        elapsed_time = time.monotonic() - start_time
        time.sleep(time_ - elapsed_time)
        x, y = point
        pygame.draw.circle(screen, "red", (x * 2, y * 2), 10)
        pygame.draw.line(
            screen,
            "green",
            (x * 2, y * 2),
            (
                x * 2 + (math.cos(rot + math.pi / 2) * 50),
                y * 2 + (math.sin(rot + math.pi / 2) * 50),
            ),
        )
        pygame.display.flip()


if __name__ == "__main__":
    main()
