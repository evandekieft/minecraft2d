import pygame
from constants import WINDOW_SIZE, GAME_HEIGHT, GRID_SIZE


class LightSource:
    """Represents a light source in the world"""
    def __init__(self, world_x, world_y, radius, light_type="player"):
        self.world_x = world_x
        self.world_y = world_y
        self.radius = radius  # Light radius in pixels
        self.light_type = light_type
        self.enabled = True
    
    def get_screen_position(self, camera):
        """Get the screen position of this light source"""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        # Center the light on the grid cell
        return screen_x + GRID_SIZE // 2, screen_y + GRID_SIZE // 2


class LightingSystem:
    """Manages the lighting overlay and light sources"""
    
    def __init__(self):
        self.darkness_alpha = 180  # Default darkness level (0-255)
        self.min_darkness = 0      # Minimum darkness (full daylight)
        self.max_darkness = 220    # Maximum darkness (very dark night)
        self.light_sources = []    # List of LightSource objects
        
        # Create the darkness surface (will be recreated when needed)
        self.darkness_surface = None
        self._create_darkness_surface()
    
    def _create_darkness_surface(self):
        """Create or recreate the darkness surface"""
        self.darkness_surface = pygame.Surface((WINDOW_SIZE[0], GAME_HEIGHT), pygame.SRCALPHA)
    
    def set_darkness_level(self, alpha):
        """Set the darkness level (0 = full light, 255 = pitch black)"""
        self.darkness_alpha = max(self.min_darkness, min(self.max_darkness, alpha))
    
    def adjust_darkness(self, delta):
        """Adjust darkness level by delta amount"""
        self.set_darkness_level(self.darkness_alpha + delta)
    
    def add_light_source(self, light_source):
        """Add a light source to the system"""
        self.light_sources.append(light_source)
    
    def remove_light_source(self, light_source):
        """Remove a light source from the system"""
        if light_source in self.light_sources:
            self.light_sources.remove(light_source)
    
    def clear_light_sources(self):
        """Remove all light sources"""
        self.light_sources.clear()
    
    def update_player_light(self, player):
        """Update or create the player light source"""
        # Find existing player light
        player_light = None
        for light in self.light_sources:
            if light.light_type == "player":
                player_light = light
                break
        
        if player_light:
            # Update existing player light position
            player_light.world_x = player.world_x
            player_light.world_y = player.world_y
        else:
            # Create new player light
            player_light = LightSource(
                player.world_x, 
                player.world_y, 
                radius=int(4 * GRID_SIZE),  # 4 block radius
                light_type="player"
            )
            self.add_light_source(player_light)
    
    def create_lighting_overlay(self, camera):
        """Create the lighting overlay surface with holes for light sources"""
        # Fill the darkness surface with semi-transparent black
        self.darkness_surface.fill((0, 0, 0, self.darkness_alpha))
        
        # Create holes for each light source
        for light_source in self.light_sources:
            if not light_source.enabled:
                continue
                
            # Get screen position accounting for camera
            screen_x, screen_y = light_source.get_screen_position(camera)
            
            # Only create light hole if the light is visible on screen
            if (-light_source.radius <= screen_x <= WINDOW_SIZE[0] + light_source.radius and
                -light_source.radius <= screen_y <= GAME_HEIGHT + light_source.radius):
                
                # Create a circular light hole
                self._create_light_hole(screen_x, screen_y, light_source.radius)
    
    def _create_light_hole(self, center_x, center_y, radius):
        """Create a circular hole in the darkness surface"""
        # Create a temporary surface for the light circle
        light_diameter = radius * 2
        light_surface = pygame.Surface((light_diameter, light_diameter), pygame.SRCALPHA)
        light_surface.fill((0, 0, 0, 0))  # Fully transparent
        
        # Draw a gradient circle for smooth light falloff
        for r in range(radius, 0, -2):
            # Calculate alpha for smooth falloff (inverted so center is brightest)
            distance_ratio = r / radius
            alpha = int(self.darkness_alpha * (1.0 - distance_ratio))
            
            # Draw circle with decreasing alpha (more transparent toward center)
            pygame.draw.circle(light_surface, (0, 0, 0, alpha), (radius, radius), r)
        
        # Position the light surface
        light_rect = light_surface.get_rect()
        light_rect.center = (center_x, center_y)
        
        # Blend the light hole with the darkness surface
        # This creates the "hole" effect by drawing transparent areas
        self.darkness_surface.blit(light_surface, light_rect, special_flags=pygame.BLEND_RGBA_SUB)
    
    def apply_lighting(self, screen, camera):
        """Apply the lighting effect to the screen"""
        # Only apply lighting if there's some darkness
        if self.darkness_alpha > 0:
            # Create the lighting overlay
            self.create_lighting_overlay(camera)
            
            # Apply the darkness overlay to the screen
            screen.blit(self.darkness_surface, (0, 0))
    
    def get_darkness_level(self):
        """Get current darkness level (0-255)"""
        return self.darkness_alpha
    
    def get_darkness_percentage(self):
        """Get current darkness as percentage (0-100)"""
        return int((self.darkness_alpha / self.max_darkness) * 100)
    
    def is_nighttime(self):
        """Check if it's currently night time (darkness > 50%)"""
        return self.darkness_alpha > (self.max_darkness / 2)


# Global lighting system instance
lighting_system = LightingSystem()