# Pelican Bike Art

A self-contained Python/Pillow art project that generates a polished PNG of a pelican riding a bicycle.

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
- The generated image is deterministic.
- Canvas size defaults to `1400x1000`.
