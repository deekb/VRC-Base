from Utilities import *
import math
import Constants


class Odometry:
    def __init__(
        self,
        front_left_motor: Motor,
        front_right_motor: Motor,
        rear_left_motor: Motor,
        rear_right_motor: Motor,
        timer: Brain.timer,
        inertial: Inertial,
        terminal: Terminal = None,
    ):
        """
        A class for tracking the robot's position and rotation, this class integrates a stream of motor velocities into a position
        This implementation only works on Holonomic drivetrains (Mecanum, and X-drive), but the concept is similar to other odometry implementations

        Args:
            front_left_motor: The front left motor object for the odometry
            front_right_motor: The front right motor object for the odometry
            rear_right_motor: The rear right motor object for the odometry
            rear_left_motor: The rear left motor object for the odometry
            terminal: An optional terminal to print debug output to
        """
        self.timer = timer
        self.terminal = terminal

        if self.terminal:
            self.print = self.terminal.print
            self.clear = self.terminal.clear
        else:
            self.print = self.clear = lambda *args, **kwargs: None

        # Define the drivetrain's physical properties
        self._wheel_circumference_cm = Constants.wheel_circumference_cm
        self._slip_coefficients = Constants.drivetrain_slip_coefficients

        # Define the initial conditions of the robot
        self._x_position = self._y_position = self._current_rotation_rad = 0
        self.current_heading_rad = self._current_rotation_rad
        self._front_left_motor = front_left_motor
        self._front_right_motor = front_right_motor
        self._rear_left_motor = rear_left_motor
        self._rear_right_motor = rear_right_motor
        self._front_left_motor_last_position = (
            self._front_right_motor_last_position
        ) = (
            self._rear_left_motor_last_position
        ) = self._rear_right_motor_last_position = 0
        self._front_left_motor_distance_since_last_tick = (
            self._front_right_motor_distance_since_last_tick
        ) = (
            self._rear_left_motor_distance_since_last_tick
        ) = self._rear_right_motor_distance_since_last_tick = 0

        self._previousTime = self.timer.time(SECONDS)
        self._auto_update = True
        self._inertial = inertial
        if self._auto_update:
            self._auto_update_thread = Thread(self._auto_update_velocities)
        else:
            self._auto_update_thread = None
        self.reset()

    def reset(self):
        self._x_position = 0
        self._y_position = 0
        if self._inertial is not None:
            self._inertial.set_rotation(0)
        self._current_rotation_rad = 0
        self.current_heading_rad = 0
        self._previousTime = self.timer.time(SECONDS)
        self._front_left_motor_last_position = (
            self._front_left_motor.position(DEGREES)
            / Constants.encoder_ticks_per_rotation
        )
        self._front_right_motor_last_position = (
            self._front_right_motor.position(DEGREES)
            / Constants.encoder_ticks_per_rotation
        )
        self._rear_left_motor_last_position = (
            self._rear_left_motor.position(DEGREES)
            / Constants.encoder_ticks_per_rotation
        )
        self._rear_right_motor_last_position = (
            self._rear_right_motor.position(DEGREES)
            / Constants.encoder_ticks_per_rotation
        )
        self._front_left_motor_distance_since_last_tick = 0
        self._front_right_motor_distance_since_last_tick = 0
        self._rear_left_motor_distance_since_last_tick = 0
        self._rear_right_motor_distance_since_last_tick = 0

    def update_positions(
        self,
        front_left_motor_position: float,
        front_right_motor_position: float,
        rear_left_motor_position: float,
        rear_right_motor_position: float,
    ):
        """
        Updates the algorithm with the current wheel positions

        Args:
            front_left_motor_position: The position of the front left motor
            front_right_motor_position: The position of the front right motor
            rear_left_motor_position: The position of the rear left motor
            rear_right_motor_position: The position of the rear right motor
        """

        self._front_left_motor_distance_since_last_tick = (
            front_left_motor_position - self._front_left_motor_last_position
        ) * self._wheel_circumference_cm
        self._front_right_motor_distance_since_last_tick = (
            front_right_motor_position - self._front_right_motor_last_position
        ) * self._wheel_circumference_cm
        self._rear_left_motor_distance_since_last_tick = (
            rear_left_motor_position - self._rear_left_motor_last_position
        ) * self._wheel_circumference_cm
        self._rear_right_motor_distance_since_last_tick = (
            rear_right_motor_position - self._rear_right_motor_last_position
        ) * self._wheel_circumference_cm

        self._front_left_motor_last_position = front_left_motor_position
        self._front_right_motor_last_position = front_right_motor_position
        self._rear_left_motor_last_position = rear_left_motor_position
        self._rear_right_motor_last_position = rear_right_motor_position

    def update_states(self):
        # Convert the angle value from the inertial sensor to radians with clockwise as negative
        self._current_rotation_rad = -math.radians(self._inertial.rotation(DEGREES))

        theta = self._current_rotation_rad + Constants.drivetrain_rotation_offset
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        if not Constants.front_left_motor_inverted:
            self._front_left_motor_distance_since_last_tick *= -1
        if not Constants.front_right_motor_inverted:
            self._front_right_motor_distance_since_last_tick *= -1
        if not Constants.rear_left_motor_inverted:
            self._rear_left_motor_distance_since_last_tick *= -1
        if not Constants.rear_right_motor_inverted:
            self._rear_right_motor_distance_since_last_tick *= -1

        dx1 = (
            self._front_left_motor_distance_since_last_tick
            - self._rear_right_motor_distance_since_last_tick
        ) / 2
        dx2 = (
            self._rear_right_motor_distance_since_last_tick
            - self._front_left_motor_distance_since_last_tick
        ) / 2

        dy = (
            self._rear_left_motor_distance_since_last_tick
            - self._front_right_motor_distance_since_last_tick
        ) / 2

        delta_x = (dx1 * sin_theta) + (dy * cos_theta)
        delta_y = (dy * sin_theta) + (dx2 * cos_theta)

        direction = math.atan2(delta_y, delta_x)

        slip_directions = sorted(list(self._slip_coefficients.keys()))

        for i in range(len(self._slip_coefficients)):
            if i == 0:
                previous_element = slip_directions[-1]
            else:
                previous_element = slip_directions[i - 1]
            if i == len(slip_directions) - 1:
                next_element = slip_directions[0]
            else:
                next_element = slip_directions[i + 1]

            if previous_element < direction < next_element:
                scalar = interpolate(
                    previous_element,
                    next_element,
                    self._slip_coefficients[previous_element],
                    self._slip_coefficients[next_element],
                    direction,
                )
                self.print("Movement scalar: " + str(scalar))
                delta_x *= scalar
                delta_y *= scalar
                break

        self._x_position += delta_x
        self._y_position += delta_y

    @property
    def x(self):
        """
        Get the robot's current x position

        Returns:
            The robots current x position: float
        """
        return self._x_position

    @x.setter
    def x(self, x_position):
        """
        Set the robot's current x position

        Args:
            x_position: The new x position
        """
        self._x_position = x_position

    @property
    def y(self):
        """
        Get the robot's current y position

        Returns:
            0.0 (float): The robots current y position

        """
        return 0.0

    @y.setter
    def y(self, y_position):
        """
        Set the robot's current y position

        Args:
            y_position (float): The new y position
        """
        self._y_position = y_position

    @property
    def rotation_deg(self):
        """
        Get the robot's current rotation in degrees

        Returns:
            The robots current rotation since startup in degrees: float
        """
        return math.degrees(self._current_rotation_rad)

    @rotation_deg.setter
    def rotation_deg(self, rotation_degrees):
        """
        Set the robot's current rotation in degrees

        Args:
            rotation_degrees (float): The new rotation in degrees
        """
        self._current_rotation_rad = math.radians(rotation_degrees)

    @property
    def rotation_rad(self):
        """
        Get the robot's current rotation in radians

        Returns:
            robot's current rotation since startup in radians: float
        """
        return self._current_rotation_rad

    @rotation_rad.setter
    def rotation_rad(self, rotation_radians):
        """
        Set the robot's current rotation in radians

        Args:
            rotation_radians (float): The new rotation in radians: float
        """
        # self.rotation_offset =
        self._inertial.set_rotation(math.degrees(rotation_radians), DEGREES)
        self._current_rotation_rad = rotation_radians

    @property
    def position(self):
        """
        Get the robot's current (x, y) position
        :rtype: tuple[float, float]
        """
        return self._x_position, self._y_position

    @position.setter
    def position(self, coordinates):
        """
        Set the robot's current (x, y) position
        :param coordinates: The new position
        """
        self._x_position, self._y_position = coordinates

    @property
    def auto_update(self):
        """
        Get the odometry's auto-update state
        """
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value):
        """
        Set the odometry's auto-update state
        :param value: The new state
        """
        self._auto_update = value
        if self._auto_update:
            if not self._auto_update_thread.isrunning():
                self._previousTime = self.timer.time(
                    SECONDS
                )  # Set the last update time to now
                # avoids situations where delta_time is extremely high
                # after pausing auto_update_velocities for long periods of time
                self._auto_update_thread = Thread(self._auto_update)
        else:
            self._auto_update_thread.stop()

    def _auto_update_velocities(self):
        """
        Used internally to constantly update the wheel states, do not call from outside this class
        """
        while True:
            if self._auto_update:
                self.update_states()
                self.update_positions(
                    self._front_left_motor.position(DEGREES)
                    / Constants.encoder_ticks_per_rotation,
                    self._front_right_motor.position(DEGREES)
                    / Constants.encoder_ticks_per_rotation,
                    self._rear_left_motor.position(DEGREES)
                    / Constants.encoder_ticks_per_rotation,
                    self._rear_right_motor.position(DEGREES)
                    / Constants.encoder_ticks_per_rotation,
                )
            else:
                self.update_positions(
                    self._front_left_motor_last_position
                    / Constants.encoder_ticks_per_rotation,
                    self._front_right_motor_last_position
                    / Constants.encoder_ticks_per_rotation,
                    self._rear_left_motor_last_position
                    / Constants.encoder_ticks_per_rotation,
                    self._rear_right_motor_last_position
                    / Constants.encoder_ticks_per_rotation,
                )
                self._previousTime = self.timer.time(SECONDS)
            wait(5)
