from vex import *


class AutonomousRoutine:
    def __init__(self, log_object):
        self.log_object = log_object

    def log(self, string):
        self.log_object.log(string)

    def run(self):
        """Your autonomous code should be declared here"""
        raise NotImplementedError


class NothingAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain._odometry.rotation_deg = 0
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        self.log("Doing nothing...")
        self.log("Done")
        self.log("That was easy!")
        self.log_object.exit()


class WinPointAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot
        robot.drivetrain.reset()

    def run(self):
        robot = self.robot

        self.log("Running win point autonomous")

        robot.intake.pull_in()
        robot.drivetrain.backwards(20, 0.7)
        robot.wings.wings_out()
        robot.drivetrain.forward(20, 0.7)
        robot.drivetrain.strafe_left(15, 0.7)
        robot.intake.stop()
        robot.drivetrain.turn_to_face_heading_deg(25)
        robot.wings.wings_in()
        robot.drivetrain.backwards(5, 0.7)
        robot.drivetrain.forward(5, 0.7)
        robot.drivetrain.forward(40, 0.7)
        robot.drivetrain.turn_to_face_heading_deg(45)
        robot.wings.wings_out()
        robot.drivetrain.forward(30, 0.5)
        robot.intake.spit_out()
        robot.drivetrain.forward(30, 1)
        robot.drivetrain.set_braking(True)
        wait(250, MSEC)
        robot.drivetrain.set_braking(False)
        robot.drivetrain.turn_to_face_heading_deg(25)

        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        robot.drivetrain.stop()

        self.log_object.exit()


class ScoringAutonomous4(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot
        self.log("Starting 4-piece autonomous")

        robot.drivetrain.stop()

        robot.drivetrain.set_braking(True)

        robot.drivetrain.forward(12, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-135)
        robot.drivetrain.forward(70, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-90)
        robot.intake.spit_out()
        robot.drivetrain.forward(40, 1)
        # Push the first triball into the goal
        robot.drivetrain.backwards(40, 0.8)
        robot.intake.stop()
        robot.drivetrain.turn_to_face_heading_deg(-21)
        robot.intake.pull_in()
        robot.drivetrain.forward(115, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-120)
        robot.drivetrain.forward(40, 0.8)
        robot.intake.spit_out()
        robot.drivetrain.backwards(10, 0.2)
        robot.drivetrain.turn_to_face_heading_deg(-55)
        robot.intake.pull_in()
        robot.drivetrain.forward(40, 0.4)
        robot.drivetrain.turn_to_face_heading_deg(-180)
        robot.wings.wings_out()
        robot.intake.spit_out()
        robot.drivetrain.forward(80, 0.8)
        robot.drivetrain.backwards(30, 0.8)
        robot.intake.stop()


        self.log("Done")
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        robot.drivetrain.stop()

        self.log_object.exit()
