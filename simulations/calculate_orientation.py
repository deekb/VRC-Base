import math
import os
import random
import sys
import time

import pygame

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)

sys.path.append(src_dir)

from RANSAC import RANSAC
from LinearRegressor import LinearRegressor

MAX_FPS = 20
DISPLAY_SCALING_FACTOR = 4
ULTRASONIC_DISTANCE_FROM_CENTER_PX = 10 * DISPLAY_SCALING_FACTOR
ULTRASONIC_SENSOR_1_ROTATION = 0
ULTRASONIC_SENSOR_2_ROTATION = math.pi / 2
ULTRASONIC_SENSOR_3_ROTATION = math.pi
ULTRASONIC_SENSOR_4_ROTATION = -math.pi / 2

FIELD_WIDTH = 712 * 2
FIELD_HEIGHT = 712 * 2

LINE_TYPE_NONE = None
LINE_TYPE_TOP = 1
LINE_TYPE_BOTTOM = 2
LINE_TYPE_LEFT = 3
LINE_TYPE_RIGHT = 4

horizontal_vertical_threshold = 20
optimal_model = LinearRegressor()
optimal_model.slope = math.inf
optimal_model.x_intercept = 712 + 44

optimal_model_position_error = -1

pygame.init()

field_map = pygame.image.load("Test_Obstacles.png")
robot = pygame.image.load("Robot.png")
font = pygame.font.Font("FreeSansBold.ttf", 10)
pygame_logo = pygame.image.load("pygame_logo.png")
clock = pygame.time.Clock()

field_map = pygame.transform.scale(
    field_map,
    (
        field_map.get_width() * DISPLAY_SCALING_FACTOR,
        field_map.get_height() * DISPLAY_SCALING_FACTOR,
    ),
)
robot = pygame.transform.scale(
    robot,
    (
        robot.get_width() * DISPLAY_SCALING_FACTOR,
        robot.get_height() * DISPLAY_SCALING_FACTOR,
    ),
)

field_map_rect = field_map.get_rect()
robot_rect = robot.get_rect()
pygame_logo_rect = pygame_logo.get_rect()
pygame_logo_rect.center = (field_map_rect.width / 2, field_map_rect.height / 2)

# robot_position = field_map.get_width() / 2, field_map.get_height() / 2

robot_position = (689, 575)  # Also test: (688, 101)

robot_rotation_rad = 0
obstacle_position = None, None

screen = pygame.display.set_mode((field_map_rect.width, field_map_rect.height))

screen.fill((255, 255, 255))
pygame.display.flip()

# for i in range (128):
#     screen.fill((255, 255, 255))
#     pygame_logo.set_alpha(i*2)
#     screen.blit(pygame_logo, pygame_logo_rect)
#     pygame.display.update()
#     clock.tick(128)
#
# time.sleep(1.5)
#
# for i in range (128, 0, -1):
#     screen.fill((255, 255, 255))
#     pygame_logo.set_alpha(i*2)
#     screen.blit(pygame_logo, pygame_logo_rect)
#     pygame.display.update()
#     clock.tick(128)


def scale_point(point, scale):
    return point[0] * scale, point[1] * scale


def convert_point_type(point, window_size):
    return point[0], window_size[1] - point[1]


def cast_ray(start_pos, direction):
    min_distance = 3.81 * DISPLAY_SCALING_FACTOR
    max_distance = 200 * DISPLAY_SCALING_FACTOR
    step_size = 1
    x, y = start_pos
    x_step = math.sin(direction)
    y_step = math.cos(direction)

    distance = min_distance

    while distance < max_distance:
        x += x_step * step_size
        y += y_step * step_size

        distance = math.dist(start_pos, (x, y))

        pixel_color = field_map.get_at((int(x), int(y)))

        if pixel_color.a > 0:  # Check for opaque pixel (obstacle)
            return distance + random.randrange(-int(distance), int(distance)) * (
                0.05 / DISPLAY_SCALING_FACTOR
            )

    return None  # No collision with obstacles within the max distance


def midpoint(p1, p2):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2


def average_points(point_list):
    total_x = 0
    total_y = 0
    for x, y in point_list:
        total_x += x
        total_y += y

    return total_x / len(point_list), total_y / len(point_list)


