import hashlib
import math
import random
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def _seed_from_prompt(prompt: str, seed: int | None) -> int:
	if seed is not None:
		return int(seed)
	digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
	return int(digest[:8], 16)


def _generate_background(width: int, height: int, rng: random.Random) -> Image.Image:
	img = Image.new("RGB", (width, height))
	pixels = img.load()

	# Radial gradient + noise
	cx = width / 2.0
	cy = height / 2.0
	max_r = math.sqrt(cx * cx + cy * cy)

	base_r = rng.randint(40, 140)
	base_g = rng.randint(40, 140)
	base_b = rng.randint(40, 140)

	for y in range(height):
		for x in range(width):
			dx = x - cx
			dy = y - cy
			r = math.sqrt(dx * dx + dy * dy)
			t = r / max_r

			# Gradient color
			r_c = int((1 - t) * (base_r + 60) + t * base_r)
			g_c = int((1 - t) * (base_g + 60) + t * base_g)
			b_c = int((1 - t) * (base_b + 60) + t * base_b)

			# Dithered noise
			n = rng.randint(-12, 12)
			pixels[x, y] = (
				max(0, min(255, r_c + n)),
				max(0, min(255, g_c + n)),
				max(0, min(255, b_c + n)),
			)
	return img


def _draw_prompt_text(img: Image.Image, prompt: str, rng: random.Random) -> None:
	draw = ImageDraw.Draw(img)
	try:
		font = ImageFont.load_default()
	except Exception:
		font = None

	max_width = int(img.width * 0.8)
	text = prompt.strip()[:180] if prompt else "No prompt"

	# Basic wrapping
	lines = []
	words = text.split()
	current = []
	for w in words:
		cand = " ".join(current + [w])
		w_size = draw.textlength(cand, font=font)
		if w_size <= max_width or not current:
			current.append(w)
		else:
			lines.append(" ".join(current))
			current = [w]
	if current:
		lines.append(" ".join(current))

	# Position in center
	line_height = (draw.textbbox((0, 0), "Ag", font=font)[3] if font else 12) + 6
	total_height = line_height * len(lines)
	y = (img.height - total_height) // 2

	# Slight shadow for contrast
	for idx, line in enumerate(lines):
		w = draw.textlength(line, font=font)
		x = (img.width - int(w)) // 2
		# Shadow
		draw.text((x + 2, y + idx * line_height + 2), line, fill=(0, 0, 0), font=font)
		# Text
		draw.text((x, y + idx * line_height), line, fill=(240, 240, 240), font=font)


def generate_image(
	prompt: str,
	size: Tuple[int, int] = (512, 512),
	seed: int | None = None,
) -> Image.Image:
	"""
	Local fallback text-to-image: generates a stylized background and overlays prompt text.
	"""
	width, height = size
	s = _seed_from_prompt(prompt, seed)
	rng = random.Random(s)
	img = _generate_background(width, height, rng)
	_draw_prompt_text(img, prompt, rng)
	return img