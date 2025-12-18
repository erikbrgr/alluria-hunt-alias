# Creature Data Export

This repository contains a Python script to export creature data from `critterdb.json` to YAML format.

## Files

- `export_creatures.py` - Python script that performs the export
- `creatures.yaml` - Generated YAML file containing creature data for all 514 creatures
- `critterdb.json` - Source JSON file containing the bestiary data

## Usage

### Running the Script

The script can be run directly from the command line:

```bash
python3 export_creatures.py
```

This will read `critterdb.json` and generate `creatures.yaml` in the current directory.

### Requirements

- Python 3.6 or higher
- PyYAML library

To install PyYAML:

```bash
pip install PyYAML
```

### Exported Fields

The script exports the following fields for each creature:

- **name** - The creature's name
- **cr** - The creature's challenge rating (CR)
- **xp** - Experience points awarded for defeating the creature
- **env** - The creature's natural environment (only included if not empty)

## Output Format

The output YAML file contains a list of creature entries. Example:

```yaml
- name: Aarakocra
  cr: 0.25
  xp: 50
- name: Adult Blue Dragon
  cr: 16
  xp: 15000
- name: K'Thar
  cr: 5
  xp: 1800
  env: Arctic
```

## Error Handling

The script includes comprehensive error handling for:
- Missing input files
- Invalid JSON format
- File permission issues
- Missing PyYAML dependency

All errors will display a clear message explaining the issue.