def do_maneuver():
    global screen, robot_position, robot_rotation_rad, horizontal_vertical_threshold
    sensor_1_collision_list = []
    sensor_2_collision_list = []
    sensor_3_collision_list = []
    sensor_4_collision_list = []

    robot_start_rotation_rad = robot_rotation_rad
    steps = 1000 / 2

    while robot_rotation_rad < robot_start_rotation_rad + math.pi / 2:
        for sensor_rotation in [
            ULTRASONIC_SENSOR_1_ROTATION,
            ULTRASONIC_SENSOR_2_ROTATION,
            ULTRASONIC_SENSOR_3_ROTATION,
            ULTRASONIC_SENSOR_4_ROTATION,
        ]:
            reading = get_ultrasonic_reading(sensor_rotation)
            if reading is None:
                continue
            collision_point = get_collision_point(sensor_rotation, reading)
            pygame.draw.line(screen, (0, 0, 0), robot_position, collision_point)
            pygame.draw.circle(screen, (255, 0, 0), collision_point, 3)
            if sensor_rotation == ULTRASONIC_SENSOR_1_ROTATION:
                sensor_1_collision_list.append(collision_point)
            elif sensor_rotation == ULTRASONIC_SENSOR_2_ROTATION:
                sensor_2_collision_list.append(collision_point)
            elif sensor_rotation == ULTRASONIC_SENSOR_3_ROTATION:
                sensor_3_collision_list.append(collision_point)
            elif sensor_rotation == ULTRASONIC_SENSOR_4_ROTATION:
                sensor_4_collision_list.append(collision_point)

        pygame.display.flip()
        robot_rotation_rad += (math.pi / 2) / steps

    point_list = sensor_1_collision_list
    point_list.extend(
        (*sensor_2_collision_list, *sensor_3_collision_list, *sensor_4_collision_list)
    )

    # for i, point in enumerate(point_list):
    #     if 2 < i < len(point_list) - 2:
    #         filtered_point_list.append(average_points(point_list[i-2:i+2]))

    # for point in filtered_point_list:
    #     pygame.draw.circle(screen, (0, 255, 0), point, 3)

    pygame.display.flip()

    print("DONE")
    print(f"point_list: {point_list}")

    models = []
    inliers = []

    def sample(self, point_list, default_sample_points):
        return random.sample(point_list, default_sample_points)

    def score_model(self, model, inliers):
        global horizontal_vertical_threshold
        if not (
            -1 / horizontal_vertical_threshold
            <= model.slope
            <= 1 / horizontal_vertical_threshold
            or -horizontal_vertical_threshold >= model.slope
            or model.slope >= horizontal_vertical_threshold
        ):
            return 0
        return len(inliers)

    def compare(
        self,
        model,
        model_error,
        model_inliers,
        reference_model,
        reference_error,
        reference_model_inliers,
    ):
        global optimal_model, optimal_model_position_error
        if reference_model is None:
            return model

        reference_model_matches_optimal = False
        new_model_matches_optimal = False

        if reference_model.slope > 1:
            y_list = [44, 712 + 44]
            x_list = reference_model.predict_x(y_list)
            for x in x_list:
                if abs(x - optimal_model.x_intercept) < optimal_model_position_error:
                    reference_model_matches_optimal = True
                    print("Reference model matches optimal model")

        if model.slope > 1:
            y_list = [44, 712 + 44]
            x_list = model.predict_x(y_list)
            for x in x_list:
                if abs(x - optimal_model.x_intercept) < optimal_model_position_error:
                    new_model_matches_optimal = True
                    print("New model matches optimal model")

        if not any((reference_model_matches_optimal, new_model_matches_optimal)):
            # Neither model matches optimal, compare using other metrics
            if model_error <= reference_error and len(model_inliers) >= len(
                reference_model_inliers
            ):
                return model
            else:
                return reference_model
        elif not reference_model_matches_optimal:
            # Reference model does not match optimal, use new model
            return model
        elif not new_model_matches_optimal:
            # The reference model matches optimal, new model does not; use the reference model
            return reference_model
        else:
            # Both models matched the optimal model, compare using other metrics
            if model_error <= reference_error and len(model_inliers) >= len(
                reference_model_inliers
            ):
                return model
            else:
                return reference_model

    start_time = time.perf_counter()

    while True:
        # `sample_points`: Minimum number of data points to estimate parameters
        # `sample_count`: Maximum iterations allowed
        # `score_threshold`: Threshold value to determine if points are fit well
        # `inlier_count_threshold`: Number of close data points required to assert model fits well
        line_detector = RANSAC(
            500, 2, 10, 90, sample=sample, score_model=score_model, compare=compare
        )

        best_model, best_inliers = line_detector.fit(point_list)

        if not best_model:
            break

        for point in best_inliers:
            point_list.remove(point)

        if not point_list:
            break

        if not (
            -1 / horizontal_vertical_threshold
            <= best_model.slope
            <= 1 / horizontal_vertical_threshold
            or -horizontal_vertical_threshold >= best_model.slope
            or best_model.slope >= horizontal_vertical_threshold
        ):
            # This line is not vertical or horizontal; try again
            print("Discarding line")
            continue

        models.append(best_model)
        inliers.append(best_inliers)

    lines = []

    top_line = LINE_TYPE_NONE
    bottom_line = LINE_TYPE_NONE
    left_line = LINE_TYPE_NONE
    right_line = LINE_TYPE_NONE

    color_index = 0

    for i, model in enumerate(models):
        if abs(model.slope) >= 1:
            y_values = [
                field_map_rect.bottomleft[1] - 22 * DISPLAY_SCALING_FACTOR,
                field_map_rect.topleft[1] + 22 * DISPLAY_SCALING_FACTOR,
            ]
            x_values = model.predict_x(y_values)
        else:
            x_values = [
                field_map_rect.bottomleft[0] + 22 * DISPLAY_SCALING_FACTOR,
                field_map_rect.bottomright[0] - 22 * DISPLAY_SCALING_FACTOR,
            ]
            y_values = model.predict_y(x_values)

        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
        ]

        color = colors[color_index % len(colors)]
        color_index += 1

        for point in inliers[i]:
            pygame.draw.circle(screen, color, tuple(point), 3)

        line_type = LINE_TYPE_NONE
        if (
            -1 / horizontal_vertical_threshold
            <= model.slope
            <= 1 / horizontal_vertical_threshold
        ):
            # y_values = [sum(y_values) / len(y_values) for _ in range(len(y_values))]
            if y_values[0] > field_map_rect.height / 2:
                line_type = LINE_TYPE_BOTTOM
                print(
                    f"Bottom Error: {y_values[0] - (field_map_rect.height - 22 * DISPLAY_SCALING_FACTOR)}"
                )
            else:
                line_type = LINE_TYPE_TOP
                print(f"Top Error: {y_values[0] - 22 * DISPLAY_SCALING_FACTOR}")

        elif (
            -horizontal_vertical_threshold >= model.slope
            or model.slope >= horizontal_vertical_threshold
        ):
            # x_values = [sum(x_values) / len(x_values) for _ in range(len(x_values))]
            if x_values[0] > field_map_rect.width / 2:
                line_type = LINE_TYPE_RIGHT
                print(
                    f"Right Error: {x_values[0] - (field_map_rect.width - 22 * DISPLAY_SCALING_FACTOR)}"
                )
            else:
                line_type = LINE_TYPE_LEFT
                print(f"Left Error: {x_values[0] - 22 * DISPLAY_SCALING_FACTOR}")

        if top_line is None and line_type == LINE_TYPE_TOP:
            top_line = list(zip(x_values, y_values))
        if bottom_line is None and line_type == LINE_TYPE_BOTTOM:
            bottom_line = list(zip(x_values, y_values))
        if left_line is None and line_type == LINE_TYPE_LEFT:
            left_line = list(zip(x_values, y_values))
        if right_line is None and line_type == LINE_TYPE_RIGHT:
            right_line = list(zip(x_values, y_values))

    print(
        f"""Left line: {left_line}
Right Line: {right_line}
Top Line: {top_line}
Bottom Line: {bottom_line}"""
    )

    left_x, right_x, top_y, bottom_y = None, None, None, None

    scaled_left_x, scaled_right_x, scaled_top_y, scaled_bottom_y = (
        None,
        None,
        None,
        None,
    )

    if any((left_line is not None, right_line is not None)):
        if left_line is not None:
            left_x = left_line[0][0]
            right_x = left_x + FIELD_WIDTH
        else:
            right_x = right_line[0][0]
            left_x = right_x - FIELD_WIDTH

    if any((top_line is not None, bottom_line is not None)):
        if top_line is not None:
            top_y = top_line[0][1]
            bottom_y = top_y + FIELD_HEIGHT
        else:
            bottom_y = bottom_line[0][1]
            top_y = bottom_y - FIELD_HEIGHT

    scale_point = robot_position

    if all((left_x is not None, right_x is not None)):
        sensed_width = right_x - left_x
        scale_x = FIELD_WIDTH / sensed_width

        distance_to_left = scale_point[0] - left_x
        distance_to_right = right_x - scale_point[0]

        scaled_left_x = scale_point[0] - scale_x * distance_to_left
        scaled_right_x = scale_point[0] + scale_x * distance_to_right

    if all((top_y is not None, bottom_y is not None)):
        sensed_height = bottom_y - top_y
        scale_y = FIELD_HEIGHT / sensed_height

        distance_to_top = scale_point[1] - top_y
        distance_to_bottom = bottom_y - scale_point[1]

        scaled_top_y = scale_point[1] - scale_y * distance_to_top
        scaled_bottom_y = scale_point[1] + scale_y * distance_to_bottom

    if all(
        (
            scaled_left_x is not None,
            scaled_top_y is not None,
            scaled_bottom_y is not None,
        )
    ):
        left_line = [(scaled_left_x, scaled_top_y), (scaled_left_x, scaled_bottom_y)]
    if all(
        (
            scaled_right_x is not None,
            scaled_top_y is not None,
            scaled_bottom_y is not None,
        )
    ):
        right_line = [(scaled_right_x, scaled_top_y), (scaled_right_x, scaled_bottom_y)]
    if all(
        (
            scaled_left_x is not None,
            scaled_right_x is not None,
            scaled_top_y is not None,
        )
    ):
        top_line = [(scaled_left_x, scaled_top_y), (scaled_right_x, scaled_top_y)]
    if all(
        (
            scaled_left_x is not None,
            scaled_right_x is not None,
            scaled_bottom_y is not None,
        )
    ):
        bottom_line = [
            (scaled_left_x, scaled_bottom_y),
            (scaled_right_x, scaled_bottom_y),
        ]

    print(f"Took {round((time.perf_counter() - start_time) * 1000)} ms")

    for line in (left_line, right_line, top_line, bottom_line):
        if line:
            pygame.draw.line(screen, (0, 0, 255), line[0], line[1], width=3)

    pygame.display.flip()
    print(lines)
    print(len(lines))


