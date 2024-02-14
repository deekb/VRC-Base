from PIDController import PIDController
from TrapezoidMovement import TrapezoidProfile, Constraints, State
from src.vex import Brain


class ProfiledPID:
    def __init__(self, pid_controller: PIDController, trapezoidal_movement_constraints: Constraints):
        self.PID = pid_controller
        self.trapezoidal_movement_constraints = trapezoidal_movement_constraints
        self.trapezoidal_movement_profile = TrapezoidProfile(trapezoidal_movement_constraints)

        self.initial_state = State(0.0, 0.0)
        self.goal_state = State(0.0, 0.0)

    def set_target_state(self, target_state: State):
        self.goal_state = target_state


class ProfiledPIDController:
    instances = 0

    def __init__(self, kp, ki, kd, constraints, period=0.02):
        self.m_controller = PIDController(kp, ki, kd, period)
        self.m_minimumInput = None
        self.m_maximumInput = None
        self.m_constraints = constraints
        self.m_profile = TrapezoidProfile(self.m_constraints)
        self.m_goal = State()
        self.m_setpoint = State()

        ProfiledPIDController.instances += 1

    def set_tunings(self, kp, ki, kd):
        self.m_controller.set_tunings(kp, ki, kd)

    def set_kp(self, kp):
        self.m_controller.kp = kp

    def set_ki(self, ki):
        self.m_controller.ki = ki

    def set_kd(self, kd):
        self.m_controller.d = kd

    def set_integral_zone(self, integral_zone):
        self.m_controller.integral_zone = integral_zone

    def get_kp(self):
        return self.m_controller.kp

    def get_ki(self):
        return self.m_controller.ki

    def get_kd(self):
        return self.m_controller.kd

    def get_integral_zone(self):
        return self.m_controller.integral_zone

    def get_time_step(self):
        return self.m_controller.time_step

    def get_position_tolerance(self):
        return self.m_controller.position_tolerance

    def get_velocity_tolerance(self):
        return self.m_controller.velocity_tolerance

    def set_goal(self, goal):
        self.m_goal = goal

    def set_constraints(self, constraints):
        self.m_constraints = constraints
        self.m_profile = TrapezoidProfile(self.m_constraints)

    def get_constraints(self):
        return self.m_constraints

    def get_setpoint(self):
        return self.m_setpoint

    def at_goal(self):
        return self.at_setpoint() and self.m_goal == self.m_setpoint

    def at_setpoint(self):
        return self.m_controller.at_setpoint()

    def enable_continuous_input(self, minimum_input, maximum_input):
        self.m_controller.enable_continuous_input(minimum_input, maximum_input)
        self.m_minimumInput = minimum_input
        self.m_maximumInput = maximum_input

    def disable_continuous_input(self):
        self.m_controller.disable_continuous_input()

    def set_integrator_range(self, minimum_integral, maximum_integral):
        self.m_controller.set_integrator_range(minimum_integral, maximum_integral)

    def set_tolerance(self, position_tolerance, velocity_tolerance=float('inf')):
        self.m_controller.set_tolerance(position_tolerance, velocity_tolerance)

    def get_position_error(self):
        return self.m_controller.get_position_error()

    def get_velocity_error(self):
        return self.m_controller.get_velocity_error()

    def calculate(self, measurement, goal=None, constraints=None):
        if goal:
            self.set_goal(goal)
        if constraints:
            self.set_constraints(constraints)

        if self.m_controller.is_continuous_input_enabled():
            error_bound = (self.m_maximumInput - self.m_minimumInput) / 2.0
            goal_min_distance = math_util.input_modulus(self.m_goal.position - measurement, -error_bound, error_bound)
            setpoint_min_distance = math_util.input_modulus(self.m_setpoint.position - measurement, -error_bound, error_bound)

            self.m_goal.position = goal_min_distance + measurement
            self.m_setpoint.position = setpoint_min_distance + measurement

        self.m_setpoint = self.m_profile.calculate(self.get_period(), self.m_setpoint, self.m_goal)
        return self.m_controller.calculate(measurement, self.m_setpoint.position)

    def reset(self, measurement):
        self.m_controller.reset()
        self.m_setpoint = measurement

    def init_sendable(self, builder):
        builder.set_smart_dashboard_type("ProfiledPIDController")
        builder.add_double_property("p", self.get_p, self.set_p)
        builder.add_double_property("i", self.get_i, self.set_i)
        builder.add_double_property("d", self.get_d, self.set_d)
        builder.add_double_property("izone", self.get_izone, self.set_integral_zone)
        builder.add_double_property("goal", lambda: self.get_goal().position, self.set_goal)




if __name__ == "__main__":
    brain = Brain()
    timer = brain.timer

    # Constants
    max_velocity = 1.0  # m/s
    max_acceleration = 0.2  # m/s^2

    trapezoidal_movement_constraints = Constraints(max_velocity, max_acceleration)

    PID_controller = PIDController(timer, 1, 0, 0, 0.05, 1)

    profiledPID = ProfiledPID(PID_controller, trapezoidal_movement_constraints)
