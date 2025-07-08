import pygame
import os
import json
from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_UP,
    K_DOWN,
    K_DELETE,
)
from constants import WINDOW_SIZE, BLACK, WHITE, GAME_HEIGHT, INVENTORY_HEIGHT


class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.current_menu = "main"  # main, world_select, create_world, pause
        self.selected_option = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.worlds_dir = "saves"
        self.ensure_saves_directory()

        # Create world input
        self.creating_world = False
        self.new_world_name = ""

    def ensure_saves_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.worlds_dir):
            os.makedirs(self.worlds_dir)

    def get_world_list(self):
        """Get list of saved worlds"""
        worlds = []
        if os.path.exists(self.worlds_dir):
            for filename in os.listdir(self.worlds_dir):
                if filename.endswith(".json"):
                    world_name = filename[:-5]  # Remove .json extension
                    worlds.append(world_name)
        return sorted(worlds)

    def handle_event(self, event):
        """Handle menu events, returns action or None"""
        if event.type == KEYDOWN:
            if self.current_menu == "main":
                return self.handle_main_menu_input(event.key)
            elif self.current_menu == "world_select":
                return self.handle_world_select_input(event.key)
            elif self.current_menu == "create_world":
                return self.handle_create_world_input(event.key)
            elif self.current_menu == "pause":
                return self.handle_pause_menu_input(event.key)
        return None

    def handle_main_menu_input(self, key):
        """Handle main menu input"""
        if key == K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == K_DOWN:
            self.selected_option = min(1, self.selected_option + 1)
        elif key == K_RETURN:
            if self.selected_option == 0:  # Play
                self.current_menu = "world_select"
                self.selected_option = 0
            elif self.selected_option == 1:  # Quit
                return "quit"
        return None

    def handle_world_select_input(self, key):
        """Handle world selection input"""
        worlds = self.get_world_list()
        max_options = len(worlds) + 1  # +1 for "Create New World"

        if key == K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == K_DOWN:
            self.selected_option = min(max_options - 1, self.selected_option + 1)
        elif key == K_RETURN:
            if self.selected_option == len(worlds):  # Create New World
                self.current_menu = "create_world"
                self.creating_world = True
                self.new_world_name = ""
                self.selected_option = 0
            else:  # Load existing world
                world_name = worlds[self.selected_option]
                return ("load_world", world_name)
        elif key == K_DELETE and worlds:
            # Delete selected world
            if self.selected_option < len(worlds):
                world_name = worlds[self.selected_option]
                self.delete_world(world_name)
                if self.selected_option >= len(self.get_world_list()):
                    self.selected_option = max(0, len(self.get_world_list()) - 1)
        elif key == K_ESCAPE:
            self.current_menu = "main"
            self.selected_option = 0
        return None

    def handle_create_world_input(self, key):
        """Handle world creation input"""
        if key == K_RETURN and self.new_world_name.strip():
            world_name = self.new_world_name.strip()
            self.creating_world = False
            return ("create_world", world_name)
        elif key == K_ESCAPE:
            self.current_menu = "world_select"
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
                return "save_and_exit"
            elif self.selected_option == 2:  # Exit without Saving
                return "exit_no_save"
        elif key == K_ESCAPE:
            return "resume"
        return None

    def delete_world(self, world_name):
        """Delete a world save file"""
        filepath = os.path.join(self.worlds_dir, f"{world_name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

    def draw(self):
        """Draw the current menu"""
        self.screen.fill(BLACK)

        if self.current_menu == "main":
            self.draw_main_menu()
        elif self.current_menu == "world_select":
            self.draw_world_select_menu()
        elif self.current_menu == "create_world":
            self.draw_create_world_menu()
        elif self.current_menu == "pause":
            self.draw_pause_menu()

    def draw_main_menu(self):
        """Draw the main menu"""
        # Title
        title_text = self.font_large.render("MINECRAFT 2D", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Menu options
        options = ["Play", "Quit"]
        start_y = 350

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, start_y + i * 60))
            self.screen.blit(text, text_rect)

    def draw_world_select_menu(self):
        """Draw the world selection menu"""
        # Title
        title_text = self.font_large.render("Select World", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 100))
        self.screen.blit(title_text, title_rect)

        # World list
        worlds = self.get_world_list()
        start_y = 200

        for i, world_name in enumerate(worlds):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(world_name, True, color)
            text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, start_y + i * 50))
            self.screen.blit(text, text_rect)

        # Create New World option
        create_color = (255, 255, 0) if len(worlds) == self.selected_option else WHITE
        create_text = self.font_medium.render("Create New World", True, create_color)
        create_rect = create_text.get_rect(
            center=(WINDOW_SIZE[0] // 2, start_y + len(worlds) * 50)
        )
        self.screen.blit(create_text, create_rect)

        # Instructions
        instructions = [
            "Press ENTER to select",
            "Press DELETE to delete world",
            "Press ESC to go back",
        ]

        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (128, 128, 128))
            text_rect = text.get_rect(
                center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] - 120 + i * 30)
            )
            self.screen.blit(text, text_rect)

    def draw_create_world_menu(self):
        """Draw the create world menu"""
        # Title
        title_text = self.font_large.render("Create New World", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Prompt
        prompt_text = self.font_medium.render("Enter world name:", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_SIZE[0] // 2, 300))
        self.screen.blit(prompt_text, prompt_rect)

        # Input box
        input_box = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, 350, 400, 50)
        pygame.draw.rect(self.screen, WHITE, input_box, 2)

        # Input text
        input_text = self.font_medium.render(self.new_world_name, True, WHITE)
        input_rect = input_text.get_rect(center=(WINDOW_SIZE[0] // 2, 375))
        self.screen.blit(input_text, input_rect)

        # Cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            cursor_x = input_rect.right + 5
            pygame.draw.line(self.screen, WHITE, (cursor_x, 360), (cursor_x, 390), 2)

        # Instructions
        instructions = ["Press ENTER to create world", "Press ESC to cancel"]

        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (128, 128, 128))
            text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, 450 + i * 30))
            self.screen.blit(text, text_rect)

    def draw_pause_menu(self):
        """Draw the pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Title
        title_text = self.font_large.render("PAUSED", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Menu options
        options = ["Resume", "Save & Exit to Menu", "Exit without Saving"]
        start_y = 350

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, start_y + i * 60))
            self.screen.blit(text, text_rect)

    def show_pause_menu(self):
        """Show the pause menu"""
        self.current_menu = "pause"
        self.selected_option = 0

    def reset_to_main_menu(self):
        """Reset to main menu"""
        self.current_menu = "main"
        self.selected_option = 0
        self.creating_world = False
        self.new_world_name = ""
