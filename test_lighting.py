#!/usr/bin/env python3
"""
Quick test script to verify lighting system functionality
"""
import pygame
from lighting import LightingSystem, LightSource

def test_lighting_system():
    """Test that lighting system methods work correctly"""
    # Initialize pygame (needed for surfaces)
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    lighting = LightingSystem()
    
    # Test initial state
    assert lighting.get_darkness_level() == 180
    assert 0 <= lighting.get_darkness_percentage() <= 100
    
    # Test darkness adjustment
    initial_darkness = lighting.get_darkness_level()
    lighting.adjust_darkness(20)
    assert lighting.get_darkness_level() == initial_darkness + 20
    
    lighting.adjust_darkness(-40)
    assert lighting.get_darkness_level() == initial_darkness - 20
    
    # Test bounds
    lighting.set_darkness_level(300)  # Should be clamped
    assert lighting.get_darkness_level() <= lighting.max_darkness
    
    lighting.set_darkness_level(-50)  # Should be clamped
    assert lighting.get_darkness_level() >= lighting.min_darkness
    
    # Test light sources
    light = LightSource(10, 10, 100, "test")
    lighting.add_light_source(light)
    assert len(lighting.light_sources) == 1
    
    lighting.remove_light_source(light)
    assert len(lighting.light_sources) == 0
    
    # Test surface creation
    lighting._create_darkness_surface()
    assert lighting.darkness_surface is not None
    
    print("✓ All lighting system tests passed!")

if __name__ == "__main__":
    test_lighting_system()