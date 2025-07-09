from crafting import crafting_requirements
from block_type import BlockType


def test_stick_requirements():
    assert crafting_requirements(BlockType.STICK) == {BlockType.WOOD: 3}


def test_torch_requirements():
    assert crafting_requirements(BlockType.TORCH) == {
        BlockType.STICK: 1,
        BlockType.COAL: 1,
    }
