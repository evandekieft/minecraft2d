import pygame
import os
from constants import GRID_SIZE


class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.scale_factor = (
            GRID_SIZE // 8
        )  # Scale 8x8 to match grid size (16x16 default)

    def load_sprite(self, path, scale_factor=None):
        """Load a sprite and scale it cleanly (no smoothing for pixel art)"""
        if scale_factor is None:
            scale_factor = self.scale_factor

        if path in self.sprites:
            return self.sprites[path]

        try:
            # Load the original sprite
            original = pygame.image.load(path).convert_alpha()

            # Get original dimensions
            orig_width, orig_height = original.get_size()

            # Calculate new dimensions
            new_width = orig_width * scale_factor
            new_height = orig_height * scale_factor

            # Scale without smoothing to preserve pixel art
            scaled = pygame.transform.scale(original, (new_width, new_height))

            # Cache the sprite
            self.sprites[path] = scaled
            return scaled

        except pygame.error as e:
            print(f"Could not load sprite {path}: {e}")
            return None

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
