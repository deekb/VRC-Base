from vex import Brain, SECONDS
from Utilities import clamp


class PIDController:
    """
    A generalized PID controller implementation.
    """

    def __init__(
        self,
        timer: Brain.timer,
        kp: float = 1.0,
        ki: float = 0.0,
        kd: float = 0.0,
        t: float = 0.05,
        integral_zone=(-float("inf"), float("inf")),
    ):
        """
        Initializes a PIDController instance.
        :param timer: The timer object used to measure time.
        :param kp: Kp value for the PID.
        :param ki: Ki value for the PID.
        :param kd: Kd value for the PID.
        :param t: Minimum time between update calls.
        All calls made before this amount of time has passed since the last calculation will be ignored.
        :param integral_zone: The lower and upper bounds for the integral term to prevent windup.
        """

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.time_step = t
        self.integral_zone = integral_zone
        self.position_tolerance = 0
        self.velocity_tolerance = 0
        self.setpoint = 0.0
        self._timer = timer
        self._previous_time = timer.time(SECONDS)
        self._current_value = 0.0
        self._error_integral = 0.0
        self._last_error_derivative = 0.0
        self._previous_error = 0.0
        self._control_output = 0.0

    def set_tunings(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd

    def set_integral_zone(self, integral_zone):
        self.integral_zone = integral_zone

    def reset(self):
        self._error_integral = 0
        self._control_output = 0
        self._previous_error = self.setpoint - self._current_value

    def update(self, current_value: float) -> float:
        """
        Update the PID state with the most recent current value and calculate the control output.

        Args:
            current_value: The current measurement or feedback value

        Returns:
            The calculated control output.
        """

        current_time = self._timer.time(SECONDS)
        delta_time = current_time - self._previous_time

        if delta_time < self.time_step:
            return self._control_output

        self._previous_time = current_time

        current_error = self.setpoint - current_value
        self._error_integral += current_error * delta_time
        # Apply integral windup prevention
        # PID integral windup is a phenomenon that occurs when the integral term of a PID
        # controller continues to accumulate error even when the controller's output is saturated.
        # This can lead to overshoot, instability, and poor performance in control systems.
        # if your Kp is reasonably low, and you are still experiencing overshoot/instability/oscillation,
        # then try decreasing the span of the integral zone
        if self.ki != 0:
            self._error_integral = clamp(
                self._error_integral, self.integral_zone[0], self.integral_zone[1]
            )
        self._last_error_derivative = (
            current_error - self._previous_error
        ) / delta_time
        self._control_output = (
            self.kp * current_error
            + self.ki * self._error_integral
            + self.kd * self._last_error_derivative
        )
        self._previous_error = current_error

        return self._control_output

    def at_setpoint(self):
        return (
            self._previous_error <= self.position_tolerance
            and self._last_error_derivative < self.velocity_tolerance
        )
