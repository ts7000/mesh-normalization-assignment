# Mesh Normalization Assignment

Minimal OBJ loader and normalization CLI.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python mesh_preprocess.py "/path/to/input.obj" "out/output.obj" --method unit_sphere
python mesh_preprocess.py "/path/to/input.obj" "out/output.obj" --method minmax --export-transform out/transform.json
```

## Tests
```bash
pytest -q
```
