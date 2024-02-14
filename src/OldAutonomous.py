import math
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
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        self.log("Doing nothing...")
        self.log("Done")
        self.log("That was easy!")
        self.log_object.exit()


class TestAuto(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot
        wait(5000, MSEC)
        robot.drivetrain.forward(61, 0.5)
        robot.intake.spit_out()
        wait(500, MSEC)
        robot.drivetrain.backwards(61, 0.5)
        robot.intake.stop()
        self.log_object.exit()

        #
        # with open("/deploy/skills_path.pth", "r") as f:
        #     points = eval(f.read())
        #
        # for point in points:
        #     if isinstance(point, str):
        #         if "intake" in point:
        #             if "stop" in point:
        #                 robot.intake.stop()
        #             elif "in" in point:
        #                 robot.intake.pull_in()
        #             elif "out" in point:
        #                 robot.intake.spit_out()
        #         if "climber" in point:
        #             if "up" in point:
        #                 robot.climber.set_velocity(50)
        #                 wait(500, MSEC)
        #                 robot.climber.climber_motor.set_max_torque(20, PERCENT)
        #                 while abs(robot.climber.climber_motor.velocity()) > 40:
        #                     pass
        #                 robot.climber.climber_motor.set_max_torque(100, PERCENT)
        #                 robot.climber.set_velocity(0)
        #             elif "down" in point:
        #                 robot.climber.set_velocity(-50)
        #                 wait(500, MSEC)
        #                 robot.climber.climber_motor.set_max_torque(20, PERCENT)
        #                 while abs(robot.climber.climber_motor.velocity()) > 40:
        #                     pass
        #                 robot.climber.climber_motor.set_max_torque(100, PERCENT)
        #                 robot.climber.set_velocity(0)
        #         if "wings" in point:
        #             if "in" in point:
        #                 robot.wings.wings_in()
        #             elif "out" in point:
        #                 robot.wings.wings_out()
        #     elif isinstance(point, tuple):
        #         self.robot.drivetrain.turn_to_face_position(point)
        #         self.robot.drivetrain.move_to_position(point, 0.8)

class ScoringAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot

        self.log("Starting scoring autonomous")

        robot.drivetrain.stop()

        robot.drivetrain.forward(7.5, 0.6)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-45 - 90))
        robot.wings.wings_out()
        robot.drivetrain.forward(20, 0.6)
        # self.drivetrain.strafe_right(10, 0.6)
        robot.drivetrain.forward(30, 0.6)
        robot.wings.wings_in()
        robot.drivetrain.forward(17, 0.6)
        robot.drivetrain.turn_to_face_heading_rad(-math.pi / 2)
        robot.intake.spit_out()
        robot.drivetrain.forward(30 + 5, 0.6)
        # Push the first triball into the goal
        robot.drivetrain.backwards(28 + 5, 0.6)
        robot.intake.stop()

        robot.drivetrain.turn_to_face_heading_rad(math.radians(-19))  # -20
        robot.drivetrain.forward(120, 0.6)
        robot.intake.pull_in()
        # Grab the second triball
        robot.drivetrain.forward(10, 0.6)
        robot.drivetrain.backwards(10, 0.6)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-140))

        robot.drivetrain.forward(20, 0.6)
        robot.drivetrain.forward(50, 0.6)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        robot.intake.spit_out()
        wait(400, MSEC)
        # Score the second triball
        robot.drivetrain.forward(18 + 5, 0.6)
        robot.drivetrain.backwards(6 + 5, 0.5)

        robot.intake.pull_in()
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-40 - 12))

        robot.drivetrain.forward(40, 0.4)

        robot.drivetrain.backwards(15, 1)

        robot.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        robot.intake.stop()

        robot.intake.spit_out()
        wait(200, MSEC)
        # self.drivetrain.forward(20, 1)
        robot.drivetrain.forward(35 + 5, 1)
        robot.drivetrain.backwards(15 + 5, 1)
        robot.intake.stop()

        self.log("Done")
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
        self.log("Starting scoring autonomous")

        robot.drivetrain.stop()

        robot.drivetrain.forward(12, 1)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-135))
        robot.drivetrain.forward(75, 1)
        robot.drivetrain.turn_to_face_heading_rad(-math.pi / 2)
        robot.intake.spit_out()
        robot.drivetrain.forward(30, 1)
        # Push the first triball into the goal
        robot.drivetrain.backwards(28, 1)
        robot.intake.stop()

        # robot.drivetrain.turn_to_face_heading_rad(math.radians(0))
        # robot.drivetrain.forward(30, 1)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-22))
        robot.drivetrain.forward(120, 1)
        robot.intake.pull_in()
        # Grab the second triball
        robot.drivetrain.forward(10, 1)
        robot.drivetrain.backwards(10, 1)
        robot.intake.stop()
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-140))

        robot.drivetrain.forward(70, 1)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        robot.intake.spit_out()
        # Score the second triball
        robot.drivetrain.forward(18, 1)
        robot.drivetrain.backwards(6, 1)

        robot.intake.pull_in()
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-25))

        robot.drivetrain.forward(40, 0.4)
        wait(100, MSEC)
        robot.drivetrain.backwards(15, 1)

        robot.intake.stop()
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-180))

        robot.drivetrain.forward(20, 1)
        robot.intake.spit_out()
        robot.drivetrain.forward(15, 1)
        robot.drivetrain.backwards(15, 1)
        robot.intake.stop()
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-15))
        robot.intake.pull_in()
        robot.drivetrain.forward(60, 1)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-180))
        robot.intake.stop()
        robot.drivetrain.forward(50, 1)
        robot.intake.spit_out()
        robot.drivetrain.forward(25, 1)

        self.log("Done")
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        robot.drivetrain.stop()

        self.log_object.exit()


class SabotageAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot
        self.log("Starting sabotage autonomous")

        robot.drivetrain.stop()

        robot.drivetrain.forward(100, 0.8)
        robot.drivetrain.strafe_right(35, 0.8)
        robot.intake.pull_in()
        robot.drivetrain.forward(30, 0.8)
        robot.drivetrain.forward(8, 0.5)
        robot.intake.stop()
        robot.drivetrain.backwards(10, 0.8)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(135))
        robot.intake.spit_out()
        wait(250, MSEC)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-90))
        robot.intake.stop()
        robot.drivetrain.strafe_left(25, 0.8)
        robot.drivetrain.backwards(115, 0.8)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(45))
        robot.intake.pull_in()
        robot.drivetrain.forward(20, 0.5)
        robot.intake.stop()
        robot.drivetrain.strafe_right(85, 0.5)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-90))
        robot.intake.spit_out()
        robot.drivetrain.forward(40, 0.8)
        wait(500, MSEC)
        robot.intake.stop()

        self.log("Done")
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        robot.drivetrain.stop()

        self.log_object.exit()


class WinPointAutonomous(AutonomousRoutine):
    def __init__(self, robot, log_object):
        super().__init__(log_object)
        self.robot = robot

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot
        self.log("Starting win point autonomous")

        robot.drivetrain.stop()

        robot.drivetrain.forward(7.5, 0.4)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-45))
        robot.wings.wings_out()
        robot.drivetrain.forward(20, 0.4)
        robot.drivetrain.strafe_left(10, 0.4)
        robot.drivetrain.forward(30, 0.4)
        robot.wings.wings_in()
        robot.drivetrain.strafe_right(20, 0.4)
        robot.drivetrain.forward(20, 0.4)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-90))
        robot.intake.spit_out()
        robot.drivetrain.forward(5, 0.4)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(-45 + 180))
        robot.drivetrain.forward(80, 0.4)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(180))
        robot.drivetrain.forward(65, 0.4)
        robot.drivetrain.strafe_left(10, 0.5)
        robot.drivetrain.turn_to_face_heading_rad(math.radians(170))

        robot.wings.wings_out()

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

        robot.drivetrain.current_position = (0, 0)
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.target_position = robot.drivetrain.current_position

    def run(self):
        robot = self.robot
        self.log("Starting skills autonomous")
        robot.drivetrain.stop()

        robot.climber.climber_motor.power()

        robot.climber.set_velocity(50)

        robot.drivetrain.strafe_left(40, 0.8)
        robot.drivetrain.turn_to_face_heading_deg(-90 - 25)

        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position
        robot.drivetrain.stop()
        robot.climber.climber_motor.set_max_torque(20, PERCENT)
        while abs(robot.climber.climber_motor.velocity()) > 40:
            pass
        robot.climber.climber_motor.set_max_torque(100, PERCENT)
        robot.climber.set_velocity(0)

        robot.catapult.start_firing()
        wait(47, SECONDS)
        robot.catapult.stop_firing()

        robot.drivetrain.turn_to_face_heading_deg(-90 - 70)
        robot.drivetrain.forward(90, 0.4)
        robot.drivetrain.turn_to_face_heading_deg(-90 - 45)
        robot.drivetrain.forward(65, 0.4)
        robot.climber.set_velocity(-100)
        robot.climber.set_locked(False)
        while robot.climber.climber_motor.position(DEGREES) > 50:
            pass
        robot.climber.set_velocity(0)

        robot.log("Done")
        robot.drivetrain.rotation_PID.setpoint = robot.drivetrain.current_direction_rad
        robot.drivetrain.clear_direction_PID_output()
        robot.drivetrain.target_position = robot.drivetrain.current_position

        self.log_object.exit()
