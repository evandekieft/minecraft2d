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


class TestInventory:
    def test_inventory_initialization(self):
        player = Player()
        assert player.inventory == {}
        assert player.active_slot == 0

    def test_add_to_inventory_new_item(self):
        player = Player()
        player.add_to_inventory("tree")
        
        assert player.inventory["tree"] == 1

    def test_add_to_inventory_existing_item(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("tree")
        
        assert player.inventory["tree"] == 2

    def test_add_multiple_item_types(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.add_to_inventory("tree")
        
        assert player.inventory["tree"] == 2
        assert player.inventory["grass"] == 1

    def test_get_top_inventory_items_empty(self):
        player = Player()
        top_items = player.get_top_inventory_items(5)
        
        assert top_items == []

    def test_get_top_inventory_items_sorted(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.add_to_inventory("tree")
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        
        top_items = player.get_top_inventory_items(5)
        
        assert top_items == [("tree", 3), ("grass", 2)]

    def test_get_top_inventory_items_limit(self):
        player = Player()
        for i in range(10):
            for j in range(i + 1):
                player.add_to_inventory(f"block_{i}")
        
        top_items = player.get_top_inventory_items(3)
        
        assert len(top_items) == 3
        assert top_items[0][1] >= top_items[1][1] >= top_items[2][1]

    def test_get_active_block_type_empty(self):
        player = Player()
        assert player.get_active_block_type() is None

    def test_get_active_block_type_valid(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.active_slot = 0
        
        assert player.get_active_block_type() == "tree"

    def test_get_active_block_type_out_of_range(self):
        player = Player()
        player.add_to_inventory("tree")
        player.active_slot = 5
        
        assert player.get_active_block_type() is None

    def test_collect_block_tree_in_front(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.type = "tree"
        mock_game.get_block.return_value = mock_block
        
        player.orientation = "north"
        player.collect_block(mock_game)
        
        assert player.inventory["tree"] == 1
        mock_game.get_block.assert_called_once_with(0, -1)

    def test_collect_block_non_tree(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.type = "grass"
        mock_game.get_block.return_value = mock_block
        
        player.collect_block(mock_game)
        
        assert player.inventory == {}

    def test_collect_block_no_block(self):
        player = Player()
        mock_game = Mock()
        mock_game.get_block.return_value = None
        
        player.collect_block(mock_game)
        
        assert player.inventory == {}

    @pytest.mark.parametrize("orientation,expected_dx,expected_dy", [
        ("north", 0, -1),
        ("south", 0, 1),
        ("east", 1, 0),
        ("west", -1, 0),
    ])
    def test_collect_block_directions(self, orientation, expected_dx, expected_dy):
        player = Player()
        player.orientation = orientation
        mock_game = Mock()
        mock_block = Mock()
        mock_block.type = "tree"
        mock_game.get_block.return_value = mock_block
        
        player.collect_block(mock_game)
        
        mock_game.get_block.assert_called_once_with(expected_dx, expected_dy)