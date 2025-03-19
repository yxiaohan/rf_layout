"""
Passive component implementations for RF Layout.
"""

import gdspy
import numpy as np
from .base import Component

class Inductor(Component):
    """Inductor component implementation"""
    
    def __init__(self, name, position, value, turns, width, spacing, layer="metal5", orientation=0):
        super().__init__(name, position, orientation)
        
        # Validate parameters
        if value <= 0:
            raise ValueError(f"Inductor value must be positive, got {value}")
        if turns <= 0:
            raise ValueError(f"Number of turns must be positive, got {turns}")
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if spacing <= 0:
            raise ValueError(f"Spacing must be positive, got {spacing}")
            
        self.value = value  # in nH
        self.turns = turns
        self.width = width  # track width
        self.spacing = spacing  # spacing between turns
        self.layer = layer
        
        # Calculate the size of the inductor based on parameters
        self._calculate_size()
        
        # Define ports
        self._calculate_ports()
    
    def _calculate_size(self):
        """Calculate the physical size of the inductor"""
        # Simple approximation - in a real design this would be more complex
        # For a square spiral inductor:
        self.outer_size = 2 * self.turns * (self.width + self.spacing)
    
    def _calculate_ports(self):
        """Calculate port positions for the inductor"""
        # For a spiral inductor, one port is at the outside, one at the center
        self.ports["port1"] = [-self.outer_size/2, 0]  # Outside port
        self.ports["port2"] = [0, 0]  # Center port
    
    def generate_geometry(self):
        """Generate GDSII geometry for the inductor"""
        # Create a new GDSII cell for this inductor
        cell = gdspy.Cell(self.name)
        
        # Create a simplified spiral inductor using polylines
        points = []
        
        # Generate a square spiral
        size = self.outer_size
        for i in range(int(self.turns * 4)):
            angle = i * np.pi / 2
            x = size/2 * np.cos(angle)
            y = size/2 * np.sin(angle)
            points.append((self.position[0] + x, self.position[1] + y))
            size -= self.spacing + self.width
            
        # Create the spiral path
        spiral = gdspy.FlexPath(
            points, 
            self.width, 
            layer=5,  # Use numeric layer, will be mapped by GDSWriter
            corners="round"
        )
        cell.add(spiral)
        
        return cell
    
    def get_bounding_box(self):
        """Get the bounding box of the inductor"""
        half_size = self.outer_size / 2
        return [
            [self.position[0] - half_size, self.position[1] - half_size],
            [self.position[0] + half_size, self.position[1] + half_size]
        ]


class Capacitor(Component):
    """Capacitor component implementation"""
    
    def __init__(self, name, position, value, width, length, top_layer="metal5", bot_layer="metal4", orientation=0):
        super().__init__(name, position, orientation)
        
        # Validate parameters
        if value <= 0:
            raise ValueError(f"Capacitor value must be positive, got {value}")
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if length <= 0:
            raise ValueError(f"Length must be positive, got {length}")
            
        self.value = value  # in pF
        self.width = width
        self.length = length
        self.top_layer = top_layer
        self.bot_layer = bot_layer
        
        # Define ports
        self._calculate_ports()
    
    def _calculate_ports(self):
        """Calculate port positions for the capacitor"""
        # For a simple parallel plate capacitor
        self.ports["port1"] = [0, self.length/2]  # Top connection (was "top")
        self.ports["port2"] = [0, -self.length/2]  # Bottom connection (was "bottom")
    
    def generate_geometry(self):
        """Generate GDSII geometry for the capacitor"""
        cell = gdspy.Cell(self.name)
        
        # Create top plate
        top_plate = gdspy.Rectangle(
            (self.position[0] - self.width/2, self.position[1] - self.length/2),
            (self.position[0] + self.width/2, self.position[1] + self.length/2),
            layer=5  # Use numeric layer for top metal
        )
        cell.add(top_plate)
        
        # Create bottom plate (slightly smaller to visualize the difference)
        margin = self.width * 0.1
        bot_plate = gdspy.Rectangle(
            (self.position[0] - self.width/2 + margin, self.position[1] - self.length/2 + margin),
            (self.position[0] + self.width/2 - margin, self.position[1] + self.length/2 - margin),
            layer=4  # Use numeric layer for bottom metal
        )
        cell.add(bot_plate)
        
        return cell
    
    def get_bounding_box(self):
        """Get the bounding box of the capacitor"""
        return [
            [self.position[0] - self.width/2, self.position[1] - self.length/2],
            [self.position[0] + self.width/2, self.position[1] + self.length/2]
        ]


class Resistor(Component):
    """Resistor component implementation"""
    
    def __init__(self, name, position, value, width, length, layer="metal1", orientation=0):
        super().__init__(name, position, orientation)
        
        # Validate parameters
        if value <= 0:
            raise ValueError(f"Resistance value must be positive, got {value}")
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if length <= 0:
            raise ValueError(f"Length must be positive, got {length}")
            
        self.value = value  # in Ohms
        self.width = width
        self.length = length
        self.layer = layer
        
        # Define ports
        self._calculate_ports()
    
    def _calculate_ports(self):
        """Calculate port positions for the resistor"""
        self.ports["port1"] = [-self.length/2, 0]
        self.ports["port2"] = [self.length/2, 0]
    
    def generate_geometry(self):
        """Generate geometry primitives for the resistor"""
        # Create a cell for this component
        cell = gdspy.Cell(self.name)
        
        # Create resistor body
        path = gdspy.FlexPath(
            [(self.position[0] - self.length/2, self.position[1]),
             (self.position[0] + self.length/2, self.position[1])],
            self.width,
            layer=1  # Metal1 layer
        )
        cell.add(path)
        
        # Add contacts at ends
        contact_size = self.width * 1.5
        for x in [self.position[0] - self.length/2, self.position[0] + self.length/2]:
            contact = gdspy.Rectangle(
                (x - contact_size/2, self.position[1] - contact_size/2),
                (x + contact_size/2, self.position[1] + contact_size/2),
                layer=2  # Contact layer
            )
            cell.add(contact)
            
        return cell
        
    def get_bounding_box(self):
        """Get the bounding box of the resistor"""
        contact_size = self.width * 1.5
        return [
            [self.position[0] - self.length/2 - contact_size/2, 
             self.position[1] - contact_size/2],
            [self.position[0] + self.length/2 + contact_size/2, 
             self.position[1] + contact_size/2]
        ]