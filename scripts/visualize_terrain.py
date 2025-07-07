#!/usr/bin/env python3
"""
Terrain Visualization Script

This script generates and visualizes the Perlin noise-based terrain
for the 2D Minecraft game. It creates a map showing different block types
with distinct colors, helping to tune terrain generation parameters.

Usage:
    python visualize_terrain.py [--width WIDTH] [--height HEIGHT] [--seed SEED]
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
from world import TerrainGenerator

# Color mapping for visualization (RGB values)
BLOCK_COLORS = {
    "water": (0.0, 0.4, 0.8),        # Blue
    "sand": (0.9, 0.8, 0.6),         # Sandy beige
    "grass": (0.2, 0.8, 0.2),        # Green
    "dirt": (0.4, 0.2, 0.1),         # Brown
    "stone": (0.5, 0.5, 0.5),        # Gray
    "wood": (0.6, 0.4, 0.2),         # Light brown
    "coal": (0.1, 0.1, 0.1),         # Black
    "lava": (1.0, 0.2, 0.0),         # Red
    "diamond": (0.0, 0.8, 1.0),      # Bright blue
}

def generate_terrain_map(width, height, seed=42, center_x=0, center_y=0):
    """Generate a terrain map of the specified size"""
    print(f"Generating {width}x{height} terrain map with seed {seed}...")
    
    # Initialize terrain generator
    terrain_gen = TerrainGenerator(seed=seed)
    
    # Create arrays to store the map data
    terrain_map = np.zeros((height, width), dtype=object)
    color_map = np.zeros((height, width, 3))
    
    # Generate terrain for each position
    for y in range(height):
        for x in range(width):
            # Calculate world coordinates (centered around center_x, center_y)
            world_x = center_x + x - width // 2
            world_y = center_y + y - height // 2
            
            # Generate block type
            block_type = terrain_gen.generate_block_type(world_x, world_y)
            terrain_map[y, x] = block_type
            
            # Map to color
            color_map[y, x] = BLOCK_COLORS.get(block_type, (1.0, 0.0, 1.0))  # Magenta for unknown
    
    return terrain_map, color_map

def print_terrain_stats(terrain_map):
    """Print statistics about the generated terrain"""
    height, width = terrain_map.shape
    total_blocks = height * width
    
    print(f"\nTerrain Statistics ({width}x{height} = {total_blocks} blocks):")
    print("-" * 50)
    
    # Count block types
    block_counts = {}
    for y in range(height):
        for x in range(width):
            block_type = terrain_map[y, x]
            block_counts[block_type] = block_counts.get(block_type, 0) + 1
    
    # Sort by count (descending)
    sorted_blocks = sorted(block_counts.items(), key=lambda x: x[1], reverse=True)
    
    for block_type, count in sorted_blocks:
        percentage = (count / total_blocks) * 100
        print(f"{block_type:>8}: {count:>6} blocks ({percentage:5.1f}%)")

def visualize_terrain(terrain_map, color_map, title="Terrain Map", save_path=None):
    """Create and display a visualization of the terrain"""
    height, width = terrain_map.shape
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Display the terrain
    ax.imshow(color_map, origin='upper', interpolation='nearest')
    
    # Customize the plot
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3, linewidth=0.5)
    
    # Create legend
    legend_elements = []
    for block_type, color in BLOCK_COLORS.items():
        if block_type in [terrain_map[y, x] for y in range(height) for x in range(width)]:
            legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, label=block_type.title()))
    
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Map saved to: {save_path}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to handle command line arguments and generate visualization"""
    parser = argparse.ArgumentParser(description="Visualize Perlin noise terrain generation")
    parser.add_argument("--width", type=int, default=200, help="Map width in blocks (default: 200)")
    parser.add_argument("--height", type=int, default=150, help="Map height in blocks (default: 150)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for generation (default: 42)")
    parser.add_argument("--center-x", type=int, default=0, help="Center X coordinate (default: 0)")
    parser.add_argument("--center-y", type=int, default=0, help="Center Y coordinate (default: 0)")
    parser.add_argument("--save", type=str, help="Save map to file (e.g., terrain_map.png)")
    parser.add_argument("--no-display", action="store_true", help="Don't display the map (useful with --save)")
    
    args = parser.parse_args()
    
    # Generate terrain map
    terrain_map, color_map = generate_terrain_map(
        width=args.width,
        height=args.height,
        seed=args.seed,
        center_x=args.center_x,
        center_y=args.center_y
    )
    
    # Print statistics
    print_terrain_stats(terrain_map)
    
    # Create visualization
    title = f"Terrain Map (Seed: {args.seed}, Size: {args.width}x{args.height})"
    
    if not args.no_display:
        visualize_terrain(terrain_map, color_map, title=title, save_path=args.save)
    elif args.save:
        # Save without displaying
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        visualize_terrain(terrain_map, color_map, title=title, save_path=args.save)

if __name__ == "__main__":
    main()