from constants import WINDOW_SIZE, GRID_SIZE, GAME_HEIGHT


class Camera:
    def __init__(self, smoothing=0.05):
        self.x = 0.0
        self.y = 0.0
        self.smoothing = smoothing

    def update(self, target_x, target_y, dt):
        # Calculate target camera position (center the player)
        target_camera_x = target_x
        target_camera_y = target_y

        # Smooth interpolation toward target (dt is available
        # but not needed for frame-rate independent smoothing)
        self.x += (target_camera_x - self.x) * self.smoothing
        self.y += (target_camera_y - self.y) * self.smoothing

    def world_to_screen(self, world_x, world_y):
        # Convert world coordinates to screen coordinates (centered in game area)
        screen_x = (world_x - self.x) * GRID_SIZE + WINDOW_SIZE[0] // 2
        screen_y = (world_y - self.y) * GRID_SIZE + GAME_HEIGHT // 2
        return screen_x, screen_y

    def get_visible_bounds(self):
        # Calculate which world coordinates are visible (only game area)
        half_screen_width = WINDOW_SIZE[0] // (2 * GRID_SIZE)
        half_screen_height = GAME_HEIGHT // (2 * GRID_SIZE)

        # Add extra margin to ensure complete coverage
        margin = 2
        left = int(self.x - half_screen_width - margin)
        right = int(self.x + half_screen_width + margin)
        top = int(self.y - half_screen_height - margin)
        bottom = int(self.y + half_screen_height + margin)

        return left, right, top, bottom
