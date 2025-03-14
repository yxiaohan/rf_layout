"""
GDSII file export for RF Layout.
"""

import gdspy
import numpy as np
import datetime

class GDSExporter:
    """Handles export of RF Layout designs to GDSII format"""
    
    def __init__(self, design_name, unit=1.0e-6, precision=1.0e-9):
        self.design_name = design_name
        self.unit = unit  # Default is 1um
        self.precision = precision  # Default is 1nm
        self.lib = None
        self.top_cell = None
        
    def initialize_lib(self):
        """Initialize new GDSII library"""
        self.lib = gdspy.GdsLibrary(name=self.design_name, unit=self.unit, precision=self.precision)
        self.top_cell = self.lib.new_cell(self.design_name)
        return self.lib
    
    def add_components(self, components):
        """Add multiple components to the top cell"""
        if self.top_cell is None:
            self.initialize_lib()
            
        # Add each component's geometry to the top cell
        for component in components:
            cell = component.generate_geometry()
            self.top_cell.add(gdspy.CellReference(cell))
    
    def add_routing(self, routes):
        """Add routing paths to the top cell"""
        if self.top_cell is None:
            self.initialize_lib()
            
        # Add each routing path to the top cell
        for route in routes:
            self.top_cell.add(route)
    
    def export_gds(self, file_path):
        """Export the design to a GDSII file"""
        if self.top_cell is None:
            raise ValueError("No design to export. Add components first.")
            
        # Write the library to a file
        self.lib.write_gds(file_path)
        return file_path
    
    def export_with_viewer(self, file_path):
        """Export the design and open GDSII viewer"""
        self.export_gds(file_path)
        
        # This would typically launch or integrate with a GDSII viewer
        # Simplified for this implementation
        gdspy.LayoutViewer(cells=self.lib.cells.values())
        
        return file_path
    
    def add_text_label(self, text, position, layer=100, height=10):
        """Add a text label to the design"""
        if self.top_cell is None:
            self.initialize_lib()
            
        text_elem = gdspy.Text(
            text, 
            height, 
            position, 
            layer=layer
        )
        self.top_cell.add(text_elem)
    
    def add_timestamp(self, position=(0, 0), layer=100, height=5):
        """Add a timestamp to the design"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_text_label(f"Generated: {timestamp}", position, layer, height)
    
    def add_design_border(self, margin=10):
        """Add a border around the design's bounding box"""
        if self.top_cell is None:
            return
        
        # Get the bounding box of the design
        bbox = self.top_cell.get_bounding_box()
        if bbox is None:
            return  # No elements in the cell
            
        # Add margin
        bbox = [
            [bbox[0][0] - margin, bbox[0][1] - margin],
            [bbox[1][0] + margin, bbox[1][1] + margin]
        ]
        
        # Create border rectangle
        border = gdspy.Rectangle(
            bbox[0],
            bbox[1],
            layer=99  # Special layer for border
        )
        self.top_cell.add(border)