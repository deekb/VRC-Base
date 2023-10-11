"""
Competition Code for VRC: Over-Under (2024-2025)
Team: 3773P (Bowbots Phosphorus) from Bow NH
Author: Derek Baier (deekb on GitHub)
Project homepage: https://github.com/deekb/VRC-OverUnder
Project archive: https://github.com/deekb/VRC-OverUnder/archive/master.zip
Contact Derek.m.baier@gmail.com for more information

This module contains part of the test code for the VRC (VEX Robotics Competition) Over-Under game,
for the 2024-2025 season.

The code is specifically developed for Team 3773P, known as Bowbots Phosphorus, and is authored by Derek Baier.

The project homepage and archive can be found on GitHub at the provided links.

For more information about the project, you can contact Derek Baier at the given email address.
"""


import time
import matplotlib.pyplot as plt


class PIDController(object):
    """
    A generalized PID controller implementation.
    """

    def __init__(self, kp: float = 1.0, ki: float = 0.0, kd: float = 0.0, t: float = 0.05, integral_limit: float = 1.0):
        """
        Initializes a PIDController instance.
        :param kp: Kp value for the PID.
        :param ki: Ki value for the PID.
        :param kd: Kd value for the PID.
        :param t: Minimum time between update calls.
        All calls made before this amount of time has passed since the last calculation will be ignored.
        :param integral_limit: The maximum absolute value for the integral term to prevent windup.
        """

        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._time_step = t
        self._previous_time = time.monotonic()
        self._current_value = 0.0
        self._target_value = 0.0
        self._error_integral = 0.0
        self._integral_limit = integral_limit
        self._previous_error = 0.0
        self._control_output = 0.0

    @property
    def kp(self) -> float:
        """
        Getter for the Kp value of the PID.
        :return: The Kp value.
        """

        return self._kp

    @kp.setter
    def kp(self, value: float):
        """
        Setter for the Kp value of the PID.
        :param value: The new Kp value.
        """

        self._kp = value

    @property
    def ki(self) -> float:
        """
        Getter for the Ki value of the PID.
        :return: The Ki value.
        """

        return self._ki

    @ki.setter
    def ki(self, value: float):
        """
        Setter for the Ki value of the PID.
        :param value: The new Ki value.
        """

        self._ki = value

    @property
    def kd(self) -> float:
        """
        Getter for the Kd value of the PID.
        :return: The Kd value.
        """

        return self._kd

    @kd.setter
    def kd(self, value: float):
        """
        Setter for the Kd value of the PID.
        :param value: The new Kd value.
        """

        self._kd = value

    @property
    def target_value(self) -> float:
        """
        Getter for the target value of the PID.
        :return: The target value.
        """

        return self._target_value

    @target_value.setter
    def target_value(self, value: float):
        """
        Setter for the target value of the PID.
        :param value: The new target value.
        """

        self._target_value = value
        self._error_integral = 0
        self._previous_error = self._target_value - self._current_value
        self._control_output = 0

    def update(self, current_value: float) -> float:
        """
        Update the PID state with the most recent current value and calculate the control output.
        :param current_value: The current measurement or feedback value.
        :return: The calculated control output.
        """

        current_time = time.monotonic()
        delta_time = current_time - self._previous_time

        if delta_time < self._time_step:
            return self._control_output

        self._previous_time = current_time

        current_error = self._target_value - current_value
        self._error_integral += current_error * delta_time
        # Apply integral windup prevention
        if self._ki != 0:
            self._error_integral = max(min(self._error_integral, self._integral_limit / self._ki),
                                       -self._integral_limit / self._ki)
        error_derivative = (current_error - self._previous_error) / delta_time
        self._control_output = (
                self._kp * current_error + self._ki * self._error_integral + self._kd * error_derivative
        )
        self._previous_error = current_error
        return self._control_output


class MotorSimulation:
    def __init__(self):
        self._current_value = 0.0

    def get_measurement(self) -> float:
        return self._current_value

    def set_input(self, control_output: float):
        # Simulate motor dynamics
        self._current_value += control_output * 0.1


# Create a PIDController instance
pid_controller = PIDController(kp=0.3, ki=0.1, kd=0.01, t=0.02, integral_limit=0.2)

# Set the target value for the PID controller
pid_controller.target_value = 100

# Create a motor simulation object
motor = MotorSimulation()

# Lists to store the measurement and control output values
measurements = []
control_outputs = []

start_time = time.monotonic()

# Simulate the motor control loop
while time.monotonic() - start_time < 10.0:
    # Get the current measurement from the motor
    current_value = motor.get_measurement()

    # Update the PID controller with the current measurement
    control_output = pid_controller.update(current_value)

    # Apply the control output to the motor
    motor.set_input(control_output)

    # Sleep for a small duration to simulate the time step
    time.sleep(0.01)

    # Append the current measurement and control output to the lists
    measurements.append(current_value)
    control_outputs.append(control_output)

    # Print the current measurement and control output
    # print(f"Measurement: {current_value:.2f}, Control Output: {control_output:.2f}")

# Plot the measurement and control output values
plt.figure()
plt.plot(measurements, label='Measurement')
plt.plot(control_outputs, label='Control Output')
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Motor Simulation')
plt.legend()
plt.grid(True)
resolution_value = 700
# plt.savefig("PID_Graph.png", format="png", dpi=resolution_value)
plt.show()
