from math import isinf, sqrt, cos, sin
from Constants import font_size, log_directory
from vex import *


class Terminal:
    def __init__(self, brain):
        self.brain = brain
        self.log = Logging("Terminal", terminal=self)
        self.brain.screen.set_font(font_size)

    def clear(self):
        """
        Clears the brain screen
        """

        self.brain.screen.set_font(font_size)
        self.log.log("{Clearing terminal}\n")
        self.brain.screen.clear_screen()
        self.brain.screen.set_cursor(1, 1)

    def print(self, text: str, end: str = "\n"):
        """
        Prints a string to a console

        Args:
            text: the text to print to the screen
            end: The string to print at the end (defaults to new line)
        """

        self.brain.screen.set_font(font_size)
        self.log.log(str(text) + str(end))

        # Deal with the vex brain class' inability to parse "\n" as a newline (^ look, Logging.log can do it ^)
        text_split = str(text).split("\n")
        i = 0
        for part in text_split:
            self.brain.screen.print(str(part))
            if i != len(text_split) - 1:
                self.brain.screen.next_row()
            i += 1

        # And again :)
        end_split = str(end).split("\n")
        i = 0
        for part in end_split:
            self.brain.screen.print(str(part))
            if i != len(end_split) - 1:
                self.brain.screen.next_row()
            i += 1


class BinarySemaphore:
    """
    Represents a binary semaphore (thread lock) with two states, locked and unlocked and a method to acquire and release the lock

    See Also:
        https://en.m.wikipedia.org/wiki/Semaphore_(programming)
    """

    def __init__(self):
        self.locked = False
        self.attempting_acquisition = False

    def is_locked(self):
        return self.locked or self.attempting_acquisition

    def acquire(self):
        self.attempting_acquisition = True
        while self.locked:
            pass
        self.locked = True
        self.attempting_acquisition = False

    def release(self):
        self.locked = False


def apply_deadzone(value: float, deadzone: float, maximum: float) -> float:
    """
    Apply a dead_zone to the passed value

    Args:
        maximum: The maximum value for the input, helps to smooth out the returned values when the value is outside the dead zone
        value: The value to apply a deadzone to
        deadzone: The lowest value that should have a nonzero output

    Returns:
        The input value with the cubic filter applied
    """

    if abs(value) < deadzone:
        return 0
    else:
        return maximum / (maximum - deadzone) * (value - deadzone)


class MotorPID:
    """
    Wrap a motor definition in this class to use a custom PID to control its movements ie: my_motor = MotorPID(Motor(...), kp, kd, t)
    **Waring, this class disables all motor functionality except the following functions:[set_velocity, set_stopping, stop, spin, velocity]**
    """

    def __init__(self, timer: Brain.timer, motor_object, kp: float = 0.4, ki: float = 0.01, kd: float = 0.05, t: float = 0.1):
        """"
        Creates an instance of the MotorPID

        Args:
            motor_object: The motor to apply the PID to
            kp: Kp value for the PID: How quickly to modify the target value if it has not yet reached the desired value
            ki: Ki value for the PID: Integral gain to reduce steady-state error
            kd: Kd value for the PID: Higher values reduce the response time and limit overshoot
            t: Time between PID updates
        """
        self.motor_object = motor_object
        self.motor_PID = PIDController(timer, kp, ki, kd)
        self.pid_thread = Thread(self._loop)
        self.t = t

    def update(self) -> None:
        """
        Update the PID state with the most recent motor and target velocities and send the normalized value to the motor
        """

        self.motor_object.set_velocity(self.motor_PID.update(self.velocity()), PERCENT)

    def _loop(self) -> None:
        """
        Used to run the PID in a new thread: updates the values the PID uses and handles
          applying the PID output to the motor
        """

        while True:
            self.update()
            wait(self.t, SECONDS)

    def set_velocity(self, velocity: float) -> None:
        """
        Set the motor's target velocity using the PID, make sure you run PID_loop in a new thread or this
        will have no effect
        :param velocity: The new target velocity of the motor
        :type velocity: float
        """

        self.motor_PID._target_value = velocity

    def spin(self, direction):
        self.motor_object.spin(direction)

    def stop(self):
        self.motor_object.stop()

    def velocity(self):
        return self.motor_object.velocity(PERCENT)


