import pytest
from world import Block
from constants import GREEN, LIGHT_BROWN, DARK_BROWN, BLUE, WHITE, BRIGHT_BLUE, RED, BLACK, SAND_COLOR, GRAY


class TestBlock:
    def test_grass_block_properties(self):
        block = Block("grass")
        assert block.type == "grass"
        assert block.walkable is True
        assert block.color == GREEN


    def test_dirt_block_properties(self):
        block = Block("dirt")
        assert block.type == "dirt"
        assert block.walkable is True
        assert block.color == DARK_BROWN

    def test_water_block_properties(self):
        block = Block("water")
        assert block.type == "water"
        assert block.walkable is False
        assert block.color == BLUE
        assert block.minable is False

    def test_sand_block_properties(self):
        block = Block("sand")
        assert block.type == "sand"
        assert block.walkable is True
        assert block.color == SAND_COLOR
        assert block.minable is False

    def test_wood_block_properties(self):
        block = Block("wood")
        assert block.type == "wood"
        assert block.walkable is False
        assert block.color == LIGHT_BROWN
        assert block.minable is True

    def test_stone_block_properties(self):
        block = Block("stone")
        assert block.type == "stone"
        assert block.walkable is False
        assert block.color == GRAY
        assert block.minable is True

    def test_coal_block_properties(self):
        block = Block("coal")
        assert block.type == "coal"
        assert block.walkable is False
        assert block.color == BLACK
        assert block.minable is True

    def test_lava_block_properties(self):
        block = Block("lava")
        assert block.type == "lava"
        assert block.walkable is False
        assert block.color == RED
        assert block.minable is False

    def test_diamond_block_properties(self):
        block = Block("diamond")
        assert block.type == "diamond"
        assert block.walkable is False
        assert block.color == BRIGHT_BLUE
        assert block.minable is True

    def test_unknown_block_type(self):
        block = Block("unknown")
        assert block.type == "unknown"
        assert block.walkable is False
        assert block.color == WHITE

    @pytest.mark.parametrize("block_type,expected_walkable", [
        ("grass", True),
        ("dirt", True),
        ("sand", True),
        ("water", False),
        ("wood", False),
        ("stone", False),
        ("coal", False),
        ("lava", False),
        ("diamond", False),
    ])
    def test_walkable_rules(self, block_type, expected_walkable):
        block = Block(block_type)
        assert block.walkable is expected_walkable

    @pytest.mark.parametrize("block_type,expected_color", [
        ("grass", GREEN),
        ("dirt", DARK_BROWN),
        ("sand", SAND_COLOR),
        ("wood", LIGHT_BROWN),
        ("stone", GRAY),
        ("coal", BLACK),
        ("lava", RED),
        ("diamond", BRIGHT_BLUE),
        ("water", BLUE),
        ("invalid", WHITE),
    ])
    def test_color_mapping(self, block_type, expected_color):
        block = Block(block_type)
        assert block.color == expected_color


class TestBlockMining:

    def test_grass_block_not_minable(self):
        block = Block("grass")
        assert block.minable is False
        assert block.mining_difficulty == 1.0
        assert block.max_health == 1.0
        assert block.current_health == 1.0

    def test_wood_block_mining_properties(self):
        block = Block("wood")
        assert block.type == "wood"
        assert block.color == LIGHT_BROWN
        assert block.minable is True
        assert block.mining_difficulty == 3.0
        assert block.max_health == 3.0
        assert block.current_health == 3.0

    def test_stone_block_mining_properties(self):
        block = Block("stone")
        assert block.minable is True
        assert block.mining_difficulty == 5.0
        assert block.max_health == 5.0
        assert block.current_health == 5.0

    def test_coal_block_mining_properties(self):
        block = Block("coal")
        assert block.minable is True
        assert block.mining_difficulty == 4.0
        assert block.max_health == 4.0
        assert block.current_health == 4.0

    def test_diamond_block_mining_properties(self):
        block = Block("diamond")
        assert block.minable is True
        assert block.mining_difficulty == 8.0
        assert block.max_health == 8.0
        assert block.current_health == 8.0

    def test_reset_health(self):
        block = Block("wood")
        block.current_health = 1.0
        
        block.reset_health()
        
        assert block.current_health == block.max_health

    def test_take_damage_not_minable(self):
        block = Block("grass")
        
        result = block.take_damage(1.0)
        
        assert result is False
        assert block.current_health == block.max_health

    def test_take_damage_minable_not_destroyed(self):
        block = Block("wood")
        
        result = block.take_damage(1.0)
        
        assert result is False
        assert block.current_health == 2.0

    def test_take_damage_minable_destroyed(self):
        block = Block("wood")
        
        result = block.take_damage(3.0)
        
        assert result is True
        assert block.current_health == 0.0

    def test_take_damage_multiple_hits(self):
        block = Block("wood")
        
        result1 = block.take_damage(1.0)
        result2 = block.take_damage(1.0)
        result3 = block.take_damage(1.0)
        
        assert result1 is False
        assert result2 is False
        assert result3 is True
        assert block.current_health == 0.0


    def test_get_mining_result_wood(self):
        block = Block("wood")
        assert block.get_mining_result() == "wood"

    def test_get_mining_result_stone(self):
        block = Block("stone")
        assert block.get_mining_result() == "stone"

    def test_get_mining_result_coal(self):
        block = Block("coal")
        assert block.get_mining_result() == "coal"

    def test_get_mining_result_diamond(self):
        block = Block("diamond")
        assert block.get_mining_result() == "diamond"

    def test_get_mining_result_non_minable(self):
        block = Block("grass")
        assert block.get_mining_result() is None


    def test_get_replacement_block_wood(self):
        block = Block("wood")
        assert block.get_replacement_block() == "grass"

    def test_get_replacement_block_stone(self):
        block = Block("stone")
        assert block.get_replacement_block() == "dirt"

    def test_get_replacement_block_coal(self):
        block = Block("coal")
        assert block.get_replacement_block() == "dirt"

    def test_get_replacement_block_diamond(self):
        block = Block("diamond")
        assert block.get_replacement_block() == "dirt"

    def test_get_replacement_block_non_minable(self):
        block = Block("grass")
        assert block.get_replacement_block() == "grass"

    @pytest.mark.parametrize("block_type,expected_minable", [
        ("wood", True),
        ("stone", True),
        ("coal", True),
        ("diamond", True),
        ("grass", False),
        ("dirt", False),
        ("sand", False),
        ("water", False),
        ("lava", False),
    ])
    def test_minable_blocks(self, block_type, expected_minable):
        block = Block(block_type)
        assert block.minable is expected_minable