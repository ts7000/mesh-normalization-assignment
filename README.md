# Mesh Normalization Assignment

Minimal Python tool to:
- Load simple OBJ meshes (supports vertex lines `v` and face lines `f`)
- Normalize vertices with one of two methods:
  - unit_sphere: center at centroid and scale so max radius = 1
  - minmax: shift to min corner and scale each axis into [0, 1]
- Save the normalized mesh back to OBJ
- Optionally export the applied transform as JSON

What’s happening:
- The script parses OBJ vertices (x, y, z) and face indices, converting OBJ’s 1-based indices to 0-based internally.
- It computes either:
  - Unit-sphere normalization: subtract centroid, divide by the maximum Euclidean norm.
  - Min–max normalization: subtract per-axis minimum, divide by per-axis range.
- Faces are preserved (polygons with any vertex count); indices are written back as 1-based for OBJ.
- If requested, it writes a small JSON with the normalization parameters (centroid/scale or min/range).

## Requirements

- Python 3.8+
- numpy, pytest (for tests)

Install (recommended: virtual environment):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Normalize to unit sphere:
```bash
python mesh_preprocess.py "/path/to/input.obj" "out/output.obj" --method unit_sphere
```

Normalize with min–max and export transform:
```bash
python mesh_preprocess.py "/path/to/input.obj" "out/output.obj" --method minmax --export-transform out/transform.json
```

Control numeric precision in output OBJ:
```bash
python mesh_preprocess.py "/path/to/input.obj" "out/output.obj" --precision 6
```

Batch process a folder (macOS):
```bash
mkdir -p out
for f in /absolute/path/to/folder/*.obj; do
  b="$(basename "$f" .obj)"
  python mesh_preprocess.py "$f" "out/${b}_norm.obj" --method unit_sphere
done
```

## Transform JSON

- unit_sphere:
  - { "centroid": [cx, cy, cz], "scale": s }
  - Apply to original verts: v' = (v - centroid) / scale
- minmax:
  - { "min": [mx, my, mz], "range": [rx, ry, rz] }
  - Apply to original verts: v' = (v - min) / range

## Tests

Run the pytest suite:
```bash
pytest -q
```

## Notes and limitations

- OBJ parsing is minimal: only `v` and `f` lines are read; texture coords, normals, materials are ignored.
- Faces are not triangulated; polygons are written back as-is.
- Empty meshes are handled gracefully (identity-like transform values).
- Output directory is created automatically.

## Troubleshooting

- ModuleNotFoundError: No module named 'numpy'
  - Activate the venv and install deps: `source .venv/bin/activate && pip install -r requirements.txt`
- FileNotFoundError for input
  - Check the path or drag-drop the file into the terminal to paste its absolute path.
- Tried to “run” an OBJ file (permission denied)
  - Pass the OBJ as an argument to the script, do not execute it.
