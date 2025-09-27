## Prompt → Image → 3D Render (Python CLI)

Generates an image from a text prompt (local fallback), converts it to a heightmap-based 3D mesh, and renders a turntable GIF.

- Text-to-image: local generator (stylized background + prompt text)
- Image-to-3D: grayscale heightmap to mesh (via numpy + trimesh)
- Render: Plotly + Kaleido for static frames; ImageIO for GIF

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

```bash
python -m prompt2mesh.cli run \
  --prompt "a mountain at sunrise" \
  --out ./outputs \
  --width 512 --height 512 \
  --frames 36
```

Outputs in `./outputs`:
- `image.png`
- `mesh.obj`
- `turntable.gif`

### Notes
- No external APIs required for this MVP.
- OBJ is geometry-only.
- The heightmap approach is a simple baseline; for photoreal 3D, integrate a hosted 2D→3D service later.