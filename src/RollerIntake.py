import Constants
from vex import *


class Intake:
    def __init__(self):
        self.left_intake_motor = Motor(
            Constants.left_intake_motor_port,
            Constants.left_intake_motor_gear_ratio,
            Constants.left_intake_motor_inverted,
        )

        self.right_intake_motor = Motor(
            Constants.right_intake_motor_port,
            Constants.right_intake_motor_gear_ratio,
            Constants.right_intake_motor_inverted,
        )

        self.left_intake_motor.set_velocity(0, PERCENT)
        self.right_intake_motor.set_velocity(0, PERCENT)

        self.left_intake_motor.spin(FORWARD)
        self.right_intake_motor.spin(FORWARD)

        self.manual_control = False
        self.state = Constants.IntakeState.off

        self.update_thread = Thread(self.intake_loop)

    def pull_in(self):
        self.manual_control = False
        self.state = Constants.IntakeState.pull_in

    def spit_out(self):
        self.manual_control = False
        self.state = Constants.IntakeState.push_out

    def stop(self):
        self.manual_control = False
        self.state = Constants.IntakeState.off

    def _set_velocity(self, velocity):
        self.left_intake_motor.set_velocity(velocity, PERCENT)
        self.right_intake_motor.set_velocity(velocity, PERCENT)

    def set_velocity(self, velocity):
        self.manual_control = True
        self._set_velocity(velocity)

    def intake_loop(self):
        while True:
            if not self.manual_control:
                if self.state == Constants.IntakeState.pull_in:
                    self._set_velocity(50)
                elif self.state == Constants.IntakeState.push_out:
                    self._set_velocity(-50)
                elif self.state == Constants.IntakeState.off:
                    self._set_velocity(0)
                wait(100, MSEC)
