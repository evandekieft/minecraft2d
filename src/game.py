from terrain import TerrainGenerator
from block import Block

from player import Player
from camera import Camera


class Game:
    def __init__(self, terrain_seed=42):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks

        # Initialize terrain generator
        self.terrain_generator = TerrainGenerator(seed=terrain_seed)

        # Day/night cycle settings
        self.day_duration = 120.0  # 2 minutes for day (in seconds)
        self.night_duration = 120.0  # 2 minutes for night (in seconds)
        self.cycle_duration = self.day_duration + self.night_duration  # Total cycle: 4 minutes
        
        # Time tracking (starts at noon - full daylight)
        self.time_elapsed = 0.0  # Time elapsed in current cycle
        self.current_time_of_day = 0.0  # 0.0 = noon, 0.5 = midnight, 1.0 = noon again
        
        # Light level (0.0 = pitch black, 1.0 = full daylight)
        self.light_level = 1.0  # Start at full daylight (noon)

        # Generate initial chunks around player
        self._generate_chunks_around_player()
    
    def update_day_cycle(self, dt):
        """Update the day/night cycle and lighting"""
        import math
        from lighting import lighting_system
        
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
