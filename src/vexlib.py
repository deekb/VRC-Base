from vex import *

AUTONOMOUS_MODE = 1
DRIVER_CONTROL_MODE = 2


class Robot:
    def __init__(self, brain):
        self.competition = Competition(
            lambda *args, **kwargs: None, lambda *args, **kwargs: None
        )
        self.brain = brain
        self.enabled = self.competition.is_enabled()
        self.previous_enabled = self.enabled
        self.mode = (
            AUTONOMOUS_MODE if self.competition.is_autonomous() else DRIVER_CONTROL_MODE
        )
        self.current_time = self.brain.timer.time(MSEC)
        self.previous_time = self.current_time
        self.previous_mode = self.mode
        self.target_tick_duration = 20

        # Start the mainloop
        self._mainloop()

    def _mainloop(self):
        """
        Handle all internal competition state logic
        """
        while True:
            self.is_enabled = self.competition.is_enabled()
            self.mode = (
                AUTONOMOUS_MODE
                if self.competition.is_autonomous()
                else DRIVER_CONTROL_MODE
            )

            # Handle instant callbacks
            if self.mode != self.previous_mode:
                if self.enabled:
                    self.on_enable()
                    if self.mode == AUTONOMOUS_MODE:
                        self.on_autonomous()
                    elif self.mode == DRIVER_CONTROL_MODE:
                        self.on_driver_control()
                else:
                    self.on_disable()
                    if self.mode == AUTONOMOUS_MODE:
                        self.on_autonomous_disable()
                    elif self.mode == DRIVER_CONTROL_MODE:
                        self.on_driver_control_disable()

            self.current_time = self.brain.timer.time(MSEC)
            if self.current_time - self.previous_time >= 20:
                # Handle continuous loops
                if self.enabled:
                    if self.mode == DRIVER_CONTROL_MODE:
                        self.driver_control_periodic()
                    elif self.mode == AUTONOMOUS_MODE:
                        self.autonomous_periodic()
                    self.enabled_periodic()
                else:
                    self.disabled_periodic()
                self.periodic()
            self.previous_mode = self.mode

    """Instant methods"""

    def on_enable(self):
        """
        Run whenever the robot is enabled while in either autonomous or driver control mode
        This means that this method is also executed when the robot is enabled and is switched from autonomous to driver control mode or vice versa
        """

    def on_disable(self):
        """
        Run whenever the robot is disabled while in either autonomous or driver control mode
        This means that this method is also executed when the robot is enabled and is switched from autonomous to driver control mode or vice versa
        """

    def on_driver_control(self):
        """
        Run whenever the robot is enabled while in driver control mode or is enabled and switches from autonomous to driver control
        """

    def on_driver_control_disable(self):
        """
        Run whenever the robot is disabled while in driver control mode or is disabled and switches from autonomous to driver control
        """

    def on_autonomous(self):
        """
        Run whenever the robot is enabled while in autonomous mode or is enabled and switches from driver control to autonomous
        """

    def on_autonomous_disable(self):
        """
        Run whenever the robot is disabled while in autonomous mode or is disabled and switches from driver control to autonomous
        """

    """Continuous methods"""

    def periodic(self):
        """
        Run periodically 50 times a second (20ms between ticks)
        """

    def driver_control_periodic(self):
        """
        Run periodically 50 times a second (20ms between ticks) while driver control is enabled
        """

    def autonomous_periodic(self):
        """
        Run periodically 50 times a second (20ms between ticks) while autonomous is enabled
        """

    def enabled_periodic(self):
        """
        Run periodically 50 times a second (20ms between ticks) while the robot is enabled
        """

    def disabled_periodic(self):
        """
        Run periodically 50 times a second (20ms between ticks) while the robot is disabled
        """
