"""
Tests for window resize functionality
"""

import pygame
from src.menu import MenuSystem
from src.game_world import GameWorld
from src.camera import Camera
from src.menu import MenuSystem
from src.lighting import lighting_system
from block_type import BlockType
from unittest.mock import Mock


class TestWindowResize:
    """Test window resize functionality"""

    def test_camera_resize_updates_dimensions(self, pygame_setup):
        """Test that camera dimensions update correctly on resize"""
        camera = Camera()

        # Initial dimensions should match constants
        assert camera.window_width == 1600
        assert camera.window_height == 1320

        # Test resize
        camera.handle_window_resize(1200, 800)
        assert camera.window_width == 1200
        assert camera.window_height == 800
        assert camera.game_height == 800 - 120  # Subtract inventory height

    def test_camera_visible_bounds_change_with_resize(self, pygame_setup):
        """Test that visible bounds change appropriately with window resize"""
        camera = Camera()

        # Get initial bounds
        initial_bounds = camera.get_visible_bounds()

        # Resize to larger window
        camera.handle_window_resize(2000, 1500)
        larger_bounds = camera.get_visible_bounds()

        # Larger window should see more area
        assert (
            larger_bounds[1] - larger_bounds[0] > initial_bounds[1] - initial_bounds[0]
        )  # width
        assert (
            larger_bounds[3] - larger_bounds[2] > initial_bounds[3] - initial_bounds[2]
        )  # height

    def test_camera_world_to_screen_updates_with_resize(self, pygame_setup):
        """Test that world-to-screen conversion updates with resize"""
        camera = Camera()

        # Test conversion at origin
        screen_x, screen_y = camera.world_to_screen(0, 0)
        initial_center_x, initial_center_y = screen_x, screen_y

        # Resize window
        camera.handle_window_resize(1200, 800)

        # Check that screen coordinates update
        new_screen_x, new_screen_y = camera.world_to_screen(0, 0)
        assert new_screen_x == 1200 // 2  # New center X
        assert new_screen_y == (800 - 120) // 2  # New center Y (minus inventory)

    def test_game_resize_generates_new_chunks_if_needed(self, pygame_setup):
        """Test that game world resize generates new chunks for expanded view"""
        game_world = GameWorld(terrain_seed=42)

        # Count initial chunks
        initial_chunk_count = len(game_world.chunks)

        # Resize to much larger window (should need more chunks)
        game_world.handle_window_resize(3000, 2000)

        # Should have generated additional chunks
        assert len(game_world.chunks) >= initial_chunk_count

    def test_game_resize_preserves_existing_chunks(self, pygame_setup):
        """Test that existing chunks are preserved during resize"""
        game_world = GameWorld(terrain_seed=42)

        # Generate some chunks and get a specific block
        test_block = game_world.get_block(10, 10)
        test_block_type = test_block.type

        # Resize window
        game_world.handle_window_resize(1200, 800)

        # Check that the same block still exists and is unchanged
        preserved_block = game_world.get_block(10, 10)
        assert preserved_block.type == test_block_type

    def test_menu_system_resize_updates_dimensions(self, pygame_setup):
        """Test that menu system updates dimensions on resize"""
        menu = MenuSystem(Mock())

        # Initial dimensions
        assert menu.window_width == 1600
        assert menu.window_height == 1320

        # Test resize
        menu.handle_window_resize(1200, 800)

        assert menu.window_width == 1200
        assert menu.window_height == 800


class TestResizeEdgeCases:
    """Test edge cases for resize functionality"""

    def test_camera_minimum_size_handling(self, pygame_setup):
        """Test camera behavior with very small window sizes"""
        camera = Camera()

        # Test with very small dimensions
        camera.handle_window_resize(100, 100)

        # Should still work without crashing
        bounds = camera.get_visible_bounds()
        assert len(bounds) == 4

        # World-to-screen should still work
        screen_x, screen_y = camera.world_to_screen(0, 0)
        assert isinstance(screen_x, (int, float))
        assert isinstance(screen_y, (int, float))

    def test_camera_large_size_handling(self, pygame_setup):
        """Test camera behavior with very large window sizes"""
        camera = Camera()

        # Test with very large dimensions
        camera.handle_window_resize(5000, 3000)

        # Should still work without crashing
        bounds = camera.get_visible_bounds()
        assert len(bounds) == 4

        # Bounds should be much larger
        left, right, top, bottom = bounds
        assert right - left > 100  # Should see a lot of blocks horizontally
        assert bottom - top > 50  # Should see a lot of blocks vertically

    def test_game_resize_with_negative_coordinates(self, pygame_setup):
        """Test that resize works correctly with negative world coordinates"""
        game_world = GameWorld(terrain_seed=42)

        # Move to negative coordinates
        game_world.player.world_x = -50
        game_world.player.world_y = -50
        game_world.camera.x = -50
        game_world.camera.y = -50

        # Test resize
        game_world.handle_window_resize(1200, 800)

        # Should still work and generate chunks in negative space
        block = game_world.get_block(-55, -55)
        assert block is not None

        valid_types = [
            BlockType.WATER,
            BlockType.SAND,
            BlockType.GRASS,
            BlockType.DIRT,
            BlockType.STONE,
            BlockType.WOOD,
            BlockType.COAL,
            BlockType.LAVA,
            BlockType.DIAMOND,
        ]
        assert block.type in valid_types

    def test_multiple_consecutive_resizes(self, pygame_setup):
        """Test multiple consecutive resizes"""
        game_world = GameWorld(terrain_seed=42)

        # Perform multiple resizes
        sizes = [(800, 600), (1200, 800), (1600, 1200), (1000, 700), (1400, 900)]

        for width, height in sizes:
            game_world.handle_window_resize(width, height)

            # Camera should be updated correctly
            assert game_world.camera.window_width == width
            assert game_world.camera.window_height == height

            # Should be able to get blocks without crashing
            block = game_world.get_block(0, 0)
            assert block is not None