def get_ultrasonic_sensor_position(
    robot_position, robot_rotation, sensor_rotation, sensor_distance_from_center
):
    return robot_position[0] + (
        math.sin(robot_rotation + sensor_rotation) * sensor_distance_from_center
    ), robot_position[1] + (
        math.cos(robot_rotation + sensor_rotation) * sensor_distance_from_center
    )


def get_ultrasonic_reading(sensor_rotation):
    global robot_position, robot_rotation_rad
    sensor_position = get_ultrasonic_sensor_position(
        robot_position,
        robot_rotation_rad,
        sensor_rotation,
        ULTRASONIC_DISTANCE_FROM_CENTER_PX,
    )

    return cast_ray(sensor_position, robot_rotation_rad + sensor_rotation)


def get_collision_point(sensor_rotation, sensor_distance):
    return robot_position[0] + (
        math.sin(robot_rotation_rad + sensor_rotation)
        * (sensor_distance + ULTRASONIC_DISTANCE_FROM_CENTER_PX)
    ), robot_position[1] + (
        math.cos(robot_rotation_rad + sensor_rotation)
        * (sensor_distance + ULTRASONIC_DISTANCE_FROM_CENTER_PX)
    )


def display_update():
    screen.fill("white")
    screen.blit(field_map, field_map_rect)
    rotated_robot = pygame.transform.rotate(
        robot, math.degrees(robot_rotation_rad + math.pi)
    )
    robot_rect.center = robot_position
    screen.blit(rotated_robot, rotated_robot.get_rect(center=robot_rect.center))
    pygame.display.flip()


def main():
    global robot_position, robot_rotation_rad, obstacle_position

    display_update()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_position = pygame.mouse.get_pos()

                if event.button == 1:  # Left click
                    print("Left click at position:", click_position)
                    robot_position = click_position
                elif event.button == 3:  # Right click
                    print("Right click at position:", click_position)
                    obstacle_position = click_position
                display_update()
                do_maneuver()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            robot_rotation_rad += 0.1
            display_update()
        if keys[pygame.K_RIGHT]:
            robot_rotation_rad -= 0.1
            display_update()

        clock.tick(MAX_FPS)  # Framerate cap

    pygame.quit()


if __name__ == "__main__":
    main()
