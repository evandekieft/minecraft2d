import pytest
from camera import Camera
from constants import WINDOW_SIZE, GRID_SIZE, GAME_HEIGHT


class TestCamera:
    def test_camera_initialization(self):
        camera = Camera()
        assert camera.x == 0.0
        assert camera.y == 0.0
        assert camera.smoothing == 0.05

    def test_camera_custom_smoothing(self):
        camera = Camera(smoothing=0.1)
        assert camera.smoothing == 0.1

    def test_camera_update_movement(self):
        camera = Camera(smoothing=1.0)  # Instant movement for testing
        
        camera.update(10, 20, 0.016)
        
        assert camera.x == 10.0
        assert camera.y == 20.0

    def test_camera_smooth_movement(self):
        camera = Camera(smoothing=0.5)
        
        # Should move halfway to target
        camera.update(10, 20, 0.016)
        
        assert camera.x == 5.0
        assert camera.y == 10.0

    def test_world_to_screen_center(self):
        camera = Camera()
        camera.x = 0.0
        camera.y = 0.0
        
        # Camera at origin, world origin should be screen center
        screen_x, screen_y = camera.world_to_screen(0, 0)
        
        expected_x = WINDOW_SIZE[0] // 2
        expected_y = GAME_HEIGHT // 2
        
        assert screen_x == expected_x
        assert screen_y == expected_y

    def test_world_to_screen_offset(self):
        camera = Camera()
        camera.x = 5.0
        camera.y = 10.0
        
        # Test coordinate transformation with camera offset
        screen_x, screen_y = camera.world_to_screen(5, 10)
        
        expected_x = WINDOW_SIZE[0] // 2
        expected_y = GAME_HEIGHT // 2
        
        assert screen_x == expected_x
        assert screen_y == expected_y

    def test_world_to_screen_relative_positions(self):
        camera = Camera()
        camera.x = 0.0
        camera.y = 0.0
        
        # Test relative positioning
        center_x, center_y = camera.world_to_screen(0, 0)
        right_x, right_y = camera.world_to_screen(1, 0)
        down_x, down_y = camera.world_to_screen(0, 1)
        
        assert right_x == center_x + GRID_SIZE
        assert right_y == center_y
        assert down_x == center_x
        assert down_y == center_y + GRID_SIZE

    def test_get_visible_bounds_centered(self):
        camera = Camera()
        camera.x = 0.0
        camera.y = 0.0
        
        left, right, top, bottom = camera.get_visible_bounds()
        
        # Should be symmetric around origin
        half_width = WINDOW_SIZE[0] // (2 * GRID_SIZE)
        half_height = GAME_HEIGHT // (2 * GRID_SIZE)
        
        assert left == -half_width - 2
        assert right == half_width + 2
        assert top == -half_height - 2
        assert bottom == half_height + 2

    def test_get_visible_bounds_offset(self):
        camera = Camera()
        camera.x = 10.0
        camera.y = 20.0
        
        left, right, top, bottom = camera.get_visible_bounds()
        
        # Should be offset by camera position
        half_width = WINDOW_SIZE[0] // (2 * GRID_SIZE)
        half_height = GAME_HEIGHT // (2 * GRID_SIZE)
        
        assert left == 10 - half_width - 2
        assert right == 10 + half_width + 2
        assert top == 20 - half_height - 2
        assert bottom == 20 + half_height + 2

    def test_visible_bounds_include_buffer(self):
        camera = Camera()
        camera.x = 0.0
        camera.y = 0.0
        
        left, right, top, bottom = camera.get_visible_bounds()
        
        # Bounds should include 2-unit buffer on each side
        half_width = WINDOW_SIZE[0] // (2 * GRID_SIZE)
        half_height = GAME_HEIGHT // (2 * GRID_SIZE)
        
        visible_width = right - left + 1
        visible_height = bottom - top + 1
        
        assert visible_width == 2 * half_width + 5  # +5 for buffer on both sides plus center
        assert visible_height == 2 * half_height + 5

    @pytest.mark.parametrize("target_x,target_y,smoothing", [
        (0, 0, 0.1),
        (100, 200, 0.5),
        (-50, -100, 0.25),
        (10.5, 20.5, 0.75),
    ])
    def test_camera_convergence(self, target_x, target_y, smoothing):
        camera = Camera(smoothing=smoothing)
        
        # Update many times to converge
        for _ in range(100):
            camera.update(target_x, target_y, 0.016)
        
        # Should be very close to target
        assert abs(camera.x - target_x) < 0.01
        assert abs(camera.y - target_y) < 0.01

    def test_coordinate_transformation_consistency(self):
        camera = Camera()
        camera.x = 5.0
        camera.y = 10.0
        
        # Test that world_to_screen and visible bounds are consistent
        left, right, top, bottom = camera.get_visible_bounds()
        
        # Transform bounds back to screen coordinates
        left_screen_x, left_screen_y = camera.world_to_screen(left, top)
        right_screen_x, right_screen_y = camera.world_to_screen(right, bottom)
        
        # Should cover the screen area (with buffer)
        assert left_screen_x < 0
        assert right_screen_x > WINDOW_SIZE[0]
        assert left_screen_y < 0
        assert right_screen_y > GAME_HEIGHT