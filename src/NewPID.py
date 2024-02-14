class PidController:
    instances = 0

    def __init__(self, kp, ki, kd, period=0.02):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        if period <= 0:
            raise ValueError("Controller period must be a non-zero positive number!")
        self.period = period
        self.maximum_integral = 1.0
        self.minimum_integral = -1.0
        self.is_continuous = False
        self.position_error = 0
        self.velocity_error = 0
        self.prev_error = 0
        self.total_error = 0
        self.position_tolerance = 0.05
        self.velocity_tolerance = float("inf")
        self.setpoint = 0
        self.measurement = 0
        self.have_measurement = False
        self.have_setpoint = False
        PidController.instances += 1

    def close(self):
        pass

    def set_pid(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def set_p(self, kp):
        self.kp = kp

    def set_i(self, ki):
        self.ki = ki

    def set_d(self, kd):
        self.kd = kd

    def set_integral_zone(self, i_zone):
        if i_zone < 0:
            raise ValueError("integral zone must be a non-negative number!")
        self.i_zone = i_zone

    def get_p(self):
        return self.kp

    def get_i(self):
        return self.ki

    def get_d(self):
        return self.kd

    def get_izone(self):
        return getattr(self, "i_zone", float("inf"))

    def get_period(self):
        return self.period

    def get_position_tolerance(self):
        return self.position_tolerance

    def get_velocity_tolerance(self):
        return self.velocity_tolerance

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
        self.have_setpoint = True
        if self.is_continuous:
            error_bound = (self.maximum_input - self.minimum_input) / 2.0
            self.position_error = (self.setpoint - self.measurement) % error_bound
        else:
            self.position_error = self.setpoint - self.measurement
        self.velocity_error = (self.position_error - self.prev_error) / self.period

    def get_setpoint(self):
        return self.setpoint

    def at_setpoint(self):
        return (
            self.have_measurement
            and self.have_setpoint
            and abs(self.position_error) < self.position_tolerance
            and abs(self.velocity_error) < self.velocity_tolerance
        )

    def enable_continuous_input(self, minimum_input, maximum_input):
        self.is_continuous = True
        self.minimum_input = minimum_input
        self.maximum_input = maximum_input

    def disable_continuous_input(self):
        self.is_continuous = False

    def is_continuous_input_enabled(self):
        return self.is_continuous

    def set_integrator_range(self, minimum_integral, maximum_integral):
        self.minimum_integral = minimum_integral
        self.maximum_integral = maximum_integral

    def set_tolerance(self, position_tolerance, velocity_tolerance=float("inf")):
        self.position_tolerance = position_tolerance
        self.velocity_tolerance = velocity_tolerance

    def get_position_error(self):
        return self.position_error

    def get_velocity_error(self):
        return self.velocity_error

    def calculate(self, measurement, setpoint=None):
        if setpoint is not None:
            self.setpoint = setpoint
            self.have_setpoint = True
        self.measurement = measurement
        self.prev_error = self.position_error
        self.have_measurement = True
        if self.is_continuous:
            error_bound = (self.maximum_input - self.minimum_input) / 2.0
            self.position_error = (self.setpoint - self.measurement) % error_bound
        else:
            self.position_error = self.setpoint - self.measurement
        self.velocity_error = (self.position_error - self.prev_error) / self.period
        if abs(self.position_error) > self.i_zone:
            self.total_error = 0
        elif self.ki != 0:
            self.total_error = max(
                min(
                    self.total_error + self.position_error * self.period,
                    self.maximum_integral / self.ki,
                ),
                self.minimum_integral / self.ki,
            )
        return (
            self.kp * self.position_error
            + self.ki * self.total_error
            + self.kd * self.velocity_error
        )

    def reset(self):
        self.position_error = 0
        self.prev_error = 0
        self.total_error = 0
        self.velocity_error = 0
        self.have_measurement = False
