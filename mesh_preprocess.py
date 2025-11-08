import argparse
import sys
import json
from pathlib import Path
import numpy as np

def load_obj(path: str):
    """Load minimal OBJ (supports 'v' and 'f'). Returns (verts[N,3], faces[M,k] 0-based)."""
    verts = []
    faces = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.strip().split()
                if len(parts) >= 4:
                    try:
                        verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
                    except ValueError:
                        continue
            elif line.startswith("f "):
                parts = line.strip().split()[1:]
                if len(parts) >= 3:
                    face = []
                    for p in parts:
                        idx = p.split("/")[0]
                        if idx:
                            try:
                                face.append(int(idx) - 1)  # to 0-based
                            except ValueError:
                                pass
                    if len(face) >= 3:
                        faces.append(face)
    return np.asarray(verts, dtype=float), np.asarray(faces, dtype=int)

def normalize_unit_sphere(verts, return_transform=False):
    if verts.size == 0:
        empty = (verts, {"centroid": [0, 0, 0], "scale": 1.0})
        return empty if return_transform else verts
    centroid = verts.mean(axis=0)
    verts_c = verts - centroid
    max_dist = np.linalg.norm(verts_c, axis=1).max()
    verts_n = verts_c / max_dist if max_dist > 0 else verts_c
    if return_transform:
        return verts_n, {"centroid": centroid.tolist(), "scale": float(max_dist)}
    return verts_n

def normalize_minmax(verts, return_transform=False):
    """Scale verts into [0,1]^3 box; also recenters to min corner."""
    if verts.size == 0:
        empty = (verts, {"min": [0, 0, 0], "range": [1, 1, 1]})
        return empty if return_transform else verts
    vmin = verts.min(axis=0)
    vmax = verts.max(axis=0)
    span = np.where((vmax - vmin) == 0, 1.0, (vmax - vmin))
    verts_n = (verts - vmin) / span
    if return_transform:
        return verts_n, {"min": vmin.tolist(), "range": span.tolist()}
    return verts_n

def save_obj(path, verts, faces, precision=6):
    fmt = f"{{:.{precision}f}}"
    with open(path, "w") as f:
        for v in verts:
            f.write("v " + " ".join(fmt.format(float(x)) for x in v[:3]) + "\n")
        for face in faces:
            # convert 0-based indices to 1-based for OBJ
            f.write("f " + " ".join(str(int(i) + 1) for i in face) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Mesh preprocessing")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--method", choices=["unit_sphere", "minmax"], default="unit_sphere")
    parser.add_argument("--precision", type=int, default=6)
    parser.add_argument("--export-transform", type=Path)
    args = parser.parse_args()

    in_path = Path(args.input).expanduser()
    if not in_path.is_file():
        print(f"Error: input OBJ not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    verts, faces = load_obj(str(in_path))
    if args.method == "unit_sphere":
        if args.export_transform:
            verts, transform = normalize_unit_sphere(verts, return_transform=True)
        else:
            verts = normalize_unit_sphere(verts); transform = None
    else:
        if args.export_transform:
            verts, transform = normalize_minmax(verts, return_transform=True)
        else:
            verts = normalize_minmax(verts); transform = None

    save_obj(str(out_path), verts, faces, precision=args.precision)

    if args.export_transform and transform is not None:
        args.export_transform.parent.mkdir(parents=True, exist_ok=True)
        with open(args.export_transform, "w") as jf:
            json.dump(transform, jf, indent=2)

if __name__ == "__main__":
    main()

def test_load_and_save_roundtrip(tmp_path: Path):
    verts = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=float)
    faces_1b = np.array([[1,2,3]], dtype=int)  # 1-based for file
    src = tmp_path / "tri.obj"
    write_obj(src, verts, faces_1b)

    v0, f0 = mp.load_obj(str(src))  # f0 is 0-based
    assert v0.shape == (3,3) and f0.shape == (1,3)

    out = tmp_path / "tri_out.obj"
    mp.save_obj(str(out), v0, f0, precision=6)

    v1, f1 = mp.load_obj(str(out))
    np.testing.assert_allclose(v1, v0, rtol=0, atol=1e-6)
    assert (f1 == f0).all()

def test_unit_sphere_normalization():
    v = np.array([[-1,0,0],[1,0,0],[0,0,0]], dtype=float)
    vn, t = mp.normalize_unit_sphere(v, return_transform=True)
    assert np.isclose(np.linalg.norm(vn, axis=1).max(), 1.0)
    assert "centroid" in t and "scale" in t

def test_minmax_normalization():
    v = np.array([[2,3,4],[3,5,7],[2,5,4]], dtype=float)
    vn, t = mp.normalize_minmax(v, return_transform=True)
    mins, maxs = vn.min(axis=0), vn.max(axis=0)
    assert np.allclose(mins, 0.0) and np.allclose(maxs, 1.0)
    assert "min" in t and "range" in t

def test_empty_inputs():
    v = np.empty((0,3), dtype=float)
    vn1, t1 = mp.normalize_unit_sphere(v, return_transform=True)
    vn2, t2 = mp.normalize_minmax(v, return_transform=True)
    assert vn1.size == 0 and vn2.size == 0
    assert t1["scale"] == 1.0 and t2["range"] == [1,1,1]