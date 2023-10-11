import math
import os

import numpy as np
import pygame

# Pygame setup
pygame.init()
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
FIELD_WIDTH, FIELD_HEIGHT = 366, 366

SRC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)
DEPLOY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deploy"
)

BACKGROUND_FILE = os.path.join(DEPLOY_DIR, "images", "Field.png")

background = pygame.image.load(BACKGROUND_FILE)

background = pygame.transform.scale(background, SCREEN_SIZE)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Path Generator")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

x_points = []  # Global variable for x-coordinates of points
y_points = []  # Global variable for y-coordinates of points

selected_point_index = None  # Index of the selected point for movement
help_shown = False  # Flag to check if help is currently displayed


def write_spline_points_to_file(x, y):
    file_path = os.path.join(DEPLOY_DIR, "path.pth")

    point_list = list(
        zip(
            map(lambda x: x * FIELD_WIDTH / SCREEN_WIDTH, x),
            map(lambda y: y * FIELD_HEIGHT / SCREEN_HEIGHT, y),
        )
    )

    with open(file_path, "w") as file:
        file.write(str(point_list))


def clear_waypoints():
    global x_points, y_points
    x_points.clear()
    y_points.clear()


def get_selected_point_index(x, y):
    for i, (px, py) in enumerate(zip(x_points, y_points)):
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
        if distance < 10:  # Adjust the radius (10) as per your preference
            return i
    return None


def get_closest_point_index(x, y):
    min_distance = float("inf")
    closest_index = None

    for i, (px, py) in enumerate(zip(x_points, y_points)):
        distance = math.hypot((x - px) + (y - py))
        if distance < min_distance:
            min_distance = distance
            closest_index = i

    return closest_index


def delete_closest_point(x, y):
    global x_points, y_points
    closest_index = get_closest_point_index(x, y)
    if closest_index is not None:
        x_points.pop(closest_index)
        y_points.pop(closest_index)


def delete_last_point():
    global x_points, y_points
    if len(x_points) > 0:
        x_points.pop()
        y_points.pop()


def add_point_on_line(x, y):
    min_distance = float("inf")
    insert_index = None

    for i in range(len(x_points) - 1):
        t_vals = np.linspace(i, i + 1, 100)
        xy_vals = cs(t_vals)
        for px, py in xy_vals:
            distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
            if distance < min_distance:
                min_distance = distance
                insert_index = i

    if min_distance <= 10 and insert_index is not None:
        x_points.insert(insert_index + 1, x)
        y_points.insert(insert_index + 1, y)


def toggle_help():
    global help_shown
    help_shown = not help_shown


def main():
    global x_points, y_points, selected_point_index
    drawing = True

    while drawing:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                drawing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    x_points.append(x)
                    y_points.append(y)
                elif event.button == 3:  # Right mouse button
                    x, y = pygame.mouse.get_pos()
                    selected_point_index = get_selected_point_index(x, y)
                    if selected_point_index is None:
                        add_point_on_line(x, y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Right mouse button release
                    selected_point_index = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    write_spline_points_to_file(x_points, y_points)
                elif event.key == pygame.K_c:
                    clear_waypoints()
                elif event.key == pygame.K_BACKSPACE:
                    delete_last_point()
                elif event.key == pygame.K_x:
                    x, y = pygame.mouse.get_pos()
                    delete_closest_point(x, y)
                elif event.key == pygame.K_h:
                    toggle_help()

        # screen.fill(WHITE)
        screen.blit(background, (0, 0))
        if help_shown:
            # Display help text
            help_text = [
                "",
                "Left-click to add a waypoint",
                "Right-click a waypoint and drag to move it",
                "Right-click on the line to add a waypoint",
                "Press 'X' to delete the waypoint closest to the cursor",
                "Press 'Backspace' to delete the green waypoint",
                "Press 'C' to clear all waypoints",
                "Press 'P' to save the spline points to a file",
            ]
            font = pygame.font.Font(None, 24)
            for i, line in enumerate(help_text):
                help_surface = font.render(line, True, BLACK)
                screen.blit(help_surface, (10, 30 + i * 30))

        if selected_point_index is not None:
            x, y = pygame.mouse.get_pos()
            x_points[selected_point_index] = x
            y_points[selected_point_index] = y

        if len(x_points) >= 2:
            spline_points = list(zip(x_points, y_points))
            pygame.draw.lines(screen, RED, False, spline_points, 2)

        for i, (x, y) in enumerate(zip(x_points, y_points)):
            color = GREEN if i == len(x_points) - 1 else RED
            pygame.draw.circle(screen, color, (x, y), 5)

        # Display "Press H for help" text in the top-left corner
        help_font = pygame.font.Font(None, 24)
        help_surface = help_font.render(
            f"Press H to {'hide' if help_shown else 'show'} help", True, BLACK
        )
        screen.blit(help_surface, (10, 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
