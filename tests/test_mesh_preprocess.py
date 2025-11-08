import numpy as np
from pathlib import Path
import mesh_preprocess as mp

def _write_obj(path: Path, verts, faces_1based):
    with open(path, "w") as f:
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces_1based:
            f.write("f " + " ".join(str(i) for i in face) + "\n")

def test_load_and_save_roundtrip(tmp_path: Path):
    verts = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=float)
    faces_1b = np.array([[1,2,3]], dtype=int)
    src = tmp_path / "tri.obj"
    _write_obj(src, verts, faces_1b)

    v0, f0 = mp.load_obj(str(src))
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