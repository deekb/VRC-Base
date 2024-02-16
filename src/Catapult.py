import Constants
from vex import *


class Catapult:
    def __init__(self):
        self.catapult_motor = Motor(
            Constants.catapult_motor_port,
            Constants.catapult_motor_gear_ratio,
            Constants.catapult_motor_inverted,
        )
        self.catapult_motor.set_velocity(0, PERCENT)
        self.catapult_motor.spin(FORWARD)
        self.firing = False
        self.speed = 0
        self.update_thread = Thread(self.update)
        self.fire_start_time = 0

    def start_firing(self):
        self.firing = True
        self.speed = Constants.catapult_motor_speed

    def set_velocity(self, velocity):
        self.speed = velocity

    def stop_firing(self):
        self.firing = False

    def fire_for_rotations(self, rotations):
        self.catapult_motor.spin_for(FORWARD, rotations, TURNS)
        self.stop_firing()

    def update(self):
        while True:
            if self.firing:
                self.catapult_motor.set_velocity(
                    Constants.catapult_motor_speed, PERCENT
                )
            else:
                self.catapult_motor.set_velocity(0)
