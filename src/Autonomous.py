import math
from vex import *


class AutonomousRoutine:
    def __init__(self, log_object):
        self.log_object = log_object

    def log(self, string):
        self.log_object.log(string)

    def run(self):
        """Your autonomous code should be declared here"""
        ...


class NothingAutonomous(AutonomousRoutine):
    def __init__(self, log_object, drivetrain, intake, terminal, startup_position):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def run(self):
        self.log("Doing nothing")
        self.log("Done")
        self.log("That was easy")
        self.log_object.exit()


class ScoringAutonomous(AutonomousRoutine):
    def __init__(self, log_object, drivetrain, intake, terminal, startup_position):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting scoring autonomous")

        self.drivetrain.stop()

        self.drivetrain.forward(10, 0.8)
        self.drivetrain.turn_to_face_heading(math.radians(-135))
        self.drivetrain.forward(70, 0.8)
        self.drivetrain.turn_to_face_heading(-math.pi / 2)
        self.drivetrain.forward(10, 0.8)
        self.intake.spit_out()
        self.drivetrain.forward(18, 0.8)
        # Push the first triball into the goal
        self.drivetrain.backwards(28, 0.8)
        self.intake.stop()

        self.drivetrain.turn_to_face_heading(math.radians(0))
        self.drivetrain.forward(30, 0.8)
        self.drivetrain.turn_to_face_heading(math.radians(-18))
        self.drivetrain.forward(90, 0.8)
        self.intake.pull_in()
        # Grab the second triball
        self.drivetrain.forward(10, 0.6)
        self.drivetrain.backwards(10, 0.8)
        self.intake.stop()
        self.drivetrain.turn_to_face_heading(math.radians(-145))

        self.drivetrain.forward(70, 0.8)
        self.drivetrain.turn_to_face_heading(math.radians(-180))
        self.intake.spit_out()
        # Score the second triball
        self.drivetrain.forward(10, 0.8)
        self.drivetrain.backwards(10, 0.8)

        self.intake.pull_in()
        self.drivetrain.turn_to_face_heading(math.radians(-46))
        self.drivetrain.forward(40, 0.8)
        self.drivetrain.backwards(10, 0.8)

        self.intake.stop()
        self.drivetrain.turn_to_face_heading(math.radians(-180))

        self.drivetrain.forward(20, 0.8)
        self.intake.spit_out()
        self.drivetrain.forward(20, 0.8)

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()

        self.log_object.exit()


class SabotageAutonomous(AutonomousRoutine):
    def __init__(self, log_object, drivetrain, intake, terminal, startup_position):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting sabotage autonomous")

        self.drivetrain.stop()

        self.drivetrain.forward(100, 0.8)
        self.drivetrain.strafe_right(35, 0.8)
        self.intake.pull_in()
        self.drivetrain.forward(30, 0.8)
        self.drivetrain.forward(8, 0.5)
        self.intake.stop()
        self.drivetrain.backwards(10, 0.8)
        self.drivetrain.turn_to_face_heading(math.radians(135))
        self.intake.spit_out()
        wait(250, MSEC)
        self.drivetrain.turn_to_face_heading(math.radians(-90))
        self.intake.stop()
        self.drivetrain.strafe_left(25, 0.8)
        self.drivetrain.backwards(115, 0.8)
        self.drivetrain.turn_to_face_heading(math.radians(45))
        self.intake.pull_in()
        self.drivetrain.forward(20, 0.5)
        self.intake.stop()
        self.drivetrain.strafe_right(85, 0.5)
        self.drivetrain.turn_to_face_heading(math.radians(-90))
        self.intake.spit_out()
        self.drivetrain.forward(40, 0.8)
        wait(500, MSEC)
        self.intake.stop()

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()

        self.log_object.exit()


available_autonomous_routines = [
    ("SabotageAutonomous", SabotageAutonomous),
    ("ScoringAutonomous", ScoringAutonomous),
    ("Nothing", NothingAutonomous),
]
