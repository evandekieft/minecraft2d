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

    def handle_keydown(self, key):
        if key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
            if key == K_LEFT:
                self.orientation = "west"
            elif key == K_RIGHT:
                self.orientation = "east"
            elif key == K_UP:
                self.orientation = "north"
            elif key == K_DOWN:
                self.orientation = "south"

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
            self.collect_block(game)

    def update(self, dt):
        # Currently no per-frame updates needed for player
        pass

    def move(self, dx, dy, game):
        new_x = self.world_x + dx
        new_y = self.world_y + dy
        
        # Check if target block is walkable
        target_block = game.get_block(new_x, new_y)
        if target_block and target_block.walkable:
            self.world_x = new_x
            self.world_y = new_y

    def collect_block(self, game):
        # Get block in front of player based on orientation
        dx, dy = 0, 0
        if self.orientation == "west":
            dx = -1
        elif self.orientation == "east":
            dx = 1
        elif self.orientation == "north":
            dy = -1
        elif self.orientation == "south":
            dy = 1
        
        target_x = self.world_x + dx
        target_y = self.world_y + dy
        target_block = game.get_block(target_x, target_y)
        
        if target_block and target_block.type == "tree":
            self.add_to_inventory(target_block.type)

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