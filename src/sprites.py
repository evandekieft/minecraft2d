import pygame
import os
from constants import GRID_SIZE


class SpriteManager:
    def __init__(self):
        self.sprites = {}

    def load_sprite(
        self, path, target_width=GRID_SIZE, target_height=GRID_SIZE
    ) -> pygame.Surface:
        """Load a sprite and scale it cleanly (no smoothing for pixel art)"""

        if path in self.sprites:
            return self.sprites[path]

        # Load the original sprite
        original = pygame.image.load(path).convert_alpha()

        # Scale without smoothing to preserve pixel art
        scaled = pygame.transform.scale(original, (target_width, target_height))

        # Cache the sprite
        self.sprites[path] = scaled
        return scaled

    def load_player_sprites(self):
        """Load all player direction sprites"""
        base_path = "assets/sprites/player/"

        player_sprites = {}
        directions = ["north", "south", "east", "west"]

        for direction in directions:
            filename = f"steve_{direction}.png"
            filepath = os.path.join(base_path, filename)

            sprite = self.load_sprite(filepath)
            if sprite:
                player_sprites[direction] = sprite
            else:
                print(f"Warning: Could not load player sprite for {direction}")

        return player_sprites

    def get_sprite_size(self):
        """Get the size that sprites will be scaled to"""
        return GRID_SIZE, GRID_SIZE


# Global sprite manager instance
sprite_manager = SpriteManager()
