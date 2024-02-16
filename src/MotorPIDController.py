from vex import *
from PIDController import PIDController


class MotorPID:
    """
    Wrap a motor definition in this class to use a custom PID to control its movements ie: my_motor = MotorPID(Motor(...), kp, kd, t)
    **Waring, this class disables all motor functionality except the following functions:[set_velocity, set_stopping, stop, spin, velocity]**
    """

    def __init__(
        self,
        timer: Brain.timer,
        motor_object,
        kp: float = 0.4,
        ki: float = 0.01,
        kd: float = 0.05,
        t: float = 0.1,
    ):
        """
        Creates an instance of the MotorPID

        Args:
            motor_object: The motor to apply the PID to
            kp: Kp value for the PID: How quickly to modify the target value if it has not yet reached the desired value
            ki: Ki value for the PID: Integral gain to reduce steady-state error
            kd: Kd value for the PID: Higher values reduce the response time and limit overshoot
            t: Time between PID updates
        """
        self.motor_object = motor_object
        self.motor_PID = PIDController(timer, kp, ki, kd)
        self.pid_thread = Thread(self._loop)
        self.t = t

    def update(self) -> None:
        """
        Update the PID state with the most recent motor and target velocities and send the normalized value to the motor
        """

        self.motor_object.set_velocity(self.motor_PID.update(self.velocity()), PERCENT)

    def _loop(self) -> None:
        """
        Used to run the PID in a new thread: updates the values the PID uses and handles
          applying the PID output to the motor
        """

        while True:
            self.update()
            wait(self.t, SECONDS)

    def set_velocity(self, velocity: float) -> None:
        """
        Set the motor's target velocity using the PID, make sure you run PID_loop in a new thread or this
        will have no effect
        :param velocity: The new target velocity of the motor
        :type velocity: float
        """

        self.motor_PID.setpoint = velocity

    def spin(self, direction):
        self.motor_object.spin(direction)

    def stop(self):
        self.motor_object.stop()

    def velocity(self):
        return self.motor_object.velocity(PERCENT)
