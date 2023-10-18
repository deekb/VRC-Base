import Constants
from vex import *


class Intake:
    def __init__(self, brain):
        self.wrist_motor = Motor(
            Constants.wrist_motor_port,
            Constants.wrist_motor_gear_ratio,
            Constants.wrist_motor_inverted,
        )
        self.claw_pneumatic_solenoid = DigitalOut(brain.three_wire_port.a)

        self.wrist_motor.stop()

        self.wrist_state = Constants.WristState.down
        self.claw_state = Constants.ClawState.open

        self.wrist_motor.set_velocity(15, PERCENT)

        self.update_thread = Thread(self.intake_loop)

    def wrist_up(self):
        self.wrist_state = Constants.WristState.up

    def wrist_down(self):
        self.wrist_state = Constants.WristState.down

    def claw_close(self):
        self.claw_state = Constants.ClawState.closed

    def claw_open(self):
        self.claw_state = Constants.ClawState.open

    def toggle_claw(self):
        if self.claw_state == Constants.ClawState.open:
            self.claw_state = Constants.ClawState.closed
        elif self.claw_state == Constants.ClawState.closed:
            self.claw_state = Constants.ClawState.open

    def toggle_wrist(self):
        if self.wrist_state == Constants.WristState.up:
            self.wrist_state = Constants.WristState.down
        elif self.wrist_state == Constants.WristState.down:
            self.wrist_state = Constants.WristState.up

    def intake_loop(self):
        while True:
            if self.wrist_state == Constants.WristState.up:
                self.wrist_motor.spin_to_position(-130, DEGREES, False)
            elif self.wrist_state == Constants.WristState.down:
                self.wrist_motor.spin_to_position(0, DEGREES, False)

            if self.claw_state == Constants.ClawState.open:
                self.claw_pneumatic_solenoid.set(False)
            elif self.claw_state == Constants.ClawState.closed:
                self.claw_pneumatic_solenoid.set(True)
            wait(100, MSEC)
