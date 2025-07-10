from unittest.mock import Mock
from block import Block
from block_type import BlockType
from player import Player
from inventory import Inventory


class TestBlock:

    def test_place_block_success(self):
        player = Player()
        player.world_x = 5
        player.world_y = 10
        player.orientation = "north"
        player.inventory = Inventory({BlockType.DIRT: 2})

        mock_game = Mock()
        mock_block = Mock()
        mock_block.type.walkable = True
        mock_game.get_block.return_value = mock_block

        # Patch get_top_inventory_items to return the correct block type in slot 0
        player.get_top_inventory_items = lambda count=5: [(BlockType.DIRT, 2)]

        player.place_block(mock_game)

        # Target position should be (5, 9) for north
        mock_game.replace_block.assert_called_once_with(5, 9, BlockType.DIRT)
        assert player.inventory.inventory[BlockType.DIRT] == 1


class TestBlockMining:

    def test_grass_block_not_minable(self):
        block = Block(BlockType.GRASS)
        assert block.type.minable is False
        assert block.type.mining_difficulty == 1.0
        assert block.max_health == 1.0
        assert block.current_health == 1.0

    def test_reset_health(self):
        block = Block(BlockType.WOOD)
        block.current_health = 1.0

        block.reset_health()

        assert block.current_health == block.max_health

    def test_take_damage_not_minable(self):
        block = Block(BlockType.GRASS)

        result = block.take_damage(1.0)

        assert result is False
        assert block.current_health == block.max_health

    def test_take_damage_minable_not_destroyed(self):
        block = Block(BlockType.WOOD)

        result = block.take_damage(1.0)

        assert result is False
        assert block.current_health == 0.5

    def test_take_damage_minable_destroyed(self):
        block = Block(BlockType.WOOD)

        result = block.take_damage(1.5)

        assert result is True
        assert block.current_health == 0.0

    def test_take_damage_multiple_hits(self):
        block = Block(BlockType.WOOD)

        result1 = block.take_damage(0.5)
        result2 = block.take_damage(0.5)
        result3 = block.take_damage(0.5)

        assert result1 is False
        assert result2 is False
        assert result3 is True
        assert block.current_health == 0.0
