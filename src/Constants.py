from vex import Ports, GearSetting, FontType
from math import pi

__title__ = "Vex V5 2023 Competition code"
__description__ = "Competition Code for VRC: Over-Under 2023-2024"
__team__ = "3773P (Bowbots Phosphorus)"
__url__ = "https://github.com/deekb/VRC-OverUnder"
__download_url__ = "https://github.com/deekb/VRC-OverUnder/archive/master.zip"
__version__ = "Working"
__author__ = "Derek Baier"
__author_email__ = "Derek.m.baier@gmail.com"
__license__ = "MIT"


class ControllerAxis:
    """A class for defining controller axis constants."""

    x_axis = 0
    y_axis = 1


class Team:
    """A class for defining the different teams"""

    red = 0
    blue = 1
    skills = 2


class DrivetrainType:
    """A class for defining the different types of drivetrains"""

    Tank = 0
    Mecanum = 1
    XDrive = 2


class ClawState:
    """A class for defining the different states of a claw"""

    open = 0
    closed = 1


class WristState:
    """A class for defining the different states of a wrist"""

    up = 0
    down = 1


class IntakeState:
    """A class for defining the different states of a roller-ed intake"""

    off = 0
    pull_in = 1
    push_out = 2


"""Sensors"""
inertial_sensor_port = Ports.PORT12

"""Catapult"""
catapult_motor_port = Ports.PORT11
catapult_motor_gear_ratio = GearSetting.RATIO_36_1
catapult_motor_inverted = False
catapult_motor_speed = 30

"""Intake"""
left_intake_motor_port = Ports.PORT17
left_intake_motor_gear_ratio = GearSetting.RATIO_18_1
left_intake_motor_inverted = False

right_intake_motor_port = Ports.PORT13
right_intake_motor_gear_ratio = GearSetting.RATIO_18_1
right_intake_motor_inverted = True


"""Drivetrain Constants"""
drivetrain_type = DrivetrainType.Mecanum
wheel_radius_cm = 3.556
front_left_motor_port = Ports.PORT16
front_right_motor_port = Ports.PORT14
rear_left_motor_port = Ports.PORT10
rear_right_motor_port = Ports.PORT21
front_left_motor_gear_ratio = GearSetting.RATIO_18_1
front_right_motor_gear_ratio = GearSetting.RATIO_18_1
rear_left_motor_gear_ratio = GearSetting.RATIO_18_1
rear_right_motor_gear_ratio = GearSetting.RATIO_18_1
front_left_motor_inverted = False
front_right_motor_inverted = True
rear_left_motor_inverted = False
rear_right_motor_inverted = True
encoder_ticks_per_rotation = 360  # Green: 360
drivetrain_rotation_offset = -pi / 4
drivetrain_slip_coefficients = {
    pi * 0: 1,
    # pi * -0.25: 1,
    pi * -0.5: 0.75,
    # pi * -0.75: 1,
    pi * 1: 1,
    # pi * 0.75: 1,
    pi * 0.5: 0.75,
    # pi * 0.25: 1,
}
# drivetrain_slip_coefficients = {
#     pi * 0: 0,
#     pi * -0.25: 0.9239,
#     pi * -0.5: 0.7071,
#     pi * -0.75: 0.9239,
#     pi * 1: 0,
#     pi * 0.75: 0.9239,
#     pi * 0.5: 0.7071,
#     pi * 0.25: 0.9239,
# }
front_left_wheel_rotation_rad = pi / 4
front_right_wheel_rotation_rad = pi / 4 + pi / 2
rear_left_wheel_rotation_rad = pi / 4 + pi / 2
rear_right_wheel_rotation_rad = pi / 4

# For tuning the rotation PID gains, please refer to the "Tuning a PID controller" section of Utilities.md
drivetrain_turn_Kp = 1.75 * 0.4
drivetrain_turn_Ki = 0
drivetrain_turn_Kd = 0


wheel_diameter_cm = wheel_radius_cm * 2
wheel_circumference_cm = wheel_diameter_cm * pi

drivetrain_allowed_positional_error_cm = 2
drivetrain_allowed_directional_error_rad = 0.025 * pi  # 4.5 degrees


"""
A note on headless mode:
    In the typical control mode, the robot's movements are relative to its current heading. For example,
    if the control input is "move forward," the robot will move in the direction it is facing.
    However, in headless mode, the control inputs are based on an absolute reference frame (the field),
    regardless of the robot's orientation.
    
    For instance, if the robot is in headless mode and the control input is "move forward,"
    the robot will move in the same direction regardless of its current heading.
    The control inputs are interpreted relative to an absolute reference frame,
    such as the global coordinate system or a predefined reference direction.
    
    Headless mode can be useful in certain scenarios where the robot's orientation or heading is not critical,
    or when controlling the robot based on external references or coordinates.
    It allows for simplified control inputs and decouples the control logic from the robot's orientation.
    
    It does take a little getting used to: Good luck :)
"""
headless_mode = False
movement_deadzone = 0.1
turn_deadzone = 0.1
turn_cubic_linearity = 0.4
movement_cubic_linearity = 0.4

skip_setup = False

movement_acceleration_time = 0.5
movement_deceleration_time = 0.5

font_size = FontType.MONO12

screen_size_y = 240
screen_size_x = 480

field_x_size = 366
field_y_size = 366

button_size_x = 100
button_size_y = 50

phosphorus_bmp_size_x = 37
phosphorus_bmp_size_y = 37

robot_start_position = 20, 78  # (field_x_size / 2, field_y_size / 2)
robot_start_rotation_deg = 90
drivetrain_braking = True

log_directory = "/logs/"
deploy_directory = "/deploy/"


# These constants can be used on their own or can be "binary or-ed" together
# for example (top | right) would be 9, the unique value for top right
# each combination of these values has a unique value 1-15
top = 1
bottom = 2
left = 4
right = 8

red = 1
blue = 2
offensive = 4
defensive = 8
