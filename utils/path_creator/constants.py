import os

# Constants
BASE_DIR = os.path.dirname(__file__)
DEPLOY_DIR = os.path.join(BASE_DIR, "deploy")
BACKGROUND_FILE = os.path.join(DEPLOY_DIR, "images", "Field.png")

# Screen constants
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
FIELD_WIDTH, FIELD_HEIGHT = 366, 366

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
