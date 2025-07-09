from enum import Enum
from typing import Optional
import pygame
from sprites import sprite_manager
from constants import (
    GRASS_GREEN,
    LIGHT_BROWN,
    DARK_BROWN,
    WATER_BLUE,
    WHITE,
    BRIGHT_BLUE,
    RED,
    BLACK,
    SAND_COLOR,
    GRAY,
)


class BlockType(Enum):
    GRASS = "grass"
    DIRT = "dirt"
    SAND = "sand"
    WOOD = "wood"
    STONE = "stone"
    COAL = "coal"
    LAVA = "lava"
    DIAMOND = "diamond"
    WATER = "water"
    STICK = "stick"
    TORCH = "torch"

    @property
    def mining_result(self) -> Optional["BlockType"]:
        """The item(s) that should be added to inventory when this block is mined"""
        return {
            BlockType.WOOD: BlockType.WOOD,
            BlockType.STONE: BlockType.STONE,
            BlockType.COAL: BlockType.COAL,
            BlockType.DIAMOND: BlockType.DIAMOND,
        }.get(self, None)

    @property
    def replacement_block(self) -> Optional["BlockType"]:
        """Get the block type that should replace this block when mined"""
        replacements = {
            BlockType.WOOD: BlockType.DIRT,
            BlockType.STONE: BlockType.DIRT,
            BlockType.COAL: BlockType.DIRT,
            BlockType.DIAMOND: BlockType.DIRT,
        }
        return replacements.get(self, None)

    @property
    def walkable(self) -> bool:
        walkable_blocks = {BlockType.GRASS, BlockType.DIRT, BlockType.SAND}
        return self in walkable_blocks

    @property
    def color(self) -> pygame.Color:
        colors = {
            BlockType.GRASS: GRASS_GREEN,
            BlockType.DIRT: DARK_BROWN,
            BlockType.SAND: SAND_COLOR,
            BlockType.WOOD: LIGHT_BROWN,
            BlockType.STONE: GRAY,
            BlockType.COAL: BLACK,
            BlockType.LAVA: RED,
            BlockType.DIAMOND: BRIGHT_BLUE,
            BlockType.WATER: WATER_BLUE,
        }
        return colors.get(self, WHITE)

    @property
    def minable(self) -> bool:
        minable_blocks = {
            BlockType.WOOD,
            BlockType.STONE,
            BlockType.DIAMOND,
            BlockType.COAL,
        }
        return self in minable_blocks

    @property
    def mining_difficulty(self) -> float:
        # Mining difficulty in health points (higher = takes longer)
        difficulties = {
            BlockType.WOOD: 1.5,  # 1.5 seconds with bare hands
            BlockType.STONE: 5.0,  # 5 seconds with bare hands
            BlockType.COAL: 4.0,  # 4 seconds with bare hands
            BlockType.DIAMOND: 8.0,  # 8 seconds with bare hands (very hard)
        }
        return difficulties.get(self, 1.0)

    @property
    def sprite(self) -> Optional[pygame.Surface]:
        sprites = {
            BlockType.WOOD: "assets/sprites/blocks/oak_log.png",
            BlockType.SAND: "assets/sprites/blocks/sand.png",
            BlockType.STONE: "assets/sprites/blocks/stone.png",
            BlockType.COAL: "assets/sprites/blocks/coal_block.png",
        }
        sprite = sprites.get(self)
        return sprite_manager.load_sprite(sprite) if sprite else None
