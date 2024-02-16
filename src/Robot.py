"""
Competition codebase for Vex robotics
Team: 3773P (Bowbots Phosphorus) from Bow NH
Author: Derek Baier (deekb on GitHub)
Project homepage: https://github.com/deekb/VRC-Base
Project archive: https://github.com/deekb/VRC-Base/archive/master.zip
Contact Derek.m.baier@gmail.com for more information

This codebase is developed for Team 3773P, known as Bowbots Phosphorus, and is authored by Derek Baier.

The project homepage and archive can be found on GitHub at the provided links.

For more information about the project, you can contact Derek Baier at the given email address.
"""

# Module-level metadata
__title__ = "Vex V5 2023-2024 Competition code"
__description__ = "Competition Code for VRC: Over-Under 2023-2024"
__team__ = "3773P (Bowbots Phosphorus)"
__url__ = "https://github.com/deekb/VRC-Base"
__download_url__ = "https://github.com/deekb/VRC-Base/archive/master.zip"
__version__ = "Working"
__author__ = "Derek Baier"
__author_email__ = "Derek.m.baier@gmail.com"
__license__ = "MIT"

# Standard library imports
import math

# Third-party imports
from vex import *

# Local or project-specific imports
from Autonomous import (
    NothingAutonomous,
    WinPointAutonomous,
    ScoringAutonomous4,
    SkillsAutonomous,
)
from Catapult import Catapult
from Climber import Climber
from HolonomicDrivetrain import Drivetrain
from PneumaticWings import Wings
from RollerIntake import Intake
from SetupUI import SetupUI
import Constants
from Utilities import *


