import os
from matplotlib import pyplot as plt
import numpy as np

plt.rcParams['figure.figsize'] = (30, 20)

rotation_log_contents = open(f"/media/{os.getenv('USER')}/VEX_V5/logs/Drivetrain_Rotation.log").read().split("\n")[:-1]

y_values = np.array([float(value) for value in rotation_log_contents])

x_values = np.arange(0, len(y_values), 1)

plt.plot(x_values, y_values)
plt.show()
