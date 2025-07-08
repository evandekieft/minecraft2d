from pygame.locals import K_w, K_a, K_s, K_d, K_SPACE
from constants import BLUE
from sprites import sprite_manager


class Player:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.color = BLUE  # Fallback color if sprites fail to load
        self.orientation = "north"  # north, south, east, west
        self.inventory = {}  # {block_type: count}
        self.active_slot = 0  # Index of active inventory slot (0-4)
        self.is_mining = False
        self.mining_target = None  # (x, y) coordinates of block being mined
        self.mining_damage_rate = 1.0  # Base mining rate (damage per second)
        
        # Sprites will be loaded after pygame display is initialized
        self.sprites = {}
        self.has_sprites = False

    def handle_keydown(self, key, game=None):
        dx, dy = 0, 0
        moved = False
        
        if key == K_a:
            self.orientation = "west"
            dx = -1
            moved = True
        elif key == K_d:
            self.orientation = "east"
            dx = 1
            moved = True
        elif key == K_w:
            self.orientation = "north"
            dy = -1
            moved = True
        elif key == K_s:
            self.orientation = "south"
            dy = 1
            moved = True
        elif key == K_SPACE and game:
            self.start_mining(game)
            return
            
        if moved and game:
            self.move(dx, dy, game)

    def handle_keyup(self, key, game):
        if key == K_SPACE:
            self.stop_mining(game)

    def update(self, dt, game=None):
        # Handle continuous mining
        if self.is_mining and game and self.mining_target:
            self.process_mining(dt, game)

    def move(self, dx, dy, game):
        new_x = self.world_x + dx
        new_y = self.world_y + dy
        
        # Check if target block is walkable
        target_block = game.get_block(new_x, new_y)
        if target_block and target_block.walkable:
            self.world_x = new_x
            self.world_y = new_y
            # Stop mining if player moves
            if self.is_mining:
                self.stop_mining(game)

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
        
        if target_block and target_block.minable:
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
        
        if not target_block or not target_block.minable:
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
        mining_result = target_block.get_mining_result()
        if mining_result:
            self.add_to_inventory(mining_result)
        
        # Replace the block
        replacement_type = target_block.get_replacement_block()
        game.replace_block(target_x, target_y, replacement_type)
        
        # Stop mining
        self.is_mining = False
        self.mining_target = None

    def add_to_inventory(self, block_type):
        if block_type in self.inventory:
            self.inventory[block_type] += 1
        else:
            self.inventory[block_type] = 1

    def get_top_inventory_items(self, count=5):
        # Get top N items by count
        sorted_items = sorted(self.inventory.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:count]

    def get_active_block_type(self):
        # Get the block type in the active slot
        top_items = self.get_top_inventory_items()
        if 0 <= self.active_slot < len(top_items):
            return top_items[self.active_slot][0]
        return None

    def load_sprites_if_needed(self):
        """Load sprites if not already loaded (after pygame display is initialized)"""
        if not self.has_sprites:
            self.sprites = sprite_manager.load_player_sprites()
            self.has_sprites = len(self.sprites) == 4

    def get_current_sprite(self):
        """Get the sprite for the current orientation, or None if using fallback color"""
        self.load_sprites_if_needed()
        if self.has_sprites and self.orientation in self.sprites:
            return self.sprites[self.orientation]
        return None