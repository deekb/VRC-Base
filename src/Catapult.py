import Constants
from vex import *


class Catapult:
    def __init__(self, catapult_motor: Motor, timer):
        self.catapult_motor = catapult_motor
        self.timer = timer
        self.catapult_motor.set_velocity(0, PERCENT)
        self.catapult_motor.spin(FORWARD)
        self.firing = False
        self.update_thread = Thread(self.update)
        self.fire_start_time = 0

    def start_firing(self):
        self.firing = True
        self.fire_start_time = self.timer.time(SECONDS)

    def stop_firing(self):
        self.firing = False

    def fire_for_rotations(self, rotations):

        self.catapult_motor.spin_for(FORWARD, rotations, TURNS)
        self.stop_firing()

    def update(self):
        while True:
            if self.firing:
                # if (self.timer.time(SECONDS) - self.fire_start_time) >
                self.catapult_motor.set_velocity(Constants.catapult_motor_speed, PERCENT)
            else:
                self.catapult_motor.set_velocity(0)
