from PIL import Image


class Env:
    def __init__(self, obstacle_map):
        self.x_size = None  # size of environment (to be determined from the image)
        self.y_size = None
        self.obstacles = self.get_obstacles(obstacle_map)  # list of positions that are obstacles

    def get_obstacles(self, obstacle_map):
        """
        Initialize obstacles' positions from the provided obstacle_map image file.

        :param obstacle_map: The filename of the image that represents the obstacle map.
        :return: Set containing tuples of obstacle positions (x, y).
        """
        img = Image.open(obstacle_map)
        self.x_size, self.y_size = img.size
        obs = set()

        # Analyze the image to determine obstacle positions
        for x in range(self.x_size):
            for y in range(self.y_size):
                pixel = img.getpixel((x, y))
                if pixel != (0, 0, 0, 0):  # Assume all non-transparent pixels are obstacles
                    obs.add((x, y))

        return obs
