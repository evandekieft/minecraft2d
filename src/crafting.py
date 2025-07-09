from block_type import BlockType
from typing import Dict, Tuple, Optional
from collections import Counter

CraftingRules = Dict[
    BlockType,
    Tuple[
        Tuple[Optional[BlockType], Optional[BlockType], Optional[BlockType]],
        Tuple[Optional[BlockType], Optional[BlockType], Optional[BlockType]],
        Tuple[Optional[BlockType], Optional[BlockType], Optional[BlockType]],
    ],
]

CRAFTING_RULES: CraftingRules = {
    BlockType.STICK: (
        (None, BlockType.WOOD, None),
        (None, BlockType.WOOD, None),
        (None, BlockType.WOOD, None),
    ),
    BlockType.TORCH: (
        (None, None, None),
        (None, BlockType.COAL, None),
        (None, BlockType.STICK, None),
    ),
}


def crafting_requirements(block_type: BlockType) -> Optional[Dict[BlockType, int]]:
    recipe = CRAFTING_RULES.get(block_type)
    if recipe:
        flattened_blocks = [
            block for row in recipe for block in row if block is not None
        ]
        return Counter(flattened_blocks)
    return None
