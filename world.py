import random
import noise
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
        }
        return colors.get(block_type, WHITE)

    def _get_minable(self, block_type):
        minable_blocks = {"wood", "stone", "diamond", "coal"}
        return block_type in minable_blocks

    def _get_mining_difficulty(self, block_type):
        # Mining difficulty in health points (higher = takes longer)
        difficulties = {
            "wood": 3.0,   # 3 seconds with bare hands
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
        }
        return mining_results.get(self.type, None)

    def get_replacement_block(self):
        """Get the block type that should replace this block when mined"""
        replacements = {
            "wood": "grass",    # Wood becomes grass when mined
            "stone": "dirt",    # Stone becomes dirt when mined
            "coal": "dirt",     # Coal becomes dirt when mined
            "diamond": "dirt",  # Diamond becomes dirt when mined
        }
        return replacements.get(self.type, self.type)


class TerrainGenerator:
    """Handles procedural terrain generation using Perlin noise"""
    
    def __init__(self, seed=42):
        self.seed = seed
        
        # Terrain generation parameters (easily adjustable)
        self.terrain_scale = 0.01   # Scale for base terrain noise
        self.feature_scale = 0.05   # Scale for feature placement noise
        self.height_scale = 0.008   # Scale for height variation
        
        # Terrain thresholds for base layer (adjusted to actual noise range)
        self.water_threshold = 0.30   # Water in low areas
        self.sand_threshold = 0.40    # Sand around water
        self.grass_threshold = 0.60   # Most common terrain
        self.stone_threshold = 0.75   # Stone in higher areas
        self.deep_stone_threshold = 1.0  # Deep stone in highest areas
        
        # Feature placement parameters
        self.wood_density = 0.08      # Chance for wood on grass/dirt
        self.coal_density = 0.15      # Chance for coal on stone
        self.lava_density = 0.08      # Chance for lava in deep areas
        self.diamond_density = 0.03   # Chance for diamond in deep areas (rarer)
        self.lava_pool_threshold = 0.5  # Threshold for lava pool formation
        
    def get_base_terrain(self, world_x, world_y):
        """Generate base terrain using multiple noise layers with better distribution"""
        # Use a combination of different frequencies for more variety
        
        # Large-scale terrain features
        large_scale = noise.pnoise1(
            world_x * 0.005,  # Very large features
            octaves=2,
            persistence=0.5,
            lacunarity=2.0,
            base=self.seed
        )
        
        # Medium-scale terrain features  
        medium_scale = noise.pnoise1(
            world_x * 0.02,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100
        )
        
        # Small-scale height variation
        small_scale = noise.pnoise2(
            world_x * 0.1,
            world_y * 0.05,
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200
        )
        
        # Weighted combination
        combined = 0.5 * large_scale + 0.3 * medium_scale + 0.2 * small_scale
        
        # Normalize and enhance distribution
        normalized = (combined + 1) / 2
        
        # Apply contrast curve to ensure full range usage
        # This S-curve helps spread the values more evenly
        x = normalized
        enhanced = 6 * x**5 - 15 * x**4 + 10 * x**3  # Smooth step function
        enhanced = max(0, min(1, enhanced))  # Clamp to [0,1]
        
        # Determine base terrain type
        if enhanced < self.water_threshold:
            return "water"
        elif enhanced < self.sand_threshold:
            return "sand"
        elif enhanced < self.grass_threshold:
            return "grass"
        elif enhanced < self.stone_threshold:
            return "stone"
        else:
            return "stone"  # Deep underground stone
    
    def is_deep_underground(self, world_x, world_y):
        """Check if location is in deep underground area"""
        # Use the same logic as get_base_terrain for consistency
        large_scale = noise.pnoise1(
            world_x * 0.005,
            octaves=2,
            persistence=0.5,
            lacunarity=2.0,
            base=self.seed
        )
        
        medium_scale = noise.pnoise1(
            world_x * 0.02,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100
        )
        
        small_scale = noise.pnoise2(
            world_x * 0.1,
            world_y * 0.05,
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200
        )
        
        combined = 0.5 * large_scale + 0.3 * medium_scale + 0.2 * small_scale
        normalized = (combined + 1) / 2
        
        x = normalized
        enhanced = 6 * x**5 - 15 * x**4 + 10 * x**3
        enhanced = max(0, min(1, enhanced))
        
        return enhanced >= self.stone_threshold
    
    def get_feature_noise(self, world_x, world_y):
        """Generate 2D feature placement noise"""
        return noise.pnoise2(
            world_x * self.feature_scale,
            world_y * self.feature_scale,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 1000  # Different seed for features
        )
    
    def should_place_lava_pool(self, world_x, world_y):
        """Determine if lava should form a pool at this location"""
        if not self.is_deep_underground(world_x, world_y):
            return False
        
        # Use different noise for lava pool formation
        lava_noise = noise.pnoise2(
            world_x * self.feature_scale * 0.5,  # Larger lava pools
            world_y * self.feature_scale * 0.5,
            octaves=2,
            persistence=0.4,
            lacunarity=2.0,
            base=self.seed + 2000
        )
        
        return lava_noise > self.lava_pool_threshold
    
    def generate_block_type(self, world_x, world_y):
        """Generate the final block type for a given coordinate"""
        # Step 1: Get base terrain
        base_terrain = self.get_base_terrain(world_x, world_y)
        
        # Step 2: Check for feature placement
        feature_noise = self.get_feature_noise(world_x, world_y)
        is_deep = self.is_deep_underground(world_x, world_y)
        
        # Seed random generator for consistent results
        random.seed(world_x * 10000 + world_y + self.seed)
        
        # Step 3: Place features based on base terrain and rules
        if base_terrain in ["grass", "dirt"]:
            # Wood can appear on grass or dirt
            if feature_noise > 0.3 and random.random() < self.wood_density:
                return "wood"
            return base_terrain
        
        elif base_terrain == "stone":
            # In deep underground areas, check for rare resources
            if is_deep:
                # Check for lava pools first (higher priority)
                if self.should_place_lava_pool(world_x, world_y):
                    return "lava"
                
                # Check for diamond (very rare)
                if feature_noise > 0.6 and random.random() < self.diamond_density:
                    return "diamond"
                
                # Check for lava (rare)
                if feature_noise > 0.4 and random.random() < self.lava_density:
                    return "lava"
            
            # Coal can appear on any stone
            if feature_noise > 0.2 and random.random() < self.coal_density:
                return "coal"
            
            return "stone"
        
        else:
            # Water, sand - no features
            return base_terrain


class Game:
    def __init__(self, terrain_seed=42):
        self.player = Player()
        self.camera = Camera()
        self.chunks = {}  # Dict to store chunks by (chunk_x, chunk_y)
        self.chunk_size = 16  # Size of each chunk in blocks
        
        # Initialize terrain generator
        self.terrain_generator = TerrainGenerator(seed=terrain_seed)
        
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
        """Generate a chunk using the new noise-based terrain system"""
        chunk = {}
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y
                
                # Use terrain generator to determine block type
                block_type = self.terrain_generator.generate_block_type(world_x, world_y)
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