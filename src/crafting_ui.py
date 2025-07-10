import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION
from typing import Optional, List, Tuple
from block_type import BlockType
from crafting import CRAFTING_RULES, crafting_requirements
from constants import BLACK, WHITE, RED, GRAY


class CraftingUI:
    """Crafting modal UI that overlays the game"""

    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)

        # UI layout constants
        self.modal_width = 800
        self.modal_height = 600
        self.modal_x = (window_width - self.modal_width) // 2
        self.modal_y = (window_height - self.modal_height) // 2

        # Grid settings
        self.box_size = 50
        self.grid_padding = 10

        # Selected crafting rule
        self.selected_craft: Optional[BlockType] = None

        # Clickable areas for craft selection
        self.craft_clickable_rects: List[Tuple[pygame.Rect, BlockType]] = []

    def handle_event(self, event, player_inventory) -> bool:
        """Handle crafting UI events. Returns True if event was handled."""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos

                # Check if clicking on a craft option
                for rect, block_type in self.craft_clickable_rects:
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.selected_craft = block_type
                        return True

        elif event.type == MOUSEMOTION:
            # Could add hover effects here if desired
            pass

        return False

    def draw(self, screen, player_inventory):
        """Draw the crafting modal"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Modal background
        modal_rect = pygame.Rect(
            self.modal_x, self.modal_y, self.modal_width, self.modal_height
        )
        pygame.draw.rect(screen, GRAY, modal_rect)
        pygame.draw.rect(screen, WHITE, modal_rect, 3)

        # Title
        title_text = self.font_medium.render("Crafting", True, WHITE)
        title_rect = title_text.get_rect(
            center=(self.modal_x + self.modal_width // 2, self.modal_y + 40)
        )
        screen.blit(title_text, title_rect)

        # Draw left side - available crafts
        self._draw_available_crafts(screen, player_inventory)

        # Draw vertical separator
        separator_x = self.modal_x + self.modal_width // 2
        pygame.draw.line(
            screen,
            WHITE,
            (separator_x, self.modal_y + 80),
            (separator_x, self.modal_y + self.modal_height - 40),
            3,
        )

        # Draw right side - crafting detail
        self._draw_crafting_detail(screen, player_inventory)

        # Instructions
        instructions = [
            "Click on a recipe to view details",
            "Press 'c' or ESC to close",
        ]
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, WHITE)
            text_rect = text.get_rect(
                center=(
                    self.modal_x + self.modal_width // 2,
                    self.modal_y + self.modal_height - 60 + i * 25,
                )
            )
            screen.blit(text, text_rect)

    def _draw_available_crafts(self, screen, player_inventory):
        """Draw the left side - available crafts list"""
        self.craft_clickable_rects.clear()

        start_x = self.modal_x + 30
        start_y = self.modal_y + 100

        crafts = list(CRAFTING_RULES.keys())

        for i, craft_type in enumerate(crafts):
            y_pos = start_y + i * (self.box_size + 20)

            # Check if player has required materials
            requirements = crafting_requirements(craft_type)
            can_craft = True
            if requirements:
                for req_block, req_count in requirements.items():
                    if player_inventory.get_item_count(req_block) < req_count:
                        can_craft = False
                        break

            # Draw craft box
            craft_rect = pygame.Rect(start_x, y_pos, self.box_size, self.box_size)
            pygame.draw.rect(screen, WHITE, craft_rect)

            # Red border if can't craft
            border_color = WHITE if can_craft else RED
            pygame.draw.rect(screen, border_color, craft_rect, 2)

            # Draw block sprite
            sprite = craft_type.sprite
            if sprite:
                sprite_rect = sprite.get_rect(center=craft_rect.center)
                screen.blit(sprite, sprite_rect)

            # Store clickable area
            self.craft_clickable_rects.append((craft_rect, craft_type))

            # Draw craft name
            name_text = self.font_small.render(craft_type.name, True, WHITE)
            name_rect = name_text.get_rect(
                left=start_x + self.box_size + 15, centery=y_pos + self.box_size // 2
            )
            screen.blit(name_text, name_rect)

    def _draw_crafting_detail(self, screen, player_inventory):
        """Draw the right side - crafting detail"""
        if not self.selected_craft:
            # Show instruction to select a craft
            text = self.font_small.render(
                "Select a recipe to view details", True, WHITE
            )
            text_rect = text.get_rect(
                center=(
                    self.modal_x + self.modal_width * 3 // 4,
                    self.modal_y + self.modal_height // 2,
                )
            )
            screen.blit(text, text_rect)
            return

        recipe = CRAFTING_RULES.get(self.selected_craft)
        if not recipe:
            return

        # Calculate positions
        right_start_x = self.modal_x + self.modal_width // 2 + 30
        grid_start_y = self.modal_y + 120

        # Draw 3x3 crafting grid
        for row in range(3):
            for col in range(3):
                x = right_start_x + col * (self.box_size + 5)
                y = grid_start_y + row * (self.box_size + 5)

                # Draw grid box
                grid_rect = pygame.Rect(x, y, self.box_size, self.box_size)
                pygame.draw.rect(screen, WHITE, grid_rect)

                # Get the block type for this position
                block_type = recipe[row][col]

                if block_type:
                    # Check if player has this block
                    has_block = player_inventory.get_item_count(block_type) > 0

                    # Count how many of this block type we need vs have
                    requirements = crafting_requirements(self.selected_craft)
                    needed_count = (
                        requirements.get(block_type, 0) if requirements else 0
                    )
                    has_count = player_inventory.get_item_count(block_type)

                    # Determine if this specific slot should be red
                    # Count how many of this block type appear before this position
                    blocks_before = 0
                    for r in range(row + 1):
                        for c in range(col + 1 if r == row else 3):
                            if r == row and c == col:
                                break
                            if recipe[r][c] == block_type:
                                blocks_before += 1

                    # This slot is red if we don't have enough for this position
                    slot_available = blocks_before < has_count

                    # Draw border - red if not available
                    border_color = WHITE if slot_available else RED
                    pygame.draw.rect(screen, border_color, grid_rect, 2)

                    # Draw block sprite
                    sprite = block_type.sprite
                    if sprite:
                        sprite_rect = sprite.get_rect(center=grid_rect.center)
                        screen.blit(sprite, sprite_rect)
                else:
                    # Empty slot - just the border
                    pygame.draw.rect(screen, GRAY, grid_rect, 2)

        # Draw arrow
        arrow_y = grid_start_y + 3 * (self.box_size + 5) + 20
        arrow_x = right_start_x + (self.box_size + 5) * 3 // 2

        # Simple downward arrow
        pygame.draw.polygon(
            screen,
            WHITE,
            [(arrow_x - 10, arrow_y), (arrow_x + 10, arrow_y), (arrow_x, arrow_y + 15)],
        )

        # Draw output box
        output_y = arrow_y + 30
        output_rect = pygame.Rect(
            arrow_x - self.box_size // 2, output_y, self.box_size, self.box_size
        )
        pygame.draw.rect(screen, WHITE, output_rect)

        # Check if output is craftable
        requirements = crafting_requirements(self.selected_craft)
        can_craft = True
        if requirements:
            for req_block, req_count in requirements.items():
                if player_inventory.get_item_count(req_block) < req_count:
                    can_craft = False
                    break

        # Red border if can't craft
        border_color = WHITE if can_craft else RED
        pygame.draw.rect(screen, border_color, output_rect, 2)

        # Draw output sprite
        sprite = self.selected_craft.sprite
        if sprite:
            sprite_rect = sprite.get_rect(center=output_rect.center)
            screen.blit(sprite, sprite_rect)

    def handle_window_resize(self, new_width: int, new_height: int):
        """Handle window resize"""
        self.window_width = new_width
        self.window_height = new_height
        self.modal_x = (new_width - self.modal_width) // 2
        self.modal_y = (new_height - self.modal_height) // 2
