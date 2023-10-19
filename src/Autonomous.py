class AutonomousRoutine:
    def __init__(self, log_object):
        self.log_object = log_object

    def log(self, string):
        self.log_object.log(string)

    def run(self):
        """Your autonomous code should be declared here"""
        ...


class NothingAutonomous(AutonomousRoutine):
    def __init__(self, log_object):
        super().__init__(log_object)

    def run(self):
        self.log("Doing nothing")
        self.log("Done")
        self.log("That was easy")
        self.log_object.close()


class SkillsAutonomous(AutonomousRoutine):
    def __init__(self, log_object, drivetrain):
        super().__init__(log_object)
        self.drivetrain = drivetrain

    def run(self):
        self.log("Starting skills")
        # Stop and reset the drivetrain
        self.drivetrain.stop()
        self.drivetrain.reset()
        self.log("Drivetrain reset")

        # Set the robot's starting position
        self.drivetrain._odometry.position = (0, 0)
        self.log(
            "Robot is at: ("
            + str(self.drivetrain._odometry.x)
            + ", "
            + str(self.drivetrain._odometry.y)
            + ")"
        )

        # Drive in a square
        self.log("Starting square maneuver 4x4 ft")
        self.drivetrain.follow_path(
            [(0, 0), (0, 121.92), (121.92, 121.92), (121.92, 0), (0, 0)]
        )

        # Stop the drivetrain
        self.log("Stopping the drivetrain")
        self.drivetrain.stop()

        self.log("Done")
        self.log_object.close()


available_autonomous_routines = [
    ("Skills", SkillsAutonomous),
    ("Nothing", NothingAutonomous),
]
