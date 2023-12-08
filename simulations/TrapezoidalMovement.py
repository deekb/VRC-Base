import time
import math
from matplotlib import pyplot as plt

SECONDS = 1
MSEC = 2


class TrapezoidalMovementProfile:
    def __init__(
        self,
        timer,
        acceleration_time,
        deceleration_time,
        target_travel_speed,
        target_travel_distance,
    ):
        self.START = 0
        self.ACCELERATING = 1
        self.TRAVELING = 2
        self.DECELERATING = 3

        self.state = self.START

        self.acceleration_time = acceleration_time
        self.deceleration_time = deceleration_time
        self.current_target_speed = 0

        self.timer = timer

        self.acceleration_start_time = None
        self.deceleration_start_time = None
        self.speed_when_deceleration_started = None
        self.distance_travelled = 0

        self.target_travel_speed = target_travel_speed
        self.target_travel_distance = target_travel_distance

        if self.target_travel_distance <= 0:
            raise ValueError("target_travel_distance must be greater than 0")

    def check_end_condition_met(self):
        return self.distance_travelled >= self.target_travel_distance - 0.01

    def update(self, distance_remaining, delta_time):
        self.distance_travelled = self.target_travel_distance - distance_remaining

        if self.check_end_condition_met():
            # We are there; stop
            return None

        if self.state == self.START:
            self.acceleration_start_time = self.timer.time(SECONDS)
            self.state = self.ACCELERATING
        elif self.state in (self.ACCELERATING, self.TRAVELING):
            # If we are currently in the accelerating state we should consider whether it is time to transition to the decelerating or traveling states
            # We know it is time to start decelerating if the amount of time that deceleration from our current speed would take is more than the amount of time we have.
            # Check how long it would take to decelerate if we start now

            distance_that_will_be_traveled_during_deceleration = ((self.current_target_speed ** 2) * self.deceleration_time) / (2 * self.current_target_speed)
            
            # print(distance_that_will_be_traveled_during_deceleration)
            
            distance_remaining_after_deceleration = (distance_remaining - distance_that_will_be_traveled_during_deceleration)

            if distance_remaining_after_deceleration <= 0:
                self.state = self.DECELERATING
                self.deceleration_start_time = self.timer.time(SECONDS)
                self.speed_when_deceleration_started = self.current_target_speed

            # We also need to check if it is time to transition into the traveling state
            elif self.timer.time(SECONDS) - self.acceleration_start_time >= self.acceleration_time:
                # If we have spent more than the allotted time for acceleration, transition straight to travelling
                self.state = self.TRAVELING

        if self.state == self.ACCELERATING:
            # Accelerate
            self.current_target_speed = (self.target_travel_speed / self.acceleration_time) * (self.timer.time(SECONDS) - self.acceleration_start_time)
            self.current_target_speed = (self.target_travel_speed / self.acceleration_time) * (self.timer.time(SECONDS) - self.acceleration_start_time)
        

        elif self.state == self.TRAVELING:
            # Travel
            self.current_target_speed = self.target_travel_speed
        elif self.state == self.DECELERATING:
            # Decelerate
            
            elapsed_time_from_deceleration_start = self.timer.time(SECONDS) - self.deceleration_start_time
            
            # time_remaining_for_deceleration = self.deceleration_time - elapsed_time_from_deceleration_start
            
            # self.current_target_speed = self.target_travel_speed * ((2 * distance_remaining) / (self.deceleration_time - (self.timer.time(SECONDS) - self.deceleration_start_time)))
            # self.current_target_speed = self.speed_when_deceleration_started * (1 - (1 / self.deceleration_time) * elapsed_time_from_deceleration_start)
            
            self.current_target_speed -= self.current_target_speed/(2 * distance_remaining) * delta_time

        return self.current_target_speed


class Timer:
    def __init__(self):
        pass
    
    def time(self, units):
        if units == SECONDS:
            return time.time()
        elif units == MSEC:
            return time.time() * 1000

distance_remaining = 10
speed = 0

timer = Timer()
movement_profile = TrapezoidalMovementProfile(timer, 0.5, 0.5, 1, distance_remaining)

current_time = timer.time(SECONDS)
start_time = current_time
last_time = current_time

times = []
speeds = []
remaining_distances = []
states = []
test = []

while current_time - start_time < 10:
    current_time = timer.time(SECONDS)
    delta_time = current_time - last_time
    last_time = current_time
    
    
    speed = movement_profile.update(distance_remaining, delta_time)
    
    if speed is None:
        print("Move done")
        break
    
    if abs(speed) > 1:
        print("clipping speed")
        speed = math.copysign(1, speed)
      
    distance_remaining -= delta_time * (speed)
    
    times.append(current_time - start_time)
    speeds.append(speed)
    states.append(movement_profile.state)
    remaining_distances.append(distance_remaining)
    if movement_profile.state == movement_profile.DECELERATING:
        test.append((movement_profile.deceleration_time - (movement_profile.timer.time(SECONDS) - movement_profile.deceleration_start_time)))
    else:
        test.append(None)

plt.plot(times, speeds, label="Speed")
plt.plot(times, remaining_distances, label="Remaining distance")
plt.plot(times, states, label="State")
# plt.plot(times, test, label="Test")
plt.plot(times, [0 for _ in times], label="0")
plt.legend(loc="upper left")
plt.ylim(-2, 4)
plt.show()