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


class SkillsAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot
        self.catapult_raised = False

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def raise_catapult(self):
        robot = self.robot
        robot.climber.set_velocity(50)
        robot.climber.climber_motor.set_max_torque(20, PERCENT)
        wait(2000, MSEC)
        while abs(robot.climber.climber_motor.velocity()) > 40:
            pass
        robot.climber.climber_motor.set_max_torque(100, PERCENT)
        robot.climber.set_velocity(0)
        self.catapult_raised = True

    def lower_catapult(self):
        robot = self.robot
        robot.climber.set_velocity(-100)
        while robot.climber.climber_motor.position(DEGREES) > 50:
            pass
        robot.climber.set_velocity(0)

    def first_segment(self):
        robot = self.robot
        self.log("Starting skills autonomous")
        robot.drivetrain.stop()

        Thread(self.raise_catapult)

        robot.drivetrain.strafe_left(40, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-90 - 25)

        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position
        robot.drivetrain.stop()

        while not self.catapult_raised:
            pass

    def second_segment(self):
        robot = self.robot
        robot.catapult.start_firing()
        wait(40, SECONDS)
        robot.catapult.stop_firing()

        Thread(self.lower_catapult)

        robot.drivetrain.turn_to_face_heading_deg(-90)

        robot.drivetrain.forward(150, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-90 - 45)
        robot.drivetrain.forward(30, 1)
        robot.wings.wings_out()
        robot.drivetrain.forward(200, 1)
        robot.drivetrain.backwards(50, 1)
        robot.drivetrain.forward(70, 1)
        robot.wings.wings_in()
        robot.drivetrain.backwards(50, 1)

    def run(self):
        robot = self.robot
        self.log("Starting skills autonomous")
        self.first_segment()
        self.second_segment()

        self.log("Done")
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        self.log_object.exit()
