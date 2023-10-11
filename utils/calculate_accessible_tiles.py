import sys
import time
import math
import os

sim_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simulations"
)

deploy_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deploy"
)

simulation_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simulations"
)


sys.path.append(sim_dir)

import pathfinding_environment

environment = pathfinding_environment.Env(
    os.path.join(simulation_dir, "Pathfinding_Obstacles_3_to_1.png")
)

accessible_tiles = set()

print("Precalculating accessible tiles")
start_time = time.perf_counter()
for tile_x in range(environment.x_size):
    for tile_y in range(environment.y_size):
        is_collision = False
        for obstacle in environment.obstacles:
            if math.hypot(obstacle[0] - tile_x, obstacle[1] - tile_y) < 6:
                is_collision = True
                break
        if not is_collision:
            accessible_tiles.add((tile_x, tile_y))

print(accessible_tiles)
with open(os.path.join(deploy_dir, "available_positions.txt"), "w") as f:
    f.write(str(accessible_tiles))

print(f"Completed in {time.perf_counter() - start_time} seconds")
