"""
Base component classes for RF Layout.
"""

from abc import ABC, abstractmethod
import gdspy
import numpy as np

class Component(ABC):
    """Base class for all RF components"""
    
    def __init__(self, name, position, orientation=0):
        self.name = name
        self.position = self._validate_position(position)
        self.orientation = float(orientation)  # degrees
        self.ports = {}  # Dictionary to store port locations
        
    def _validate_position(self, position):
        """Validate and convert position to proper format"""
        if not isinstance(position, (list, tuple, np.ndarray)) or len(position) != 2:
            raise ValueError(f"Position must be a 2D coordinate [x,y], got {position}")
        return [float(position[0]), float(position[1])]
        
    @abstractmethod
    def generate_geometry(self):
        """Generate GDSII geometry for the component"""
        pass
        
    def get_port_position(self, port_name):
        """Get absolute position of a port"""
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} not defined in component {self.name}")
        
        relative_pos = self.ports[port_name]
        if not isinstance(relative_pos, (list, tuple, np.ndarray)) or len(relative_pos) != 2:
            raise ValueError(f"Port position must be a 2D coordinate [x,y], got {relative_pos}")
            
        # Convert to numpy array for rotation
        relative_pos = np.array([float(relative_pos[0]), float(relative_pos[1])])
        
        # Handle rotation based on orientation
        if self.orientation != 0:
            angle = np.radians(self.orientation)
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            relative_pos = np.dot(rot_matrix, relative_pos)
        
        # Calculate absolute position
        return [
            float(self.position[0] + relative_pos[0]), 
            float(self.position[1] + relative_pos[1])
        ]
    
    def get_bounding_box(self):
        """Get the bounding box of the component"""
        # Default implementation - should be overridden by complex components
        # This is a placeholder that assumes the component occupies a 1x1 unit box
        return [
            [self.position[0] - 0.5, self.position[1] - 0.5],
            [self.position[0] + 0.5, self.position[1] + 0.5]
        ]