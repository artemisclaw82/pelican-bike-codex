# Pelican Bike Art

A self-contained Python/Pillow art project that generates a polished PNG of a pelican riding a bicycle. The scene is drawn procedurally with a visible saddle, pedals, webbed feet, and a recognizable pelican beak and pouch.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate

```bash
python main.py
```

The image is written to:

```text
output/pelican_bike.png
```

## Notes

- Uses only Pillow for rendering.
- Renders at 2x resolution, then downsamples with Lanczos antialiasing for smoother edges.
- The generated image is deterministic.
- Canvas size defaults to `1400x1000`.