class PIDController:
    """
    A generalized PID controller implementation.
    """

    def __init__(
        self,
        timer: Brain.timer,
        kp: float = 1.0,
        ki: float = 0.0,
        kd: float = 0.0,
        t: float = 0.05,
        integral_limit: float = 1.0,
    ):
        """
        Initializes a PIDController instance.
        :param timer: The timer object used to measure time.
        :param kp: Kp value for the PID.
        :param ki: Ki value for the PID.
        :param kd: Kd value for the PID.
        :param t: Minimum time between update calls.
        All calls made before this amount of time has passed since the last calculation will be ignored.
        :param integral_limit: The maximum absolute value for the integral term to prevent windup.
        """

        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._timer = timer
        self._time_step = t
        self._previous_time = timer.time(SECONDS)
        self._current_value = 0.0
        self._target_value = 0.0
        self._error_integral = 0.0
        self._integral_limit = integral_limit
        self._previous_error = 0.0
        self._control_output = 0.0

    @property
    def kp(self) -> float:
        """
        Getter for the Kp value of the PID.
        :return: The Kp value.
        """

        return self._kp

    @kp.setter
    def kp(self, value: float):
        """
        Setter for the Kp value of the PID.
        :param value: The new Kp value.
        """

        self._kp = value

    @property
    def ki(self) -> float:
        """
        Getter for the Ki value of the PID.
        :return: The Ki value.
        """

        return self._ki

    @ki.setter
    def ki(self, value: float):
        """
        Setter for the Ki value of the PID.
        :param value: The new Ki value.
        """

        self._ki = value

    @property
    def kd(self) -> float:
        """
        Getter for the Kd value of the PID.
        :return: The Kd value.
        """

        return self._kd

    @kd.setter
    def kd(self, value: float):
        """
        Setter for the Kd value of the PID.
        :param value: The new Kd value.
        """

        self._kd = value

    @property
    def setpoint(self) -> float:
        """
        Getter for the target value of the PID.
        :return: The target value.
        """

        return self._target_value

    @setpoint.setter
    def setpoint(self, value: float):
        """
        Setter for the target value of the PID.
        :param value: The new target value.
        """
        self._target_value = value

    def reset(self):
        self._error_integral = 0
        self._control_output = 0
        self._previous_error = self._target_value - self._current_value

    def update(self, current_value: float) -> float:
        """
        Update the PID state with the most recent current value and calculate the control output.

        Args:
            current_value: The current measurement or feedback value

        Returns:
            The calculated control output.
        """

        current_time = self._timer.time(SECONDS)
        delta_time = current_time - self._previous_time

        if delta_time < self._time_step:
            return self._control_output

        self._previous_time = current_time

        current_error = self._target_value - current_value
        self._error_integral += current_error * delta_time
        # Apply integral windup prevention
        # PID integral windup is a phenomenon that occurs when the integral term of a PID
        # controller continues to accumulate error even when the controller's output is saturated.
        # This can lead to overshoot, instability, and poor performance in control systems.
        # if your Kp is reasonably low, and you are still experiencing overshoot/instability/oscillation,
        # then try decreasing the integral limit
        if self._ki != 0:
            self._error_integral = clamp(
                self._error_integral, -self._integral_limit, self._integral_limit
            )
        error_derivative = (current_error - self._previous_error) / delta_time
        self._control_output = (
            self._kp * current_error
            + self._ki * self._error_integral
            + self._kd * error_derivative
        )
        self._previous_error = current_error
        return self._control_output


class Logging(object):
    """
    A log that can buffer it's output and when a Micro-SD card is present, can store the buffer in the Mico-SD card
    """

    def __init__(self, log_name, flush_interval=3, terminal=None):
        """
        Logging initializer

        Args:
            log_name: The name to use for the log, logs will be placed in the "logs" directory on the Micro-SD card, make sure to create this directory or logs will be unable to save
            flush_interval: How often (in seconds) to flush the log buffer to the Micro-SD card
            terminal:
        """

        self.terminal = terminal

        if self.terminal:
            self.print = self.terminal.print
            self.clear = self.terminal.clear
        else:
            self.print, self.clear = lambda *args, **kwargs: None

        self.file_name = log_directory + str(log_name) + ".log"
        self.file_object = open(
            self.file_name,
            "w",
        )
        self.write_queue = []
        self.log("Starting log at " + self.file_name)

        Thread(self.auto_flush_logs, [flush_interval])

    def log(self, string: str):
        """
        Send a string to the file, using the log format
        :param string:
        """

        try:
            self.write_queue.append(string)
        except MemoryError:
            self.write_queue.clear()
            self.log(
                "WARNING:Ran out of memory while appending to write_queue, some log messages will be omitted\n"
            )

    def exit(self):
        """
        Close the log object
        """

        self.log("Ending log at " + self.file_name)
        self.flush_file_contents()
        self.file_object.close()

    def flush_file_contents(self):
        try:
            with open(self.file_name, "a") as self.file_object:
                for _ in range(len(self.write_queue)):
                    self.file_object.write(self.write_queue.pop(0))
                self.file_object.flush()
        except OSError:
            self.print("Failed to flush log write queue (Was the SD card removed?)")

    def auto_flush_logs(self, interval_sec):
        while True:
            wait(interval_sec, SECONDS)
            self.flush_file_contents()


