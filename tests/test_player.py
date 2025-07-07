import pytest
from unittest.mock import Mock
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
from player import Player
from world import Game, Block


class TestPlayer:
    def test_player_initialization(self):
        player = Player()
        assert player.world_x == 0
        assert player.world_y == 0
        assert player.orientation == "north"

    @pytest.mark.parametrize("key,expected_orientation", [
        (K_LEFT, "west"),
        (K_RIGHT, "east"),
        (K_UP, "north"),
        (K_DOWN, "south"),
    ])
    def test_orientation_updates(self, key, expected_orientation):
        player = Player()
        player.handle_keydown(key)
        assert player.orientation == expected_orientation

    def test_movement_with_walkable_block(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block
        
        player.orientation = "east"
        player.handle_keyup(K_RIGHT, mock_game)
        
        assert player.world_x == 1
        assert player.world_y == 0
        mock_game.get_block.assert_called_once_with(1, 0)

    def test_movement_blocked_by_unwalkable_block(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = False
        mock_game.get_block.return_value = mock_block
        
        player.orientation = "east"
        player.handle_keyup(K_RIGHT, mock_game)
        
        assert player.world_x == 0
        assert player.world_y == 0

    def test_movement_blocked_by_no_block(self):
        player = Player()
        mock_game = Mock()
        mock_game.get_block.return_value = None
        
        player.orientation = "east"
        player.handle_keyup(K_RIGHT, mock_game)
        
        assert player.world_x == 0
        assert player.world_y == 0

    @pytest.mark.parametrize("orientation,expected_dx,expected_dy", [
        ("north", 0, -1),
        ("south", 0, 1),
        ("east", 1, 0),
        ("west", -1, 0),
    ])
    def test_movement_directions(self, orientation, expected_dx, expected_dy):
        player = Player()
        player.orientation = orientation
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block
        
        player.handle_keyup(K_RIGHT, mock_game)
        
        assert player.world_x == expected_dx
        assert player.world_y == expected_dy

    def test_multiple_movements(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block
        
        # Move east
        player.orientation = "east"
        player.handle_keyup(K_RIGHT, mock_game)
        assert player.world_x == 1
        assert player.world_y == 0
        
        # Move north
        player.orientation = "north"
        player.handle_keyup(K_UP, mock_game)
        assert player.world_x == 1
        assert player.world_y == -1

    def test_direct_move_method(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block
        
        player.move(2, 3, mock_game)
        
        assert player.world_x == 2
        assert player.world_y == 3
        mock_game.get_block.assert_called_once_with(2, 3)

    def test_update_method_no_op(self):
        player = Player()
        initial_x = player.world_x
        initial_y = player.world_y
        
        player.update(0.016)
        
        assert player.world_x == initial_x
        assert player.world_y == initial_y