from math import sqrt


class Constraints:
    maxVelocity: float
    maxAcceleration: float

    def __init__(self, maxVelocity, maxAcceleration):
        self.maxVelocity = maxVelocity
        self.maxAcceleration = maxAcceleration


class State:
    position: float
    velocity: float

    def __init__(self, position=0.0, velocity=0.0):
        self.position = position
        self.velocity = velocity


class TrapezoidProfile:
    def __init__(self, constraints):
        self.m_constraints = constraints
        self.m_newAPI = True
        self.m_direction = 1
        self.m_current = State()
        self.m_goal = State()
        self.m_endAccel = 0.0
        self.m_endFullSpeed = 0.0
        self.m_endDeccel = 0.0

    @staticmethod
    def should_flip_acceleration(initial, goal):
        return initial.position > goal.position

    def direct(self, inp):
        result = State(inp.position, inp.velocity)
        result.position = result.position * self.m_direction
        result.velocity = result.velocity * self.m_direction
        return result

    def calculate(self, t, current, goal):
        self.m_direction = -1 if self.should_flip_acceleration(current, goal) else 1
        self.m_current = self.direct(current)
        goal = self.direct(goal)

        if self.m_current.velocity > self.m_constraints.maxVelocity:
            self.m_current.velocity = self.m_constraints.maxVelocity

        cutoffBegin = self.m_current.velocity / self.m_constraints.maxAcceleration
        cutoffDistBegin = (
            cutoffBegin * cutoffBegin * self.m_constraints.maxAcceleration / 2.0
        )

        cutoffEnd = goal.velocity / self.m_constraints.maxAcceleration
        cutoffDistEnd = cutoffEnd * cutoffEnd * self.m_constraints.maxAcceleration / 2.0

        fullTrapezoidDist = (
            cutoffDistBegin
            + (goal.position - self.m_current.position)
            + cutoffDistEnd
        )
        accelerationTime = self.m_constraints.maxVelocity / self.m_constraints.maxAcceleration

        fullSpeedDist = (
            fullTrapezoidDist
            - accelerationTime * accelerationTime * self.m_constraints.maxAcceleration
        )

        if fullSpeedDist < 0:
            accelerationTime = sqrt(fullTrapezoidDist / self.m_constraints.maxAcceleration)
            fullSpeedDist = 0

        self.m_endAccel = accelerationTime - cutoffBegin
        self.m_endFullSpeed = self.m_endAccel + fullSpeedDist / self.m_constraints.maxVelocity
        self.m_endDeccel = self.m_endFullSpeed + accelerationTime - cutoffEnd
        result = State(self.m_current.position, self.m_current.velocity)

        if t < self.m_endAccel:
            result.velocity += t * self.m_constraints.maxAcceleration
            result.position += (
                self.m_current.velocity
                + t * self.m_constraints.maxAcceleration / 2.0
            ) * t
        elif t < self.m_endFullSpeed:
            result.velocity = self.m_constraints.maxVelocity
            result.position += (
                self.m_current.velocity
                + self.m_endAccel * self.m_constraints.maxAcceleration / 2.0
            ) * self.m_endAccel + self.m_constraints.maxVelocity * (t - self.m_endAccel)
        elif t <= self.m_endDeccel:
            result.velocity = (
                goal.velocity + (self.m_endDeccel - t) * self.m_constraints.maxAcceleration
            )
            timeLeft = self.m_endDeccel - t
            result.position = (
                goal.position
                - (
                    goal.velocity
                    + timeLeft * self.m_constraints.maxAcceleration / 2.0
                )
                * timeLeft
            )
        else:
            result = goal

        return self.direct(result)

    def timeLeftUntil(self, target):
        position = self.m_current.position * self.m_direction
        velocity = self.m_current.velocity * self.m_direction

        endAccel = self.m_endAccel * self.m_direction
        endFullSpeed = self.m_endFullSpeed * self.m_direction - endAccel

        if target < position:
            endAccel = -endAccel
            endFullSpeed = -endFullSpeed
            velocity = -velocity

        endAccel = max(endAccel, 0)
        endFullSpeed = max(endFullSpeed, 0)

        acceleration = self.m_constraints.maxAcceleration
        decceleration = -self.m_constraints.maxAcceleration

        distToTarget = abs(target - position)
        if distToTarget < 1e-6:
            return 0

        accelDist = velocity * endAccel + 0.5 * acceleration * endAccel * endAccel

        deccelVelocity = sqrt(
            abs(velocity * velocity + 2 * acceleration * accelDist)
        ) if endAccel > 0 else velocity

        fullSpeedDist = self.m_constraints.maxVelocity * endFullSpeed
        deccelDist = distToTarget - fullSpeedDist - accelDist

        accelTime = (
            -velocity
            + sqrt(abs(velocity * velocity + 2 * acceleration * accelDist))
        ) / acceleration

        deccelTime = (
            -deccelVelocity
            + sqrt(
                abs(
                    deccelVelocity
                    * deccelVelocity
                    + 2 * decceleration * deccelDist
                )
            )
        ) / decceleration

        fullSpeedTime = fullSpeedDist / self.m_constraints.maxVelocity

        return accelTime + fullSpeedTime + deccelTime

    def totalTime(self):
        return self.m_endDeccel

    def isFinished(self, t):
        return t >= self.totalTime()


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
    total_time = profile.totalTime()

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

