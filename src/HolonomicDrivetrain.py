from HolonomicOdometry import Odometry
from Utilities import *

x_axis = Constants.ControllerAxis.x_axis
y_axis = Constants.ControllerAxis.y_axis


class Drivetrain:
    """
    A drivetrain controller for a holonomic drive base
    """

    def __init__(self, timer: Brain.timer, terminal: Terminal = None) -> None:
        """
        Initialize a new drivetrain with the specified properties
        :param timer: A brain.timer object used for getting delta times
        :type timer: Brain.timer
        :param terminal: An optional terminal to print debug output to
        :type terminal: Terminal | None
        """
        self.timer = timer
        self.terminal = terminal

        if self.terminal:
            self.print = self.terminal.print
            self.clear = self.terminal.clear
        else:
            self.print, self.clear = lambda *args, **kwargs: None

        self._motor_1 = Motor(
            Constants.motor_1_port,
            Constants.motor_1_gear_ratio,
            Constants.motor_1_inverted,
        )
        self._motor_2 = Motor(
            Constants.motor_2_port,
            Constants.motor_2_gear_ratio,
            Constants.motor_2_inverted,
        )
        self._motor_3 = Motor(
            Constants.motor_3_port,
            Constants.motor_3_gear_ratio,
            Constants.motor_3_inverted,
        )
        self._motor_4 = Motor(
            Constants.motor_4_port,
            Constants.motor_4_gear_ratio,
            Constants.motor_4_inverted,
        )
        self._inertial = Inertial(Constants.inertial_sensor_port)

        self._wheel_1_rotation_rad = Constants.wheel_1_direction_rad
        self._wheel_2_rotation_rad = Constants.wheel_2_direction_rad
        self._wheel_3_rotation_rad = Constants.wheel_3_direction_rad
        self._wheel_4_rotation_rad = Constants.wheel_4_direction_rad
        self._movement_allowed_error = Constants.drivetrain_allowed_positional_error_cm
        self._wheel_circumference_cm = Constants.wheel_circumference_cm
        self._driver_control_deadzone = Constants.driver_control_deadzone
        self._rotation_PID = PIDController(
            self.timer,
            Constants.drivetrain_turn_Kp,
            Constants.drivetrain_turn_Ki,
            Constants.drivetrain_turn_Kd,
        )

        self._rotation_PID_output = 0
        self.auto_update_PID = True

        self._current_target_direction = 0
        self._current_target_x_cm = 0
        self._current_target_y_cm = 0
        self._last_move_with_controller_execution_time = None
        self._current_move_with_controller_execution_time = None
        self._motor_1.set_velocity(0, PERCENT)
        self._motor_2.set_velocity(0, PERCENT)
        self._motor_3.set_velocity(0, PERCENT)
        self._motor_4.set_velocity(0, PERCENT)
        self._motor_1.spin(FORWARD)
        self._motor_2.spin(FORWARD)
        self._motor_3.spin(FORWARD)
        self._motor_4.spin(FORWARD)

        self.odometry = Odometry(
            self._motor_1,
            self._motor_2,
            self._motor_3,
            self._motor_4,
            timer=self.timer,
            inertial=self._inertial,
            terminal=self.terminal,
        )

    def calibrate_inertial_sensor(self):
        self._inertial.calibrate()
        while self._inertial.is_calibrating():
            wait(5, MSEC)

    def move_to_position(self, target_position, maximum_speed: float) -> None:
        """
        Move to the specified position
        :param target_position: The position to mave to
        :type target_position: tuple[float, float]
        :param maximum_speed: The maximum speed between zero and one for the robot
        :type maximum_speed: float
        """
        self._current_target_x_cm, self._current_target_y_cm = target_position
        while (
            hypotenuse(
                target_position[0] - self.odometry.x,
                target_position[1] - self.odometry.y,
            )
            > self._movement_allowed_error
        ):
            # Calculate the direction to move in the reach the target
            direction_rad = math.atan2(
                self._current_target_y_cm - self.odometry.y,
                self._current_target_x_cm - self.odometry.x,
            )

            # calculate the remaining distance to move
            distance_cm = hypotenuse(
                self._current_target_x_cm - self.odometry.x,
                self._current_target_y_cm - self.odometry.y,
            )

            self.move_headless(direction_rad, maximum_speed)
        self.stop()

    def follow_path(self, point_list, maximum_speed):
        for point in point_list:
            self.move_to_position(point, maximum_speed)
        self.stop()

    def move(self, direction, speed, spin=None) -> None:
        if spin is None:
            spin = self._rotation_PID_output
        speed = clamp(speed, 0, 1)
        self._motor_1.set_velocity(
            (
                calculate_wheel_power(direction, speed, self._wheel_1_rotation_rad)
                - (-spin if Constants.motor_1_inverted else spin)
            )
            * 100,
            PERCENT,
        )
        self._motor_2.set_velocity(
            (
                calculate_wheel_power(direction, speed, self._wheel_2_rotation_rad)
                - (-spin if Constants.motor_2_inverted else spin)
            )
            * 100,
            PERCENT,
        )
        self._motor_3.set_velocity(
            (
                calculate_wheel_power(direction, speed, self._wheel_3_rotation_rad)
                - (-spin if Constants.motor_3_inverted else spin)
            )
            * 100,
            PERCENT,
        )
        self._motor_4.set_velocity(
            (
                calculate_wheel_power(direction, speed, self._wheel_4_rotation_rad)
                - (-spin if Constants.motor_4_inverted else spin)
            )
            * 100,
            PERCENT,
        )

    def calculate_optimal_turn(self, target_heading):
        # Calculate the angular difference
        current_heading = self.target_heading_rad % (math.pi * 2)
        target_heading = target_heading % (math.pi * 2)

        angular_difference = target_heading - current_heading

        # Normalize the angular difference between -π and π
        if angular_difference > math.pi:
            angular_difference -= 2 * math.pi
        elif angular_difference < -math.pi:
            angular_difference += 2 * math.pi

        return angular_difference

    def turn_to_face_position(self, position):
        direction_to_point = (
            math.atan2(self.odometry.y - position[1], self.odometry.x - position[0])
            + math.pi / 2
        )  # We add math.pi / 2 because the drivetrain 0 degrees is actually on the right
        self.turn_to_face_heading(direction_to_point)

    def turn_to_face_heading(self, heading_rad):
        angular_difference = self.calculate_optimal_turn(heading_rad)
        self._rotation_PID.target_value += angular_difference

    def stop(self):
        self.move(0, 0)

    def move_headless(self, direction, magnitude, spin=None):
        direction -= (
            self.odometry.rotation_rad
        )  # Factor out the robot's current rotation from the desired direction
        self.move(direction, magnitude, spin)

    def move_with_controller(
        self, controller: Controller, headless: bool = False, PID_turning: bool = False
    ) -> None:
        """
        Move using the controller input

        Args:
            controller: The controller to pull input from
            headless: Whether to move the robot in headless mode
            PID_turning: Whether to control the direction of the drivetrain with PID
        """

        self._current_move_with_controller_execution_time = self.timer.time(SECONDS)
        if self._last_move_with_controller_execution_time is not None:
            delta_time = (
                self._current_move_with_controller_execution_time
                - self._last_move_with_controller_execution_time
            )
        else:
            delta_time = 0
        if delta_time > 0.1:
            self.print("move_with_controller: delta_time > 100ms")
            delta_time = 0

        left_stick = (controller.axis4.position() * 0.01, controller.axis3.position() * 0.01)
        right_stick = (controller.axis1.position() * 0.01, controller.axis1.position() * 0.01)

        movement_direction = math.atan2(left_stick[1], left_stick[0])

        # Normalize the turning amount across a cubic curve
        normalized_right_x = cubic_filter(right_stick[0], Constants.turn_cubic_linearity)

        if PID_turning:
            # The line below uses -= because the PID direction is in positive counterclockwise
            self._rotation_PID.target_value -= (
                normalized_right_x * Constants.driver_control_turn_speed_rad_per_second
            ) * delta_time

        magnitude = hypotenuse(left_stick[0], left_stick[1])

        if headless:
            if PID_turning:
                self.move_headless(movement_direction, magnitude)
            else:
                self.move_headless(movement_direction, magnitude, -normalized_right_x)
        else:
            if PID_turning:
                self.move(movement_direction, magnitude)
            else:
                self.move(movement_direction, magnitude, -normalized_right_x)

        self._last_move_with_controller_execution_time = (
            self._current_move_with_controller_execution_time
        )

    def update_direction_PID(self):
        self._rotation_PID_output = self._rotation_PID.update(
            self.odometry.rotation_rad
        )

    def reset(self) -> None:
        """
        Reset all the drivetrain to its newly instantiated state
        """
        self._motor_1.set_velocity(0, PERCENT)
        self._motor_2.set_velocity(0, PERCENT)
        self._motor_3.set_velocity(0, PERCENT)
        self._motor_4.set_velocity(0, PERCENT)
        self._motor_1.spin(FORWARD)
        self._motor_2.spin(FORWARD)
        self._motor_3.spin(FORWARD)
        self._motor_4.spin(FORWARD)
        if self._inertial:
            self._inertial.set_heading(0, DEGREES)
        self._rotation_PID_output = 0
        self._rotation_PID.target_value = 0
        self._current_target_direction = 0
        self._current_target_x_cm = 0
        self._current_target_y_cm = 0
        self.odometry.reset()

    @property
    def target_position(self) -> tuple:
        """
        Get the position of the robot, useful for displaying on the screen
        :returns: A tuple; x, y
        :rtype: tuple[float, float]
        """
        return self._current_target_x_cm, self._current_target_y_cm

    @target_position.setter
    def target_position(self, position) -> None:
        """
        Set the target position of the robot, useful after calibration to set it to a specific position without modifying heading
        :param position: The robot's new coordinate pair (x, y)
        :type position: tuple[float, float]
        """
        self._current_target_x_cm, self._current_target_y_cm = position

    @property
    def target_heading_rad(self) -> float:
        """
        Get the current target heading in radians
        :returns: The current target heading of the robot in radians (use heading_deg for degrees)
        """
        return self._rotation_PID.target_value

    @target_heading_rad.setter
    def target_heading_rad(self, heading) -> None:
        """
        Set the current target heading in radians
        :param heading: New target heading in radians
        """
        self._rotation_PID.target_value = heading

    @property
    def target_heading_deg(self) -> float:
        """
        Get the current target heading in degrees
        :returns: The current target heading of the robot in degrees (use heading_deg for radians)
        """
        return math.degrees(self._rotation_PID.target_value)

    @target_heading_deg.setter
    def target_heading_deg(self, heading) -> None:
        """
        Set the current target heading in degrees
        :param heading: New target heading in degrees
        """
        self._rotation_PID.target_value = math.radians(heading)

    def set_braking(self, braking):
        if braking:
            self._motor_1.set_stopping(BRAKE)
            self._motor_2.set_stopping(BRAKE)
            self._motor_3.set_stopping(BRAKE)
            self._motor_4.set_stopping(BRAKE)
        else:
            self._motor_1.set_stopping(COAST)
            self._motor_2.set_stopping(COAST)
            self._motor_3.set_stopping(COAST)
            self._motor_4.set_stopping(COAST)
