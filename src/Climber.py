from vex import *
from Utilities import sign
import Constants


class Climber:
    def __init__(self):
        self.climber_motor = Motor(
            Constants.climber_motor_port,
            Constants.climber_motor_gear_ratio,
            Constants.climber_motor_inverted,
        )
        self.climber_motor.set_velocity(0, PERCENT)
        self.climber_motor.set_stopping(HOLD)
        self.climber_motor.spin(FORWARD)
        self.allowed_turns = 9.72222  # (3500 degrees)
        self.locking_mechanism = DigitalOut(Constants.climber_locking_port)
        self.locking_mechanism_state = Constants.PneumaticsState.out
        self.target_climber_velocity = 0
        self.update_thread = Thread(self.climber_loop)

    # def calibrate(self):
    #     self.climber_motor.spin(REVERSE, 7, VOLT)
    #     wait(250, MSEC)
    #     while abs(self.climber_motor.velocity()) > 15:
    #         wait(100, MSEC)
    #     self.climber_motor.set_position(0, DEGREES)
    #     self.climber_motor.set_velocity(0, PERCENT)
    #     self.climber_motor.spin(FORWARD)

    def _climber_inside_allowed_range(self):
        if self.climber_motor.position(DEGREES) / 360 >= self.allowed_turns:
            return -1
        elif self.climber_motor.position(DEGREES) / 360 <= 0:
            return 1
        else:
            return None

    def set_velocity(self, velocity):
        self.target_climber_velocity = velocity

    def set_locked(self, locked):
        self.locking_mechanism_state = (
            Constants.PneumaticsState.out if locked else Constants.PneumaticsState.in_
        )

    def toggle_locked(self):
        self.locking_mechanism_state = (
            Constants.PneumaticsState.out
            if self.locking_mechanism_state == Constants.PneumaticsState.in_
            else Constants.PneumaticsState.in_
        )
        print("Toggled lock state")

    def climber_loop(self):
        while True:
            if self.locking_mechanism_state == Constants.PneumaticsState.in_:
                self.locking_mechanism.set(False)

            if self.locking_mechanism_state == Constants.PneumaticsState.out:
                self.locking_mechanism.set(True)

            if self._climber_inside_allowed_range() is not None:
                # CLimber is hitting one of the constraints of motion
                if sign(self.target_climber_velocity) == sign(
                    self._climber_inside_allowed_range()
                ):
                    # The sign of the target velocity matches the sign of the allowed movement direction
                    self.climber_motor.set_velocity(
                        self.target_climber_velocity * 100, PERCENT
                    )
                else:
                    # The sign of the target velocity does not match the sign of the allowed movement direction
                    self.climber_motor.set_velocity(0, PERCENT)
            else:
                self.climber_motor.set_velocity(
                    self.target_climber_velocity * 100, PERCENT
                )
            print("Tick")

            wait(100, MSEC)
