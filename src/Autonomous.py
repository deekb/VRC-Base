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
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def run(self):
        self.log("Doing nothing")
        self.log("Done")
        self.log("That was easy")
        self.log_object.exit()


class TestAuto(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def run(self):
        wait(5000, MSEC)
        self.drivetrain.forward(61, 0.5)
        self.intake.spit_out()
        wait(500, MSEC)
        self.drivetrain.backwards(61, 0.5)
        self.intake.stop()
        self.log_object.exit()


class ScoringAutonomous(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting scoring autonomous")

        self.drivetrain.stop()

        self.drivetrain.forward(7.5, 0.6)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-45 - 90))
        self.wings.wings_out()
        self.drivetrain.forward(20, 0.6)
        # self.drivetrain.strafe_right(10, 0.6)
        self.drivetrain.forward(30, 0.6)
        self.wings.wings_in()
        self.drivetrain.forward(17, 0.6)
        self.drivetrain.turn_to_face_heading_rad(-math.pi / 2)
        self.intake.spit_out()
        self.drivetrain.forward(30+5, 0.6)
        # Push the first triball into the goal
        self.drivetrain.backwards(28+5, 0.6)
        self.intake.stop()

        self.drivetrain.turn_to_face_heading_rad(math.radians(-19))  # -20
        self.drivetrain.forward(120, 0.6)
        self.intake.pull_in()
        # Grab the second triball
        self.drivetrain.forward(10, 0.6)
        self.drivetrain.backwards(10, 0.6)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-140))

        self.drivetrain.forward(20, 0.6)
        self.drivetrain.forward(50, 0.6)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        self.intake.spit_out()
        wait(400, MSEC)
        # Score the second triball
        self.drivetrain.forward(18+5, 0.6)
        self.drivetrain.backwards(6+5, 0.5)

        self.intake.pull_in()
        self.drivetrain.turn_to_face_heading_rad(math.radians(-40 - 12))

        self.drivetrain.forward(40, 0.4)

        self.drivetrain.backwards(15, 1)

        self.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        self.intake.stop()

        self.intake.spit_out()
        wait(200, MSEC)
        # self.drivetrain.forward(20, 1)
        self.drivetrain.forward(35+5, 1)
        self.drivetrain.backwards(15+5, 1)
        self.intake.stop()

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()

        self.log_object.exit()


class ScoringAutonomous4(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting scoring autonomous")

        self.drivetrain.stop()

        self.drivetrain.forward(12, 1)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-135))
        self.drivetrain.forward(75, 1)
        self.drivetrain.turn_to_face_heading_rad(-math.pi / 2)
        self.intake.spit_out()
        self.drivetrain.forward(30, 1)
        # Push the first triball into the goal
        self.drivetrain.backwards(28, 1)
        self.intake.stop()

        # self.drivetrain.turn_to_face_heading_rad(math.radians(0))
        # self.drivetrain.forward(30, 1)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-22))
        self.drivetrain.forward(120, 1)
        self.intake.pull_in()
        # Grab the second triball
        self.drivetrain.forward(10, 1)
        self.drivetrain.backwards(10, 1)
        self.intake.stop()
        self.drivetrain.turn_to_face_heading_rad(math.radians(-140))

        self.drivetrain.forward(70, 1)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        self.intake.spit_out()
        # Score the second triball
        self.drivetrain.forward(18, 1)
        self.drivetrain.backwards(6, 1)

        self.intake.pull_in()
        self.drivetrain.turn_to_face_heading_rad(math.radians(-25))

        self.drivetrain.forward(40, 0.4)
        wait(100, MSEC)
        self.drivetrain.backwards(15, 1)

        self.intake.stop()
        self.drivetrain.turn_to_face_heading_rad(math.radians(-180))

        self.drivetrain.forward(20, 1)
        self.intake.spit_out()
        self.drivetrain.forward(15, 1)
        self.drivetrain.backwards(15, 1)
        self.intake.stop()
        self.drivetrain.turn_to_face_heading_rad(math.radians(-15))
        self.intake.pull_in()
        self.drivetrain.forward(60, 1)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        self.intake.stop()
        self.drivetrain.forward(50, 1)
        self.intake.spit_out()
        self.drivetrain.forward(25, 1)

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()

        self.log_object.exit()


