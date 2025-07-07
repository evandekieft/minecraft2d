import random
from constants import (GREEN, LIGHT_BROWN, DARK_BROWN, BLUE, WHITE, BRIGHT_BLUE, 
                      RED, BLACK, SAND_COLOR, GRAY)
from player import Player
from camera import Camera


class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.walkable = self._get_walkable(block_type)
        self.color = self._get_color(block_type)
        self.minable = self._get_minable(block_type)
        self.mining_difficulty = self._get_mining_difficulty(block_type)
        self.max_health = self.mining_difficulty
        self.current_health = self.max_health
    
    def _get_walkable(self, block_type):
        walkable_blocks = {"grass", "dirt", "sand"}
        return block_type in walkable_blocks
    
    def _get_color(self, block_type):
        colors = {
            "grass": GREEN,
            "dirt": DARK_BROWN,
            "sand": SAND_COLOR,
            "wood": LIGHT_BROWN,
            "stone": GRAY,
            "coal": BLACK,
            "lava": RED,
            "diamond": BRIGHT_BLUE,
            "water": BLUE,
            # Legacy support
            "tree": LIGHT_BROWN,  # Trees render as wood blocks
        }
        return colors.get(block_type, WHITE)

    def _get_minable(self, block_type):
        minable_blocks = {"wood", "stone", "diamond", "coal", "tree"}  # tree for legacy
        return block_type in minable_blocks

    def _get_mining_difficulty(self, block_type):
        # Mining difficulty in health points (higher = takes longer)
        difficulties = {
            "wood": 3.0,   # 3 seconds with bare hands
            "tree": 3.0,   # Legacy support
            "stone": 5.0,  # 5 seconds with bare hands  
            "coal": 4.0,   # 4 seconds with bare hands
            "diamond": 8.0, # 8 seconds with bare hands (very hard)
        }
        return difficulties.get(block_type, 1.0)

    def reset_health(self):
        """Reset block health to maximum (when mining is interrupted)"""
        self.current_health = self.max_health

    def take_damage(self, damage):
        """Apply mining damage to the block. Returns True if block is destroyed."""
        if not self.minable:
            return False
        
        self.current_health -= damage
        return self.current_health <= 0

    def get_mining_result(self):
        """Get the item(s) that should be added to inventory when this block is mined"""
        mining_results = {
            "wood": "wood",
            "stone": "stone", 
            "coal": "coal",
            "diamond": "diamond",
            "tree": "wood",  # Legacy support
        }
        return mining_results.get(self.type, None)

    def get_replacement_block(self):
        """Get the block type that should replace this block when mined"""
        replacements = {
            "wood": "grass",    # Wood becomes grass when mined
            "stone": "dirt",    # Stone becomes dirt when mined
            "coal": "stone",    # Coal becomes stone when mined (coal is in stone)
            "diamond": "stone", # Diamond becomes stone when mined
            "tree": "dirt",     # Legacy support
        }
        return replacements.get(self.type, self.type)


class Game:
    def __init__(self):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks
        
        # Generate initial chunks around player
        self._generate_chunks_around_player()
    
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