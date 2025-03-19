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
        """Generate geometry primitives for the component.
        
        This should return a list of GDSPY geometry primitives (Rectangle, Path, etc.)
        rather than creating a cell directly. The GDSWriter will handle cell creation
        and naming.
        """
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
            # Create rotation matrix for counter-clockwise rotation
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            relative_pos = np.dot(rot_matrix, relative_pos)
        
        # Calculate absolute position by adding the rotated relative position to component position
        return [
            float(self.position[0] + relative_pos[0]),
            float(self.position[1] + relative_pos[1])
        ]
        
    def get_bounding_box(self):
        """Get the bounding box of the component"""
        # Get rotated corner points
        points = []
        bbox = [
            [self.position[0] - 0.5, self.position[1] - 0.5],  # Bottom left
            [self.position[0] + 0.5, self.position[1] - 0.5],  # Bottom right
            [self.position[0] - 0.5, self.position[1] + 0.5],  # Top left
            [self.position[0] + 0.5, self.position[1] + 0.5]   # Top right
        ]
        
        if self.orientation != 0:
            angle = np.radians(self.orientation)
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            
            # Rotate each corner point
            center = np.array(self.position)
            for point in bbox:
                # Translate to origin, rotate, then translate back
                vec = np.array(point) - center
                rotated = np.dot(rot_matrix, vec)
                points.append(rotated + center)
        else:
            points = bbox
            
        # Calculate bounding box of rotated points
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        return [
            [min(x_coords), min(y_coords)],
            [max(x_coords), max(y_coords)]
        ]