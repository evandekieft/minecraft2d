import pygame
import math
from terrain_generator_v2 import create_terrain_generator
from block import Block
from player import Player
from camera import Camera
from lighting import lighting_system
from constants import (
    GRID_SIZE,
    BLACK,
    WHITE,
    INVENTORY_HEIGHT,
)


class Game:
    def __init__(self, terrain_seed=42):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks

        # Initialize terrain generator
        self.terrain_generator = create_terrain_generator(seed=terrain_seed)

        # Day/night cycle settings
        self.day_duration = 120.0  # 2 minutes for day (in seconds)
        self.night_duration = 120.0  # 2 minutes for night (in seconds)
        self.cycle_duration = (
            self.day_duration + self.night_duration
        )  # Total cycle: 4 minutes

        # Time tracking (starts at noon - full daylight)
        self.time_elapsed = 0.0  # Time elapsed in current cycle
        self.current_time_of_day = 0.0  # 0.0 = noon, 0.5 = midnight, 1.0 = noon again

        # Light level (0.0 = pitch black, 1.0 = full daylight)
        self.light_level = 1.0  # Start at full daylight (noon)

        # Generate initial chunks around player
        self._generate_chunks_around_player()

    def update_day_cycle(self, dt):
        """Update the day/night cycle and lighting"""
        # Update time
        self.time_elapsed += dt

        # Calculate current time of day (0.0 = noon, 0.5 = midnight, 1.0 = noon again)
        self.current_time_of_day = (self.time_elapsed / self.cycle_duration) % 1.0

        # Calculate light level using smooth sine wave
        # At 0.0 (noon): light_level = 1.0 (full daylight)
        # At 0.5 (midnight): light_level = 0.0 (pitch black)
        # Smooth transition between day and night
        self.light_level = (math.cos(self.current_time_of_day * 2 * math.pi) + 1) / 2

        # Convert light level to darkness alpha (0-220)
        # light_level 1.0 -> darkness_alpha 0 (full light)
        # light_level 0.0 -> darkness_alpha 220 (very dark)
        max_darkness = 220
        darkness_alpha = int(max_darkness * (1.0 - self.light_level))

        # Update lighting system
        lighting_system.set_darkness_level(darkness_alpha)

    def get_time_of_day_string(self):
        """Get a readable string representing the current time of day"""
        if 0.0 <= self.current_time_of_day < 0.25:
            return "Afternoon"
        elif 0.25 <= self.current_time_of_day < 0.5:
            return "Evening"
        elif 0.5 <= self.current_time_of_day < 0.75:
            return "Night"
        else:
            return "Dawn"

    def is_daytime(self):
        """Check if it's currently daytime (light level > 0.5)"""
        return self.light_level > 0.5

    def _generate_chunks_around_player(self):
        # Generate chunks in a 5x5 area around player to prevent black borders
        # With 25x19 visible blocks and 16x16 chunks, we need more coverage
        player_chunk_x = self.player.world_x // self.chunk_size
        player_chunk_y = self.player.world_y // self.chunk_size

        for cy in range(player_chunk_y - 2, player_chunk_y + 3):
            for cx in range(player_chunk_x - 2, player_chunk_x + 3):
                if (cx, cy) not in self.chunks:
                    self._generate_chunk(cx, cy)

    def _generate_chunk(self, chunk_x, chunk_y):
        """Generate a chunk using the new noise-based terrain system"""
        chunk = {}
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y

                # Use terrain generator to determine block type
                block_type = self.terrain_generator.generate_block_type(
                    world_x, world_y
                )
                chunk[(x, y)] = Block(block_type)

        self.chunks[(chunk_x, chunk_y)] = chunk

    def get_block(self, world_x, world_y):
        # Get block at world coordinates
        chunk_x = world_x // self.chunk_size
        chunk_y = world_y // self.chunk_size

        if (chunk_x, chunk_y) not in self.chunks:
            self._generate_chunk(chunk_x, chunk_y)

        chunk = self.chunks[(chunk_x, chunk_y)]
        local_x = world_x % self.chunk_size
        local_y = world_y % self.chunk_size

        return chunk.get((local_x, local_y))

    def replace_block(self, world_x, world_y, new_block_type):
        """Replace a block at the given coordinates with a new block type"""
        chunk_x = world_x // self.chunk_size
        chunk_y = world_y // self.chunk_size

        if (chunk_x, chunk_y) not in self.chunks:
            return False

        chunk = self.chunks[(chunk_x, chunk_y)]
        local_x = world_x % self.chunk_size
        local_y = world_y % self.chunk_size

        if (local_x, local_y) in chunk:
            chunk[(local_x, local_y)] = Block(new_block_type)
            return True
        return False

    def draw(self, screen):
        """Draw the game world"""
        screen.fill(BLACK)

        # Draw world - only visible blocks
        left, right, top, bottom = self.camera.get_visible_bounds()

        for world_y in range(top, bottom + 1):
            for world_x in range(left, right + 1):
                screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                # Only draw if on screen (within game area)
                if (
                    -GRID_SIZE < screen_x < self.camera.window_width
                    and -GRID_SIZE < screen_y < self.camera.game_height
                ):
                    block = self.get_block(world_x, world_y)
                    if block:
                        # Check if this block is being mined
                        is_being_mined = (
                            self.player.is_mining
                            and self.player.mining_target == (world_x, world_y)
                        )
                        mining_progress = 0.0
                        if is_being_mined and block.minable:
                            mining_progress = 1.0 - (
                                block.current_health / block.max_health
                            )

                        block.draw(
                            screen, screen_x, screen_y, is_being_mined, mining_progress
                        )
                    else:
                        # Draw empty block (air)
                        Block.draw_empty_block(screen, screen_x, screen_y)

        # Draw targeting border around the block the player is facing
        target_x, target_y = self.player.get_target_position()
        target_screen_x, target_screen_y = self.camera.world_to_screen(
            target_x, target_y
        )

        # Only draw if target is on screen
        if (
            -GRID_SIZE < target_screen_x < self.camera.window_width
            and -GRID_SIZE < target_screen_y < self.camera.game_height
        ):
            target_block = self.get_block(target_x, target_y)
            if target_block:  # Only show border if there's actually a block there
                # Draw a subtle border - light gray, thin line
                border_rect = pygame.Rect(
                    target_screen_x, target_screen_y, GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(screen, (200, 200, 200), border_rect, 2)

        # Apply lighting effect
        lighting_system.apply_lighting(screen, self.camera)

        # Draw player (after lighting, so player is visible in darkness)
        self._draw_player(screen)

        # Draw inventory (UI should be on top of lighting)
        self._draw_inventory(screen)

    def _draw_player(self, screen):
        """Draw the player"""
        player_screen_x, player_screen_y = self.camera.world_to_screen(
            self.player.world_x, self.player.world_y
        )

        # Try to use sprite first, fall back to colored rectangle
        player_sprite = self.player.get_current_sprite()
        if player_sprite:
            # Center the sprite in the grid cell
            sprite_rect = player_sprite.get_rect()
            sprite_rect.center = (
                player_screen_x + GRID_SIZE // 2,
                player_screen_y + GRID_SIZE // 2,
            )
            screen.blit(player_sprite, sprite_rect)
        else:
            # Fallback to colored rectangle with orientation arrow
            player_rect = pygame.Rect(
                player_screen_x + 2, player_screen_y + 2, GRID_SIZE - 4, GRID_SIZE - 4
            )
            pygame.draw.rect(screen, self.player.color, player_rect)

            # Draw orientation indicator
            center_x = player_screen_x + GRID_SIZE // 2
            center_y = player_screen_y + GRID_SIZE // 2
            arrow_length = 4

            if self.player.orientation == "north":
                end_x, end_y = center_x, center_y - arrow_length
            elif self.player.orientation == "south":
                end_x, end_y = center_x, center_y + arrow_length
            elif self.player.orientation == "east":
                end_x, end_y = center_x + arrow_length, center_y
            elif self.player.orientation == "west":
                end_x, end_y = center_x - arrow_length, center_y

            pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 2)

    def _draw_inventory(self, screen):
        """Draw the player inventory"""
        # Draw black inventory background
        inventory_rect = pygame.Rect(0, self.camera.game_height, self.camera.window_width, INVENTORY_HEIGHT)
        pygame.draw.rect(screen, BLACK, inventory_rect)

        # Get top 5 inventory items
        top_items = self.player.get_top_inventory_items(5)

        # Calculate slot dimensions and positions
        slot_size = 50
        slot_spacing = 10
        total_width = 5 * slot_size + 4 * slot_spacing
        start_x = (self.camera.window_width - total_width) // 2
        start_y = self.camera.game_height + (INVENTORY_HEIGHT - slot_size) // 2

        # Draw 5 inventory slots
        for i in range(5):
            slot_x = start_x + i * (slot_size + slot_spacing)
            slot_y = start_y

            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            pygame.draw.rect(screen, (64, 64, 64), slot_rect)  # Dark gray

            # Draw border (highlight active slot)
            border_color = WHITE if i == self.player.active_slot else (128, 128, 128)
            border_width = 3 if i == self.player.active_slot else 1
            pygame.draw.rect(screen, border_color, slot_rect, border_width)

            # Draw block if available
            if i < len(top_items):
                block_type, count = top_items[i]

                # Get block color (import from world to get Block class)
                temp_block = Block(block_type)

                # Draw block color
                block_rect = pygame.Rect(
                    slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 30
                )
                pygame.draw.rect(screen, temp_block.color, block_rect)

                # Draw count text
                font = pygame.font.Font(None, 24)
                count_text = font.render(str(count), True, WHITE)
                text_x = slot_x + slot_size // 2 - count_text.get_width() // 2
                text_y = slot_y + slot_size - 20
                screen.blit(count_text, (text_x, text_y))

        # Draw day/night indicator with sun/moon visual
        self._draw_day_night_indicator(screen)

    def _draw_day_night_indicator(self, screen):
        """Draw a visual day/night indicator with sun/moon"""
        # Position for the indicator (right side of inventory area, vertically centered)
        indicator_x = self.camera.window_width - 120
        indicator_y = self.camera.game_height + (INVENTORY_HEIGHT // 2)
        indicator_size = 25

        # Colors
        sun_color = (255, 255, 0)  # Yellow
        moon_color = (220, 220, 220)  # Light gray
        night_sky_color = (20, 20, 40)  # Dark blue
        day_sky_color = (135, 206, 235)  # Sky blue

        # Calculate background color based on time of day
        sky_blend = self.light_level
        bg_color = (
            int(night_sky_color[0] * (1 - sky_blend) + day_sky_color[0] * sky_blend),
            int(night_sky_color[1] * (1 - sky_blend) + day_sky_color[1] * sky_blend),
            int(night_sky_color[2] * (1 - sky_blend) + day_sky_color[2] * sky_blend),
        )

        # Draw background circle
        pygame.draw.circle(screen, bg_color, (indicator_x, indicator_y), indicator_size)
        pygame.draw.circle(screen, WHITE, (indicator_x, indicator_y), indicator_size, 2)

        # Draw sun or moon centered in the circle
        if self.is_daytime():
            # Draw sun centered in the circle
            sun_radius = 8
            pygame.draw.circle(
                screen, sun_color, (indicator_x, indicator_y), sun_radius
            )

            # Draw sun rays
            for i in range(8):
                ray_angle = i * math.pi / 4
                ray_length = 12
                ray_start_x = indicator_x + int((sun_radius + 2) * math.cos(ray_angle))
                ray_start_y = indicator_y + int((sun_radius + 2) * math.sin(ray_angle))
                ray_end_x = indicator_x + int(
                    (sun_radius + ray_length) * math.cos(ray_angle)
                )
                ray_end_y = indicator_y + int(
                    (sun_radius + ray_length) * math.sin(ray_angle)
                )
                pygame.draw.line(
                    screen,
                    sun_color,
                    (ray_start_x, ray_start_y),
                    (ray_end_x, ray_end_y),
                    2,
                )
        else:
            # Draw moon centered in the circle
            moon_radius = 8
            pygame.draw.circle(
                screen, moon_color, (indicator_x, indicator_y), moon_radius
            )

            # Draw moon craters (simple circles)
            crater_color = (180, 180, 180)
            pygame.draw.circle(
                screen, crater_color, (indicator_x - 2, indicator_y - 2), 2
            )
            pygame.draw.circle(
                screen, crater_color, (indicator_x + 3, indicator_y + 1), 1
            )
            pygame.draw.circle(
                screen, crater_color, (indicator_x - 1, indicator_y + 3), 1
            )

        # Draw time text below the indicator
        font_small = pygame.font.Font(None, 18)
        time_text = self.get_time_of_day_string()
        light_pct = int(self.light_level * 100)
        display_text = f"{time_text} ({light_pct}%)"
        text_surface = font_small.render(display_text, True, WHITE)
        text_x = indicator_x - text_surface.get_width() // 2
        text_y = indicator_y + indicator_size + 8
        screen.blit(text_surface, (text_x, text_y))

    def update_state(self, dt):
        """Update game state every time tick (dt)"""
        self.player.update(dt, self)
        self.camera.update(self.player.world_x, self.player.world_y, dt)
        self._generate_chunks_around_player()

        # Update day cycle
        self.update_day_cycle(dt)
    
    def handle_window_resize(self, new_width, new_height):
        """Handle window resize - update camera and potentially generate new chunks"""
        # Update camera with new screen dimensions
        self.camera.handle_window_resize(new_width, new_height)
        
        # Force chunk generation around player to cover new visible area
        # This ensures we have terrain for the potentially larger visible area
        self._generate_chunks_around_player_extended()
    
    def _generate_chunks_around_player_extended(self):
        """Generate chunks in a larger area around player for window resize"""
        # Calculate how many chunks we need based on current window size
        # Use the camera's visible bounds to determine required chunks
        left, right, top, bottom = self.camera.get_visible_bounds()
        
        # Convert world bounds to chunk bounds
        chunk_left = left // self.chunk_size - 1  # Extra margin
        chunk_right = right // self.chunk_size + 1
        chunk_top = top // self.chunk_size - 1
        chunk_bottom = bottom // self.chunk_size + 1
        
        # Generate any missing chunks in the visible area
        for cy in range(chunk_top, chunk_bottom + 1):
            for cx in range(chunk_left, chunk_right + 1):
                if (cx, cy) not in self.chunks:
                    self._generate_chunk(cx, cy)
