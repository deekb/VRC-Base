import Constants
from vex import *


class Wings:
    def __init__(self):
        self.left_wing = DigitalOut(Constants.left_wing_port)
        self.right_wing = DigitalOut(Constants.right_wing_port)

        self.left_wing_state = Constants.PneumaticsState.in_
        self.right_wing_state = Constants.PneumaticsState.in_

        self.update_thread = Thread(self.wings_loop)

    def wings_out(self):
        self.left_wing_out()
        self.right_wing_out()

    def wings_in(self):
        self.left_wing_in()
        self.right_wing_in()

    def left_wing_out(self):
        self.left_wing_state = Constants.PneumaticsState.out

    def left_wing_in(self):
        self.left_wing_state = Constants.PneumaticsState.in_

    def right_wing_out(self):
        self.right_wing_state = Constants.PneumaticsState.out

    def right_wing_in(self):
        self.right_wing_state = Constants.PneumaticsState.in_

    def wings_loop(self):
        while True:
            if self.left_wing_state == Constants.PneumaticsState.in_:
                self.left_wing.set(False)
            elif self.left_wing_state == Constants.PneumaticsState.out:
                self.left_wing.set(True)

            if self.right_wing_state == Constants.PneumaticsState.in_:
                self.right_wing.set(False)
            elif self.right_wing_state == Constants.PneumaticsState.out:
                self.right_wing.set(True)

            wait(100, MSEC)
