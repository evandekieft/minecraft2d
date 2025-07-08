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

        # Terrain thresholds for base layer (adjusted to actual noise range)
        self.water_threshold = 0.30  # Water in low areas
        self.sand_threshold = 0.40  # Sand around water
        self.grass_threshold = 0.60  # Most common terrain
        self.stone_threshold = 0.75  # Stone in higher areas
        self.deep_stone_threshold = 1.0  # Deep stone in highest areas

        # Feature placement parameters
        self.wood_density = 0.08  # Chance for wood on grass/dirt
        self.coal_density = 0.15  # Chance for coal on stone
        self.lava_density = 0.08  # Chance for lava in deep areas
        self.diamond_density = 0.03  # Chance for diamond in deep areas (rarer)
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
            base=self.seed,
        )

        # Medium-scale terrain features
        medium_scale = noise.pnoise1(
            world_x * 0.02,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100,
        )

        # Small-scale height variation
        small_scale = noise.pnoise2(
            world_x * 0.1,
            world_y * 0.05,
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200,
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
            world_x * 0.005, octaves=2, persistence=0.5, lacunarity=2.0, base=self.seed
        )

        medium_scale = noise.pnoise1(
            world_x * 0.02,
            octaves=3,
            persistence=0.6,
            lacunarity=2.0,
            base=self.seed + 100,
        )

        small_scale = noise.pnoise2(
            world_x * 0.1,
            world_y * 0.05,
            octaves=2,
            persistence=0.3,
            lacunarity=2.0,
            base=self.seed + 200,
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
