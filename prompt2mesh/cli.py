import sys
from pathlib import Path

import click

from .text_to_image import generate_image
from .image_to_mesh import image_to_mesh
from .render import render_turntable


@click.group()
def cli() -> None:
	pass


@cli.command("run")
@click.option("--prompt", required=True, type=str, help="Text prompt to generate the image.")
@click.option("--out", "out_dir", required=True, type=click.Path(file_okay=False), help="Output directory.")
@click.option("--width", default=512, show_default=True, type=int)
@click.option("--height", default=512, show_default=True, type=int)
@click.option("--seed", default=None, type=int, help="Optional seed for reproducibility.")
@click.option("--z-scale", default=0.25, show_default=True, type=float, help="Height amplification for mesh.")
@click.option("--stride", default=2, show_default=True, type=int, help="Subsample factor for speed.")
@click.option("--frames", default=36, show_default=True, type=int, help="Number of frames in the turntable.")
@click.option("--gif-fps", default=18, show_default=True, type=int, help="GIF playback FPS.")
def run(
	prompt: str,
	out_dir: str,
	width: int,
	height: int,
	seed: int | None,
	z_scale: float,
	stride: int,
	frames: int,
	gif_fps: int,
) -> None:
	"""
	Full pipeline: prompt -> image -> mesh -> turntable GIF (local fallbacks).
	"""
	out = Path(out_dir)
	out.mkdir(parents=True, exist_ok=True)

	image_path = out / "image.png"
	mesh_path = out / "mesh.obj"
	gif_path = out / "turntable.gif"

	# 1) Text to image
	click.echo("Generating image from prompt...")
	img = generate_image(prompt, size=(width, height), seed=seed)
	img.save(image_path.as_posix())
	click.echo(f"Saved: {image_path}")

	# 2) Image to 3D (heightmap)
	click.echo("Converting image to 3D mesh...")
	image_to_mesh(image_path, mesh_path, z_scale=z_scale, stride=stride)
	click.echo(f"Saved: {mesh_path}")

	# 3) Render turntable GIF
	click.echo("Rendering turntable GIF...")
	render_turntable(mesh_path, gif_path, frames=frames, fps=gif_fps)
	click.echo(f"Saved: {gif_path}")


def main() -> int:
	cli(prog_name="prompt2mesh")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())