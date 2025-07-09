from constants import GRID_SIZE
from block_type import BlockType
import pygame


def draw_block(
    block_type: BlockType,
    screen: pygame.Surface,
    screen_x: int,
    screen_y: int,
    size: int = GRID_SIZE,
    is_being_mined=False,
    mining_progress=0.0,
):
    """Draw a given block type at the given screen coordinates with given size"""
    rect = pygame.Rect(screen_x, screen_y, size, size)

    # Draw the main block
    pygame.draw.rect(screen, block_type.color, rect)

    # Draw mining progress bar if being mined
    if is_being_mined and mining_progress > 0:
        # Calculate progress bar dimensions
        bar_height = max(2, GRID_SIZE // 10)  # At least 2 pixels high
        bar_width = int(GRID_SIZE * 0.8)  # 80% of block width
        bar_x = screen_x + (GRID_SIZE - bar_width) // 2
        bar_y = screen_y + GRID_SIZE - bar_height - 2  # 2px from bottom

        # Draw background of progress bar (empty part)
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Draw filled part of progress bar
        fill_width = int(bar_width * mining_progress)
        if fill_width > 0:
            # Color changes from red to green as progress increases
            red = int(255 * (1 - mining_progress))
            green = int(255 * mining_progress)
            pygame.draw.rect(
                screen, (red, green, 0), (bar_x, bar_y, fill_width, bar_height)
            )
