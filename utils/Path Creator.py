import math
import os
import random

import numpy as np
import pygame

is_nuitka = "__compiled__" in globals()

# Pygame setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_SIZE = (1000, 800)
FIELD_WIDTH, FIELD_HEIGHT = 366, 366

BASE_DIR = (
    os.path.dirname(__file__)
    if is_nuitka
    else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

SRC_DIR = os.path.join(BASE_DIR, "src")

DEPLOY_DIR = os.path.join(BASE_DIR, "deploy")

BACKGROUND_FILE = os.path.join(DEPLOY_DIR, "Field.png")

background = pygame.transform.scale(
    pygame.image.load(BACKGROUND_FILE), (min(SCREEN_SIZE), min(SCREEN_SIZE))
)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Path Generator")
font = pygame.font.Font("freesansbold.ttf", 20)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

x_points = []  # Global variable for x-coordinates of points
y_points = []  # Global variable for y-coordinates of points

selected_point_index = None  # Index of the selected point for movement
help_shown = False  # Flag to check if help is currently displayed


class ActionButtonContainer:
    def __init__(self, position, size, button_size):
        self.x_position, self.y_position = self.position = position
        self.width, self.height = self.size = size
        self.button_width, self.button_height = self.button_size = button_size
        self.action_buttons = {}

    def add_button(self, action, display_name, active):
        self.action_buttons[action] = [display_name, active]

    def is_button_active(self, action):
        return self.action_buttons[action][1]

    def render(self):
        for i, button in enumerate(self.action_buttons):
            pygame.draw.rect(
                screen,
                (GREEN if self.is_button_active(button) else RED),
                (
                    self.x_position,
                    self.y_position + (i * self.button_height),
                    self.button_width,
                    self.button_height,
                ),
            )
            text = font.render(button, True, BLUE)
            screen.blit(
                text,
                (
                    self.x_position,
                    self.y_position + (i * self.button_height),
                    self.button_width,
                    self.button_height,
                ),
            )
        pygame.display.flip()


def write_spline_points_to_file(x, y):
    file_path = os.path.join(DEPLOY_DIR, "path.pth")

    point_list = list(
        zip(
            map(lambda x: (x * FIELD_WIDTH / SCREEN_WIDTH), x),
            map(lambda y: FIELD_WIDTH - (y * FIELD_HEIGHT / SCREEN_HEIGHT), y),
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
        distance = math.hypot((x - px), (y - py))
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
        xy_vals = [(x, y)]
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

    action_button_container = ActionButtonContainer(
        (min(SCREEN_SIZE), 0),
        (max(SCREEN_SIZE) - min(SCREEN_SIZE), SCREEN_HEIGHT),
        (max(SCREEN_SIZE) - min(SCREEN_SIZE), SCREEN_HEIGHT / 12),
    )

    action_button_container.add_button("example_action", "Example DisplayName", True)

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
                elif event.key == pygame.K_l:
                    print("Loading from file")

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
                "Press 'L' to load a pointset from a file",
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

        action_button_container.render()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
