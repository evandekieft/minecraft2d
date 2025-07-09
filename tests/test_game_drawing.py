import pygame
from game_world import GameWorld


class TestGameWorldDrawing:
    """Test drawing methods for GameWorld class"""

    def setup_class(self):
        self.screen = pygame.Surface((800, 600))
        self.game_world = GameWorld(terrain_seed=42)

    def test_draw_game_world(self, pygame_setup):
        """Test that game_world.draw() can run without errors."""
        self.game_world.draw(self.screen)
