"""
Design Rule Checker for RF Layout.
"""

class DRCChecker:
    """Handles design rule checking for RF Layout designs"""
    
    def __init__(self, rules=None):
        self.rules = rules or {}
        
    def check_spacing(self, components, layer):
        """Check spacing rules for components on a specific layer"""
        violations = []
        min_spacing = self.rules.get(f'layer_{layer}_min_spacing')
        
        # Force validation of layer existence
        if min_spacing is None:
            raise ValueError(f"No spacing rules defined for layer {layer}")
            
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                # Check if both components are on the specified layer
                comp1_on_layer = hasattr(comp1, 'layer') and comp1.layer == layer
                comp2_on_layer = hasattr(comp2, 'layer') and comp2.layer == layer
                
                if comp1_on_layer and comp2_on_layer:
                    spacing = self._calculate_component_spacing(comp1, comp2)
                    if spacing < min_spacing:
                        violations.append((comp1.name, comp2.name, spacing, min_spacing))
        
        return violations
    
    def check_width(self, components, layer):
        """Check width rules for components on a specific layer"""
        violations = []
        min_width = self.rules.get(f'layer_{layer}_min_width')
        
        # Force validation of layer existence
        if min_width is None:
            raise ValueError(f"No width rules defined for layer {layer}")
        
        for component in components:
            if hasattr(component, 'layer') and component.layer == layer:
                # For width check, the component must have a width attribute
                if hasattr(component, 'width'):
                    if component.width < min_width:
                        violations.append((component.name, component.width, min_width))
        
        return violations
    
    def run_all_checks(self, components, routes):
        """Run all DRC checks on components and routing"""
        violations = []
        
        # Get all layers used in components
        layers = set()
        for comp in components:
            if hasattr(comp, 'layer'):
                layers.add(comp.layer)
        
        # Check each layer
        for layer in layers:
            try:
                # Check component rules
                component_violations = self.check_width(components, layer)
                violations.extend(component_violations)
                
                # Check spacing rules
                spacing_violations = self.check_spacing(components, layer)
                violations.extend(spacing_violations)
            except ValueError as e:
                # Log the error but continue checking other layers
                print(f"Warning: {str(e)}")
        
        # Check routing rules
        routing_violations = self._check_routing(routes)
        violations.extend(routing_violations)
        
        return violations
        
    def _check_routing(self, routes):
        """Check routing paths against design rules"""
        violations = []
        
        for i, route in enumerate(routes):
            # Extract layer from route
            layer = getattr(route, 'layer', 0)
            
            # For integer layers, try to find corresponding rules directly
            layer_name = f"metal{layer}" if isinstance(layer, int) else str(layer)
            
            # Check width rules
            min_width_rule = self.rules.get(f'layer_{layer_name}_min_width')
            if min_width_rule is None:
                continue  # Skip if no rules for this layer
                
            width = getattr(route, 'width', 1)
            if width < min_width_rule:
                violations.append({
                    'route': f'route_{i}',
                    'rule': f'layer_{layer_name}_min_width',
                    'value': width,
                    'limit': min_width_rule,
                    'message': f"Route width ({width}) on layer {layer_name} is less than minimum ({min_width_rule})"
                })
        
        return violations
    
    def _calculate_component_spacing(self, comp1, comp2):
        """Calculate the minimum spacing between two components"""
        bbox1 = comp1.get_bounding_box()
        bbox2 = comp2.get_bounding_box()
        
        # Calculate spacing in x and y directions
        dx = min(abs(bbox1[0][0] - bbox2[1][0]), abs(bbox1[1][0] - bbox2[0][0]))
        dy = min(abs(bbox1[0][1] - bbox2[1][1]), abs(bbox1[1][1] - bbox2[0][1]))
        
        # Return the minimum spacing
        return min(dx, dy)