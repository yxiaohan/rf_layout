# RF Layout

A robust solution for RFIC designers to define complex RF circuits using a human-readable YAML format, which will then be automatically translated into industry-standard GDSII layout files.

## Overview

RF Layout is a Python library that simplifies the process of creating layout files for RF circuits. By describing your circuit in a YAML file, RF Layout handles:

- Component placement and orientation
- Connection routing
- Design rule checking
- GDSII export

## Installation

### Requirements

- Python 3.6+
- Required packages: gdspy, numpy, pyyaml, jsonschema

### Install from Source

```bash
git clone https://github.com/rflayout/rf_layout.git
cd rf_layout
pip install -e .
```

## Usage

### Basic Usage

1. Create a YAML file describing your RF circuit design
2. Use the RF Layout API or command line tool to convert it to GDSII

Example:

```python
from rf_layout.main import RFLayout

# Initialize with optional technology file
rf_layout = RFLayout("tech_file.yaml")

# Process design from YAML to GDSII
rf_layout.process_design(
    yaml_file="my_design.yaml",
    output_gds="my_design.gds",
    auto_place=True
)
```

### Command Line Interface

```bash
# Basic usage
rf_layout my_design.yaml output.gds

# With custom technology file
rf_layout my_design.yaml output.gds tech_file.yaml
```

## YAML Format

RF Layout uses a simple YAML structure to define circuits. Here's a basic example:

```yaml
design:
  name: my_circuit
  technology: default_tech
  description: "Simple example circuit"
  components:
    - type: nmos
      name: M1
      position: [0, 0]
      parameters:
        width: 10.0
        length: 0.18
        fingers: 4
    # More components...
  
  connections:
    - from: M1.drain
      to: M2.source
      width: 1.0
      layer: metal1
      routing_strategy: manhattan
    # More connections...
```

## Supported Components

- Transistors: NMOS, PMOS
- Passives: Resistors, Capacitors, Inductors
- More components coming soon!

## Examples

Check the `examples/` directory for sample designs and scripts.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Thanks to the GDSPY library for GDSII file handling
- Inspired by the needs of RFIC designers who wanted a simpler workflow