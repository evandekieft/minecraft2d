import pygame
from typing import Optional
from constants import (
    GREEN,
    LIGHT_BROWN,
    DARK_BROWN,
    BLUE,
    WHITE,
    BRIGHT_BLUE,
    RED,
    BLACK,
    SAND_COLOR,
    GRAY,
    GRID_SIZE,
)
from block_type import BlockType


class Block:
    def __init__(self, block_type: BlockType):
        self.type: BlockType = block_type
        self.walkable = self._get_walkable(block_type)
        self.color = self._get_color(block_type)
        self.minable = self._get_minable(block_type)
        self.mining_difficulty = self._get_mining_difficulty(block_type)
        self.max_health = self.mining_difficulty
        self.current_health = self.max_health

    def _get_walkable(self, block_type: BlockType) -> bool:
        walkable_blocks = {BlockType.GRASS, BlockType.DIRT, BlockType.SAND}
        return block_type in walkable_blocks

    def _get_color(self, block_type: BlockType):
        colors = {
            BlockType.GRASS: GREEN,
            BlockType.DIRT: DARK_BROWN,
            BlockType.SAND: SAND_COLOR,
            BlockType.WOOD: LIGHT_BROWN,
            BlockType.STONE: GRAY,
            BlockType.COAL: BLACK,
            BlockType.LAVA: RED,
            BlockType.DIAMOND: BRIGHT_BLUE,
            BlockType.WATER: BLUE,
        }
        return colors.get(block_type, WHITE)

    def _get_minable(self, block_type: BlockType) -> bool:
        minable_blocks = {
            BlockType.WOOD,
            BlockType.STONE,
            BlockType.DIAMOND,
            BlockType.COAL,
        }
        return block_type in minable_blocks

    def _get_mining_difficulty(self, block_type: BlockType) -> float:
        # Mining difficulty in health points (higher = takes longer)
        difficulties = {
            BlockType.WOOD: 1.5,  # 1.5 seconds with bare hands
            BlockType.STONE: 5.0,  # 5 seconds with bare hands
            BlockType.COAL: 4.0,  # 4 seconds with bare hands
            BlockType.DIAMOND: 8.0,  # 8 seconds with bare hands (very hard)
        }
        return difficulties.get(block_type, 1.0)

    def reset_health(self):
        """Reset block health to maximum (when mining is interrupted)"""
        self.current_health = self.max_health

    def take_damage(self, damage):
        """Apply mining damage to the block. Returns True if block is destroyed."""
        if not self.minable:
            return False

        self.current_health -= damage
        return self.current_health <= 0

    def get_mining_result(self) -> Optional[str]:
        """Get the item(s) that should be added to inventory when this block is mined"""
        mining_results = {
            BlockType.WOOD: "wood",
            BlockType.STONE: "stone",
            BlockType.COAL: "coal",
            BlockType.DIAMOND: "diamond",
        }
        return mining_results.get(self.type, None)

    def get_replacement_block(self) -> BlockType:
        """Get the block type that should replace this block when mined"""
        replacements = {
            BlockType.WOOD: BlockType.GRASS,  # Wood becomes grass when mined
            BlockType.STONE: BlockType.DIRT,  # Stone becomes dirt when mined
            BlockType.COAL: BlockType.DIRT,  # Coal becomes dirt when mined
            BlockType.DIAMOND: BlockType.DIRT,  # Diamond becomes dirt when mined
        }
        return replacements.get(self.type, self.type)

    def draw(
        self, screen, screen_x, screen_y, is_being_mined=False, mining_progress=0.0
    ):
        """Draw the block at the given screen coordinates"""
        rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)

        # Draw the main block
        pygame.draw.rect(screen, self.color, rect)

        # Draw mining progress bar if being mined
        if is_being_mined and mining_progress > 0:
            # Calculate progress bar dimensions
            bar_height = max(2, GRID_SIZE // 10)  # At least 2 pixels high
            bar_width = int(GRID_SIZE * 0.8)  # 80% of block width
            bar_x = screen_x + (GRID_SIZE - bar_width) // 2
            bar_y = screen_y + GRID_SIZE - bar_height - 2  # 2px from bottom

            # Draw background of progress bar (empty part)
            pygame.draw.rect(
                screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height)
            )

            # Draw filled part of progress bar
            fill_width = int(bar_width * mining_progress)
            if fill_width > 0:
                # Color changes from red to green as progress increases
                red = int(255 * (1 - mining_progress))
                green = int(255 * mining_progress)
                pygame.draw.rect(
                    screen, (red, green, 0), (bar_x, bar_y, fill_width, bar_height)
                )

    @staticmethod
    def draw_empty_block(screen, screen_x, screen_y):
        """Draw an empty block (air) at the given screen coordinates"""
        rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, WHITE, rect, 1)
