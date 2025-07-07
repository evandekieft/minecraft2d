import random
from constants import GREEN, LIGHT_BROWN, DARK_BROWN, BLUE, WHITE
from player import Player
from camera import Camera


class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.walkable = self._get_walkable(block_type)
        self.color = self._get_color(block_type)
    
    def _get_walkable(self, block_type):
        walkable_blocks = {"grass", "dirt", "water"}
        return block_type in walkable_blocks
    
    def _get_color(self, block_type):
        colors = {
            "grass": GREEN,
            "tree": LIGHT_BROWN,
            "dirt": DARK_BROWN,
            "water": BLUE
        }
        return colors.get(block_type, WHITE)


class Game:
    def __init__(self):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks
        
        # Generate initial chunks around player
        self._generate_chunks_around_player()
    
    def _generate_chunks_around_player(self):
        # Generate chunks in a 3x3 area around player
        player_chunk_x = self.player.world_x // self.chunk_size
        player_chunk_y = self.player.world_y // self.chunk_size
        
        for cy in range(player_chunk_y - 1, player_chunk_y + 2):
            for cx in range(player_chunk_x - 1, player_chunk_x + 2):
                if (cx, cy) not in self.chunks:
                    self._generate_chunk(cx, cy)
    
    def _generate_chunk(self, chunk_x, chunk_y):
        # Generate a chunk at the given chunk coordinates
        chunk = {}
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y
                
                # Use world coordinates for consistent random generation
                random.seed(world_x * 1000 + world_y)
                if random.random() < 0.9:
                    chunk[(x, y)] = Block("grass")
                else:
                    chunk[(x, y)] = Block("tree")
        
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