class SabotageAutonomous(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
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
        self.drivetrain.turn_to_face_heading_rad(math.radians(135))
        self.intake.spit_out()
        wait(250, MSEC)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-90))
        self.intake.stop()
        self.drivetrain.strafe_left(25, 0.8)
        self.drivetrain.backwards(115, 0.8)
        self.drivetrain.turn_to_face_heading_rad(math.radians(45))
        self.intake.pull_in()
        self.drivetrain.forward(20, 0.5)
        self.intake.stop()
        self.drivetrain.strafe_right(85, 0.5)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-90))
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


class WinPointAutonomous(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting win point autonomous")

        self.drivetrain.stop()

        self.drivetrain.forward(7.5, 0.4)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-45))
        self.wings.wings_out()
        self.drivetrain.forward(20, 0.4)
        self.drivetrain.strafe_left(10, 0.4)
        self.drivetrain.forward(30, 0.4)
        self.wings.wings_in()
        self.drivetrain.strafe_right(20, 0.4)
        self.drivetrain.forward(20, 0.4)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-90))
        self.intake.spit_out()
        self.drivetrain.forward(5, 0.4)
        self.drivetrain.turn_to_face_heading_rad(math.radians(-45 + 180))
        self.drivetrain.forward(80, 0.4)
        self.drivetrain.turn_to_face_heading_rad(math.radians(180))
        self.drivetrain.forward(65, 0.4)
        self.drivetrain.strafe_left(10, 0.5)
        self.drivetrain.turn_to_face_heading_rad(math.radians(170))

        self.wings.wings_out()

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop()

        self.log_object.exit()


class SkillsAutonomous(AutonomousRoutine):
    def __init__(
        self,
        log_object,
        drivetrain,
        intake,
        climber,
        catapult,
        wings,
        terminal,
        startup_position,
    ):
        super().__init__(log_object)
        self.terminal = terminal
        self.drivetrain = drivetrain
        self.intake = intake
        self.climber = climber
        self.catapult = catapult
        self.wings = wings
        self.drivetrain.current_position = startup_position
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.target_position = self.drivetrain.current_position

    def log(self, string):
        self.log_object.log(string + "\n")
        self.terminal.print(string)

    def run(self):
        self.log("Starting skills autonomous")
        self.drivetrain.stop()

        self.climber.climber_motor.power()

        self.climber.set_velocity(50)

        self.drivetrain.strafe_left(40, 0.8)
        self.drivetrain.turn_to_face_heading_deg(-90 - 25)

        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position
        self.drivetrain.stop()
        self.climber.climber_motor.set_max_torque(20, PERCENT)
        while abs(self.climber.climber_motor.velocity()) > 40:
            pass
        self.climber.climber_motor.set_max_torque(100, PERCENT)
        self.climber.set_velocity(0)

        self.catapult.start_firing()
        wait(47, SECONDS)
        self.catapult.stop()

        self.drivetrain.turn_to_face_heading_deg(-90 - 70)
        self.drivetrain.forward(90, 0.4)
        self.drivetrain.turn_to_face_heading_deg(-90 - 45)
        self.drivetrain.forward(65, 0.4)
        self.climber.set_velocity(-100)
        self.climber.set_locked(False)
        while self.climber.climber_motor.position(DEGREES) > 50:
            pass
        self.climber.set_velocity(0)

        self.log("Done")
        self.drivetrain.rotation_PID.setpoint = self.drivetrain.current_direction_rad
        self.drivetrain.clear_direction_PID_output()
        self.drivetrain.target_position = self.drivetrain.current_position

        self.drivetrain.stop_firing()

        self.log_object.exit()


available_autonomous_routines = [
    ("SabotageAutonomous", SabotageAutonomous),
    ("ScoringAutonomous", ScoringAutonomous),
    ("WinPointAutonomous", WinPointAutonomous),
    ("Nothing", NothingAutonomous),
]
