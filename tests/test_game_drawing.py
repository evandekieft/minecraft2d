import pygame
from game import Game


class TestGameDrawing:
    """Test drawing methods for Game class"""

    def setup_class(self):
        self.screen = pygame.Surface((800, 600))
        self.game = Game(terrain_seed=42)

    def test_draw_game(self, pygame_setup):
        """Test that game.draw() can run without errors."""
        self.game.draw(self.screen)
