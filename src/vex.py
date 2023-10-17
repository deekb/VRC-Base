"""
This file is for Pycharm autocomplete only and has no functionality,
it will NOT be uploaded to the robot or placed on the SD card
it does not need to be formatted correctly or error-free
"""

# noinspection PyUnusedLocal
# noinspection PyPep8Naming
SECONDS = "SECONDS"
PERCENT = "PERCENT"
DEGREES = "DEGREES"
MM = "MM"
MSEC = "MSEC"
VOLT = "VOLT"
PRIMARY = "PRIMARY"
PARTNER = "PARTNER"
COAST = "COAST"
BRAKE = "BRAKE"
HOLD = "HOLD"
FORWARD = "FORWARD"
REVERSE = "REVERSE"


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
def Thread(function, args: tuple | list | set = (None,)):
    pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Competition:
    def __init__(self, driver_control_function, autonomous_function):
        pass

    @staticmethod
    def is_enabled() -> bool:
        return False

    @staticmethod
    def is_autonomous() -> bool:
        return False

    @staticmethod
    def is_driver_control() -> bool:
        return False


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Inertial:
    # noinspection PyUnusedLocal
    def __init__(self, port):
        pass

    @staticmethod
    def calibrate() -> None:
        pass

    @staticmethod
    def heading():
        pass

    @staticmethod
    def rotation(unit):
        pass

    @staticmethod
    def is_calibrating() -> bool:
        return False

    @staticmethod
    def set_heading(value, unit=DEGREES):
        pass

    @staticmethod
    def set_rotation(*args):
        pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Distance:
    def __init__(self, port):
        pass

    def object_distance(self, units):
        pass

    def is_object_detected(self):
        pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Optical:
    def __init__(self, port):
        pass

    def set_light_power(self, value, unit):
        pass

    def hue(self):
        pass

    def is_near_object(self):
        pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class DigitalOut:
    def __init__(self, port):
        pass

    def set(self, state: bool):
        pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class ControllerButton:
    def __init__(self):
        pass

    @staticmethod
    def pressed(*args) -> bool:
        pass

    @staticmethod
    def pressing() -> bool:
        pass


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Controller:
    def __init__(self, port):
        self.port = port
        pass

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonL1(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonL2(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonR1(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonR2(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class screen:
        @staticmethod
        def print(text):
            pass

        @staticmethod
        def set_cursor(row, column):
            pass

        @staticmethod
        def next_row():
            pass

        @staticmethod
        def clear_screen():
            pass

        @staticmethod
        def clear_row(row=-1):
            pass

        @staticmethod
        def draw_pixel(x, y):
            pass

        @staticmethod
        def draw_line(start_x, start_y, end_x, end_y):
            pass

        @staticmethod
        def draw_rectangle(x, y, width, height):
            pass

        @staticmethod
        def draw_circle(x, y, radius):
            pass

        @staticmethod
        def set_font(font_type):
            pass

        @staticmethod
        def set_pen_width(pen_width):
            pass

        @staticmethod
        def set_pen_color(color):
            pass

        @staticmethod
        def set_fill_color(color):
            pass

        @staticmethod
        def pressed(callback):
            pass

        @staticmethod
        def released(callback):
            pass

        @staticmethod
        def row():
            return 20

        @staticmethod
        def column():
            return 80

        @staticmethod
        def pressing():
            return False

        @staticmethod
        def x_position():
            return 0

        @staticmethod
        def y_position():
            return 0

        @classmethod
        def draw_image_from_file(cls, *args):
            pass

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonLeft(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonRight(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonA(ControllerButton):
        def __init__(self):
            super().__init__()

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class buttonB(ControllerButton):
        def __init__(self):
            super().__init__()

    @staticmethod
    def rumble(pattern="-"):
        pass

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class axis1:
        @staticmethod
        def position():
            return 0

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class axis2:
        @staticmethod
        def position():
            return 0

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class axis3:
        @staticmethod
        def position():
            return 0

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class axis4:
        @staticmethod
        def position():
            return 0


class Motor:
    # noinspection PyUnusedLocal
    def __init__(self, port, gear_ratio, inverted):
        pass

    @staticmethod
    def spin(direction, voltage=10, unit=VOLT):
        pass

    @staticmethod
    def spin_for(direction, amount, unit=DEGREES):
        pass

    @staticmethod
    def stop():
        pass

    @staticmethod
    def set_position(position, unit=DEGREES):
        pass

    @staticmethod
    def position(*args):
        pass

    @staticmethod
    def set_velocity(velocity, unit=PERCENT):
        pass

    @staticmethod
    def velocity():
        return 0

    @staticmethod
    def set_stopping(stopping_mode):
        pass

    @staticmethod
    def spin_to_position(position, unit, wait=True):
        pass

    @staticmethod
    def set_max_torque(amount, unit=PERCENT):
        pass

    @staticmethod
    def set_timeout(time, unit=SECONDS):
        pass


class MotorGroup:
    def __init__(self, *motors):
        pass

    def spin(self, direction):
        pass

    def set_stopping(self, stopping_mode):
        pass

    def set_velocity(self, velocity, unit=PERCENT):
        pass

    # noinspection PyUnusedLocal
    @staticmethod
    def position(unit=DEGREES):
        return 0

    def stop(self):
        pass


class Ports:
    PORT1 = "Port 1"
    PORT2 = "Port 2"
    PORT3 = "Port 3"
    PORT4 = "Port 4"
    PORT5 = "Port 5"
    PORT6 = "Port 6"
    PORT7 = "Port 7"
    PORT8 = "Port 8"
    PORT9 = "Port 9"
    PORT10 = "Port 10"
    PORT11 = "Port 11"
    PORT12 = "Port 12"
    PORT13 = "Port 13"
    PORT14 = "Port 14"
    PORT15 = "Port 15"
    PORT16 = "Port 16"
    PORT17 = "Port 17"
    PORT18 = "Port 18"
    PORT19 = "Port 19"
    PORT20 = "Port 20"
    PORT21 = "Port 21"


class GearSetting:
    RATIO_6_1 = "6 to 1"
    RATIO_18_1 = "18 to 1"
    RATIO_36_1 = "36 to 1"


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class FontType:
    MONO12 = "MONO12"
    MONO15 = "MONO15"
    MONO20 = "MONO20"
    MONO30 = "MONO30"
    MONO40 = "MONO40"
    MONO60 = "MONO60"

    PROP20 = "PROP20"
    PROP30 = "PROP30"
    PROP40 = "PROP40"
    PROP60 = "PROP60"


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Color:
    BLACK = "BLACK"
    WHITE = "WHITE"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    PURPLE = "PURPLE"
    CYAN = "CYAN"
    TRANSPARENT = "TRANSPARENT"


# noinspection PyUnusedLocal
# noinspection PyPep8Naming
class Brain:
    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class screen:
        @staticmethod
        def print(text):
            pass

        @staticmethod
        def set_cursor(row, column):
            pass

        @staticmethod
        def next_row():
            pass

        @staticmethod
        def clear_screen():
            pass

        @staticmethod
        def clear_row(row=-1):
            pass

        @staticmethod
        def draw_pixel(x, y):
            pass

        @staticmethod
        def draw_line(start_x, start_y, end_x, end_y):
            pass

        @staticmethod
        def draw_rectangle(x, y, width, height):
            pass

        @staticmethod
        def draw_circle(x, y, radius):
            pass

        @staticmethod
        def set_font(font_type):
            pass

        @staticmethod
        def set_pen_width(pen_width):
            pass

        @staticmethod
        def set_pen_color(color):
            pass

        @staticmethod
        def set_fill_color(color):
            pass

        @staticmethod
        def pressed(callback):
            callback()

        @staticmethod
        def released():
            pass

        @staticmethod
        def row():
            return 20

        @staticmethod
        def column():
            return 80

        @staticmethod
        def pressing():
            return False

        @staticmethod
        def x_position():
            return 0

        @staticmethod
        def y_position():
            return 0

        @classmethod
        def draw_image_from_file(cls, filename, x, y):
            pass

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class sdcard:
        @staticmethod
        def is_inserted() -> bool:
            pass

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class battery:
        @staticmethod
        def voltage():
            return 12.0

        @staticmethod
        def current():
            return 16.0

        @staticmethod
        def capacity():
            return 100.0

    # noinspection PyUnusedLocal
    # noinspection PyPep8Naming
    class timer:
        @staticmethod
        def event(callback, time):
            pass

        @staticmethod
        def clear():
            pass

        @staticmethod
        def time(units):
            pass


# noinspection PyUnusedLocal
def wait(amount, unit=MSEC):
    pass
