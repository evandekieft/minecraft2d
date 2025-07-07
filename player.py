from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
from constants import BLUE


class Player:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.color = BLUE
        self.orientation = "north"  # north, south, east, west

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