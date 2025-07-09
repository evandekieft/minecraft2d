import random
import noise


class TerrainGenerator:
    """Handles procedural terrain generation using Perlin noise"""

    def __init__(self, seed=42):
        self.seed = seed

        # Terrain generation parameters (easily adjustable)
        self.terrain_scale = 0.01  # Scale for base terrain noise
        self.feature_scale = 0.05  # Scale for feature placement noise
        self.height_scale = 0.008  # Scale for height variation

        # Terrain thresholds for base layer (adjusted for 2D noise distribution)
        self.water_threshold = 0.25  # Water in low areas (25% target)
        self.sand_threshold = 0.35  # Sand around water (10% target)
        self.grass_threshold = 0.70  # Most common terrain (35% target)
        self.stone_threshold = 0.84  # Stone in higher areas (14% target)
        self.deep_stone_threshold = 1.0  # Deep stone in highest areas

        # Feature placement parameters (adjusted for target distribution)
        self.wood_density = 0.75  # Chance for wood on grass/dirt (10% target)
        self.coal_density = 0.15  # Chance for coal on stone
        self.lava_density = 0.80  # Chance for lava in deep areas (5% target)
        self.diamond_density = 0.30  # Chance for diamond in deep areas (1% target)
        self.lava_pool_threshold = 0.2  # Threshold for lava pool formation (lower = more pools)

    def get_base_terrain(self, world_x, world_y):
        """Generate base terrain using multiple noise layers with better distribution"""
        # Use a combination of different frequencies for more variety

        # Large-scale terrain features (continents, oceans)
        large_scale = noise.pnoise2(
            world_x * 0.002,  # Very large features
            world_y * 0.002,  # Equal scaling for round features
            octaves=3,
            persistence=0.5,
            lacunarity=2.0,
            base=self.seed,
        )

        # Medium-scale terrain features (biomes, regions)
        medium_scale = noise.pnoise2(
            world_x * 0.01,
            world_y * 0.01,  # Equal scaling for organic shapes
            octaves=4,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100,
        )

        # Small-scale height variation (local details)
        small_scale = noise.pnoise2(
            world_x * 0.05,
            world_y * 0.05,  # Equal scaling for natural variation
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200,
        )

        # Weighted combination
        combined = 0.5 * large_scale + 0.3 * medium_scale + 0.2 * small_scale

        # Normalize to [0,1] range
        normalized = (combined + 1) / 2

        # Stretch the distribution to use full [0,1] range
        # 2D noise has different distribution than 1D noise
        # Adjust for better spread
        min_expected = 0.35
        max_expected = 0.65
        stretched = (normalized - min_expected) / (max_expected - min_expected)
        enhanced = max(0, min(1, stretched))  # Clamp to [0,1]

        # Debug: uncomment to see noise value distribution
        # if world_x % 50 == 0 and world_y % 50 == 0:
        #     print(f"Debug: combined={combined:.3f}, normalized={normalized:.3f}, enhanced={enhanced:.3f}")

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
        large_scale = noise.pnoise2(
            world_x * 0.002,
            world_y * 0.002,
            octaves=3,
            persistence=0.5,
            lacunarity=2.0,
            base=self.seed,
        )

        medium_scale = noise.pnoise2(
            world_x * 0.01,
            world_y * 0.01,
            octaves=4,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100,
        )

        small_scale = noise.pnoise2(
            world_x * 0.05,
            world_y * 0.05,
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200,
        )

        combined = 0.5 * large_scale + 0.3 * medium_scale + 0.2 * small_scale
        normalized = (combined + 1) / 2

        # Stretch the distribution to use full [0,1] range  
        min_expected = 0.35
        max_expected = 0.65
        stretched = (normalized - min_expected) / (max_expected - min_expected)
        enhanced = max(0, min(1, stretched))  # Clamp to [0,1]

        return enhanced >= self.stone_threshold

    def get_feature_noise(self, world_x, world_y):
        """Generate 2D feature placement noise"""
        return noise.pnoise2(
            world_x * self.feature_scale,
            world_y * self.feature_scale,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 1000,  # Different seed for features
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
            base=self.seed + 2000,
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
