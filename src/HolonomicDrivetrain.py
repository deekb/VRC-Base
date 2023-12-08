from HolonomicOdometry import Odometry
import Constants
import math
from Utilities import *
import TrapezoidMovement

x_axis = Constants.ControllerAxis.x_axis
y_axis = Constants.ControllerAxis.y_axis


class Drivetrain:
    """
    A drivetrain controller for a holonomic drive base
    """

    def __init__(self, timer: Brain.timer, terminal: Terminal = None):
        """
        Initialize a new drivetrain with the specified properties
        :param timer: A brain.timer() object used for getting delta times
        :type timer: Brain.timer()
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

        self._front_left_motor = Motor(
            Constants.front_left_motor_port,
            Constants.front_left_motor_gear_ratio,
            Constants.front_left_motor_inverted,
        )
        self._front_right_motor = Motor(
            Constants.front_right_motor_port,
            Constants.front_right_motor_gear_ratio,
            Constants.front_right_motor_inverted,
        )
        self._rear_left_motor = Motor(
            Constants.rear_left_motor_port,
            Constants.rear_left_motor_gear_ratio,
            Constants.rear_left_motor_inverted,
        )
        self._rear_right_motor = Motor(
            Constants.rear_right_motor_port,
            Constants.rear_right_motor_gear_ratio,
            Constants.rear_right_motor_inverted,
        )
        self._inertial = Inertial(Constants.inertial_sensor_port)

        self._front_left_wheel_rotation_rad = Constants.front_left_wheel_rotation_rad
        self._front_right_wheel_rotation_rad = Constants.front_right_wheel_rotation_rad
        self._rear_left_wheel_rotation_rad = Constants.rear_left_wheel_rotation_rad
        self._rear_right_wheel_rotation_rad = Constants.rear_right_wheel_rotation_rad

        self._movement_allowed_error = Constants.drivetrain_allowed_positional_error_cm
        self._wheel_circumference_cm = Constants.wheel_circumference_cm
        self.rotation_PID = PIDController(
            self.timer,
            Constants.drivetrain_turn_Kp,
            Constants.drivetrain_turn_Ki,
            Constants.drivetrain_turn_Kd,
        )

        self._rotation_PID_output = 0

        self._current_target_direction = 0
        self._current_target_x_cm = 0
        self._current_target_y_cm = 0

        self._front_left_motor.set_velocity(0, PERCENT)
        self._front_right_motor.set_velocity(0, PERCENT)
        self._rear_left_motor.set_velocity(0, PERCENT)
        self._rear_right_motor.set_velocity(0, PERCENT)

        self._front_left_motor.spin(FORWARD)
        self._front_right_motor.spin(FORWARD)
        self._rear_left_motor.spin(FORWARD)
        self._rear_right_motor.spin(FORWARD)

        self._odometry = Odometry(
            self._front_left_motor,
            self._front_right_motor,
            self._rear_left_motor,
            self._rear_right_motor,
            timer=self.timer,
            inertial=self._inertial,
            terminal=self.terminal,
        )

    def calibrate_inertial_sensor(self):
        self._inertial.calibrate()
        while self._inertial.is_calibrating():
            wait(5, MSEC)

    def move_to_position(self, target_position, speed: float) -> None:
        """
        Move to the specified position
        :param target_position: The position to mave to
        :type target_position: tuple[float, float]
        :param speed: The speed (0-1) for the move
        :type speed: float
        """

        # Ensure the drivetrain doesn't jerk when we start the move
        self.clear_direction_PID_output()
        self.stop()

        # Set the target_x and target_y from the target position
        self._current_target_x_cm, self._current_target_y_cm = target_position

        # While the distance between our current position and our target position is greater than tha allowed movement error
        # continuously calculate the direction we need to travel to reach the target and the remaining distance
        while (
            hypotenuse(
                target_position[0] - self._odometry.x,
                target_position[1] - self._odometry.y,
            )
            > self._movement_allowed_error
        ):
            # Calculate the direction to move in the reach the target
            direction_rad = math.atan2(
                self._current_target_y_cm - self._odometry.y,
                self._current_target_x_cm - self._odometry.x,
            )

            # calculate the remaining distance to move
            distance_cm = hypotenuse(
                self._current_target_x_cm - self._odometry.x,
                self._current_target_y_cm - self._odometry.y,
            )

            # Update the rotation PID to keep us facing the same direction throughout the move
            self.update_direction_PID()
            self.move_headless(direction_rad, speed, 0)
        self.stop()

    def move_to_position_trap(
        self, target_position, speed: float, acceleration_time, deceleration_time
    ) -> None:
        """
        Move to the specified position
        :param target_position: The position to mave to
        :type target_position: tuple[float, float]
        :param speed: The speed (0-1) for the move
        :type speed: float
        """
        # Ensure the drivetrain doesn't jerk when we start the move
        self.clear_direction_PID_output()
        self.stop()

        distance_remaining_pid = PIDController(self.timer, kp=0.01)

        # Set the target_x and target_y from the target position
        self._current_target_x_cm, self._current_target_y_cm = target_position

        distance_remaining = hypotenuse(
            self._current_target_y_cm - self._odometry.y,
            self._current_target_x_cm - self._odometry.x,
        )

        distance_remaining_pid.setpoint = distance_remaining

        movement_constraints = TrapezoidMovement.Constraints(1, 0.2)

        initial_state = TrapezoidMovement.State(distance_remaining, 0)
        goal_state = TrapezoidMovement.State(0, 0)

        movement_profile = TrapezoidMovement.TrapezoidProfile(movement_constraints)

        start_time = self.timer.time(SECONDS)

        # While the distance between our current position and our target position is greater than tha allowed movement error
        # continuously calculate the direction we need to travel to reach the target and the remaining distance
        while distance_remaining > self._movement_allowed_error:
            current_time = self.timer.time(SECONDS)
            elapsed_time = current_time - start_time

            # Calculate the direction to move in the reach the target
            direction_rad = math.atan2(
                self._current_target_y_cm - self._odometry.y,
                self._current_target_x_cm - self._odometry.x,
            )

            # calculate the remaining distance to move
            distance_remaining = hypotenuse(
                self._current_target_x_cm - self._odometry.x,
                self._current_target_y_cm - self._odometry.y,
            )

            # Update the rotation PID to keep us facing the same direction throughout the move
            self.update_direction_PID()

            target_state = movement_profile.calculate(
                elapsed_time, initial_state, goal_state
            )

            # Get our target speed from the movement profile
            distance_remaining_pid.setpoint = target_state.position

            speed = distance_remaining_pid.update(-distance_remaining)

            self.print("distance_remaining: " + str(distance_remaining))
            self.print("distance_remaining_pid.setpoint: " + str(distance_remaining_pid.setpoint))
            self.print("distance_remaining_pid output: " + str(speed))
            self.print("target_state: " + str(target_state))
            self.print("target_state.position: " + str(target_state.position))
            self.print("target_state.velocity: " + str(target_state.velocity))
            self.print("elapsed_time: " + str(elapsed_time))
            self.print("movement_profile.isFinished: " + str(movement_profile.isFinished(elapsed_time)))

            if movement_profile.isFinished(elapsed_time):
                # We have overshot
                break

            self.move_headless(direction_rad, speed, 0)
            wait(50, MSEC)
        self.stop()

    def follow_path(self, point_list, maximum_speed):
        for point in point_list:
            self.move_to_position(point, maximum_speed)
        self.stop()

    def move_towards_direction_for_distance(self, direction, distance_cm, speed):
        delta_x = math.cos(direction) * distance_cm
        delta_y = math.sin(direction) * distance_cm

        self.move_to_position(
            (self._current_target_x_cm + delta_x, self._current_target_y_cm + delta_y),
            speed,
            # 2,
            # 2,
        )

    def forward(self, distance_cm, speed=1, field_relative=False):
        movement_direction = math.pi / 2
        if not field_relative:
            movement_direction += self.rotation_PID.setpoint

        self.move_towards_direction_for_distance(movement_direction, distance_cm, speed)

    def backwards(self, distance_cm, speed=1, field_relative=False):
        movement_direction = -math.pi / 2
        if not field_relative:
            movement_direction += self.rotation_PID.setpoint

        self.move_towards_direction_for_distance(movement_direction, distance_cm, speed)

    def strafe_left(self, distance_cm, speed=1, field_relative=False):
        movement_direction = math.pi
        if not field_relative:
            movement_direction += self.rotation_PID.setpoint

        self.move_towards_direction_for_distance(movement_direction, distance_cm, speed)

    def strafe_right(self, distance_cm, speed=1, field_relative=False):
        movement_direction = 0
        if not field_relative:
            movement_direction += self.rotation_PID.setpoint

        self.move_towards_direction_for_distance(movement_direction, distance_cm, speed)

    def move(self, direction, speed, spin) -> None:
        spin += self._rotation_PID_output
        # self.clear()
        # self.print(spin)
        # self.print(self._rotation_PID_output)

        speed = clamp(speed, 0, 1)  # This will ensure that speed is between 0 and 1
        spin = clamp(spin, -1, 1)  # This will ensure that spin is between -1 and 1

        target_front_left_wheel_speed = calculate_wheel_power(
            direction, speed, self._front_left_wheel_rotation_rad
        ) + (spin if Constants.front_left_motor_inverted else -spin)
        target_front_right_wheel_speed = calculate_wheel_power(
            direction, speed, self._front_right_wheel_rotation_rad
        ) + (spin if Constants.front_right_motor_inverted else -spin)
        target_rear_left_wheel_speed = calculate_wheel_power(
            direction, speed, self._rear_left_wheel_rotation_rad
        ) + (spin if Constants.rear_left_motor_inverted else -spin)
        target_rear_right_wheel_speed = calculate_wheel_power(
            direction, speed, self._rear_right_wheel_rotation_rad
        ) + (spin if Constants.rear_right_motor_inverted else -spin)

        maximum_power = max(
            target_front_left_wheel_speed,
            target_front_right_wheel_speed,
            target_rear_left_wheel_speed,
            target_rear_right_wheel_speed,
        )

        if maximum_power > 1:
            # At least one of the motor velocities are over the maximum possible velocity
            # This will result in clipping, meaning that the motor speeds will be "clipped" off to the maximum (1)
            # We will lose some control of our turning while we are moving quickly
            # To solve this issue we can detect if any motor velocities exceed the maximum possible velocity and
            # Use the inverse of the maximum motor power as a salar by dividing by it.
            # This wil always output all values in a range from 0-1
            target_front_left_wheel_speed /= maximum_power
            target_front_right_wheel_speed /= maximum_power
            target_rear_left_wheel_speed /= maximum_power
            target_rear_right_wheel_speed /= maximum_power

        self._front_left_motor.set_velocity(
            target_front_left_wheel_speed * 142.8, PERCENT
        )
        self._front_right_motor.set_velocity(
            target_front_right_wheel_speed * 142.8, PERCENT
        )
        self._rear_left_motor.set_velocity(target_rear_left_wheel_speed * 142.8, PERCENT)
        self._rear_right_motor.set_velocity(
            target_rear_right_wheel_speed * 142.8, PERCENT
        )

    def move_headless(self, direction, magnitude, spin):
        direction -= (
            self._odometry.rotation_rad
        )  # Factor out the robot's current rotation from the desired direction
        self.move(direction, magnitude, spin)

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
            math.atan2(self._odometry.y - position[1], self._odometry.x - position[0])
            + math.pi / 2
        )
        # We add math.pi / 2  to direction_to_point because on the drivetrain 0 degrees is actually on the right. This means we must shift our atan2 calculation
        # in order to point the front of the robot towards the target
        self.turn_to_face_heading_rad(direction_to_point)

    def turn_to_face_heading_rad(self, heading_rad, wait_=True):
        # Calculate the optimal turn, this will return a number between -pi and pi
        # that the drivetrain should rotate in order to end facing the correct direction
        angular_difference = self.calculate_optimal_turn(heading_rad)
        self.rotation_PID.setpoint += angular_difference
        if wait_:
            while (
                abs(self._odometry.rotation_rad - self.rotation_PID.setpoint)
                > Constants.drivetrain_allowed_directional_error_rad
            ):
                self.update_direction_PID()
                self.stop()  # In order to not move but continue turning
                wait(5, MSEC)

    def turn_to_face_heading_deg(self, heading_deg, wait_=True):
        # Calculate the optimal turn, this will return a number between -pi and pi
        # that the drivetrain should rotate in order to end facing the correct direction
        angular_difference = self.calculate_optimal_turn(math.radians(heading_deg))
        self.rotation_PID.setpoint += angular_difference
        if wait_:
            while (
                abs(self._odometry.rotation_rad - self.rotation_PID.setpoint)
                > Constants.drivetrain_allowed_directional_error_rad
            ):
                self.update_direction_PID()
                self.stop()  # In order to not move but continue turning
                wait(5, MSEC)

    def stop(self):
        self.move(0, 0, 0)

    def update_direction_PID(self):
        self._rotation_PID_output = self.rotation_PID.update(self.current_direction_rad)

    def clear_direction_PID_output(self):
        self._rotation_PID_output = 0

    def reset(self) -> None:
        """
        Reset all the drivetrain to its newly instantiated state
        """
        self._front_left_motor.set_velocity(0, PERCENT)
        self._front_right_motor.set_velocity(0, PERCENT)
        self._rear_left_motor.set_velocity(0, PERCENT)
        self._rear_right_motor.set_velocity(0, PERCENT)
        self._front_left_motor.spin(FORWARD)
        self._front_right_motor.spin(FORWARD)
        self._rear_left_motor.spin(FORWARD)
        self._rear_right_motor.spin(FORWARD)
        if self._inertial:
            self._inertial.set_heading(0, DEGREES)
        self._rotation_PID_output = 0
        self.rotation_PID.setpoint = 0
        self._current_target_direction = 0
        self._current_target_x_cm = 0
        self._current_target_y_cm = 0
        self._odometry.reset()

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
    def current_position(self):
        return self._odometry.position

    @current_position.setter
    def current_position(self, position):
        # When setting the position, it is automatically set as the targeted position
        self._odometry.position = position
        self._current_target_x_cm, self._current_target_y_cm = position

    @property
    def current_direction_rad(self):
        return self._odometry.rotation_rad

    @current_direction_rad.setter
    def current_direction_rad(self, rotation_rad):
        self._odometry.rotation_rad = rotation_rad
        self.target_heading_rad = rotation_rad

    @property
    def target_heading_rad(self) -> float:
        """
        Get the current target heading in radians
        :returns: The current target heading of the robot in radians (use heading_deg for degrees)
        """
        return self.rotation_PID.setpoint

    @target_heading_rad.setter
    def target_heading_rad(self, heading) -> None:
        """
        Set the current target heading in radians
        :param heading: New target heading in radians
        """
        self.rotation_PID.setpoint = heading

    @property
    def target_heading_deg(self) -> float:
        """
        Get the current target heading in degrees
        :returns: The current target heading of the robot in degrees (use heading_deg for radians)
        """
        return math.degrees(self.rotation_PID.setpoint)

    @target_heading_deg.setter
    def target_heading_deg(self, heading) -> None:
        """
        Set the current target heading in degrees
        :param heading: New target heading in degrees
        """
        self.rotation_PID.setpoint = math.radians(heading)

    def set_braking(self, braking):
        if braking:
            self._front_left_motor.set_stopping(BRAKE)
            self._front_right_motor.set_stopping(BRAKE)
            self._rear_left_motor.set_stopping(BRAKE)
            self._rear_right_motor.set_stopping(BRAKE)
        else:
            self._front_left_motor.set_stopping(COAST)
            self._front_right_motor.set_stopping(COAST)
            self._rear_left_motor.set_stopping(COAST)
            self._rear_right_motor.set_stopping(COAST)
