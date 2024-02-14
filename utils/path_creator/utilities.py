import numpy as np
import os
from constants import *


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


def clear_waypoints(path_creator):
    path_creator.x_points.clear()
    path_creator.y_points.clear()


def get_selected_point_index(path_creator, x, y):
    for i, (px, py) in enumerate(zip(path_creator.x_points, path_creator.y_points)):
        distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
        if distance < 10:  # Adjust the radius (10) as per your preference
            return i
    return None


def delete_closest_point(path_creator, x, y):
    closest_index = get_closest_point_index(path_creator, x, y)
    if closest_index is not None:
        path_creator.x_points.pop(closest_index)
        path_creator.y_points.pop(closest_index)


def delete_last_point(path_creator):
    if len(path_creator.x_points) > 0:
        path_creator.x_points.pop()
        path_creator.y_points.pop()


def add_point_on_line(x, y):
    min_distance = float("inf")
    insert_index = None

    for i in range(len(path_creator.x_points) - 1):
        xy_vals = [(x, y)]
        for px, py in xy_vals:
            distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
            if distance < min_distance:
                min_distance = distance
                insert_index = i

    if min_distance <= 10 and insert_index is not None:
        path_creator.x_points.insert(insert_index + 1, x)
        path_creator.y_points.insert(insert_index + 1, y)


def toggle_help(path_creator):
    path_creator.help_shown = not path_creator.help_shown
