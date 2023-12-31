"""
Competition codebase for Vex robotics
Team: 3773P (Bowbots Phosphorus) from Bow NH
Author: Derek Baier (deekb on GitHub)
Project homepage: https://github.com/deekb/VRC-Base
Project archive: https://github.com/deekb/VRC-Base/archive/master.zip
Contact Derek.m.baier@gmail.com for more information

The code is developed for Team 3773P, known as Bowbots Phosphorus, and is authored by Derek Baier.

The project homepage and archive can be found on GitHub at the provided links.

For more information about the project, you can contact Derek Baier at the given email address.
"""

__title__ = "Vex V5 2023 Competition code"
__description__ = "Competition Code for VRC: Over-Under 2023-2024"
__team__ = "3773P (Bowbots Phosphorus)"
__url__ = "https://github.com/deekb/VRC-OverUnder"
__download_url__ = "https://github.com/deekb/VRC-OverUnder/archive/master.zip"
__version__ = "Working"
__author__ = "Derek Baier"
__author_email__ = "Derek.m.baier@gmail.com"
__license__ = "MIT"

import math

import Constants
from Autonomous import (
    ScoringAutonomous,
    ScoringAutonomous4,
    SabotageAutonomous,
    NothingAutonomous,
    SkillsAutonomous,
    WinPointAutonomous
)
from Catapult import Catapult
from Climber import Climber
from HolonomicDrivetrain import Drivetrain
from PneumaticWings import Wings
from RollerIntake import Intake
from SetupUI import SetupUI
from Utilities import *
from vex import *

brain = Brain()


