#!/usr/bin/env python
"""
Example script for RF Layout tool - CMOS Amplifier Generator

This example demonstrates loading the CMOS amplifier YAML description 
and generating a GDSII layout file.
"""

import os
import sys
import logging

# Add parent directory to path to allow importing rf_layout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rf_layout.main import RFLayout

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Generate GDSII for a CMOS amplifier from YAML description"""
    
    # Input and output file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_file = os.path.join(current_dir, 'cmos_amplifier.yaml')
    output_gds = os.path.join(current_dir, 'cmos_amplifier.gds')
    
    logger.info(f"Loading YAML design from: {yaml_file}")
    logger.info(f"Output will be saved to: {output_gds}")
    
    # Initialize RF Layout tool
    rf_layout = RFLayout()
    
    try:
        # Process the design from YAML to GDSII
        output_path = rf_layout.process_design(
            yaml_file=yaml_file,
            output_gds=output_gds,
            auto_place=True  # Use automatic placement
        )
        
        logger.info(f"GDSII file generated successfully: {output_path}")
        logger.info(f"Design contains {len(rf_layout.components)} components")
        logger.info(f"Design contains {len(rf_layout.connections)} connections")
        
    except Exception as e:
        logger.error(f"Error processing design: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())