def distance_from_point_to_line(point, slope, x_intercept, y_intercept):
    # Convert the line equation to standard form: (Ax - y + C = 0)

    a = slope
    b = -1
    c = y_intercept
    # Extract the coordinates of the point
    x0, y0 = point
    # Calculate the distance using the formula
    if isinf(slope):
        return abs(x0 - x_intercept)
    else:
        return abs(a * x0 + b * y0 + c) / sqrt(a**2 + b**2)


def clamp(value: float, lower_limit: float = None, upper_limit: float = None) -> float:
    """
    Restricts a value within a specified range.

    Args:
        value: The value to be clamped.
        lower_limit: The lower limit of the range. If None, no lower limit is applied.
        upper_limit: The upper limit of the range. If None, no upper limit is applied.

    Returns:
        The clamped value.
    """

    if upper_limit < lower_limit:
        raise ValueError(
            "The value of upper_limit should be greater than or equal to that of lower_limit"
        )

    if lower_limit is not None:
        if value < lower_limit:
            return lower_limit
    if upper_limit is not None:
        if value > upper_limit:
            return upper_limit
    return value


def get_collision_point(
    robot_position,
    robot_rotation_rad,
    sensor_rotation,
    sensor_distance_cm,
    sensor_distance_from_center_cm,
):
    return robot_position[0] + (
        sin(robot_rotation_rad + sensor_rotation)
        * (sensor_distance_cm + sensor_distance_from_center_cm)
    ), robot_position[1] + (
        cos(robot_rotation_rad + sensor_rotation)
        * (sensor_distance_cm + sensor_distance_from_center_cm)
    )


def hypotenuse(x: float, y: float) -> float:
    """
    Get the hypotenuse length of a right triangle with sides x and y

    Args:
        x: One leg of the triangle
        y: The second leg of the triangle

    Returns:
        The hypotenuse length of a right triangle with sides x and y
    """

    return sqrt(pow(x, 2) + pow(y, 2))


def interpolate(x1: float, x2: float, y1: float, y2: float, x: float) -> float:
    """
    Perform linear interpolation for x between (x1,y1) and (x2,y2)

    Args:
        x1: The first point's X value
        x2: The first point's Y value
        y1: The second point's X value
        y2: The second point's Y value
        x: The x value to interpolate the Y value for

    Returns:
        The Y value for the given x value, calculated using linear interpolation from the points given
    """

    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)


def calculate_wheel_power(
    movement_angle_rad: float, movement_speed: float, wheel_angle_rad: float
) -> float:
    """
    Calculate the necessary wheel power for a wheel pointing in the specified angle to move the robot toward the desired target
    This function must be run for all wheels in the drivetrain separately

    Args:
        movement_angle_rad: The angle to move the robot
        movement_speed: The speed to move at
        wheel_angle_rad: The angle of the wheel to calculate power for

    Returns:
        The calculated power for the wheel
    """

    return movement_speed * cos(wheel_angle_rad - movement_angle_rad)


def cubic_filter(value, linearity=0) -> float:
    """
    Apply a cubic filter to a value with a given linearity

    Args:
        value: The value between -1 to 1 to apply the filter to
        linearity: How linear to make the filter

    Returns:
        The input value with a cubic filter applied
    """

    if abs(value) > 1:
        raise ValueError("Input value must be between -1 and 1")
    if linearity < 0:
        raise ValueError("Linearity must be equal to or greater than 0")
    if isinf(linearity):
        raise ValueError("Linearity may not be infinite")

    return (value**3 + linearity * value) / (1 + linearity)
