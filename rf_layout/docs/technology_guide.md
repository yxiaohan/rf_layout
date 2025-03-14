# Technology Configuration Guide

## Overview

RF Layout uses technology files to define foundry-specific design rules and layer mappings. This document explains how to create and use custom technology files with RF Layout.

## File Format

Technology files can be defined in either YAML or JSON format. Both formats support the same structure.

## Basic Structure

```yaml
name: my_custom_technology
description: "Custom 45nm CMOS technology"
rules:
  # Design rules for minimum widths, spacings, etc.
  layer_metal1_min_width: 0.1
  layer_metal1_min_spacing: 0.1
  # ...more rules
layers:
  # Layer definitions for GDS mapping
  metal1:
    number: 10
    datatype: 0
  # ...more layers
```

## Required Sections

### Rules

The `rules` section defines the design rules for each layer. Common rules include:

- `layer_X_min_width`: Minimum width for layer X
- `layer_X_min_spacing`: Minimum spacing for layer X
- `via_min_size`: Minimum size for vias
- `via_min_spacing`: Minimum spacing between vias

### Layers

The `layers` section defines the GDSII layer numbers and datatypes for each named layer in your design. Each layer entry requires:

- `number`: The GDSII layer number
- `datatype`: The GDSII datatype (usually 0)

## Example Technology File

```yaml
name: example_cmos_65nm
description: "Example 65nm CMOS Technology"
rules:
  layer_metal1_min_width: 0.1
  layer_metal1_min_spacing: 0.1
  layer_metal2_min_width: 0.1
  layer_metal2_min_spacing: 0.1
  layer_metal3_min_width: 0.2
  layer_metal3_min_spacing: 0.2
  layer_metal4_min_width: 0.2
  layer_metal4_min_spacing: 0.2
  layer_metal5_min_width: 0.5
  layer_metal5_min_spacing: 0.5
  via_min_size: 0.1
  via_min_spacing: 0.1
layers:
  substrate: {number: 0, datatype: 0}
  nwell: {number: 1, datatype: 0}
  pwell: {number: 2, datatype: 0}
  active: {number: 3, datatype: 0}
  poly: {number: 4, datatype: 0}
  metal1: {number: 10, datatype: 0}
  metal2: {number: 11, datatype: 0}
  metal3: {number: 12, datatype: 0}
  metal4: {number: 13, datatype: 0}
  metal5: {number: 14, datatype: 0}
  via12: {number: 20, datatype: 0}
  via23: {number: 21, datatype: 0}
  via34: {number: 22, datatype: 0}
  via45: {number: 23, datatype: 0}
```

## Using Technology Files

To use a technology file with RF Layout:

```python
from rf_layout.main import RFLayout

# Initialize with technology file
rf_layout = RFLayout("path/to/tech_file.yaml")

# Process design
rf_layout.process_design("design.yaml", "output.gds")
```

Or via command line:

```bash
rf_layout design.yaml output.gds tech_file.yaml
```

## Built-in Default Technology

RF Layout includes a default technology that will be used if no technology file is specified. This default is suitable for basic examples but should be replaced with an actual foundry technology for real designs.