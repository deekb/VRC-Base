# Robot
**The Robot module represents the high-level instructions for the robot. It includes a class called Robot which handles the creation and use of motors, sensors, and controllers. The module defines functions for handling autonomous and driver control, as well as a utility function for debugging. Additionally, it handles the selection of autonomous routines, and coordinates the execution of autonomous and driver control based on the competition mode.**

Dependencies
-------------------

* Constants
* HolonomicDrivetrain
* HolonomicOdometry
* Utilities
* Autonomous


Classes
-------

* `Robot`: A class representing the robot in its entirety. All high-level robot logic belongs here


Functions
---------

* `autonomous_handler()`: Coordinate when to run the autonomous function(s).
* `select_autonomous()`: Selects which autonomous routine to execute using the controller.
* `driver_handler()`: Coordinate when to run the driver function(s).
* `on_driver()`: This is the function designated to run when the driver control portion of the program is triggered.
* `on_autonomous()`: This is the function designated to run when the autonomous portion of the program is triggered.


> The following functions are for debugging only and will likely be removed soon
> * `debug_thread()`: This function is for testing purposes and displays the position and direction of the drivetrain. It also allows resetting the drivetrain when button A is pressed and performing pre-determined actions when button B is pressed.
