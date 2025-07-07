# Window and grid configuration
INVENTORY_HEIGHT = 120  # Height of inventory area at bottom (scaled up)
GAME_HEIGHT = 1200  # Height of game area
WINDOW_SIZE = (1600, GAME_HEIGHT + INVENTORY_HEIGHT)
GRID_SIZE = 64  # Size of each grid cell in pixels
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BRIGHT_BLUE = (0, 191, 255)  # Diamond
RED = (255, 0, 0)  # Lava
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)
SAND_COLOR = (238, 203, 173)
GRAY = (128, 128, 128)  # Stone