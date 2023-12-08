from vex import *


class Climber:
    def __init__(self, climber_motor: Motor):
        self.climber_motor = climber_motor
        self.climber_motor.set_velocity(0, PERCENT)
        self.climber_motor.set_stopping(HOLD)
        self.climber_motor.spin(FORWARD)
        self.allowed_turns = 2.45

    def calibrate(self):
        self.climber_motor.spin(REVERSE, 7, VOLT)
        wait(250, MSEC)
        while abs(self.climber_motor.velocity()) > 15:
            wait(100, MSEC)
        self.climber_motor.set_position(0, DEGREES)
        self.climber_motor.set_velocity(0, PERCENT)
        self.climber_motor.spin(FORWARD)

    def climber_inside_allowed_range(self):
        return abs(self.climber_motor.position(DEGREES) / 360) <= self.allowed_turns

    def set_velocity(self, velocity):
        if velocity > 0:
            if self.climber_inside_allowed_range():
                self.climber_motor.set_velocity(velocity * 100, PERCENT)
            else:
                self.climber_motor.set_velocity(0, PERCENT)
        else:
            self.climber_motor.set_velocity(velocity * 100, PERCENT)
