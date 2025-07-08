import pytest
import pygame
from unittest.mock import patch
from block import Block
from constants import (
    GREEN,
    LIGHT_BROWN,
    DARK_BROWN,
    BLUE,
    WHITE,
    GRAY,
    GRID_SIZE,
)


class TestBlockDrawing:
    """Test drawing methods for Block class"""

    def setup_class(self):
        self.screen = pygame.Surface((800, 600))

    def test_draw_basic_block(self):
        """Test drawing a basic block without mining progress"""
        block = Block("grass")
        screen_x, screen_y = 100, 200

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, screen_x, screen_y)

            # Should draw the main block
            mock_draw_rect.assert_called_once()
            args = mock_draw_rect.call_args[0]
            assert args[0] == self.screen  # screen
            assert args[1] == block.color  # color
            # args[2] is the rect - check it has correct position and size
            rect = args[2]
            assert rect.x == screen_x
            assert rect.y == screen_y
            assert rect.width == GRID_SIZE
            assert rect.height == GRID_SIZE

    def test_draw_block_with_mining_progress(self):
        """Test drawing a block with mining progress bar"""
        block = Block("wood")
        screen_x, screen_y = 50, 75
        mining_progress = 0.6  # 60% mined

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(
                self.screen,
                screen_x,
                screen_y,
                is_being_mined=True,
                mining_progress=mining_progress,
            )

            # Should draw multiple rectangles:
            # 1. Main block
            # 2. Progress bar background
            # 3. Progress bar fill
            assert mock_draw_rect.call_count == 3

            # First call should be the main block
            first_call = mock_draw_rect.call_args_list[0][0]
            assert first_call[0] == self.screen
            assert first_call[1] == block.color

            # Second call should be progress bar background (gray)
            second_call = mock_draw_rect.call_args_list[1][0]
            assert second_call[1] == (100, 100, 100)  # Gray background

            # Third call should be progress bar fill (red-green gradient)
            third_call = mock_draw_rect.call_args_list[2][0]
            fill_color = third_call[1]
            # At 60% progress: red should be 40% of 255, green should be 60% of 255
            expected_red = int(255 * (1 - mining_progress))
            expected_green = int(255 * mining_progress)
            assert fill_color == (expected_red, expected_green, 0)

    def test_draw_block_no_mining_progress_when_not_being_mined(self):
        """Test that no progress bar is drawn when not being mined"""
        block = Block("stone")

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, 0, 0, is_being_mined=False, mining_progress=0.8)

            # Should only draw the main block, no progress bar
            mock_draw_rect.assert_called_once()

    def test_draw_block_no_mining_progress_when_zero_progress(self):
        """Test that no progress bar is drawn when progress is zero"""
        block = Block("coal")

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, 0, 0, is_being_mined=True, mining_progress=0.0)

            # Should only draw the main block, no progress bar
            mock_draw_rect.assert_called_once()

    def test_draw_empty_block(self):
        """Test drawing an empty block (air)"""
        screen_x, screen_y = 300, 400

        with patch("pygame.draw.rect") as mock_draw_rect:
            Block.draw_empty_block(self.screen, screen_x, screen_y)

            # Should draw a white outline
            mock_draw_rect.assert_called_once()
            args = mock_draw_rect.call_args[0]
            assert args[0] == self.screen
            assert args[1] == WHITE  # White color
            # Check rect position and size
            rect = args[2]
            assert rect.x == screen_x
            assert rect.y == screen_y
            assert rect.width == GRID_SIZE
            assert rect.height == GRID_SIZE
            # Check that it's drawn as outline (width=1)
            assert len(mock_draw_rect.call_args[0]) == 4  # screen, color, rect, width
            assert mock_draw_rect.call_args[0][3] == 1  # width=1 for outline

    def test_progress_bar_dimensions(self):
        """Test that progress bar has correct dimensions"""
        block = Block("diamond")

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, 0, 0, is_being_mined=True, mining_progress=0.5)

            # Get the progress bar background call (second call)
            bg_call = mock_draw_rect.call_args_list[1][0]
            bg_rect_args = bg_call[2]  # This is the rect tuple (x, y, width, height)

            # Progress bar should be 80% of block width
            expected_width = int(GRID_SIZE * 0.8)
            if hasattr(bg_rect_args, "width"):
                assert bg_rect_args.width == expected_width
            else:
                # Handle tuple case (x, y, width, height)
                assert bg_rect_args[2] == expected_width

            # Progress bar should be at least 2 pixels high
            expected_height = max(2, GRID_SIZE // 10)
            if hasattr(bg_rect_args, "height"):
                assert bg_rect_args.height == expected_height
            else:
                assert bg_rect_args[3] == expected_height

    def test_progress_bar_fill_width(self):
        """Test that progress bar fill has correct width based on progress"""
        block = Block("stone")
        progress = 0.75  # 75% progress

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, 0, 0, is_being_mined=True, mining_progress=progress)

            # Get the progress bar fill call (third call)
            fill_call = mock_draw_rect.call_args_list[2][0]
            fill_rect_args = fill_call[2]

            # Fill width should be progress * bar_width
            bar_width = int(GRID_SIZE * 0.8)
            expected_fill_width = int(bar_width * progress)
            if hasattr(fill_rect_args, "width"):
                assert fill_rect_args.width == expected_fill_width
            else:
                # Handle tuple case (x, y, width, height)
                assert fill_rect_args[2] == expected_fill_width

    @pytest.mark.parametrize(
        "block_type,expected_color",
        [
            ("grass", GREEN),
            ("dirt", DARK_BROWN),
            ("wood", LIGHT_BROWN),
            ("stone", GRAY),
            ("water", BLUE),
        ],
    )
    def test_draw_different_block_types(self, block_type, expected_color):
        """Test drawing different block types with correct colors"""
        block = Block(block_type)

        with patch("pygame.draw.rect") as mock_draw_rect:
            block.draw(self.screen, 0, 0)

            # Check that the block is drawn with the correct color
            args = mock_draw_rect.call_args[0]
            assert args[1] == expected_color
