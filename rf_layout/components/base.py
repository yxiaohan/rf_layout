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
        self.position = position  # [x, y]
        self.orientation = orientation  # degrees
        self.ports = {}  # Dictionary to store port locations
        
    @abstractmethod
    def generate_geometry(self):
        """Generate GDSII geometry for the component"""
        pass
        
    def get_port_position(self, port_name):
        """Get absolute position of a port"""
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} not defined in component {self.name}")
        
        relative_pos = self.ports[port_name]
        
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
            self.position[0] + relative_pos[0], 
            self.position[1] + relative_pos[1]
        ]
    
    def get_bounding_box(self):
        """Get the bounding box of the component"""
        # Default implementation - should be overridden by complex components
        # This is a placeholder that assumes the component occupies a 1x1 unit box
        return [
            [self.position[0] - 0.5, self.position[1] - 0.5],
            [self.position[0] + 0.5, self.position[1] + 0.5]
        ]