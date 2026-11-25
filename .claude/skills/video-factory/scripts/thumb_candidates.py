#!/usr/bin/env python3
"""Extrai N frames candidatos a thumbnail (1280x720, JPG < 2 MB) nos cortes de cena mais fortes."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("outdir")
    ap.add_argument("-n", type=int, default=8)
    ap.add_argument("--threshold", type=float, default=0.3, help="sensibilidade de troca de cena (0-1)")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado no PATH")

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.input, "-vf", f"select='gt(scene,{a.threshold})',showinfo",
                        "-f", "null", "-"], capture_output=True, text=True)
    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
    total = duration(a.input)
    if len(times) < a.n and total > 0:  # fallback: evenly spaced, skipping first/last 5%
        step = total * 0.9 / (a.n + 1)
        times += [total * 0.05 + step * (i + 1) for i in range(a.n)]
    # spread picks across the video
    times = sorted(set(round(t, 2) for t in times))
    if len(times) > a.n:
        idx = [round(i * (len(times) - 1) / (a.n - 1)) for i in range(a.n)] if a.n > 1 else [0]
        times = [times[i] for i in idx]

    files = []
    for i, t in enumerate(times[: a.n], 1):
        f = out / f"thumb_{i:02d}_{t:.1f}s.jpg"
        subprocess.run(["ffmpeg", "-hide_banner", "-y", "-ss", str(t), "-i", a.input, "-frames:v", "1",
                        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", "-q:v", "3", str(f)],
                       capture_output=True)
        if f.exists():
            files.append({"file": str(f), "time_s": t, "bytes": f.stat().st_size})
    print(json.dumps({"ok": True, "candidates": files}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
