import io
import math
from pathlib import Path
from typing import Iterable

import imageio
import numpy as np
import plotly.graph_objects as go
import trimesh
from PIL import Image


def _trimesh_to_plotly(mesh: trimesh.Trimesh) -> go.Mesh3d:
	verts = mesh.vertices
	faces = mesh.faces

	x = verts[:, 0]
	y = verts[:, 1]
	z = verts[:, 2]

	# Use z as intensity for a simple shaded look
	z_norm = (z - z.min()) / (max(1e-8, (z.max() - z.min())))
	intensity = z_norm

	return go.Mesh3d(
		x=x,
		y=y,
		z=z,
		i=faces[:, 0],
		j=faces[:, 1],
		k=faces[:, 2],
		intensity=intensity,
		colorscale="Viridis",
		showscale=False,
		lighting=dict(ambient=0.5, diffuse=0.9, specular=0.2),
		flatshading=False,
		opacity=1.0,
	)


def _make_figure(mesh: trimesh.Trimesh, width: int, height: int) -> go.Figure:
	mesh3d = _trimesh_to_plotly(mesh)
	fig = go.Figure(data=[mesh3d])
	fig.update_layout(
		scene=dict(
			xaxis=dict(visible=False),
			yaxis=dict(visible=False),
			zaxis=dict(visible=False),
			aspectmode="data",
		),
		margin=dict(l=0, r=0, t=0, b=0),
		width=width,
		height=height,
		paper_bgcolor="white",
		plot_bgcolor="white",
	)
	return fig


def _camera_eye(angle_rad: float, distance: float, elevation: float = 0.25) -> dict:
	return dict(
		x=distance * math.cos(angle_rad),
		y=distance * math.sin(angle_rad),
		z=distance * elevation,
	)


def _fig_to_image_array(fig: go.Figure, scale: int = 2) -> np.ndarray:
	img_bytes = fig.to_image(format="png", scale=scale, engine="kaleido")
	pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
	return np.array(pil_img)


def render_turntable(
	mesh_path: str | Path,
	out_gif: str | Path,
	frames: int = 36,
	width: int = 800,
	height: int = 600,
	distance: float = 2.0,
	elevation: float = 0.25,
	scale: int = 2,
	fps: int = 18,
) -> Path:
	"""
	Render a rotating turntable GIF of the mesh using Plotly+Kaleido.
	"""
	mesh_path = Path(mesh_path)
	out_gif = Path(out_gif)
	out_gif.parent.mkdir(parents=True, exist_ok=True)

	mesh = trimesh.load(mesh_path.as_posix(), force="mesh")
	fig = _make_figure(mesh, width=width, height=height)

	images: list[np.ndarray] = []
	for f in range(frames):
		angle = 2.0 * math.pi * (f / frames)
		eye = _camera_eye(angle, distance=distance, elevation=elevation)
		fig.update_layout(scene_camera=dict(eye=eye))
		img = _fig_to_image_array(fig, scale=scale)
		images.append(img)

	imageio.mimsave(out_gif.as_posix(), images, duration=max(1e-6, 1.0 / fps))
	return out_gif