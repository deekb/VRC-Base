# Utilities
**This module offers a comprehensive set of tools and functions that can be utilized for tasks related to screen interaction, PID control, motor control, logging, deadzone application, distance checking, and value restriction.**

Classes
-------

* `Terminal`: Represents a terminal object.
  - `clear()`: Clears the brain screen.
  - `print()`: Prints a string to the console.


* `PIDController`: A generalized PID controller implementation.
  - `__init__()`: Initializes a PIDController instance.
  - `update()`: Update the PID state with the most recent current value and calculate the control output.
  - `target_value`: Getter and setter for the target value of the PID.
  - `kp`: Getter and setter for the Kp value of the PID.
  - `ki`: Getter and setter for the Ki value of the PID.
  - `kd`: Getter and setter for the Kd value of the PID.
  > ### PID Explained
  > PID can be confusing, I hope this mini-guide gives you enough information on PID to tune the provided PID and maybe even start using it in your own projects:\
  > \
  > PID (Proportional-Integral-Derivative) is a control algorithm used in engineering and robotics. It adjusts its output based on the error signal, which represents the deviation from the desired setpoint. The gains, namely Kp, Ki, and Kd, determine the contribution of each component. PID gains are prefixed with a "K" to indicate that they are coefficients or constants used to scale the effect of each component. Such effects are explained below, as well as a guide on tuning their gains.
  > * Kp is the **Proportional** gain, it determines the response of the control system based on the current error. It is directly proportional to the error, meaning a higher value of Kp will result in a stronger response to the error. However, if Kp is set too highly, it can lead to overshooting and instability or oscillation.
  > * Ki: is the **Integral** gain, it accounts for the accumulated error over time and helps eliminate steady-state errors. It integrates the error signal and produces a control output that reduces the cumulative error. A higher value of Ki increases the response to long-term error, but it can also introduce oscillations and instability if set too high.
  > * Kd: is the **Derivative** gain, it is responsible for anticipating future error trends by analyzing the rate of change of the error signal. It provides a damping effect by reducing the response as the error approaches zero. A higher value of Kd helps to stabilize the system and improve response time, but excessive values can cause high-frequency noise amplification and instability.

  > ### Tuning a PID controller:
  > Tuning a PID controller involves adjusting the values of Kp, Ki, and Kd, also called gains, in order to achieve the desired system response. Here are some general guidelines for tuning a PID controller:
  > 1. Start by setting all gains to zero.
  > 2. Increase the value of Kp slowly (start in increments of 0.05) until the system starts to respond quickly to changes but without excessive oscillations or overshoot.
  > 3. Add a small value of Ki to eliminate steady-state errors (when the system has stabilized but has not yet reached the setpoint) and bring the system to the desired setpoint.
  > 4. Adjust Kd to dampen oscillations and improve system stability without introducing excessive noise.
  > 5. Repeat steps 2-4, fine-tuning each gain until the system response meets the desired requirements.
  > 6. It may also be necessary to consider additional advanced tuning techniques such as Ziegler-Nichols or trial-and-error methods for more complex systems.

> Here is an example of what a properly tuned PID response can look like under **ideal** (smooth, linear, and predictable) conditions (Click for full size!)\
> [<img src="https://github.com/deekb/VRC-OverUnder/blob/assets/images/PID_Tests/Motor_Simulation.png?raw=true" width="800"/>](https://github.com/deekb/VRC-OverUnder/blob/working/diagrams/Motor_Simulation.png?raw=true)\
> This response was simulated and plotted by my PID_Test script, check it out to see how a PID should respond to changes in gains!


* `MotorPID`: Wrap a motor definition in this class to use a tunable PID to control its movements.
  - `__init__()`: Initializes a MotorPID instance.
  - `update()`: Update the PID state with the most recent motor and target velocities and send the normalized value to the motor.
  - `loop()`: Used to run the PID in a new thread.
  - `set_velocity()`: Set the motor's target velocity using the PID.
  - `spin()`: Spin the motor in the specified direction.
  - `stop()`: Stop the motor.
  - `velocity()`: Get the motor's velocity.
  > Confused? see [PID Explained](#pid-explained) and [Tuning A PID Controller](#tuning-a-pid-controller) above.


* `Logging`: A class that can run multiple logs for different events and store their outputs to the SD card.
  - `__init__()`: Create a new instance of the class.
  - `log()`: Send a string to the file, using the log format.
  - `exit()`: Close the log object.

Functions
---------

* `apply_deadzone()`: Apply a deadzone to the passed value.
  > The deadzone in a controller joystick creates a neutral zone where small joystick movements have no effect on the controlled system. This helps mitigate minor disturbances and noise. However, it's important to set an appropriate deadzone size to avoid sluggish response and reduced sensitivity. Balancing the deadzone size ensures optimal control performance while rejecting noise effectively.


* `hypotenuse(x, y)`: Get the hypotenuse length of a triangle with sides x and y.
  > The hypotenuse function calculates the hypotenuse length of a triangle with known side lengths x and y.\
  > This can be used to calculate the distance between two points if it is passed (x2-x1) and (y2-y1) as it's arguments\
  > This function represents the following code internally: `d = √(x² + y²)`


* `clamp(value, lower_limit, upper_limit)`: Restricts a value within a specified range.
  > The clamp function restricts an input value between a lower_limit and upper_limit. If the input value exceeds the range, the function sets it to the nearest limit.
