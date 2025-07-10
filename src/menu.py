import pygame
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    K_RETURN,
    K_UP,
    K_DOWN,
    K_DELETE,
)
from constants import WINDOW_SIZE, BLACK, WHITE
from enum import Enum
from world_storage import WorldStorage


class MenuOption(Enum):
    MAIN = "main"
    WORLD_SELECT = "world_select"
    PAUSE = "pause"
    SAVE_WORLD = "save_world"


class MenuSystem:
    def __init__(self, world_storage: WorldStorage):
        self.current_menu: MenuOption = MenuOption.MAIN
        self.selected_option = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.world_storage = world_storage

        # Window dimensions (start with constants, update on resize)
        self.window_width = WINDOW_SIZE[0]
        self.window_height = WINDOW_SIZE[1]

        # Load logo
        self.logo_original = pygame.image.load("assets/logo/minecraft2d_logo.png")
        self.logo_original = self.logo_original.convert_alpha()
        # Resize logo to a fixed width while maintaining aspect ratio
        logo_width = 700  # Increased since logo is now cropped tighter
        aspect_ratio = self.logo_original.get_height() / self.logo_original.get_width()
        logo_height = int(logo_width * aspect_ratio)
        self.logo = pygame.transform.smoothscale(
            self.logo_original, (logo_width, logo_height)
        )

    def handle_event(self, event):
        """Handle menu events, returns action or None"""
        if event.type == KEYDOWN:
            if self.current_menu == MenuOption.MAIN:
                return self.handle_main_menu_input(event.key)
            elif self.current_menu == MenuOption.WORLD_SELECT:
                return self.handle_world_select_input(event.key)
            elif self.current_menu == MenuOption.PAUSE:
                return self.handle_pause_menu_input(event.key)
            elif self.current_menu == MenuOption.SAVE_WORLD:
                return self.handle_save_world_input(event.key)
        return None

    def handle_main_menu_input(self, key):
        """Handle main menu input"""
        if key == K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == K_DOWN:
            self.selected_option = min(1, self.selected_option + 1)
        elif key == K_RETURN:
            if self.selected_option == 0:  # Play
                self.current_menu = MenuOption.WORLD_SELECT
                self.selected_option = 0
            elif self.selected_option == 1:  # Quit
                return "quit"
        return None

    def handle_world_select_input(self, key):
        """Handle world selection input"""
        worlds = self.world_storage.get_world_list()
        max_options = len(worlds) + 1  # +1 for "Create New World"

        if key == K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == K_DOWN:
            self.selected_option = min(max_options - 1, self.selected_option + 1)
        elif key == K_RETURN:
            if self.selected_option == len(worlds):  # Create New World
                # Directly create world without name prompt
                return ("create_world", None)
            else:  # Load existing world
                world_name = worlds[self.selected_option]
                return ("load_world", world_name)
        elif key == K_DELETE and worlds:
            # Delete selected world
            if self.selected_option < len(worlds):
                world_name = worlds[self.selected_option]
                self.world_storage.delete_world(world_name)
                if self.selected_option >= len(self.world_storage.get_world_list()):
                    self.selected_option = max(
                        0, len(self.world_storage.get_world_list()) - 1
                    )
        elif key == K_ESCAPE:
            self.current_menu = MenuOption.MAIN
            self.selected_option = 0
        return None

    def handle_create_world_input(self, key):
        """Handle world creation input"""
        if key == K_RETURN and self.new_world_name.strip():
            world_name = self.new_world_name.strip()
            self.creating_world = False
            return ("create_world", world_name)
        elif key == K_ESCAPE:
            self.current_menu = MenuOption.WORLD_SELECT
            self.creating_world = False
            self.new_world_name = ""
            self.selected_option = 0
        else:
            # Handle text input
            if key == 8:  # Backspace
                self.new_world_name = self.new_world_name[:-1]
            elif 32 <= key <= 126:  # Printable characters
                if len(self.new_world_name) < 20:  # Limit name length
                    self.new_world_name += chr(key)
        return None

    def handle_pause_menu_input(self, key):
        """Handle pause menu input"""
        if key == K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == K_DOWN:
            self.selected_option = min(2, self.selected_option + 1)
        elif key == K_RETURN:
            if self.selected_option == 0:  # Resume
                return "resume"
            elif self.selected_option == 1:  # Save & Exit to Menu
                # Switch to save world menu to get name
                self.current_menu = MenuOption.SAVE_WORLD
                self.saving_world = True
                self.save_world_name = ""
                self.selected_option = 0
                return None
            elif self.selected_option == 2:  # Exit without Saving
                return "exit_no_save"
        elif key == K_ESCAPE:
            return "resume"
        return None

    def handle_save_world_input(self, key):
        """Handle save world name input"""
        if key == K_RETURN and self.save_world_name.strip():
            world_name = self.save_world_name.strip()
            self.saving_world = False
            return ("save_and_exit", world_name)
        elif key == K_ESCAPE:
            # Return to pause menu
            self.current_menu = MenuOption.PAUSE
            self.saving_world = False
            self.save_world_name = ""
            self.selected_option = 1
        else:
            # Handle text input
            if key == 8:  # Backspace
                self.save_world_name = self.save_world_name[:-1]
            elif 32 <= key <= 126:  # Printable characters
                if len(self.save_world_name) < 20:  # Limit name length
                    self.save_world_name += chr(key)
        return None

    def draw(self, screen):
        """Draw the current menu"""
        screen.fill(BLACK)

        if self.current_menu == MenuOption.MAIN:
            self._draw_main_menu(screen)
        elif self.current_menu == MenuOption.WORLD_SELECT:
            self._draw_world_select_menu(screen)
        elif self.current_menu == MenuOption.PAUSE:
            self._draw_pause_menu(screen)
        elif self.current_menu == MenuOption.SAVE_WORLD:
            self._draw_save_world_menu(screen)

    def handle_window_resize(self, new_width, new_height):
        """Handle window resize for the menu system"""
        self.window_width = new_width
        self.window_height = new_height

    def _draw_main_menu(self, screen):
        """Draw the main menu"""
        # Logo - positioned with good top margin
        logo_top_margin = 100
        logo_rect = self.logo.get_rect(
            center=(
                self.window_width // 2,
                logo_top_margin + self.logo.get_height() // 2,
            )
        )
        screen.blit(self.logo, logo_rect)

        # Menu options - positioned dynamically based on logo
        options = ["Play", "Quit"]
        # Start menu options below logo with some spacing
        start_y = logo_rect.bottom + 60  # Reduced spacing since logo is tighter

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.window_width // 2, start_y + i * 60))
            screen.blit(text, text_rect)

    def _draw_world_select_menu(self, screen):
        """Draw the world selection menu"""
        # Title
        title_text = self.font_large.render("Select World", True, WHITE)
        title_rect = title_text.get_rect(center=(self.window_width // 2, 100))
        screen.blit(title_text, title_rect)

        # World list
        worlds = self.world_storage.get_world_list()
        start_y = 200

        for i, world_name in enumerate(worlds):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(world_name, True, color)
            text_rect = text.get_rect(center=(self.window_width // 2, start_y + i * 50))
            screen.blit(text, text_rect)

        # Create New World option
        create_color = (255, 255, 0) if len(worlds) == self.selected_option else WHITE
        create_text = self.font_medium.render("Create New World", True, create_color)
        create_rect = create_text.get_rect(
            center=(self.window_width // 2, start_y + len(worlds) * 50)
        )
        screen.blit(create_text, create_rect)

        # Instructions
        instructions = [
            "Press ENTER to select",
            "Press DELETE to delete world",
            "Press ESC to go back",
        ]

        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (128, 128, 128))
            text_rect = text.get_rect(
                center=(self.window_width // 2, WINDOW_SIZE[1] - 120 + i * 30)
            )
            screen.blit(text, text_rect)

    def _draw_pause_menu(self, screen):
        """Draw the pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font_large.render("PAUSED", True, WHITE)
        title_rect = title_text.get_rect(center=(self.window_width // 2, 200))
        screen.blit(title_text, title_rect)

        # Menu options
        options = ["Resume", "Save & Exit to Menu", "Exit without Saving"]
        start_y = 350

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.window_width // 2, start_y + i * 60))
            screen.blit(text, text_rect)

    def _draw_save_world_menu(self, screen):
        """Draw the save world menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font_large.render("Save World", True, WHITE)
        title_rect = title_text.get_rect(center=(self.window_width // 2, 200))
        screen.blit(title_text, title_rect)

        # Prompt
        prompt_text = self.font_medium.render("Enter world name:", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(self.window_width // 2, 300))
        screen.blit(prompt_text, prompt_rect)

        # Input box
        input_box = pygame.Rect(self.window_width // 2 - 200, 350, 400, 50)
        pygame.draw.rect(screen, WHITE, input_box, 2)

        # Input text
        input_text = self.font_medium.render(self.save_world_name, True, WHITE)
        input_rect = input_text.get_rect(center=(self.window_width // 2, 375))
        screen.blit(input_text, input_rect)

        # Cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            cursor_x = input_rect.right + 5
            pygame.draw.line(screen, WHITE, (cursor_x, 360), (cursor_x, 390), 2)

        # Instructions
        instructions = ["Press ENTER to save world", "Press ESC to cancel"]

        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (128, 128, 128))
            text_rect = text.get_rect(center=(self.window_width // 2, 450 + i * 30))
            screen.blit(text, text_rect)

    def show_pause_menu(self):
        """Show the pause menu"""
        self.current_menu = MenuOption.PAUSE
        self.selected_option = 0

    def reset_to_main_menu(self):
        """Reset to main menu"""
        self.current_menu = MenuOption.MAIN
        self.selected_option = 0
        self.creating_world = False
        self.new_world_name = ""
        self.saving_world = False
        self.save_world_name = ""
