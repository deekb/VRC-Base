from math import sqrt


class Constraints:
    maxVelocity: float
    maxAcceleration: float

    def __init__(self, max_velocity, max_acceleration):
        self.maxVelocity = max_velocity
        self.maxAcceleration = max_acceleration


class State:
    position: float
    velocity: float

    def __init__(self, position=0.0, velocity=0.0):
        self.position = position
        self.velocity = velocity


class TrapezoidProfile:
    def __init__(self, constraints):
        self.constraints = constraints
        self.newAPI = True
        self.direction = 1
        self.current = State()
        self.goal = State()
        self.end_accel = 0.0
        self.end_full_speed = 0.0
        self.end_deccel = 0.0

    @staticmethod
    def should_flip_acceleration(initial, goal):
        return initial.position > goal.position

    def _direct(self, inp):
        result = State(inp.position, inp.velocity)
        result.position = result.position * self.direction
        result.velocity = result.velocity * self.direction
        return result

    def calculate(self, t, current, goal):
        self.direction = -1 if self.should_flip_acceleration(current, goal) else 1
        self.current = self._direct(current)
        goal = self._direct(goal)

        if self.current.velocity > self.constraints.maxVelocity:
            self.current.velocity = self.constraints.maxVelocity

        cutoff_begin = self.current.velocity / self.constraints.maxAcceleration
        cutoff_dist_begin = (
                cutoff_begin * cutoff_begin * self.constraints.maxAcceleration / 2.0
        )

        cutoff_end = goal.velocity / self.constraints.maxAcceleration
        cutoff_dist_end = cutoff_end * cutoff_end * self.constraints.maxAcceleration / 2.0

        full_trapezoid_dist = (
            cutoff_dist_begin
            + (goal.position - self.current.position)
            + cutoff_dist_end
        )
        acceleration_time = self.constraints.maxVelocity / self.constraints.maxAcceleration

        full_speed_dist = (
            full_trapezoid_dist
            - acceleration_time * acceleration_time * self.constraints.maxAcceleration
        )

        if full_speed_dist < 0:
            acceleration_time = sqrt(full_trapezoid_dist / self.constraints.maxAcceleration)
            full_speed_dist = 0

        self.end_accel = acceleration_time - cutoff_begin
        self.end_full_speed = self.end_accel + full_speed_dist / self.constraints.maxVelocity
        self.end_deccel = self.end_full_speed + acceleration_time - cutoff_end
        result = State(self.current.position, self.current.velocity)

        if t < self.end_accel:
            result.velocity += t * self.constraints.maxAcceleration
            result.position += (
                                       self.current.velocity
                                       + t * self.constraints.maxAcceleration / 2.0
            ) * t
        elif t < self.end_full_speed:
            result.velocity = self.constraints.maxVelocity
            result.position += (
                                       self.current.velocity
                                       + self.end_accel * self.constraints.maxAcceleration / 2.0
            ) * self.end_accel + self.constraints.maxVelocity * (t - self.end_accel)
        elif t <= self.end_deccel:
            result.velocity = (
                    goal.velocity + (self.end_deccel - t) * self.constraints.maxAcceleration
            )
            time_left = self.end_deccel - t
            result.position = (
                goal.position
                - (
                        goal.velocity
                        + time_left * self.constraints.maxAcceleration / 2.0
                )
                * time_left
            )
        else:
            result = goal

        return self._direct(result)

    def time_left_until(self, target):
        position = self.current.position * self.direction
        velocity = self.current.velocity * self.direction

        end_accel = self.end_accel * self.direction
        end_full_speed = self.end_full_speed * self.direction - end_accel

        if target < position:
            end_accel = -end_accel
            end_full_speed = -end_full_speed
            velocity = -velocity

        end_accel = max(end_accel, 0)
        end_full_speed = max(end_full_speed, 0)

        acceleration = self.constraints.maxAcceleration
        deceleration = -self.constraints.maxAcceleration

        dist_to_target = abs(target - position)
        if dist_to_target < 1e-6:
            return 0

        accel_dist = velocity * end_accel + 0.5 * acceleration * end_accel * end_accel

        deccel_velocity = sqrt(
            abs(velocity * velocity + 2 * acceleration * accel_dist)
        ) if end_accel > 0 else velocity

        full_speed_dist = self.constraints.maxVelocity * end_full_speed
        deccel_dist = dist_to_target - full_speed_dist - accel_dist

        accel_time = (
            -velocity
            + sqrt(abs(velocity * velocity + 2 * acceleration * accel_dist))
        ) / acceleration

        deccel_time = (
            -deccel_velocity
            + sqrt(
                abs(
                    deccel_velocity
                    * deccel_velocity
                    + 2 * deceleration * deccel_dist
                )
            )
        ) / deceleration

        full_speed_time = full_speed_dist / self.constraints.maxVelocity

        return accel_time + full_speed_time + deccel_time

    def total_time(self):
        return self.end_deccel

    def is_finished(self, t):
        return t >= self.total_time()


if __name__ == "__main__":
    # import matplotlib.pyplot as plt
    # import numpy as np

    # Constants
    max_velocity = 1.0  # m/s
    max_acceleration = 0.2  # m/s^2

    # Create TrapezoidProfile
    constraints = Constraints(max_velocity, max_acceleration)
    initial_state = State(0.0, 0.0)
    goal_state = State(10, 0)
    profile = TrapezoidProfile(constraints)

    profile.calculate(0, initial_state, goal_state)

    # Calculate total time for the profile
    total_time = profile.total_time()

    # Simulate the profile
    dt = 0.01
    simulation_time = np.arange(0.0, total_time, dt)

    positions = []
    velocities = []

    for t in simulation_time:
        state = profile.calculate(t, initial_state, goal_state)
        positions.append(state.position)
        velocities.append(state.velocity)

    # Plotting
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(simulation_time, positions, label="Position")
    plt.title("Trapezoid Profile Simulation")
    plt.ylabel("Position (m)")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(simulation_time, velocities, label="Velocity")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()

    plt.tight_layout()
    plt.show()