class Robot:
    """
    Represents a robot
    """

    def __init__(self, brain):
        # Brain and Terminal-related variables
        self.brain = brain
        self.terminal = Terminal(self.brain)
        self.print = self.terminal.print
        self.clear = self.terminal.clear

        # Controllers
        self.primary_controller = Controller(PRIMARY)
        self.secondary_controller = Controller(PARTNER)

        # Robot Subsystems
        self.intake = Intake()
        self.climber = Climber()
        self.wings = Wings()
        self.catapult = Catapult()
        self.drivetrain = Drivetrain(timer=self.brain.timer, terminal=self.terminal)

        # Threads and Flags
        self.driver_control_threads = []
        self.autonomous_threads = []
        self.setup_complete = False
        self.started_skills_driver_assist_maneuver = False
        self.disable_driver_control = False
        self.driver_control_start_time = 0

        # Autonomous
        self.autonomous_task = NothingAutonomous
        self.autonomous_startup_position = (0, 0)

        # States for Handling Toggle Controls
        self.wings_toggled_last_tick = False
        self.catapult_toggled_last_tick = False

        # Configuration Settings
        self.catapult.catapult_motor.set_stopping(HOLD)
        self.drivetrain.set_braking(Constants.drivetrain_braking)

        # Competition State Handling
        self.competition = Competition(self.driver_handler, self.autonomous_handler)

    def on_autonomous(self):
        """
        Runs when the competition is switched to autonomous mode
        """
        # Ensure setup is complete
        if not self.setup_complete:
            raise RuntimeError("Setup not complete, unable to start autonomous")
        autonomous_log_object = Logging(log_name="Autonomous")

        autonomous = self.autonomous_task(self, autonomous_log_object)
        autonomous.run()

    def on_driver_control(self):
        """
        Runs when the competition is switched to driver controlled mode
        """
        # Wait for setup to finish
        while not self.setup_complete:
            wait(5)
        self.drivetrain.set_braking(Constants.drivetrain_braking)

        self.driver_control_start_time = self.brain.timer.time(SECONDS)
        self.wings.wings_in()
        self.climber.climber_motor.set_max_torque(100, PERCENT)
        while True:
            if not self.disable_driver_control:
                # The joysticks report outputs in the range -100 to 100, but it is easier to do math on inputs in the range
                # -1 to 1, so we scale them to -1 to 1
                left_stick = (
                    clamp(self.primary_controller.axis4.position() / 100, -1, 1),
                    clamp(self.primary_controller.axis3.position() / 100, -1, 1),
                )
                right_stick = (
                    clamp(self.primary_controller.axis1.position() / 100, -1, 1),
                    clamp(self.primary_controller.axis1.position() / 100, -1, 1),
                )

                left_stick = (
                    apply_deadzone(left_stick[0], Constants.movement_deadzone, 1),
                    apply_deadzone(left_stick[1], Constants.movement_deadzone, 1),
                )
                right_stick = (
                    apply_deadzone(right_stick[0], Constants.turn_deadzone, 1),
                    apply_deadzone(right_stick[1], Constants.turn_deadzone, 1),
                )

                # Normalize the turning amount across a cubic curve
                normalized_right_x = cubic_filter(
                    right_stick[0], Constants.turn_cubic_linearity
                )

                movement_direction = math.atan2(left_stick[1], left_stick[0])

                movement_speed = hypotenuse(left_stick[0], left_stick[1])

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

                if self.autonomous_task is SkillsAutonomous:
                    # Driver-skills-specific controller bindings

                    if (
                        self.primary_controller.buttonA.pressing()
                        and not self.started_skills_driver_assist_maneuver
                    ):
                        self.started_skills_driver_assist_maneuver = True
                        autonomous_log_object = Logging(log_name="Temp Autonomous")
                        temp_autonomous = SkillsAutonomous(self, autonomous_log_object)
                        temp_autonomous.first_segment()

                    if self.primary_controller.buttonB.pressing():
                        if not self.catapult_toggled_last_tick:
                            self.catapult.firing = not self.catapult.firing
                            self.catapult.set_velocity(Constants.catapult_motor_speed)
                        self.catapult_toggled_last_tick = True
                    else:
                        self.catapult_toggled_last_tick = False
                else:
                    # Competition-specific controller bindings
                    if self.primary_controller.buttonB.pressing():
                        self.catapult.start_firing()
                        self.catapult.set_velocity(50)
                    else:
                        self.catapult.stop_firing()

                if self.primary_controller.buttonY.pressing():
                    self.wings.toggle_wings()
                    while self.primary_controller.buttonY.pressing():
                        pass
                if self.primary_controller.buttonL2.pressing():
                    self.climber.set_velocity(1)
                elif self.primary_controller.buttonR2.pressing():
                    self.climber.set_velocity(-1)
                else:
                    self.climber.set_velocity(0)

                if self.primary_controller.buttonRight.pressing():
                    self.climber.toggle_locked()
                    while self.primary_controller.buttonRight.pressing():
                        pass

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
            self.display_thread,
        ):
            self.driver_control_threads.append(Thread(_function))

        self.print("Started all driver control tasks")
        while self.competition.is_driver_control() and self.competition.is_enabled():
            wait(10, MSEC)
        for thread in self.driver_control_threads:
            thread.stop()
        self.print("Stopped all driver control tasks")

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

            if setup_ui.team == Constants.Team.skills:
                self.autonomous_task = SkillsAutonomous
            else:
                if setup_ui.robot_position == Constants.defensive | Constants.red:
                    self.autonomous_task = WinPointAutonomous
                elif setup_ui.robot_position == Constants.defensive | Constants.blue:
                    self.autonomous_task = WinPointAutonomous
                elif setup_ui.robot_position == Constants.offensive | Constants.red:
                    self.autonomous_task = ScoringAutonomous4
                elif setup_ui.robot_position == Constants.offensive | Constants.blue:
                    self.autonomous_task = ScoringAutonomous4

        self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.set_pen_color(Color.WHITE)

        self.drivetrain.calibrate_inertial_sensor()

        # Ensure you set the direction of the robot after the inertial sensor is calibrated or calibrating will wipe your setting
        self.drivetrain.current_position = Constants.robot_start_position
        self.autonomous_startup_position = Constants.robot_start_position

        self.drivetrain.current_direction_rad = math.radians(
            Constants.robot_start_rotation_deg
        )
        self.drivetrain.target_heading_rad = Constants.robot_start_rotation_deg

        self.print("Robot:INFO: Setup complete")
        self.primary_controller.rumble(".")
        self.brain.screen.draw_image_from_file(
            Constants.deploy_directory + "Please_Connect_Controller.png", 0, 0
        )
        self.setup_complete = True
