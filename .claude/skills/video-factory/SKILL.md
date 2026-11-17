---
name: video-factory
description: >
  Produção e edição de vídeo local com ffmpeg: cortar vídeo longo em Shorts/Reels/TikTok
  9:16 (crop central ou fundo desfocado), queimar legendas .srt, texto de gancho,
  normalizar áudio para -14 LUFS, e extrair frames candidatos a thumbnail 1280x720.
  Use quando o usuário pedir "cortes", "fazer Shorts", "transformar em vertical",
  "legendar", "repurpose", "thumbnail do vídeo" ou preparar arquivos para upload.
---

# Video Factory — cortes, Shorts e thumbnails com ffmpeg

Requisito: `ffmpeg` e `ffprobe` no PATH. Sem dependências Python externas.

## 1. Short vertical a partir de vídeo longo

```bash
python scripts/make_short.py entrada.mp4 short_01.mp4 \
  --start 00:03:12 --end 00:03:41 --mode crop \
  --srt legendas.srt --hook "O erro que custa 80% dos seus leads"
```

- `--mode crop`: pessoa falando no centro. Ajuste `--x-offset 0.3` se estiver à esquerda.
- `--mode blur`: tela/slides/gravação de tela — mantém tudo visível com fundo desfocado.
- `--srt` usa tempos do vídeo original (o script compensa o corte).
- Áudio normalizado a -14 LUFS (padrão de plataformas); desligue com `--no-loudnorm`.
- Saída: H.264 1080x1920 30fps, AAC 48 kHz, `+faststart` — aceita por YouTube, Instagram, TikTok.
- Use `--dry-run` para ver o comando ffmpeg sem renderizar.

## 2. Como escolher os trechos (o que realmente importa)

Cortar é fácil; escolher o trecho certo é o trabalho. Processo:

1. Obtenha a transcrição com timestamps (skill `youtube-full` para vídeos publicados,
   ou Whisper local: `pip install faster-whisper`).
2. Selecione 3–8 trechos de 20–45 s que tenham: **gancho nos primeiros 2 s**
   (afirmação forte, número, contradição), **uma única ideia** e **fim com payoff**.
3. Descarte trechos que dependem de contexto anterior ("como eu disse antes...").
4. Para cada trecho, escreva um gancho de tela de até 8 palavras.

## 3. Thumbnails candidatas

```bash
python scripts/thumb_candidates.py video.mp4 thumbs/ -n 8
```

Gera JPGs 1280x720 nos cortes de cena. Frames são só base: thumbnails que convertem
normalmente têm rosto com emoção clara, ≤ 4 palavras e alto contraste. Para gerar a
arte final use a skill `youtube` (`/youtube thumbnail`) para o briefing e Canva,
Adobe ou Kling AI (se conectados) para executar.

## 4. Vídeo do zero (sem gravação)

- Vídeo programático (motion graphics, listas, dados, legendas animadas):
  skill `remotion-best-practices`.
- Cenas geradas por IA: conector Kling AI (`text_to_video`, `image_to_video`).
  Toda geração é cobrada — confirme parâmetros com o usuário antes.
- Avatar/apresentador: HeyGen (HyperFrames), se autorizado.
- Se o vídeo tiver pessoas/cenas realistas geradas por IA, publique com
  `--synthetic-media` na skill `youtube-upload`.

## Checklist de entrega

- [ ] 9:16, 1080x1920, ≤ 3 min (Short) — idealmente 20–45 s
- [ ] Legenda queimada legível (a maioria assiste sem som)
- [ ] Gancho visual/texto nos primeiros 2 s
- [ ] Áudio sem clipping, -14 LUFS
- [ ] Thumbnail JPG ≤ 2 MB (vídeos longos)
