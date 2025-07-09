#!/usr/bin/env python3
"""
Example: Advanced Terrain Tuning

This example shows how to use the advanced terrain analyzer
to easily tune terrain parameters and add new block types.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from terrain_config import TerrainConfig, TerrainLayer, FeatureRule
from terrain_generator_v2 import ConfigurableTerrainGenerator
from terrain_analyzer import TerrainAnalyzer


def create_ice_world_config():
    """Create an ice world terrain configuration"""
    
    config = TerrainConfig()
    
    # Ice world base terrain
    config.base_layers = [
        TerrainLayer("ice", 0.30, 40.0, "Frozen ice sheets"),
        TerrainLayer("snow", 0.60, 30.0, "Snow-covered ground"),
        TerrainLayer("stone", 0.80, 20.0, "Rocky mountains"),
        TerrainLayer("obsidian", 0.95, 10.0, "Volcanic rock"),
    ]
    
    # Ice world features
    config.feature_rules = [
        FeatureRule("ice_crystal", ["ice"], 0.30, 0.4, False, 8.0, "Ice crystals"),
        FeatureRule("coal", ["stone"], 0.25, 0.3, False, 5.0, "Coal deposits"),
        FeatureRule("lava", ["obsidian"], 0.60, 0.2, True, 3.0, "Geothermal vents"),
        FeatureRule("diamond", ["obsidian"], 0.20, 0.7, True, 1.0, "Rare diamonds"),
    ]
    
    return config


def demonstrate_terrain_tuning():
    """Demonstrate automatic terrain tuning"""
    
    print("TERRAIN TUNING DEMONSTRATION")
    print("=" * 50)
    
    # Create ice world configuration
    config = create_ice_world_config()
    print("Created ice world configuration")
    
    # Create analyzer
    analyzer = TerrainAnalyzer(config)
    
    # Show initial configuration
    print("\nInitial Configuration:")
    print("-" * 30)
    target_dist = config.get_target_distribution()
    for block_type, percentage in sorted(target_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {block_type}: {percentage:.1f}%")
    
    # Analyze initial distribution
    print("\nAnalyzing initial distribution...")
    result = analyzer.analyze_distribution(width=100, height=100, seed=42)
    
    print("\nInitial Results:")
    analyzer.compare_to_target(result['stats'])
    
    # Auto-tune the parameters
    print("\n" + "=" * 50)
    print("AUTO-TUNING TERRAIN PARAMETERS")
    print("=" * 50)
    
    final_error = analyzer.auto_tune(
        max_iterations=5,
        target_error=8.0,
        width=100,
        height=100,
        seed=42
    )
    
    print(f"\nFinal tuning error: {final_error:.1f}%")
    
    # Show final configuration
    print("\nFinal Configuration:")
    print("-" * 30)
    for layer in config.base_layers:
        print(f"  {layer.name}: threshold={layer.threshold:.3f}, target={layer.target_percentage:.1f}%")


def show_easy_block_addition():
    """Show how easy it is to add new block types"""
    
    print("\n" + "=" * 50)
    print("ADDING NEW BLOCK TYPES")
    print("=" * 50)
    
    # Start with default config
    config = TerrainConfig()
    
    print("Original block types:")
    for layer in config.base_layers:
        print(f"  Base: {layer.name}")
    for rule in config.feature_rules:
        print(f"  Feature: {rule.name}")
    
    # Add new block types
    print("\nAdding new block types...")
    
    # Add new base terrain: swamp
    config.base_layers.insert(1, TerrainLayer("swamp", 0.30, 8.0, "Murky swampland"))
    
    # Adjust other thresholds
    config.base_layers[2].threshold = 0.40  # sand
    config.base_layers[3].threshold = 0.75  # grass
    config.base_layers[4].threshold = 0.88  # stone
    
    # Add new features
    config.feature_rules.extend([
        FeatureRule("mushroom", ["swamp"], 0.40, 0.3, False, 3.0, "Swamp mushrooms"),
        FeatureRule("vine", ["grass"], 0.20, 0.6, False, 2.0, "Hanging vines"),
        FeatureRule("crystal", ["stone"], 0.15, 0.5, True, 1.5, "Magical crystals"),
    ])
    
    print("New block types added!")
    print("Updated configuration:")
    for layer in config.base_layers:
        print(f"  Base: {layer.name} (threshold: {layer.threshold:.3f})")
    for rule in config.feature_rules:
        print(f"  Feature: {rule.name} (chance: {rule.spawn_chance:.2f})")
    
    # Validate the new configuration
    issues = config.validate_configuration()
    if issues:
        print(f"\n❌ Configuration issues: {issues}")
    else:
        print("\n✅ Configuration is valid!")
        
        # Test generation
        generator = ConfigurableTerrainGenerator(config, seed=42)
        
        print("\nTesting generation with new block types...")
        sample_blocks = {}
        
        for y in range(20):
            for x in range(20):
                block_type = generator.generate_block_type(x, y)
                sample_blocks[block_type] = sample_blocks.get(block_type, 0) + 1
        
        print("Sample results (20x20):")
        total = sum(sample_blocks.values())
        for block_type, count in sorted(sample_blocks.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"  {block_type}: {count} blocks ({percentage:.1f}%)")


if __name__ == "__main__":
    demonstrate_terrain_tuning()
    show_easy_block_addition()