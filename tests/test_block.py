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