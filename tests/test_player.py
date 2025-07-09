import pytest
from unittest.mock import Mock
from pygame.locals import K_a, K_d, K_w, K_s
from player import Player
from block_type import BlockType
from inventory import Inventory


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
        # Movement now happens in update(), need to wait for move interval
        player.update(player.move_interval + 0.01, mock_game)

        assert player.world_x == 1
        assert player.world_y == 0
        mock_game.get_block.assert_called_with(1, 0)

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
        # Movement now happens in update(), need to wait for move interval
        player.update(player.move_interval + 0.01, mock_game)

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
        player.update(player.move_interval + 0.01, mock_game)
        assert player.world_x == 1
        assert player.world_y == 0

        # Release east key and move north
        player.handle_keyup(K_d, mock_game)
        player.orientation = "north"
        player.handle_keydown(K_w, mock_game)
        player.update(player.move_interval + 0.01, mock_game)
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

    def test_continuous_movement_timing(self):
        """Test that continuous movement respects timing constraints"""
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block

        player.orientation = "east"
        player.handle_keydown(K_d, mock_game)

        # First update should not move (insufficient time)
        player.update(0.01, mock_game)
        assert player.world_x == 0

        # Add more time to reach the move interval
        player.update(player.move_interval - 0.01, mock_game)
        assert player.world_x == 1

    def test_movement_speed_configuration(self):
        """Test that movement speed is configurable"""
        player = Player()
        assert player.movement_speed == 6.0
        assert player.move_interval == 1 / 6.0

    def test_key_press_tracking(self):
        """Test that key presses are tracked correctly"""
        player = Player()
        mock_game = Mock()

        # Initially no keys pressed
        assert len(player.pressed_keys) == 0

        # Press a key
        player.handle_keydown(K_w, mock_game)
        assert K_w in player.pressed_keys

        # Release the key
        player.handle_keyup(K_w, mock_game)
        assert K_w not in player.pressed_keys

    def test_continuous_movement_while_held(self):
        """Test that movement continues while key is held"""
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.walkable = True
        mock_game.get_block.return_value = mock_block

        player.orientation = "east"
        player.handle_keydown(K_d, mock_game)  # Hold down D key

        # Move multiple times while key is held
        for i in range(3):
            player.update(player.move_interval, mock_game)
            assert player.world_x == i + 1

        # Release key
        player.handle_keyup(K_d, mock_game)

        # Should not move anymore
        old_x = player.world_x
        player.update(player.move_interval, mock_game)
        assert player.world_x == old_x


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
        mock_block.type.minable = True
        mock_game.get_block.return_value = mock_block

        player.start_mining(mock_game)

        assert player.is_mining is True
        assert player.mining_target == (0, -1)  # North of origin

    def test_start_mining_non_minable_block(self):
        player = Player()
        mock_game = Mock()
        mock_block = Mock()
        mock_block.type.minable = False
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
        mock_block.type.minable = True
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
        mock_block.type.minable = True
        mock_block.take_damage.return_value = True  # Block destroyed
        mock_block.type.mining_result = BlockType.WOOD
        mock_block.type.replacement_block = BlockType.DIRT
        mock_game.get_block.return_value = mock_block

        player.process_mining(1.0, mock_game)

        mock_block.take_damage.assert_called_once_with(1.0)
        assert player.inventory.inventory[BlockType.WOOD] == 1
        mock_game.replace_block.assert_called_once_with(5, 10, BlockType.DIRT)
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
        mock_block.type.mining_result = None
        mock_block.type.replacement_block = BlockType.DIRT

        player.complete_mining(mock_game, 5, 10, mock_block)

        assert player.inventory.inventory == {}
        mock_game.replace_block.assert_called_once_with(5, 10, BlockType.DIRT)
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
        mock_block.type.minable = True
        mock_block.take_damage.return_value = False
        mock_game.get_block.return_value = mock_block

        player.update(0.1, mock_game)

        mock_block.take_damage.assert_called_once_with(0.1)
