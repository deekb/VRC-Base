HolonomicDrivetrain
====================

**This module provides a drivetrain controller for any standard holonomic drive base (Mecanum and X-Drive). It allows you to control the drivetrain using a controller, move to specific positions, follow paths, and more.**

Classes
-------


* `Drivetrain(timer, terminal)`: Represents a new drivetrain.
    > `timer`: A timer object, an instance of the `Brain.timer` class.\
    `terminal`: The terminal object to print debugging data to, an instance of the `Utilities.Terminal` class.

  Methods
  -------
  - `move_to_position(target_position, maximum_speed)`: Move to the specified position.
    > `target_position`: The position to move to. \
    `maximum_speed`: The maximum speed between zero and one for the robot to move while trying to reach the target_position.

  - `follow_path(point_list)`: Move the robot along a given path.
    > `point_list`: The list of points (x, y positions) to follow.

  - `move(direction, speed, spin) -> None`: Move the drivetrain towards a vector. This function is mostly used internally, however, it is available for debugging if needed
    > `direction`: The direction to move in, relative to the robots current heading, in radians.\
    `speed`: The speed of movement, 0-1.\
    `spin`: The speed at which to spin 0-1 or None to allow the internal PID to set it automatically.

  - `move_headless(direction, magnitude, spin)`: Move the drivetrain in a headless manner (without considering the current heading).
    > `direction`: The direction to move in, relative to the field, in radians.\
    `speed`: The speed of movement, 0-1.\
    `spin`: The speed at which to spin 0-1 or None to allow the internal PID to set it automatically.

  - `calculate_optimal_turn(target_direction)`: Calculate the optimal turn amount in order to face a specific heading
    > `target_direction`: The target drivetrain heading

  - `turn_to_face_direction(heading_rad)`: Turn towards the passed heading in the most efficient way
    > `heading_rad`: The target heading

  - `stop`: Stop the drivetrain, (doesn't stop PID)

  - `_direction_pid_update`: Update the direction PID, called internally

  - `move_with_controller(controller, headless)`: Move the drivetrain using the passed controller.
    >`controller`: The controller to get input from.\
    `headless`: Whether to move the robot in headless mode (defaults to False).
    
  - `reset()`: Reset the drivetrain to its initial state.

  Properties
  ----------
  - `target_position`: The currently targeted position of the robot.\
  - `target_heading_rad`: The current target heading in radians.\
  - `target_heading_deg`: The current target heading in degrees.
