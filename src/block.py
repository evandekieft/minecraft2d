import pygame
from constants import (
    WHITE,
    GRID_SIZE,
)
from block_type import BlockType


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
        self, screen, screen_x, screen_y, is_being_mined=False, mining_progress=0.0
    ):
        """Draw the block at the given screen coordinates"""
        rect = pygame.Rect(screen_x, screen_y, GRID_SIZE, GRID_SIZE)

        # Draw the main block
        pygame.draw.rect(screen, self.type.color, rect)

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
