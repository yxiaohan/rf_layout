"""
Placement module for arranging components in the layout.
"""

import numpy as np

class Placement:
    """Handles component placement in the layout"""
    
    def __init__(self, components):
        self.components = components
        self.placement_grid = None
        
    def set_grid(self, grid_size, origin=(0,0)):
        """Set placement grid size and origin"""
        self.placement_grid = {
            'size': grid_size,
            'origin': origin
        }
    
    def snap_to_grid(self, component):
        """Snap component position to grid"""
        if not self.placement_grid:
            return  # No grid defined
            
        grid_size = self.placement_grid['size']
        origin = self.placement_grid['origin']
        
        # Calculate grid-aligned position
        x = origin[0] + round((component.position[0] - origin[0]) / grid_size) * grid_size
        y = origin[1] + round((component.position[1] - origin[1]) / grid_size) * grid_size
        
        # Update component position
        component.position = [x, y]
    
    def snap_all_to_grid(self):
        """Snap all components to grid"""
        if not self.placement_grid:
            return  # No grid defined
            
        for component in self.components:
            self.snap_to_grid(component)
    
    def auto_place(self, spacing=10):
        """Auto-place components with simple row-based strategy"""
        if not self.components:
            return
            
        # Sort components by type for better grouping
        comp_types = {}
        for comp in self.components:
            comp_type = comp.__class__.__name__
            if comp_type not in comp_types:
                comp_types[comp_type] = []
            comp_types[comp_type].append(comp)
        
        # Simple row-based placement
        current_y = 0
        for comp_type, comps in comp_types.items():
            current_x = 0
            row_height = 0
            
            for comp in comps:
                # Get component bounding box
                bbox = comp.get_bounding_box()
                width = bbox[1][0] - bbox[0][0]
                height = bbox[1][1] - bbox[0][1]
                
                # Update row height if this component is taller
                row_height = max(row_height, height)
                
                # Set component position
                comp.position = [current_x + width/2, current_y + height/2]
                
                # Move to next position in row
                current_x += width + spacing
            
            # Move to next row
            current_y += row_height + spacing
    
    def detect_overlaps(self):
        """Detect overlapping components"""
        overlaps = []
        
        # Check each pair of components for overlaps
        for i, comp1 in enumerate(self.components):
            bbox1 = comp1.get_bounding_box()
            
            for j, comp2 in enumerate(self.components[i+1:], i+1):
                bbox2 = comp2.get_bounding_box()
                
                # Check if bounding boxes overlap
                if (bbox1[0][0] < bbox2[1][0] and bbox1[1][0] > bbox2[0][0] and
                    bbox1[0][1] < bbox2[1][1] and bbox1[1][1] > bbox2[0][1]):
                    overlaps.append((comp1, comp2))
        
        return overlaps
    
    def resolve_overlaps(self, spacing=5):
        """Attempt to resolve component overlaps"""
        overlaps = self.detect_overlaps()
        
        while overlaps:
            # Get first overlapping pair
            comp1, comp2 = overlaps[0]
            
            # Calculate vector between components
            vec_x = comp2.position[0] - comp1.position[0]
            vec_y = comp2.position[1] - comp1.position[1]
            
            # Normalize and apply spacing
            dist = np.sqrt(vec_x**2 + vec_y**2)
            if dist < 0.001:  # Avoid division by zero
                vec_x, vec_y = 1, 0
            else:
                vec_x /= dist
                vec_y /= dist
                
            # Get bounding boxes
            bbox1 = comp1.get_bounding_box()
            bbox2 = comp2.get_bounding_box()
            
            # Calculate sizes
            width1 = bbox1[1][0] - bbox1[0][0]
            height1 = bbox1[1][1] - bbox1[0][1]
            width2 = bbox2[1][0] - bbox2[0][0]
            height2 = bbox2[1][1] - bbox2[0][1]
            
            # Calculate required movement
            move_dist = (max(width1, width2) + max(height1, height2)) / 2 + spacing
            
            # Move comp2 away from comp1
            comp2.position[0] += vec_x * move_dist
            comp2.position[1] += vec_y * move_dist
            
            # Check for remaining overlaps
            overlaps = self.detect_overlaps()
            
        # Optional: snap to grid after resolving overlaps
        if self.placement_grid:
            self.snap_all_to_grid()