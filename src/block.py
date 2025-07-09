import pygame
from constants import (
    WHITE,
    GRID_SIZE,
)
from block_type import BlockType
from block_drawing import draw_block


class Block:
    def __init__(self, block_type: BlockType):
        self.type: BlockType = block_type
        self.max_health: float = self.type.mining_difficulty
        self.current_health: float = self.max_health

    def reset_health(self):
        """Reset block health to maximum (when mining is interrupted)"""
        self.current_health = self.max_health

    def take_damage(self, damage: float) -> bool:
        """Apply mining damage to the block. Returns True if block is destroyed."""
        if not self.type.minable:
            return False

        self.current_health -= damage
        return self.current_health <= 0

    def draw(
        self,
        screen: pygame.Surface,
        screen_x: int,
        screen_y: int,
        is_being_mined=False,
        mining_progress=0.0,
    ):
        """Draw the block at the given screen coordinates"""
        draw_block(
            self.type,
            screen,
            screen_x,
            screen_y,
            is_being_mined=is_being_mined,
            mining_progress=mining_progress,
        )
