import pytest
from unittest.mock import Mock
from block import Block
from block_type import BlockType
from player import Player
from inventory import Inventory
from constants import (
    GREEN,
    LIGHT_BROWN,
    DARK_BROWN,
    BLUE,
    BRIGHT_BLUE,
    RED,
    BLACK,
    SAND_COLOR,
    GRAY,
)


class TestBlock:
    def test_grass_block_properties(self):
        block = Block(BlockType.GRASS)
        assert block.type == BlockType.GRASS
        assert block.type.walkable is True
        assert block.type.color == GREEN

    def test_dirt_block_properties(self):
        block = Block(BlockType.DIRT)
        assert block.type == BlockType.DIRT
        assert block.type.walkable is True
        assert block.type.color == DARK_BROWN

    def test_water_block_properties(self):
        block = Block(BlockType.WATER)
        assert block.type == BlockType.WATER
        assert block.type.walkable is False
        assert block.type.color == BLUE
        assert block.type.minable is False

    def test_sand_block_properties(self):
        block = Block(BlockType.SAND)
        assert block.type == BlockType.SAND
        assert block.type.walkable is True
        assert block.type.color == SAND_COLOR
        assert block.type.minable is False

    def test_wood_block_properties(self):
        block = Block(BlockType.WOOD)
        assert block.type == BlockType.WOOD
        assert block.type.walkable is False
        assert block.type.color == LIGHT_BROWN
        assert block.type.minable is True

    def test_stone_block_properties(self):
        block = Block(BlockType.STONE)
        assert block.type == BlockType.STONE
        assert block.type.walkable is False
        assert block.type.color == GRAY
        assert block.type.minable is True

    def test_coal_block_properties(self):
        block = Block(BlockType.COAL)
        assert block.type == BlockType.COAL
        assert block.type.walkable is False
        assert block.type.color == BLACK
        assert block.type.minable is True

    def test_lava_block_properties(self):
        block = Block(BlockType.LAVA)
        assert block.type == BlockType.LAVA
        assert block.type.walkable is False
        assert block.type.color == RED
        assert block.type.minable is False

    def test_diamond_block_properties(self):
        block = Block(BlockType.DIAMOND)
        assert block.type == BlockType.DIAMOND
        assert block.type.walkable is False
        assert block.type.color == BRIGHT_BLUE
        assert block.type.minable is True

    def test_unknown_block_type(self):
        # This test should handle invalid enum values
        with pytest.raises(ValueError):
            BlockType("unknown")

    @pytest.mark.parametrize(
        "block_type,expected_walkable",
        [
            (BlockType.GRASS, True),
            (BlockType.DIRT, True),
            (BlockType.SAND, True),
            (BlockType.WATER, False),
            (BlockType.WOOD, False),
            (BlockType.STONE, False),
            (BlockType.COAL, False),
            (BlockType.LAVA, False),
            (BlockType.DIAMOND, False),
        ],
    )
    def test_walkable_rules(self, block_type, expected_walkable):
        block = Block(block_type)
        assert block.type.walkable is expected_walkable

    @pytest.mark.parametrize(
        "block_type,expected_color",
        [
            (BlockType.GRASS, GREEN),
            (BlockType.DIRT, DARK_BROWN),
            (BlockType.SAND, SAND_COLOR),
            (BlockType.WOOD, LIGHT_BROWN),
            (BlockType.STONE, GRAY),
            (BlockType.COAL, BLACK),
            (BlockType.LAVA, RED),
            (BlockType.DIAMOND, BRIGHT_BLUE),
            (BlockType.WATER, BLUE),
        ],
    )
    def test_color_mapping(self, block_type, expected_color):
        block = Block(block_type)
        assert block.type.color == expected_color

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

    def test_wood_block_mining_properties(self):
        block = Block(BlockType.WOOD)
        assert block.type == BlockType.WOOD
        assert block.type.color == LIGHT_BROWN
        assert block.type.minable is True
        assert block.type.mining_difficulty == 1.5
        assert block.max_health == 1.5
        assert block.current_health == 1.5

    def test_stone_block_mining_properties(self):
        block = Block(BlockType.STONE)
        assert block.type.minable is True
        assert block.type.mining_difficulty == 5.0
        assert block.max_health == 5.0
        assert block.current_health == 5.0

    def test_coal_block_mining_properties(self):
        block = Block(BlockType.COAL)
        assert block.type.minable is True
        assert block.type.mining_difficulty == 4.0
        assert block.max_health == 4.0
        assert block.current_health == 4.0

    def test_diamond_block_mining_properties(self):
        block = Block(BlockType.DIAMOND)
        assert block.type.minable is True
        assert block.type.mining_difficulty == 8.0
        assert block.max_health == 8.0
        assert block.current_health == 8.0

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

    def test_get_mining_result_wood(self):
        block = Block(BlockType.WOOD)
        assert block.type.mining_result == BlockType.WOOD

    def test_get_mining_result_stone(self):
        block = Block(BlockType.STONE)
        assert block.type.mining_result == BlockType.STONE

    def test_get_mining_result_coal(self):
        block = Block(BlockType.COAL)
        assert block.type.mining_result == BlockType.COAL

    def test_get_mining_result_diamond(self):
        block = Block(BlockType.DIAMOND)
        assert block.type.mining_result == BlockType.DIAMOND

    def test_get_mining_result_non_minable(self):
        block = Block(BlockType.GRASS)
        assert block.type.mining_result is None

    def test_get_replacement_block_wood(self):
        block = Block(BlockType.WOOD)
        assert block.type.replacement_block == BlockType.DIRT

    def test_get_replacement_block_stone(self):
        block = Block(BlockType.STONE)
        assert block.type.replacement_block == BlockType.DIRT

    def test_get_replacement_block_coal(self):
        block = Block(BlockType.COAL)
        assert block.type.replacement_block == BlockType.DIRT

    def test_get_replacement_block_diamond(self):
        block = Block(BlockType.DIAMOND)
        assert block.type.replacement_block == BlockType.DIRT

    def test_get_replacement_block_non_minable(self):
        block = Block(BlockType.GRASS)
        assert block.type.replacement_block is None

    @pytest.mark.parametrize(
        "block_type,expected_minable",
        [
            (BlockType.WOOD, True),
            (BlockType.STONE, True),
            (BlockType.COAL, True),
            (BlockType.DIAMOND, True),
            (BlockType.GRASS, False),
            (BlockType.DIRT, False),
            (BlockType.SAND, False),
            (BlockType.WATER, False),
            (BlockType.LAVA, False),
        ],
    )
    def test_minable_blocks(self, block_type, expected_minable):
        block = Block(block_type)
        assert block.type.minable is expected_minable
