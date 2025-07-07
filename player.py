from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE
from constants import BLUE


class Player:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.color = BLUE
        self.orientation = "north"  # north, south, east, west
        self.inventory = {}  # {block_type: count}
        self.active_slot = 0  # Index of active inventory slot (0-4)
        self.is_mining = False
        self.mining_target = None  # (x, y) coordinates of block being mined
        self.mining_damage_rate = 1.0  # Base mining rate (damage per second)

    def handle_keydown(self, key, game=None):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            if key == K_LEFT:
                self.orientation = "west"
            elif key == K_RIGHT:
                self.orientation = "east"
            elif key == K_UP:
                self.orientation = "north"
            elif key == K_DOWN:
                self.orientation = "south"
        elif key == K_SPACE and game:
            self.start_mining(game)

    def handle_keyup(self, key, game):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            dx, dy = 0, 0
            if self.orientation == "west":
                dx = -1
            elif self.orientation == "east":
                dx = 1
            elif self.orientation == "north":
                dy = -1
            elif self.orientation == "south":
                dy = 1
            self.move(dx, dy, game)
        elif key == K_SPACE:
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