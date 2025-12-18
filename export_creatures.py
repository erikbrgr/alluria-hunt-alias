#!/usr/bin/env python3
"""
Export creature data from critterdb.json to YAML format.

This script extracts the following fields for each creature:
- name
- challengeRating
- experiencePoints
- environment

Requirements:
    - PyYAML: Install with 'pip install PyYAML'
"""

import json
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Please install it with: pip install PyYAML")
    sys.exit(1)


def export_creatures_to_yaml(input_file='critterdb.json', output_file='creatures.yaml'):
    """
    Export creature data from JSON to YAML format.
    
    Args:
        input_file: Path to the input JSON file (default: critterdb.json)
        output_file: Path to the output YAML file (default: creatures.yaml)
        
    Raises:
        FileNotFoundError: If the input file does not exist
        json.JSONDecodeError: If the input file contains invalid JSON
        IOError: If there are issues writing the output file
    """
    # Read the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{input_file}': {e}")
        sys.exit(1)
    
    # Extract creature data
    creatures = []
    for creature in data.get('creatures', []):
        creature_data = {
            'name': creature.get('name', ''),
            'challengeRating': creature.get('stats', {}).get('challengeRating', 0),
            'experiencePoints': creature.get('stats', {}).get('experiencePoints', 0),
            'environment': creature.get('flavor', {}).get('environment', ''),
            'flavor': creature.get('flavor', {}).get('description', '')
        }
        creatures.append(creature_data)
    
    # Write to YAML file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(creatures, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except IOError as e:
        print(f"Error: Cannot write to '{output_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error writing YAML file: {e}")
        sys.exit(1)
    
    print(f"Successfully exported {len(creatures)} creatures to {output_file}")


if __name__ == '__main__':
    export_creatures_to_yaml()
