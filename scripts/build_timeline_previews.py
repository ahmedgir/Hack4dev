from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]


def stretch(data: np.ndarray) -> np.ndarray:
    finite = data[np.isfinite(data)]
    if not finite.size:
        return np.zeros(data.shape, dtype=np.uint8)
    low, high = np.percentile(finite, [5, 99.7])
    scaled = np.clip((data - low) / max(high - low, 1e-6), 0, 1)
    return (np.arcsinh(8 * scaled) / np.arcsinh(8) * 255).astype(np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a WebP preview for every frame in one analysed session.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--size", type=int, default=520)
    args = parser.parse_args()
    output_dir = ROOT / "outputs" / args.target.lower().replace("-", "_") / args.date
    timeline_path = output_dir / "web_timeline.json"
    if not timeline_path.exists():
        raise FileNotFoundError(f"Run the pipeline first; missing {timeline_path}")
    points = json.loads(timeline_path.read_text(encoding="utf-8"))
    session_dirs = sorted((ROOT / "database" / "observations" / args.date / args.target).glob("session_*"))
    if not session_dirs:
        raise FileNotFoundError("Science session not found")
    science_paths = sorted(session_dirs[0].glob("*.fits"))
    if len(points) != len(science_paths):
        raise RuntimeError("Timeline and FITS frame counts differ; rerun the pipeline")
    destination = output_dir / "timeline_frames"
    destination.mkdir(parents=True, exist_ok=True)
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    target_x = summary["target_x_reference"]
    target_y = summary["target_y_reference"]
    for point, path in zip(points, science_paths):
        data = fits.getdata(path).astype("float32")
        image = Image.fromarray(stretch(data), mode="L").convert("RGB")
        image.thumbnail((args.size, args.size), Image.Resampling.LANCZOS)
        scale_x = image.width / data.shape[1]
        scale_y = image.height / data.shape[0]
        x = (target_x + point["shift_x"]) * scale_x
        y = image.height - (target_y + point["shift_y"]) * scale_y
        draw = ImageDraw.Draw(image)
        color = "#22c55e" if point["accepted"] else "#ef4444"
        radius = 12
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=3)
        image.save(destination / f'{point["frame_index"]:04d}.webp', "WEBP", quality=72, method=6)
    print(f"Built {len(points)} timeline previews in {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
