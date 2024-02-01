import Constants
from vex import *


class Wings:
    def __init__(self):
        self.wings = DigitalOut(Constants.wing_port)

        self.wings_state = Constants.PneumaticsState.in_

        self.update_thread = Thread(self.wings_loop)

    def wings_out(self):
        self.wings_state = Constants.PneumaticsState.out

    def wings_in(self):
        self.wings_state = Constants.PneumaticsState.in_

    def toggle_wings(self):
        self.wings_state = Constants.PneumaticsState.out if self.wings_state == Constants.PneumaticsState.in_ else Constants.PneumaticsState.in_

    def wings_loop(self):
        while True:
            if self.wings_state == Constants.PneumaticsState.in_:
                self.wings.set(False)

            if self.wings_state == Constants.PneumaticsState.out:
                self.wings.set(True)

            wait(100, MSEC)
