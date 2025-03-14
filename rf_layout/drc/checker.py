"""
Design Rule Checker for RF Layout.
"""

class DRCChecker:
    """Handles design rule checking for RF Layout designs"""
    
    def __init__(self, rules=None):
        """Initialize DRC checker with optional rules"""
        self.rules = rules or {}
        
    def run_all_checks(self, components, routes):
        """Run all DRC checks on components and routing"""
        violations = []
        
        # Check component rules
        component_violations = self._check_components(components)
        violations.extend(component_violations)
        
        # Check routing rules
        routing_violations = self._check_routing(routes)
        violations.extend(routing_violations)
        
        # Check component-to-component spacing
        spacing_violations = self._check_component_spacing(components)
        violations.extend(spacing_violations)
        
        return violations
    
    def _check_components(self, components):
        """Check components against design rules"""
        violations = []
        
        for component in components:
            # Get component type
            comp_type = component.__class__.__name__.lower()
            
            # Check rules specific to component types
            if comp_type == 'transistor' or comp_type == 'nmos' or comp_type == 'pmos':
                # Check transistor rules (width, length, etc.)
                min_length_rule = self.rules.get('transistor_min_length', 0.1)
                if hasattr(component, 'length') and component.length < min_length_rule:
                    violations.append({
                        'component': component.name,
                        'rule': 'transistor_min_length',
                        'value': component.length,
                        'limit': min_length_rule,
                        'message': f"Transistor {component.name} length ({component.length}) is less than minimum ({min_length_rule})"
                    })
            
            # Check appropriate layer rules for all components
            if hasattr(component, 'layer'):
                layer_name = component.layer
                min_width_rule = self.rules.get(f'layer_{layer_name}_min_width', 0)
                
                if hasattr(component, 'width') and component.width < min_width_rule:
                    violations.append({
                        'component': component.name,
                        'rule': f'layer_{layer_name}_min_width',
                        'value': component.width,
                        'limit': min_width_rule,
                        'message': f"Component {component.name} width ({component.width}) on layer {layer_name} is less than minimum ({min_width_rule})"
                    })
        
        return violations
    
    def _check_routing(self, routes):
        """Check routing paths against design rules"""
        violations = []
        
        for i, route in enumerate(routes):
            # Extract layer from route (assuming routes have a layer attribute)
            layer = getattr(route, 'layer', 0)
            layer_name = None
            
            # Convert layer number to name if possible
            if isinstance(layer, int):
                # Try to find layer name from number
                for name, props in self.rules.items():
                    if name.startswith('layer_') and props.get('number') == layer:
                        layer_name = name.replace('layer_', '')
                        break
            
            # If we have a layer name, check width rules
            if layer_name:
                min_width_rule = self.rules.get(f'layer_{layer_name}_min_width', 0)
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
    
    def _check_component_spacing(self, components):
        """Check spacing between components"""
        violations = []
        
        # Check each pair of components
        for i, comp1 in enumerate(components):
            for j, comp2 in enumerate(components[i+1:], i+1):
                # Get bounding boxes
                bbox1 = comp1.get_bounding_box()
                bbox2 = comp2.get_bounding_box()
                
                # Calculate separation
                x_overlap = (bbox1[0][0] < bbox2[1][0] and bbox1[1][0] > bbox2[0][0])
                y_overlap = (bbox1[0][1] < bbox2[1][1] and bbox1[1][1] > bbox2[0][1])
                
                # If components overlap in both dimensions, they're too close
                if x_overlap and y_overlap:
                    violations.append({
                        'component1': comp1.name,
                        'component2': comp2.name,
                        'rule': 'component_overlap',
                        'message': f"Components {comp1.name} and {comp2.name} overlap"
                    })
                    continue
                
                # Calculate minimum required spacing
                min_spacing = 0
                
                # If components have layers, check layer-specific spacing
                if hasattr(comp1, 'layer') and hasattr(comp2, 'layer'):
                    layer1, layer2 = comp1.layer, comp2.layer
                    spacing_rule = self.rules.get(f'layer_{layer1}_to_{layer2}_spacing')
                    
                    if not spacing_rule:
                        # Try reverse ordering
                        spacing_rule = self.rules.get(f'layer_{layer2}_to_{layer1}_spacing')
                    
                    if spacing_rule:
                        min_spacing = spacing_rule
                
                # If no specific layer rule, use default spacing
                if min_spacing == 0:
                    min_spacing = self.rules.get('default_component_spacing', 1.0)
                
                # Calculate actual spacing
                if x_overlap:
                    # Components overlap in x dimension, check y spacing
                    spacing = min(abs(bbox1[0][1] - bbox2[1][1]), abs(bbox1[1][1] - bbox2[0][1]))
                    if spacing < min_spacing:
                        violations.append({
                            'component1': comp1.name,
                            'component2': comp2.name,
                            'rule': 'min_component_spacing',
                            'value': spacing,
                            'limit': min_spacing,
                            'message': f"Spacing between {comp1.name} and {comp2.name} ({spacing}) is less than minimum ({min_spacing})"
                        })
                elif y_overlap:
                    # Components overlap in y dimension, check x spacing
                    spacing = min(abs(bbox1[0][0] - bbox2[1][0]), abs(bbox1[1][0] - bbox2[0][0]))
                    if spacing < min_spacing:
                        violations.append({
                            'component1': comp1.name,
                            'component2': comp2.name,
                            'rule': 'min_component_spacing',
                            'value': spacing,
                            'limit': min_spacing,
                            'message': f"Spacing between {comp1.name} and {comp2.name} ({spacing}) is less than minimum ({min_spacing})"
                        })
        
        return violations