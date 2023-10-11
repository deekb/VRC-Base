"""
Competition codebase for VRC
Team: 3773P (Bowbots Phosphorus) from Bow NH
Author: Derek Baier (deekb on GitHub)
Project homepage: https://github.com/deekb/VRC-Base
Project archive: https://github.com/deekb/VRC-Base/archive/master.zip
Contact Derek.m.baier@gmail.com for more information

The code is developed for Team 3773P, known as Bowbots Phosphorus, and is authored by Derek Baier.

The project homepage and archive can be found on GitHub at the provided links.

For more information about the project, you can contact Derek Baier at the given email address.
"""

from vex import *
import Constants
from Utilities import Terminal, Logging, BinarySemaphore
from HolonomicDrivetrain import Drivetrain
from Autonomous import NothingAutonomous
from Intake import Intake
from SetupUI import SetupUI

__title__ = Constants.__title__
__description__ = Constants.__description__
__team__ = Constants.__team__
__url__ = Constants.__url__
__download_url__ = Constants.__download_url__
__version__ = Constants.__version__
__author__ = Constants.__author__
__author_email__ = Constants.__author_email__
__license__ = Constants.__license__


brain = Brain()


class Robot:
    def __init__(self, brain):
        self.brain = brain
        self.terminal = Terminal(self.brain)
        self.print = self.terminal.print
        self.clear = self.terminal.clear

        self.primary_controller = Controller(PRIMARY)
        self.secondary_controller = Controller(PARTNER)

        self.optical_sensor = Optical(Constants.optical_sensor_port)
        self.optical_sensor.set_light_power(100, PERCENT)

        self.triball_detected = False
        self.previous_triball_detected = False

        self.driver_control_threads = []
        self.autonomous_threads = []
        self.setup_complete = False

        self.autonomous_task = None

        self.drivetrain = Drivetrain(timer=self.brain.timer, terminal=self.terminal)

        self.drivetrain_thread_lock = BinarySemaphore()

        self.intake = Intake(self.brain)

        self.drivetrain.odometry.position = Constants.robot_start_position
        self.drivetrain.odometry.rotation_deg = Constants.robot_start_rotation_deg
        self.drivetrain.set_braking(Constants.drivetrain_braking)

        # Register the competition handler
        self.competition = Competition(self.driver_handler, self.autonomous_handler)

    def on_autonomous(self):
        """
        This is the function designated to run when the autonomous portion of the program is triggered
        """
        # Ensure setup is complete
        if not self.setup_complete:
            print("[on_autonomous]: setup not complete, can't start autonomous")
            return
        autonomous_log_object = Logging(log_name="Autonomous")
        autonomous = NothingAutonomous(autonomous_log_object)
        autonomous.run()

    def check_triball_detected(self):
        return (
            abs(self.optical_sensor.hue() - 80) <= 10
            and self.optical_sensor.is_near_object()
        )

    def on_driver_control(self):
        """
        This is the function designated to run when the driver control portion of the program is triggered
        """
        # Wait for setup to finish
        while not self.setup_complete:
            wait(5)
        while True:
            self.drivetrain_thread_lock.acquire()  # Ensure this thread is allowed to use the drivetrain
            self.drivetrain.move_with_controller(
                self.primary_controller, headless=Constants.driver_control_headless, PID_turning=Constants.PID_turning
            )
            self.drivetrain_thread_lock.release()  # Allow other threads that are waiting to acquire the drivetrain to do so
            # self.triball_detected = self.check_triball_detected()
            # if (
            #     self.triball_detected != self.previous_triball_detected
            #     and self.triball_detected
            # ):
            #     self.intake.claw_close()
            #     self.intake.wrist_up()
            # self.previous_triball_detected = self.triball_detected
            wait(5, MSEC)

    def debug_thread(self):
        while True:
            if self.setup_complete:
                if self.primary_controller.buttonA.pressing():
                    self.drivetrain_thread_lock.acquire()
                    try:
                        self.drivetrain.reset()
                    finally:
                        self.drivetrain_thread_lock.release()
                if self.primary_controller.buttonB.pressing():
                    self.drivetrain_thread_lock.acquire()
                    try:
                        self.drivetrain.follow_path(
                            [(0, 0), (100, 0), (100, 100), (0, 0)], 0.4
                        )
                        self.drivetrain.follow_path(
                            [(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)], 0.4
                        )
                    finally:
                        self.drivetrain_thread_lock.release()
                # if self.primary_controller.buttonR2.pressing():
                #     self.drivetrain_thread_lock.acquire()
                #     try:
                #         self.drivetrain.turn_to_face_position((0, 0))
                #     finally:
                #         self.drivetrain_thread_lock.release()

    def display_thread(self):
        def field_coordinates_to_screen(position):
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

            current_x, current_y = field_coordinates_to_screen(
                self.drivetrain.odometry.position
            )
            target_x, target_y = field_coordinates_to_screen(
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
        Coordinate when to run the autonomous function(s)
        """
        while not self.setup_complete and (
            self.competition.is_autonomous() and self.competition.is_enabled()
        ):
            wait(5, MSEC)
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
        Coordinate when to run the driver function(s)
        """
        while not self.setup_complete and (
            self.competition.is_driver_control() and self.competition.is_enabled()
        ):
            wait(5, MSEC)
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

        self.primary_controller.buttonL1.pressed(self.intake.toggle_wrist)
        self.primary_controller.buttonR1.pressed(self.intake.toggle_claw)

    def main(self):
        setup_ui = SetupUI(self.terminal, self.brain.screen)

        while not setup_ui.finished:
            wait(10, MSEC)
            setup_ui.tick()

        self.brain.screen.set_fill_color(Color.TRANSPARENT)
        self.brain.screen.set_pen_color(Color.WHITE)

        self.drivetrain.calibrate_inertial_sensor()

        # Set up controller callbacks here to avoid triggering them by pressing buttons during setup
        self.setup_controller_bindings()

        self.print("Robot:INFO: Setup complete")
        self.primary_controller.rumble(".")
        self.brain.screen.draw_image_from_file(
            Constants.deploy_directory + "Please_Connect_Controller.png", 0, 0
        )
        self.setup_complete = True
