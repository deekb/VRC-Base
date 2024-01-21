import Constants
from vex import *


class Catapult:
    def __init__(self, catapult_motor: Motor):
        self.catapult_motor = catapult_motor
        self.catapult_motor.set_velocity(0, PERCENT)
        self.catapult_motor.spin(FORWARD)

    def start_firing(self):
        self.catapult_motor.set_velocity(Constants.catapult_motor_speed)

    def stop_firing(self):
        self.catapult_motor.set_velocity(0)

    def fire_for_rotations(self, rotations):
        self.catapult_motor.spin_for(FORWARD, rotations, TURNS)
        self.stop_firing()
