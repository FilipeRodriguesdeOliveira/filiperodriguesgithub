#!/usr/bin/env python3
"""Upload / schedule a video on YouTube via the Data API v3.

Validates metadata locally first. Use --dry-run to check everything without
touching the API (no credentials needed).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("YOUTUBE_UPLOAD_CONFIG", Path.home() / ".config" / "youtube-upload"))
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".wmv", ".flv", ".webm", ".mkv", ".mpeg", ".mpg", ".3gp"}
THUMB_EXTS = {".jpg", ".jpeg", ".png"}


def die(msg: str) -> None:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def parse_bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "sim", "y"}


def validate(args) -> dict:
    errors, warnings = [], []

    if args.file:
        p = Path(args.file)
        if not p.is_file():
            errors.append(f"arquivo de vídeo não encontrado: {p}")
        elif p.suffix.lower() not in VIDEO_EXTS:
            warnings.append(f"extensão incomum para vídeo: {p.suffix}")

    title = args.title or ""
    if args.file and not title.strip():
        errors.append("título obrigatório")
    if len(title) > 100:
        errors.append(f"título com {len(title)} caracteres (máx. 100)")
    if any(c in title for c in "<>"):
        errors.append("título não pode conter < ou >")

    description = ""
    if args.description_file:
        description = Path(args.description_file).read_text(encoding="utf-8")
    elif args.description:
        description = args.description
    if len(description.encode("utf-8")) > 5000:
        errors.append(f"descrição com {len(description.encode('utf-8'))} bytes (máx. 5000)")
    if any(c in description for c in "<>"):
        errors.append("descrição não pode conter < ou >")

    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    # API counts tags with spaces as quoted (+2 chars) and separators.
    tag_len = sum(len(t) + (2 if " " in t else 0) for t in tags) + max(len(tags) - 1, 0)
    if tag_len > 500:
        errors.append(f"tags somam {tag_len} caracteres (máx. ~500)")

    publish_at = None
    if args.publish_at:
        try:
            when = dt.datetime.fromisoformat(args.publish_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("publish-at inválido; use ISO 8601, ex. 2026-11-20T18:00:00-03:00")
        else:
            if when.tzinfo is None:
                errors.append("publish-at precisa de fuso horário (ex. -03:00)")
            elif when <= dt.datetime.now(dt.timezone.utc):
                errors.append("publish-at precisa estar no futuro")
            else:
                publish_at = when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
                if args.privacy != "private":
                    warnings.append("agendamento exige privacy=private; ajustado automaticamente")
                    args.privacy = "private"

    if args.thumbnail:
        t = Path(args.thumbnail)
        if not t.is_file():
            errors.append(f"thumbnail não encontrada: {t}")
        else:
            if t.suffix.lower() not in THUMB_EXTS:
                errors.append("thumbnail deve ser JPG ou PNG")
            if t.stat().st_size > 2 * 1024 * 1024:
                errors.append("thumbnail maior que 2 MB")

    if args.privacy == "public":
        warnings.append("privacy=public: o vídeo fica visível imediatamente após o processamento")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": str(args.category),
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": bool(args.made_for_kids),
            "license": args.license,
            "embeddable": True,
        },
    }
    if args.language:
        body["snippet"]["defaultLanguage"] = args.language
        body["snippet"]["defaultAudioLanguage"] = args.language
    if publish_at:
        body["status"]["publishAt"] = publish_at
    if args.synthetic_media:
        body["status"]["containsSyntheticMedia"] = True

    return {"errors": errors, "warnings": warnings, "body": body}


def get_service(client_secrets: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        die("dependências ausentes: pip install -r scripts/requirements.txt")

    token_path = CONFIG_DIR / "token.json"
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secrets.exists():
                die(f"client_secret não encontrado em {client_secrets}. Veja a seção Credenciais do SKILL.md")
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")
        os.chmod(token_path, 0o600)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def resumable_upload(youtube, body: dict, file_path: str, notify: bool) -> str:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    import random
    import time

    media = MediaFileUpload(file_path, chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media, notifySubscribers=notify
    )
    response, retries = None, 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"progresso: {int(status.progress() * 100)}%", file=sys.stderr)
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and retries < 8:
                retries += 1
                time.sleep(min(2 ** retries, 64) + random.random())
                continue
            die(f"erro da API ({e.resp.status}): {e}")
        except (ConnectionError, TimeoutError, OSError) as e:
            if retries < 8:
                retries += 1
                time.sleep(min(2 ** retries, 64) + random.random())
                continue
            die(f"falha de rede: {e}")
    if "id" not in response:
        die(f"resposta inesperada: {response}")
    return response["id"]


def set_thumbnail(youtube, video_id: str, thumb: str) -> None:
    from googleapiclient.http import MediaFileUpload

    youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb)).execute()


def add_to_playlist(youtube, video_id: str, playlist_id: str) -> None:
    youtube.playlistItems().insert(
        part="snippet",
        body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
    ).execute()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="arquivo de vídeo")
    ap.add_argument("--title")
    ap.add_argument("--description")
    ap.add_argument("--description-file")
    ap.add_argument("--tags", help="separadas por vírgula")
    ap.add_argument("--category", default="22", help="22=People&Blogs, 27=Education, 28=Science&Tech, 24=Entertainment, 26=Howto&Style")
    ap.add_argument("--language", help="ex. pt-BR")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    ap.add_argument("--publish-at", help="ISO 8601 com fuso; força private + agendamento")
    ap.add_argument("--thumbnail")
    ap.add_argument("--playlist")
    ap.add_argument("--made-for-kids", action="store_true")
    ap.add_argument("--synthetic-media", action="store_true", help="declara conteúdo realista gerado/alterado por IA")
    ap.add_argument("--license", choices=["youtube", "creativeCommon"], default="youtube")
    ap.add_argument("--notify-subscribers", default="true")
    ap.add_argument("--set-thumbnail", metavar="VIDEO_ID", help="só troca a thumbnail de um vídeo existente")
    ap.add_argument("--client-secrets", default=str(CONFIG_DIR / "client_secret.json"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.set_thumbnail:
        if not args.thumbnail:
            die("--set-thumbnail exige --thumbnail")
        v = validate(args)
        if v["errors"]:
            die("; ".join(v["errors"]))
        if args.dry_run:
            print(json.dumps({"ok": True, "dry_run": True, "action": "set_thumbnail", "video_id": args.set_thumbnail}))
            return
        yt = get_service(Path(args.client_secrets))
        set_thumbnail(yt, args.set_thumbnail, args.thumbnail)
        print(json.dumps({"ok": True, "video_id": args.set_thumbnail, "thumbnail": "updated"}))
        return

    if not args.file:
        die("--file é obrigatório (ou use --set-thumbnail)")

    v = validate(args)
    for w in v["warnings"]:
        print(f"aviso: {w}", file=sys.stderr)
    if v["errors"]:
        die("; ".join(v["errors"]))

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "request_body": v["body"],
                          "thumbnail": args.thumbnail, "playlist": args.playlist}, ensure_ascii=False, indent=2))
        return

    yt = get_service(Path(args.client_secrets))
    video_id = resumable_upload(yt, v["body"], args.file, parse_bool(args.notify_subscribers))
    result = {
        "ok": True,
        "video_id": video_id,
        "url": f"https://youtu.be/{video_id}",
        "privacy": v["body"]["status"]["privacyStatus"],
        "publish_at": v["body"]["status"].get("publishAt"),
    }
    if args.thumbnail:
        try:
            set_thumbnail(yt, video_id, args.thumbnail)
            result["thumbnail"] = "set"
        except Exception as e:  # channel may not be verified for custom thumbnails
            result["thumbnail_error"] = str(e)
    if args.playlist:
        try:
            add_to_playlist(yt, video_id, args.playlist)
            result["playlist"] = args.playlist
        except Exception as e:
            result["playlist_error"] = str(e)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
