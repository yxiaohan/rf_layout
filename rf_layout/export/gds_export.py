"""
GDSII file export for RF Layout.
"""
import gdspy
import numpy as np
import datetime

class GDSWriter:
    """Handles export of RF Layout designs to GDSII format"""
    
    def __init__(self, design_name, unit=1.0e-6, precision=1.0e-9):
        self.design_name = design_name
        self.unit = unit  # Default is 1um
        self.precision = precision  # Default is 1nm
        self.lib = None
        self.top_cell = None
        self.layer_mapping = {}
        self._cell_counter = {}  # Track cell name usage
        
        # Initialize library immediately to ensure it's the current one
        self.initialize_lib()
        
    def _get_unique_cell_name(self, base_name):
        """Generate a unique cell name by adding a suffix if needed"""
        if base_name not in self._cell_counter:
            self._cell_counter[base_name] = 0
            return base_name
        
        self._cell_counter[base_name] += 1
        return f"{base_name}_{self._cell_counter[base_name]}"
        
    def initialize_lib(self):
        """Initialize new GDSII library"""
        # Create a fresh library
        self.lib = gdspy.GdsLibrary(
            name=self.design_name,
            unit=self.unit,
            precision=self.precision
        )
        # Set as current library to avoid conflicts
        gdspy.current_library = self.lib
        
        # Create top cell with unique name
        self.top_cell = self.lib.new_cell(self._get_unique_cell_name(self.design_name))
        return self.lib
    
    def add_components(self, components):
        """Add multiple components to the top cell"""
        if not components:
            return
            
        # Ensure we're using our library
        prev_lib = gdspy.current_library
        gdspy.current_library = self.lib
        
        try:
            # Add each component's geometry to the top cell
            for component in components:
                # Generate component geometry
                geometry = component.generate_geometry()
                if not isinstance(geometry, (list, tuple)):
                    geometry = [geometry]
                    
                # Create cell for the component with a unique name
                cell_name = self._get_unique_cell_name(component.name)
                cell = self.lib.new_cell(cell_name)
                
                # Add geometry primitives to the cell
                for primitive in geometry:
                    cell.add(primitive)
                
                # Create reference in top cell with proper orientation
                ref = gdspy.CellReference(
                    cell,
                    origin=component.position,
                    rotation=component.orientation if hasattr(component, 'orientation') else 0
                )
                self.top_cell.add(ref)
        finally:
            # Restore previous library
            gdspy.current_library = prev_lib
    
    def add_routing(self, routes):
        """Add routing paths to the top cell"""
        if not self.top_cell:
            self.initialize_lib()
            
        # Add each routing path to the top cell
        for route in routes:
            self.top_cell.add(route)
    
    def write_gds(self, file_path):
        """Export the design to a GDSII file"""
        if not self.top_cell:
            raise ValueError("No design to export. Add components first.")
            
        # Write the library to a file
        self.lib.write_gds(file_path)
        return file_path
    
    def export_gds(self, file_path):
        """Export the design to a GDSII file (alias for write_gds)"""
        return self.write_gds(file_path)
    
    def export_with_viewer(self, file_path):
        """Export the design and open GDSII viewer"""
        self.write_gds(file_path)
        
        # This would typically launch or integrate with a GDSII viewer
        # Simplified for this implementation
        gdspy.LayoutViewer(cells=self.lib.cells.values())
        
        return file_path
    
    def add_text_label(self, text, position, layer=100, height=10):
        """Add a text label to the design"""
        if not self.top_cell:
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
        if not self.top_cell:
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
    
    def add_routes(self, routes):
        """Add routing paths to the top cell (alias for add_routing)"""
        self.add_routing(routes)
    
    def set_layer_mapping(self, mapping):
        """Set layer name to number mapping"""
        self.layer_mapping = mapping.copy()