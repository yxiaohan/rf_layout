"""
Transistor component implementations for RF Layout.
"""

import gdspy
import numpy as np
from .base import Component

class Transistor(Component):
    """MOSFET transistor component"""
    
    def __init__(self, name, position, width, length, fingers=1, orientation=0, layer="active"):
        super().__init__(name, position, orientation)
        
        # Validate parameters
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if length <= 0:
            raise ValueError(f"Length must be positive, got {length}")
        if fingers < 1:
            raise ValueError(f"Number of fingers must be at least 1, got {fingers}")
            
        self.width = width
        self.length = length
        self.fingers = fingers
        self.layer = layer
        
        # Define ports
        self._calculate_ports()
        
    def _calculate_ports(self):
        """Calculate port positions based on transistor geometry"""
        # Calculate base dimensions
        gate_width = self.width * self.fingers
        
        # Calculate port positions - the orientation will be handled by the base class's get_port_position
        self.ports["source"] = [-gate_width/2, 0]
        self.ports["drain"] = [gate_width/2, 0]
        self.ports["gate"] = [0, -self.length/2]
        self.ports["bulk"] = [0, self.length/2]
        
    def generate_geometry(self):
        """Generate GDSII geometry for the transistor"""
        # Create a new GDSII cell for this transistor
        cell = gdspy.Cell(self.name)
        
        # Calculate dimensions based on parameters
        gate_width = self.width * self.fingers
        
        # Create active area (simplified rectangle for now)
        active = gdspy.Rectangle(
            (self.position[0] - gate_width/2 - self.length, 
             self.position[1] - self.width/2),
            (self.position[0] + gate_width/2 + self.length, 
             self.position[1] + self.width/2),
            layer=1  # Active layer
        )
        cell.add(active)
        
        # Create gate(s)
        for i in range(self.fingers):
            offset = -gate_width/2 + i * self.width * 2
            gate = gdspy.Rectangle(
                (self.position[0] + offset, 
                 self.position[1] - self.width),
                (self.position[0] + offset + self.length, 
                 self.position[1] + self.width),
                layer=2  # Poly layer
            )
            cell.add(gate)
            
        return cell
    
    def get_bounding_box(self):
        """Get the bounding box of the transistor"""
        gate_width = self.width * self.fingers
        
        # Define the bounding box based on transistor dimensions
        return [
            [self.position[0] - gate_width/2 - self.length, self.position[1] - self.width],
            [self.position[0] + gate_width/2 + self.length, self.position[1] + self.width]
        ]


class NMOS(Transistor):
    """NMOS transistor implementation"""
    
    def __init__(self, name, position, width, length, fingers=1, orientation=0, layer="active"):
        super().__init__(name, position, width, length, fingers, orientation, layer)
        self.device_type = "nmos"
    
    def generate_geometry(self):
        """Generate GDSII geometry for the NMOS transistor"""
        cell = super().generate_geometry()
        # Add NMOS-specific geometry (e.g., n-well)
        return cell


class PMOS(Transistor):
    """PMOS transistor implementation"""
    
    def __init__(self, name, position, width, length, fingers=1, orientation=0, layer="active"):
        super().__init__(name, position, width, length, fingers, orientation, layer)
        self.device_type = "pmos"
    
    def generate_geometry(self):
        """Generate GDSII geometry for the PMOS transistor"""
        cell = super().generate_geometry()
        # Add PMOS-specific geometry (e.g., p-well)
        return cell