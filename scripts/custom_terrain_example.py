#!/usr/bin/env python3
"""
Example: Custom Terrain Configuration

This example shows how easy it is to add new block types and adjust
terrain distribution using the configuration system.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from terrain_config import TerrainConfig, TerrainLayer, FeatureRule
from terrain_generator_v2 import ConfigurableTerrainGenerator


def create_fantasy_terrain():
    """Create a fantasy-themed terrain configuration"""
    
    config = TerrainConfig()
    
    # Add new base terrain types
    config.base_layers = [
        TerrainLayer("water", 0.20, 20.0, "Mystical waters"),
        TerrainLayer("sand", 0.30, 8.0, "Desert sands"),
        TerrainLayer("grass", 0.60, 30.0, "Enchanted grasslands"),
        TerrainLayer("stone", 0.75, 20.0, "Rocky mountains"),
        TerrainLayer("obsidian", 0.90, 2.0, "Volcanic obsidian"),  # New!
    ]
    
    # Add fantasy features
    config.feature_rules = [
        FeatureRule("wood", ["grass"], 0.40, 0.3, False, 8.0, "Ancient trees"),
        FeatureRule("mushroom", ["grass"], 0.15, 0.7, False, 3.0, "Magic mushrooms"),  # New!
        FeatureRule("crystal", ["stone"], 0.25, 0.6, False, 2.0, "Glowing crystals"),  # New!
        FeatureRule("gold", ["stone"], 0.20, 0.5, True, 1.5, "Precious gold"),  # New!
        FeatureRule("lava", ["obsidian"], 0.70, 0.2, True, 3.0, "Molten lava"),
        FeatureRule("diamond", ["obsidian"], 0.40, 0.8, True, 0.5, "Rare diamonds"),
    ]
    
    return config


def create_modern_terrain():
    """Create a modern/urban terrain configuration"""
    
    config = TerrainConfig()
    
    # Urban-themed base terrain
    config.base_layers = [
        TerrainLayer("water", 0.15, 15.0, "Rivers and lakes"),
        TerrainLayer("concrete", 0.40, 25.0, "Urban concrete"),  # New!
        TerrainLayer("grass", 0.70, 35.0, "Parks and lawns"),
        TerrainLayer("stone", 0.85, 20.0, "Building foundations"),
        TerrainLayer("metal", 0.95, 5.0, "Industrial metal"),  # New!
    ]
    
    # Urban features
    config.feature_rules = [
        FeatureRule("tree", ["grass"], 0.60, 0.4, False, 12.0, "City trees"),
        FeatureRule("building", ["concrete"], 0.30, 0.5, False, 8.0, "Buildings"),  # New!
        FeatureRule("pipe", ["stone"], 0.40, 0.3, True, 5.0, "Underground pipes"),  # New!
        FeatureRule("wire", ["metal"], 0.50, 0.2, False, 3.0, "Electrical wires"),  # New!
    ]
    
    return config


def demonstrate_terrain_configs():
    """Demonstrate different terrain configurations"""
    
    configs = {
        "Fantasy": create_fantasy_terrain(),
        "Modern": create_modern_terrain(),
        "Default": TerrainConfig()  # Original configuration
    }
    
    print("TERRAIN CONFIGURATION EXAMPLES")
    print("=" * 50)
    
    for name, config in configs.items():
        print(f"\n{name} Configuration:")
        print("-" * 30)
        
        # Validate configuration
        issues = config.validate_configuration()
        if issues:
            print(f"❌ Configuration issues: {issues}")
            continue
        
        print("✅ Configuration valid")
        
        # Show target distribution
        target_dist = config.get_target_distribution()
        print(f"Target distribution ({len(target_dist)} block types):")
        for block_type, percentage in sorted(target_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"  {block_type}: {percentage:.1f}%")
        
        # Create generator and show summary
        generator = ConfigurableTerrainGenerator(config, seed=42)
        summary = generator.get_configuration_summary()
        print(f"Generator summary: {summary['base_layers']} base layers, {summary['feature_rules']} feature rules")


def quick_test_generation():
    """Quick test of terrain generation with custom config"""
    
    print("\n" + "=" * 50)
    print("QUICK GENERATION TEST")
    print("=" * 50)
    
    # Create fantasy terrain
    config = create_fantasy_terrain()
    generator = ConfigurableTerrainGenerator(config, seed=42)
    
    # Generate a small sample
    print("Generating 10x10 sample with fantasy terrain...")
    sample_blocks = {}
    
    for y in range(10):
        for x in range(10):
            block_type = generator.generate_block_type(x, y)
            sample_blocks[block_type] = sample_blocks.get(block_type, 0) + 1
    
    print("Sample results:")
    total = sum(sample_blocks.values())
    for block_type, count in sorted(sample_blocks.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"  {block_type}: {count} blocks ({percentage:.1f}%)")


if __name__ == "__main__":
    demonstrate_terrain_configs()
    quick_test_generation()