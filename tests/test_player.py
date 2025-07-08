import pytest
from unittest.mock import Mock
from pygame.locals import K_a, K_d, K_w, K_s, K_UP
from player import Player
from game import Game
from block import Block


class TestPlayer:
    def test_player_initialization(self):
        player = Player()
        assert player.world_x == 0
        assert player.world_y == 0
        assert player.orientation == "north"

    @pytest.mark.parametrize(
        "key,expected_orientation",
        [
            (K_a, "west"),
            (K_d, "east"),
            (K_w, "north"),
            (K_s, "south"),
        ],
    )
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
        player.handle_keydown(K_d, mock_game)

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
        player.handle_keydown(K_d, mock_game)

        assert player.world_x == 0
        assert player.world_y == 0

    def test_movement_blocked_by_no_block(self):
        player = Player()
        mock_game = Mock()
        mock_game.get_block.return_value = None

        player.orientation = "east"
        player.handle_keydown(K_d, mock_game)

        assert player.world_x == 0
        assert player.world_y == 0

    @pytest.mark.parametrize(
        "key,orientation,expected_dx,expected_dy",
        [
            (K_w, "north", 0, -1),
            (K_s, "south", 0, 1),
            (K_d, "east", 1, 0),
            (K_a, "west", -1, 0),
        ],
    )
    def test_movement_directions(self, key, orientation, expected_dx, expected_dy):
        player = Player()
        player.orientation = orientation
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block

        player.handle_keydown(key, mock_game)

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
        player.handle_keydown(K_d, mock_game)
        assert player.world_x == 1
        assert player.world_y == 0

        # Move north
        player.orientation = "north"
        player.handle_keydown(K_w, mock_game)
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


class TestMining:
    def test_mining_initialization(self):
        player = Player()
        assert player.is_mining is False
        assert player.mining_target is None
        assert player.mining_damage_rate == 1.0

    def test_get_target_position(self):
        player = Player()
        player.world_x = 5
        player.world_y = 10

        player.orientation = "north"
        assert player.get_target_position() == (5, 9)

        player.orientation = "south"
        assert player.get_target_position() == (5, 11)

        player.orientation = "east"
        assert player.get_target_position() == (6, 10)

        player.orientation = "west"
        assert player.get_target_position() == (4, 10)

    def test_start_mining_minable_block(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.minable = True
        mock_game.get_block.return_value = mock_block

        player.start_mining(mock_game)

        assert player.is_mining is True
        assert player.mining_target == (0, -1)  # North of origin

    def test_start_mining_non_minable_block(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.minable = False
        mock_game.get_block.return_value = mock_block

        player.start_mining(mock_game)

        assert player.is_mining is False
        assert player.mining_target is None

    def test_start_mining_no_block(self):
        player = Player()
        mock_game = Mock()
        mock_game.get_block.return_value = None

        player.start_mining(mock_game)

        assert player.is_mining is False
        assert player.mining_target is None

    def test_stop_mining_resets_block_health(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_block = Mock()
        mock_game.get_block.return_value = mock_block

        player.stop_mining(mock_game)

        assert player.is_mining is False
        assert player.mining_target is None
        mock_block.reset_health.assert_called_once()

    def test_stop_mining_no_target(self):
        player = Player()
        player.is_mining = False
        player.mining_target = None

        mock_game = Mock()

        player.stop_mining(mock_game)

        assert player.is_mining is False
        assert player.mining_target is None

    def test_process_mining_damages_block(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_block = Mock()
        mock_block.minable = True
        mock_block.take_damage.return_value = False  # Block not destroyed
        mock_game.get_block.return_value = mock_block

        player.process_mining(0.5, mock_game)  # 0.5 seconds

        mock_block.take_damage.assert_called_once_with(0.5)  # 1.0 * 0.5

    def test_process_mining_destroys_block(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_block = Mock()
        mock_block.minable = True
        mock_block.take_damage.return_value = True  # Block destroyed
        mock_block.get_mining_result.return_value = "wood"
        mock_block.get_replacement_block.return_value = "dirt"
        mock_game.get_block.return_value = mock_block

        player.process_mining(1.0, mock_game)

        mock_block.take_damage.assert_called_once_with(1.0)
        assert player.inventory["wood"] == 1
        mock_game.replace_block.assert_called_once_with(5, 10, "dirt")
        assert player.is_mining is False
        assert player.mining_target is None

    def test_process_mining_no_target(self):
        player = Player()
        player.is_mining = True
        player.mining_target = None

        mock_game = Mock()

        player.process_mining(1.0, mock_game)

        mock_game.get_block.assert_not_called()

    def test_process_mining_invalid_block(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_game.get_block.return_value = None

        player.process_mining(1.0, mock_game)

        assert player.is_mining is False
        assert player.mining_target is None

    def test_complete_mining_no_result(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_block = Mock()
        mock_block.get_mining_result.return_value = None
        mock_block.get_replacement_block.return_value = "dirt"

        player.complete_mining(mock_game, 5, 10, mock_block)

        assert player.inventory == {}
        mock_game.replace_block.assert_called_once_with(5, 10, "dirt")
        assert player.is_mining is False

    def test_move_stops_mining(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_walkable_block = Mock()
        mock_walkable_block.walkable = True
        mock_mining_block = Mock()
        mock_game.get_block.side_effect = [mock_walkable_block, mock_mining_block]

        player.move(1, 0, mock_game)

        assert player.world_x == 1
        assert player.world_y == 0
        assert player.is_mining is False
        assert player.mining_target is None
        mock_mining_block.reset_health.assert_called_once()

    def test_update_processes_mining(self):
        player = Player()
        player.is_mining = True
        player.mining_target = (5, 10)

        mock_game = Mock()
        mock_block = Mock()
        mock_block.minable = True
        mock_block.take_damage.return_value = False
        mock_game.get_block.return_value = mock_block

        player.update(0.1, mock_game)

        mock_block.take_damage.assert_called_once_with(0.1)
