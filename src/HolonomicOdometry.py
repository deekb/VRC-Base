from Utilities import *
import Constants


class Odometry:
    def __init__(
        self,
        motor_1: Motor,
        motor_2: Motor,
        motor_3: Motor,
        motor_4: Motor,
        timer: Brain.timer,
        inertial: Inertial,
        terminal: Terminal = None,
    ) -> None:
        """
        A class for tracking the robot's position and rotation, this class integrates a stream of motor velocities into a position
        This implementation only works on Holonomic drivetrains (Mecanum, and X-drive), but the concept is similar to other odometry implementations
        :param motor_1: Motor 1
        :type motor_1: Motor
        :param motor_2: Motor 2
        :type motor_2: Motor
        :param motor_3: Motor 3
        :type motor_3: Motor
        :param motor_4: Motor 4
        :type motor_4: Motor
        :param terminal: An optional terminal to print debug output to
        :type terminal: Terminal | None
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
        self._motor_1 = motor_1
        self._motor_2 = motor_2
        self._motor_3 = motor_3
        self._motor_4 = motor_4
        self._wheel_1_last_position = (
            self._wheel_2_last_position
        ) = self._wheel_3_last_position = self._wheel_4_last_position = 0
        self._wheel_1_distance_since_last_tick = (
            self._wheel_2_distance_since_last_tick
        ) = (
            self._wheel_3_distance_since_last_tick
        ) = self._wheel_4_distance_since_last_tick = 0
        self._previousTime = self.timer.time(SECONDS)
        self._auto_update = True
        self._inertial = inertial
        if self._auto_update:
            self._auto_update_thread = Thread(self._auto_update_velocities)
        else:
            self._auto_update_thread = None
        self.reset()

    def reset(self) -> None:
        self._x_position = 0
        self._y_position = 0
        if self._inertial is not None:
            self._inertial.set_rotation(0)
        self._current_rotation_rad = 0
        self.current_heading_rad = 0
        self._previousTime = self.timer.time(SECONDS)
        self._wheel_1_last_position = self._motor_1.position(DEGREES) / Constants.encoder_ticks_per_rotation
        self._wheel_2_last_position = self._motor_2.position(DEGREES) / Constants.encoder_ticks_per_rotation
        self._wheel_3_last_position = self._motor_3.position(DEGREES) / Constants.encoder_ticks_per_rotation
        self._wheel_4_last_position = self._motor_4.position(DEGREES) / Constants.encoder_ticks_per_rotation
        self._wheel_1_distance_since_last_tick = 0
        self._wheel_2_distance_since_last_tick = 0
        self._wheel_3_distance_since_last_tick = 0
        self._wheel_4_distance_since_last_tick = 0

    def update_positions(
        self,
        motor_1_position: float,
        motor_2_position: float,
        motor_3_position: float,
        motor_4_position: float,
    ) -> None:
        """
        Updates the algorithm with the current wheel positions
        :param motor_1_position: Motor 1's position
        :param motor_2_position: Motor 2's position
        :param motor_3_position: Motor 3's position
        :param motor_4_position: Motor 4's position
        """

        self._wheel_1_distance_since_last_tick = (motor_1_position - self._wheel_1_last_position) * self._wheel_circumference_cm
        self._wheel_2_distance_since_last_tick = (motor_2_position - self._wheel_2_last_position) * self._wheel_circumference_cm
        self._wheel_3_distance_since_last_tick = (motor_3_position - self._wheel_3_last_position) * self._wheel_circumference_cm
        self._wheel_4_distance_since_last_tick = (motor_4_position - self._wheel_4_last_position) * self._wheel_circumference_cm

        self._wheel_1_last_position = motor_1_position
        self._wheel_2_last_position = motor_2_position
        self._wheel_3_last_position = motor_3_position
        self._wheel_4_last_position = motor_4_position

    def update_states(self) -> None:
        # Convert the angle value from the inertial sensor to radians with clockwise as negative
        self._current_rotation_rad = -math.radians(
            self._inertial.rotation(DEGREES)
        )

        theta = self._current_rotation_rad + Constants.drivetrain_rotation_offset
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        if not Constants.motor_1_inverted:
            self._wheel_1_distance_since_last_tick *= -1
        if not Constants.motor_2_inverted:
            self._wheel_2_distance_since_last_tick *= -1
        if not Constants.motor_3_inverted:
            self._wheel_3_distance_since_last_tick *= -1
        if not Constants.motor_4_inverted:
            self._wheel_4_distance_since_last_tick *= -1

        dx1 = (self._wheel_1_distance_since_last_tick - self._wheel_3_distance_since_last_tick) / 2
        dx2 = (self._wheel_3_distance_since_last_tick - self._wheel_1_distance_since_last_tick) / 2

        dy = (self._wheel_4_distance_since_last_tick - self._wheel_2_distance_since_last_tick) / 2

        delta_x = ((dx1 * sin_theta) + (dy * cos_theta))
        delta_y = ((dy * sin_theta) + (dx2 * cos_theta))

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
                scalar = interpolate(previous_element, next_element, self._slip_coefficients[previous_element], self._slip_coefficients[next_element], direction)
                delta_x *= scalar
                delta_y *= scalar
                break

        self._x_position += delta_x
        self._y_position += delta_y

    @property
    def x(self) -> float:
        """
        Get the robot's current x position
        """
        return self._x_position

    @x.setter
    def x(self, x_position) -> None:
        """
        Set the robot's current x position
        :param x_position: The new x position
        """
        self._x_position = x_position

    @property
    def y(self) -> float:
        """
        Get the robot's current y position
        """
        return self._y_position

    @y.setter
    def y(self, y_position) -> None:
        """
        Set the robot's current y position
        :param y_position: The new y position
        """
        self._y_position = y_position

    @property
    def rotation_deg(self) -> float:
        """
        Get the robot's current rotation in degrees
        """
        return math.degrees(self._current_rotation_rad)

    @rotation_deg.setter
    def rotation_deg(self, rotation_degrees) -> None:
        """
        Set the robot's current rotation in degrees
        :param rotation_degrees: The new rotation
        """
        self._current_rotation_rad = math.radians(rotation_degrees)

    @property
    def rotation_rad(self) -> float:
        """
        Get the robot's current rotation in radians
        """
        return self._current_rotation_rad

    @rotation_rad.setter
    def rotation_rad(self, rotation_radians) -> None:
        """
        Set the robot's current rotation in radians
        :param rotation_radians: The new rotation
        """
        self._current_rotation_rad = rotation_radians

    def get_heading_deg(self):
        return math.degrees(self._current_rotation_rad % (math.pi * 2))

    def get_heading_rad(self):
        return self._current_rotation_rad % (math.pi * 2)

    @property
    def position(self) -> tuple:
        """
        Get the robot's current (x, y) position
        :rtype: tuple[float, float]
        """
        return self._x_position, self._y_position

    @position.setter
    def position(self, coordinates) -> None:
        """
        Set the robot's current (x, y) position
        :param coordinates: The new position
        """
        self._x_position, self._y_position = coordinates

    @property
    def auto_update(self) -> bool:
        """
        Get the odometry's auto-update state
        """
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value) -> None:
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

    def _auto_update_velocities(self) -> None:
        """
        Used internally to constantly update the wheel states, do not call from outside this class
        """
        while True:
            if self._auto_update:
                self.update_states()
                self.update_positions(
                    self._motor_1.position(DEGREES) / Constants.encoder_ticks_per_rotation,
                    self._motor_2.position(DEGREES) / Constants.encoder_ticks_per_rotation,
                    self._motor_3.position(DEGREES) / Constants.encoder_ticks_per_rotation,
                    self._motor_4.position(DEGREES) / Constants.encoder_ticks_per_rotation,
                )
            else:
                self.update_positions(self._wheel_1_last_position / Constants.encoder_ticks_per_rotation, self._wheel_2_last_position / Constants.encoder_ticks_per_rotation, self._wheel_3_last_position / Constants.encoder_ticks_per_rotation, self._wheel_4_last_position / Constants.encoder_ticks_per_rotation)
                self._previousTime = self.timer.time(SECONDS)
            wait(5)
