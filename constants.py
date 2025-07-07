# Window and grid configuration
INVENTORY_HEIGHT = 80  # Height of inventory area at bottom
GAME_HEIGHT = 600  # Height of game area
WINDOW_SIZE = (800, GAME_HEIGHT + INVENTORY_HEIGHT)
GRID_SIZE = 16  # Size of each grid cell in pixels
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)