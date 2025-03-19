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
        """Generate geometry primitives for the component"""
        pass
    
    def get_port_position(self, port_name):
        """Get absolute position of a port including rotation"""
        if port_name not in self.ports:
            raise ValueError(f"Port {port_name} not defined in component {self.name}")
            
        # Get relative port position
        rel_pos = self.ports[port_name]
        if not isinstance(rel_pos, (list, tuple, np.ndarray)) or len(rel_pos) != 2:
            raise ValueError(f"Port position must be a 2D coordinate [x,y], got {rel_pos}")
            
        # Convert to numpy array for rotation
        rel_pos = np.array([float(rel_pos[0]), float(rel_pos[1])])
        
        # Rotate relative position if orientation is not 0
        if self.orientation != 0:
            angle = np.radians(-self.orientation)  # Negative angle for clockwise rotation
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            rel_pos = np.dot(rot_matrix, rel_pos)
        
        # Add rotated relative position to component position
        final_pos = [
            self.position[0] + rel_pos[0],
            self.position[1] + rel_pos[1]
        ]
        return final_pos
    
    def get_bounding_box(self):
        """Get the bounding box of the component including rotation"""
        # Default implementation - override in subclasses for more accurate bounds
        size = 1.0  # Default size if not specified by subclass
        corners = [
            [-size/2, -size/2],
            [size/2, -size/2],
            [-size/2, size/2],
            [size/2, size/2]
        ]
        
        # Rotate corners if orientation is not 0
        if self.orientation != 0:
            angle = np.radians(self.orientation)
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            corners = [np.dot(rot_matrix, np.array(corner)) for corner in corners]
        
        # Translate corners to component position
        corners = [[c[0] + self.position[0], c[1] + self.position[1]] for c in corners]
        
        # Calculate bounds
        x_coords = [c[0] for c in corners]
        y_coords = [c[1] for c in corners]
        return [
            [min(x_coords), min(y_coords)],
            [max(x_coords), max(y_coords)]
        ]