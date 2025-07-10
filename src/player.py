from pygame.locals import (
    K_w,
    K_a,
    K_s,
    K_d,
    K_SPACE,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)
from sprites import sprite_manager
from inventory import Inventory
from block_type import BlockType
import pygame
import os


class Player:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.orientation = "south"  # north, south, east, west
        self.inventory: Inventory = Inventory()
        self.is_mining = False
        self.mining_target = None  # (x, y) coordinates of block being mined
        self.mining_damage_rate = 1.0  # Base mining rate (damage per second)
        self.just_finished_mining = (
            False  # Prevent immediate block placement after mining
        )

        # Sprites will be loaded after pygame display is initialized
        self.sprites = {}

        # Movement system
        self.movement_speed = 6.0  # blocks per second
        self.pressed_keys = set()  # Track currently pressed keys
        self.movement_timer = 0.0  # Accumulator for movement timing
        self.move_interval = 1.0 / self.movement_speed  # Time between moves

    def handle_keydown(self, key, game=None):
        # Handle movement keys (both WASD and arrow keys)
        if key in [K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            self.pressed_keys.add(key)
            # Handle immediate orientation change if needed
            target_orientation = None
            if key == K_a or key == K_LEFT:
                target_orientation = "west"
            elif key == K_d or key == K_RIGHT:
                target_orientation = "east"
            elif key == K_w or key == K_UP:
                target_orientation = "north"
            elif key == K_s or key == K_DOWN:
                target_orientation = "south"

            if target_orientation and self.orientation != target_orientation:
                self.orientation = target_orientation
                # Reset movement timing when changing orientation
                self.movement_timer = 0.0
        elif key == K_SPACE and game:
            self.start_mining(game)
            return
        elif key == K_1:
            self.set_active_slot(0)
        elif key == K_2:
            self.set_active_slot(1)
        elif key == K_3:
            self.set_active_slot(2)
        elif key == K_4:
            self.set_active_slot(3)
        elif key == K_5:
            self.set_active_slot(4)

    def handle_keyup(self, key, game):
        # Handle movement keys (both WASD and arrow keys)
        if key in [K_w, K_a, K_s, K_d, K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            self.pressed_keys.discard(key)
        elif key == K_SPACE:
            if self.is_mining:
                self.stop_mining(game)
            elif not self.just_finished_mining:
                self.place_block(game)
            # Reset the flag after handling
            self.just_finished_mining = False

    def update(self, dt, game=None):
        # Handle continuous movement
        if self.pressed_keys and game:
            self.process_movement(dt, game)

        # Handle continuous mining
        if self.is_mining and game and self.mining_target:
            self.process_mining(dt, game)

    def process_movement(self, dt, game):
        """Process continuous movement based on held keys"""
        # Accumulate time
        self.movement_timer += dt

        # Check if enough time has passed since last move
        if self.movement_timer < self.move_interval:
            return

        # Determine movement direction based on pressed keys
        dx, dy = 0, 0
        target_orientation = None

        # Priority: most recent key press determines direction
        # Check keys in order of typical priority (check both WASD and arrow keys)
        if K_w in self.pressed_keys or K_UP in self.pressed_keys:
            target_orientation = "north"
            dy = -1
        elif K_s in self.pressed_keys or K_DOWN in self.pressed_keys:
            target_orientation = "south"
            dy = 1
        elif K_a in self.pressed_keys or K_LEFT in self.pressed_keys:
            target_orientation = "west"
            dx = -1
        elif K_d in self.pressed_keys or K_RIGHT in self.pressed_keys:
            target_orientation = "east"
            dx = 1

        # Move if we have a direction and are facing the right way
        if target_orientation and self.orientation == target_orientation:
            if self.move(dx, dy, game):
                self.movement_timer = 0.0  # Reset timer after successful move

    def move(self, dx, dy, game):
        new_x = self.world_x + dx
        new_y = self.world_y + dy

        # Check if target block is walkable
        target_block = game.get_block(new_x, new_y)
        if target_block and target_block.type.walkable:
            self.world_x = new_x
            self.world_y = new_y
            # Stop mining if player moves
            if self.is_mining:
                self.stop_mining(game)
            return True
        return False

    def get_target_position(self):
        """Get the position of the block the player is facing"""
        dx, dy = 0, 0
        if self.orientation == "west":
            dx = -1
        elif self.orientation == "east":
            dx = 1
        elif self.orientation == "north":
            dy = -1
        elif self.orientation == "south":
            dy = 1

        return self.world_x + dx, self.world_y + dy

    def start_mining(self, game):
        """Start mining the block the player is facing"""
        target_x, target_y = self.get_target_position()
        target_block = game.get_block(target_x, target_y)

        if target_block and target_block.type.minable:
            self.is_mining = True
            self.mining_target = (target_x, target_y)

    def stop_mining(self, game):
        """Stop mining and reset block health"""
        if self.is_mining and self.mining_target and game:
            target_x, target_y = self.mining_target
            target_block = game.get_block(target_x, target_y)
            if target_block:
                target_block.reset_health()

        self.is_mining = False
        self.mining_target = None

    def process_mining(self, dt, game):
        """Process mining damage over time"""
        if not self.mining_target:
            return

        target_x, target_y = self.mining_target
        target_block = game.get_block(target_x, target_y)

        if not target_block or not target_block.type.minable:
            self.stop_mining(game)
            return

        # Calculate mining damage this frame
        damage = self.mining_damage_rate * dt

        # Apply damage to block
        if target_block.take_damage(damage):
            # Block is destroyed
            self.complete_mining(game, target_x, target_y, target_block)

    def complete_mining(self, game, target_x, target_y, target_block):
        """Complete the mining process - add items to inventory and replace block"""
        # Add mined item to inventory
        mining_result = target_block.type.mining_result
        if mining_result:
            self.add_to_inventory(mining_result)

        # Replace the block
        replacement_type = target_block.type.replacement_block
        game.replace_block(target_x, target_y, replacement_type)

        # Stop mining and set flag to prevent immediate placement
        self.is_mining = False
        self.mining_target = None
        self.just_finished_mining = True

    def add_to_inventory(self, block_type: BlockType):
        self.inventory.add(block_type)

    def get_top_inventory_items(self, count=5):
        return self.inventory.get_top_inventory_items(count)

    def get_active_block_type(self):
        return self.inventory.get_active_block_type()

    def load_sprites_if_needed(self):
        """Load sprites if not already loaded (after pygame display is initialized)"""
        if not self.sprites:
            base_path = "assets/sprites/player/"
            directions = ["north", "south", "east", "west"]

            for direction in directions:
                filename = f"steve_{direction}.png"
                filepath = os.path.join(base_path, filename)

                sprite = sprite_manager.load_sprite(filepath)
                self.sprites[direction] = sprite

    def get_current_sprite(self) -> pygame.Surface:
        """Get the sprite for the current orientation, or None if using fallback color"""
        self.load_sprites_if_needed()
        return self.sprites[self.orientation]

    def set_active_slot(self, slot: int):
        self.inventory.set_active_slot(slot)

    def place_block(self, game):
        """Place a block at the target position and remove it from inventory"""
        target_x, target_y = self.get_target_position()
        block_type = self.get_active_block_type()
        target_block = game.get_block(target_x, target_y)

        if block_type and target_block and target_block.type.walkable:
            # Check if we have the block in inventory
            if self.inventory.has_block_type(block_type):
                # Place the block
                game.replace_block(target_x, target_y, block_type)
                # Remove one from inventory
                self.inventory.remove(block_type)
