import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from game import Game
from block import Block
from constants import WINDOW_SIZE, GRID_SIZE, BLACK, WHITE, GAME_HEIGHT, INVENTORY_HEIGHT


class TestGameDrawing:
    """Test drawing methods for Game class"""

    def setup_class(self):
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.game = Game(terrain_seed=42)
    
    def test_draw_game(self):
        """Test that draw() fills the screen with black background"""
        self.game.draw(self.screen)
        
   