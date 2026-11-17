#!/usr/bin/env python3
"""Corta um trecho de um vídeo horizontal e gera um Short vertical 9:16 (1080x1920).

Modos de enquadramento:
  crop  - recorta o centro (rosto/ação no meio do quadro)
  blur  - vídeo inteiro no centro com fundo desfocado (bom para telas/slides)

Opcional: legenda queimada (.srt), normalização de áudio (-14 LUFS), texto de gancho no topo.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def ts(v: str) -> float:
    parts = [float(p) for p in v.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def esc_filter_path(p: Path) -> str:
    s = str(p.resolve())
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--start", required=True, help="ex. 00:01:23 ou 83.5")
    ap.add_argument("--end", required=True)
    ap.add_argument("--mode", choices=["crop", "blur"], default="crop")
    ap.add_argument("--x-offset", type=float, default=0.5, help="crop: posição horizontal 0..1 (0.5=centro)")
    ap.add_argument("--srt", help="legenda .srt para queimar (tempos relativos ao vídeo ORIGINAL)")
    ap.add_argument("--hook", help="texto fixo no topo nos primeiros segundos")
    ap.add_argument("--hook-seconds", type=float, default=3.0)
    ap.add_argument("--no-loudnorm", action="store_true")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true", help="só imprime o comando ffmpeg")
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado no PATH")
    start, end = ts(a.start), ts(a.end)
    dur = end - start
    if dur <= 0:
        sys.exit("--end precisa ser maior que --start")
    warnings = []
    if dur > 180:
        warnings.append(f"duração {dur:.0f}s > 180s: não será classificado como Short")
    elif dur > 60:
        warnings.append(f"duração {dur:.0f}s: Shorts até 3 min são aceitos, mas 20-45s costuma reter melhor")

    if a.mode == "crop":
        x = max(0.0, min(1.0, a.x_offset))
        vf = [f"crop='min(iw,ih*9/16)':ih:'(iw-min(iw,ih*9/16))*{x}':0", "scale=1080:1920:flags=lanczos", "setsar=1"]
        chain = ",".join(vf)
        fc = f"[0:v]{chain}[v0]"
    else:
        fc = ("[0:v]split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
              "[b]scale=1080:-2:flags=lanczos[fg];"
              "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v0]")

    last = "v0"
    if a.srt:
        srt = Path(a.srt)
        if not srt.is_file():
            sys.exit(f"srt não encontrado: {srt}")
        # input is seeked with -ss before -i, so shift subtitles by -start via setpts trick
        style = "Fontname=Arial,Fontsize=14,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=90"
        fc += (f";[{last}]setpts=PTS+{start}/TB,subtitles='{esc_filter_path(srt)}':force_style='{style}',"
               f"setpts=PTS-{start}/TB[v1]")
        last = "v1"
    if a.hook:
        hook_file = Path(a.output).with_suffix(".hook.txt")
        hook_file.write_text(a.hook, encoding="utf-8")
        fc += (f";[{last}]drawtext=textfile='{esc_filter_path(hook_file)}':expansion=none:fontcolor=white:fontsize=72:borderw=6:bordercolor=black:"
               f"x=(w-text_w)/2:y=h*0.12:enable='lt(t,{a.hook_seconds})'[v2]")
        last = "v2"

    cmd = ["ffmpeg", "-hide_banner", "-y", "-ss", f"{start}", "-i", a.input, "-t", f"{dur}",
           "-filter_complex", fc, "-map", f"[{last}]", "-map", "0:a?"]
    if not a.no_loudnorm:
        cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", a.output]

    if a.dry_run:
        print(json.dumps({"cmd": cmd, "warnings": warnings}, ensure_ascii=False, indent=2))
        return
    for w in warnings:
        print(f"aviso: {w}", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if a.hook:
        hook_file.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-3000:])
    print(json.dumps({"ok": True, "output": a.output, "duration_s": round(dur, 2), "warnings": warnings}, ensure_ascii=False))


if __name__ == "__main__":
    main()