class Robot:
    """
    Represents a robot
    """

    def __init__(self, brain):
        self.brain = brain
        self.terminal = Terminal(self.brain)
        self.print = self.terminal.print
        self.clear = self.terminal.clear

        self.drivetrain_position_log = Logging(log_name="Drivetrain_Position")

        self.primary_controller = Controller(PRIMARY)
        self.secondary_controller = Controller(PARTNER)

        self.driver_control_threads = []
        self.autonomous_threads = []
        self.setup_complete = False

        self.disable_driver_control = False

        self.autonomous_task = NothingAutonomous
        self.autonomous_startup_position = (0, 0)

        self.drivetrain = Drivetrain(timer=self.brain.timer, terminal=self.terminal)

        self.intake = Intake()

        self.wings = Wings()

        self.catapult_motor = Motor(
            Constants.catapult_motor_port,
            Constants.catapult_motor_gear_ratio,
            Constants.catapult_motor_inverted,
        )
        self.catapult = Catapult(self.catapult_motor)

        self.climber_motor = Motor(
            Constants.climber_motor_port,
            Constants.climber_motor_gear_ratio,
            Constants.climber_motor_inverted,
        )

        self.climber = Climber(self.climber_motor)

        self.drivetrain.set_braking(Constants.drivetrain_braking)

        # Register the competition handler
        self.competition = Competition(self.driver_handler, self.autonomous_handler)

    def on_autonomous(self):
        """
        Runs when the competition is switched to autonomous mode
        """
        # Ensure setup is complete
        if not self.setup_complete:
            print("[on_autonomous]: setup not complete, can't start autonomous")
            return
        autonomous_log_object = Logging(log_name="Autonomous")

        autonomous = self.autonomous_task(
            autonomous_log_object,
            self.drivetrain,
            self.intake,
            self.catapult,
            self.wings,
            self.terminal,
            self.autonomous_startup_position,
        )
        autonomous.run()

    def on_driver_control(self):
        """
        Runs when the competition is switched to driver controlled mode
        """
        # Wait for setup to finish
        while not self.setup_complete:
            wait(5)
        while True:
            if not self.disable_driver_control:
                # The joysticks report outputs in the range -100 to 100, but it is easier to do math on inputs in the range
                # 0 to 1, so we multiply the inputs by 0.01 (same as dividing by 100 but slightly more computationally efficient)
                left_stick = (
                    clamp(self.primary_controller.axis4.position() * 0.01, -1, 1),
                    clamp(self.primary_controller.axis3.position() * 0.01, -1, 1),
                )
                right_stick = (
                    clamp(self.primary_controller.axis1.position() * 0.01, -1, 1),
                    clamp(self.primary_controller.axis1.position() * 0.01, -1, 1),
                )

                left_stick = (
                    apply_deadzone(left_stick[0], Constants.movement_deadzone, 1),
                    apply_deadzone(left_stick[1], Constants.movement_deadzone, 1),
                )

                movement_direction = math.atan2(left_stick[1], left_stick[0])

                movement_speed = hypotenuse(left_stick[0], left_stick[1])

                # Apply a deadzone to the turning amount
                deadzoned_right_x = apply_deadzone(
                    right_stick[0], Constants.turn_deadzone, 1
                )

                # Normalize the turning amount across a cubic curve
                normalized_right_x = cubic_filter(
                    deadzoned_right_x, Constants.turn_cubic_linearity
                )

                if Constants.headless_mode:
                    self.drivetrain.move_headless(
                        movement_direction, movement_speed, -normalized_right_x
                    )
                else:
                    self.drivetrain.move(
                        movement_direction, movement_speed, -normalized_right_x
                    )

                if self.primary_controller.buttonL1.pressing():
                    self.intake.pull_in()
                elif self.primary_controller.buttonR1.pressing():
                    self.intake.spit_out()
                else:
                    self.intake.stop()

                if self.primary_controller.buttonA.pressing():
                    self.catapult.start_firing()
                else:
                    self.catapult.stop_firing()

                if self.primary_controller.buttonY.pressing():
                    self.wings.wings_out()
                else:
                    self.wings.wings_in()

                if self.primary_controller.buttonL2.pressing():
                    self.climber.set_velocity(1)
                elif self.primary_controller.buttonR2.pressing():
                    self.climber.set_velocity(-1)
                else:
                    self.climber.set_velocity(0)

    def debug_thread(self):
        # Runs as a background thread during driver control to provide debugging functionality
        while True:
            # self.drivetrain_position_log.log(
            #     str(self.brain.timer.time(SECONDS))
            #     + ", "
            #     + str(self.drivetrain.current_position)
            #     + ", "
            #     + str(self.drivetrain.current_direction_rad)
            #     + "\n"
            # )
            wait(20, MSEC)
            # if self.primary_controller.buttonLeft.pressing():
            #     self.drivetrain.turn_to_face_heading_deg(90)
            #     for _ in range(100):
            #         self.drivetrain.update_direction_PID()
            #         self.drivetrain.stop()
            #         wait(10, MSEC)
            #     self.drivetrain.rotation_PID.setpoint = (
            #         self.drivetrain.current_direction_rad
            #     )
            #     self.drivetrain.clear_direction_PID_output()
            #     self.drivetrain.target_position = self.drivetrain.current_position
            # elif self.primary_controller.buttonRight.pressing():
            #     self.drivetrain.turn_to_face_heading_deg(0)
            #     for _ in range(100):
            #         self.drivetrain.update_direction_PID()
            #         self.drivetrain.stop()
            #         wait(10, MSEC)
            #     self.drivetrain.rotation_PID.setpoint = (
            #         self.drivetrain.current_direction_rad
            #     )
            #     self.drivetrain.clear_direction_PID_output()
            #     self.drivetrain.target_position = self.drivetrain.current_position

    def display_thread(self):
        # Runs as a background thread during driver control to display information about the robot on the screen
        def field_coordinates_to_screen_coordinates(position):
            """
            Convert x,y coordinates from the field (0,0 at bottom left) to the screen (0,0 at top left)

            Args:
                position: The position to convert

            Returns:
                The converted position
            """
            x, y = position
            x *= (Constants.screen_size_x / 2) / Constants.field_x_size
            y *= Constants.screen_size_y / Constants.field_y_size

            y = Constants.screen_size_y - y  # Flip Y axis
            return x, y

        while not self.setup_complete:
            wait(10, MSEC)
        self.brain.screen.clear_screen()
        self.brain.screen.set_fill_color(Color.WHITE)
        while True:
            self.brain.screen.draw_image_from_file(
                Constants.deploy_directory + "Field.png", 240, 0
            )

            current_x, current_y = field_coordinates_to_screen_coordinates(
                self.drivetrain.current_position
            )
            target_x, target_y = field_coordinates_to_screen_coordinates(
                self.drivetrain.target_position
            )

            self.brain.screen.set_pen_color(Color.CYAN)
            self.brain.screen.set_fill_color(Color.CYAN)

            self.brain.screen.draw_circle(
                current_x + Constants.screen_size_x / 2, current_y, 3
            )

            self.brain.screen.set_pen_color(Color.RED)
            self.brain.screen.set_fill_color(Color.RED)

            self.brain.screen.draw_circle(
                target_x + Constants.screen_size_x / 2, target_y, 3
            )

            wait(100, MSEC)

    def autonomous_handler(self):
        """
        This function is run by the competition handler "self.competition" whenever the controller is connected and
        either no competition switch is connected, or the competition switch connected to the controller is set to
        "autonomous enabled"
        """
        while not self.setup_complete and (
            self.competition.is_autonomous() and self.competition.is_enabled()
        ):
            wait(5, MSEC)

        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()
        self.clear()

        for _function in (self.on_autonomous,):
            self.autonomous_threads.append(Thread(_function))
        self.print("Started autonomous")
        while self.competition.is_autonomous() and self.competition.is_enabled():
            wait(10, MSEC)
        for thread in self.autonomous_threads:
            thread.stop()

    def driver_handler(self):
        """
        This function is run by the competition handler "self.competition" whenever the controller and competition
        switch are connected and set to "driver control enabled"
        """
        while not self.setup_complete and (
            self.competition.is_driver_control() and self.competition.is_enabled()
        ):
            wait(5, MSEC)

        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()
        self.clear()

        for _function in (
            self.on_driver_control,
            self.debug_thread,
            self.display_thread,
        ):
            self.driver_control_threads.append(Thread(_function))

        self.print("Started all driver control tasks")
        while self.competition.is_driver_control() and self.competition.is_enabled():
            wait(10, MSEC)
        for thread in self.driver_control_threads:
            thread.stop()
        self.print("Stopped all driver control tasks")

    def setup_controller_bindings(self):
        """
        Run when the robot boots up, after the setup process, sets up controller button callbacks
        """
        # self.primary_controller.buttonL1.pressed(
        #     lambda: setattr(self.drivetrain, "target_heading_deg", 0)
        # )
        # self.primary_controller.buttonL2.pressed(
        #     lambda: setattr(self.drivetrain, "target_heading_deg", 90)
        # )
        # self.primary_controller.buttonR1.pressed(
        #     lambda: setattr(self.drivetrain, "target_heading_deg", 180)
        # )
        # self.primary_controller.buttonR2.pressed(
        #     lambda: setattr(self.drivetrain, "target_heading_deg", 270)
        # )

    def main(self):
        """
        initializes and sets up the robot, including calibrating sensors, selecting an autonomous routine, and setting
        a startup position for the robot
        """
        if not Constants.skip_setup:
            setup_ui = SetupUI(self.terminal, self.brain.screen)

            while not setup_ui.finished:
                wait(10, MSEC)
                setup_ui.tick()

            self.brain.screen.set_fill_color(Color.TRANSPARENT)

            self.brain.screen.set_pen_color(Color.WHITE)
            self.print("Team: " + str(setup_ui.team))
            self.print("Position: " + str(setup_ui.robot_position))
            wait(1000, MSEC)

            if setup_ui.team == Constants.Team.skills:
                self.autonomous_task = SkillsAutonomous  # WinPointAutonomous
            else:
                if setup_ui.robot_position == Constants.defensive | Constants.red:
                    self.autonomous_task = SabotageAutonomous
                elif setup_ui.robot_position == Constants.defensive | Constants.blue:
                    self.autonomous_task = SabotageAutonomous
                elif setup_ui.robot_position == Constants.offensive | Constants.red:
                    self.autonomous_task = ScoringAutonomous
                elif setup_ui.robot_position == Constants.offensive | Constants.blue:
                    self.autonomous_task = ScoringAutonomous

        self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.set_pen_color(Color.WHITE)

        self.drivetrain.calibrate_inertial_sensor()
        self.climber.calibrate()

        # Ensure you set the direction of the robot after the inertial sensor is calibrated or calibrating will wipe your setting
        self.drivetrain.current_position = Constants.robot_start_position
        self.autonomous_startup_position = Constants.robot_start_position
        self.drivetrain.current_direction_rad = math.radians(
            Constants.robot_start_rotation_deg
        )
        self.drivetrain.target_heading_rad = Constants.robot_start_rotation_deg

        # Set up controller callbacks here to avoid triggering them by pressing buttons during setup
        self.setup_controller_bindings()

        self.print("Robot:INFO: Setup complete")
        self.primary_controller.rumble(".")
        self.brain.screen.draw_image_from_file(
            Constants.deploy_directory + "Please_Connect_Controller.png", 0, 0
        )
        self.setup_complete = True
