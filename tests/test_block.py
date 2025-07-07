import pytest
from world import Block
from constants import GREEN, LIGHT_BROWN, DARK_BROWN, BLUE, WHITE


class TestBlock:
    def test_grass_block_properties(self):
        block = Block("grass")
        assert block.type == "grass"
        assert block.walkable is True
        assert block.color == GREEN

    def test_tree_block_properties(self):
        block = Block("tree")
        assert block.type == "tree"
        assert block.walkable is False
        assert block.color == LIGHT_BROWN

    def test_dirt_block_properties(self):
        block = Block("dirt")
        assert block.type == "dirt"
        assert block.walkable is True
        assert block.color == DARK_BROWN

    def test_water_block_properties(self):
        block = Block("water")
        assert block.type == "water"
        assert block.walkable is True
        assert block.color == BLUE

    def test_unknown_block_type(self):
        block = Block("unknown")
        assert block.type == "unknown"
        assert block.walkable is False
        assert block.color == WHITE

    @pytest.mark.parametrize("block_type,expected_walkable", [
        ("grass", True),
        ("dirt", True),
        ("water", True),
        ("tree", False),
        ("stone", False),
        ("lava", False),
    ])
    def test_walkable_rules(self, block_type, expected_walkable):
        block = Block(block_type)
        assert block.walkable is expected_walkable

    @pytest.mark.parametrize("block_type,expected_color", [
        ("grass", GREEN),
        ("tree", LIGHT_BROWN),
        ("dirt", DARK_BROWN),
        ("water", BLUE),
        ("invalid", WHITE),
    ])
    def test_color_mapping(self, block_type, expected_color):
        block = Block(block_type)
        assert block.color == expected_color


class TestBlockMining:
    def test_tree_block_mining_properties(self):
        block = Block("tree")
        assert block.minable is True
        assert block.mining_difficulty == 3.0
        assert block.max_health == 3.0
        assert block.current_health == 3.0

    def test_grass_block_not_minable(self):
        block = Block("grass")
        assert block.minable is False
        assert block.mining_difficulty == 1.0
        assert block.max_health == 1.0
        assert block.current_health == 1.0

    def test_wood_block_properties(self):
        block = Block("wood")
        assert block.type == "wood"
        assert block.color == LIGHT_BROWN
        assert block.minable is False

    def test_reset_health(self):
        block = Block("tree")
        block.current_health = 1.0
        
        block.reset_health()
        
        assert block.current_health == block.max_health

    def test_take_damage_not_minable(self):
        block = Block("grass")
        
        result = block.take_damage(1.0)
        
        assert result is False
        assert block.current_health == block.max_health

    def test_take_damage_minable_not_destroyed(self):
        block = Block("tree")
        
        result = block.take_damage(1.0)
        
        assert result is False
        assert block.current_health == 2.0

    def test_take_damage_minable_destroyed(self):
        block = Block("tree")
        
        result = block.take_damage(3.0)
        
        assert result is True
        assert block.current_health == 0.0

    def test_take_damage_multiple_hits(self):
        block = Block("tree")
        
        result1 = block.take_damage(1.0)
        result2 = block.take_damage(1.0)
        result3 = block.take_damage(1.0)
        
        assert result1 is False
        assert result2 is False
        assert result3 is True
        assert block.current_health == 0.0

    def test_get_mining_result_tree(self):
        block = Block("tree")
        assert block.get_mining_result() == "wood"

    def test_get_mining_result_non_minable(self):
        block = Block("grass")
        assert block.get_mining_result() is None

    def test_get_replacement_block_tree(self):
        block = Block("tree")
        assert block.get_replacement_block() == "dirt"

    def test_get_replacement_block_non_minable(self):
        block = Block("grass")
        assert block.get_replacement_block() == "grass"

    @pytest.mark.parametrize("block_type,expected_minable", [
        ("tree", True),
        ("grass", False),
        ("dirt", False),
        ("water", False),
        ("wood", False),
    ])
    def test_minable_blocks(self, block_type, expected_minable):
        block = Block(block_type)
        assert block.minable is expected_minable