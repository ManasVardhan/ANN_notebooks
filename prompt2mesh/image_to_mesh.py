from pathlib import Path
from typing import Tuple

import numpy as np
import trimesh
from PIL import Image


def _image_to_heightmap(image_path: str | Path, stride: int = 1) -> np.ndarray:
	"""
	Load image and convert to normalized grayscale [0, 1].
	Optionally subsample with stride for speed.
	"""
	img = Image.open(image_path).convert("L")
	arr = np.array(img, dtype=np.float32) / 255.0
	if stride > 1:
		arr = arr[::stride, ::stride]
	return arr


def _grid_to_mesh(heightmap: np.ndarray, z_scale: float = 0.25) -> trimesh.Trimesh:
	"""
	Convert grayscale heightmap (H,W) into a TriMesh by forming a grid and two triangles per cell.
	x, y are normalized to [-0.5, 0.5], z is heightmap * z_scale.
	"""
	h, w = heightmap.shape
	# Create normalized grid coordinates
	ys = np.linspace(-0.5, 0.5, h, dtype=np.float32)
	xs = np.linspace(-0.5, 0.5, w, dtype=np.float32)

	xv, yv = np.meshgrid(xs, ys)  # (H, W)
	zv = heightmap * float(z_scale)

	# Vertices: (H*W, 3)
	vertices = np.stack([xv, yv, zv], axis=-1).reshape(-1, 3)

	# Faces: two triangles per cell
	faces = []
	for i in range(h - 1):
		for j in range(w - 1):
			idx = i * w + j
			# Triangle 1
			faces.append([idx, idx + 1, idx + w])
			# Triangle 2
			faces.append([idx + 1, idx + w + 1, idx + w])
	faces = np.array(faces, dtype=np.int32)

	mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
	mesh.remove_degenerate_faces()
	mesh.remove_duplicate_faces()
	mesh.remove_infinite_values()
	mesh.remove_unreferenced_vertices()
	mesh.rezero()
	return mesh


def image_to_mesh(
	image_path: str | Path,
	mesh_out: str | Path,
	z_scale: float = 0.25,
	stride: int = 2,
) -> Path:
	"""
	Convert an image to a heightmap-based mesh and export to OBJ.
	"""
	mesh_out = Path(mesh_out)
	mesh_out.parent.mkdir(parents=True, exist_ok=True)
	heightmap = _image_to_heightmap(image_path, stride=stride)
	mesh = _grid_to_mesh(heightmap, z_scale=z_scale)
	mesh.export(mesh_out.as_posix())
	return mesh_out