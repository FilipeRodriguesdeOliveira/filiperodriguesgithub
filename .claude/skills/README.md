# Skills de YouTube, vídeo e postagem

Skills de projeto do Claude Code: carregam automaticamente quando o Claude Code roda
neste repositório. Para usar em qualquer projeto na sua máquina, copie as pastas para
`~/.claude/skills/`.

| Skill | Origem | Função | Precisa de |
|-------|--------|--------|-----------|
| `youtube` | [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube) @ `84c3fa6` (MIT) | Auditoria, SEO, roteiro, hook, thumbnail, Shorts, calendário, monetização, concorrentes (`/youtube <comando>`) | Opcional: `YOUTUBE_API_KEY`, DataForSEO MCP |
| `youtube-full` | [ZeroPointRepo/youtube-skills](https://github.com/ZeroPointRepo/youtube-skills) @ `4f7994b` (MIT) | Transcrições, busca, canais e playlists do YouTube | `TRANSCRIPT_API_KEY` (serviço terceiro, 100 créditos grátis) |
| `remotion-best-practices` | [remotion-dev/skills](https://github.com/remotion-dev/skills) @ `3e20ac7` | Criar vídeos programáticos em React (motion graphics, legendas animadas, render) | Node.js; licença Remotion paga para empresas com 4+ pessoas |
| `youtube-upload` | própria | Upload/agendamento via YouTube Data API v3, thumbnail, playlist | OAuth do Google Cloud (ver SKILL.md) |
| `video-factory` | própria | Cortes 9:16 para Shorts/Reels/TikTok, legenda queimada, gancho, -14 LUFS, thumbnails | `ffmpeg` |
| `youtube-autopilot` | própria | Orquestra o pipeline completo até a captura de lead | as skills acima |
| `last30days` | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) @ `7c2e1c2` v4.6.0 (MIT) | Pesquisa o que as pessoas disseram nos últimos 30 dias sobre um tema (Reddit, X, YouTube, TikTok, HN, Polymarket, GitHub, web) — use para achar dores e ganchos antes de roteirizar (`/last30days <tema>`) | Python 3; grátis com Reddit/HN/web; opcional `yt-dlp` (YouTube), `SCRAPECREATORS_API_KEY` (TikTok/Instagram), chaves de X. Leitura de cookies do navegador só com consentimento explícito |

`last30days` foi copiado sem as imagens/áudio de demonstração (14 MB) e sem os scripts de
desenvolvimento, conforme o `.skillignore` do próprio projeto. Alternativa com atualização
automática no seu computador: `/plugin marketplace add mvanhorn/last30days-skill` e depois
`/plugin install last30days` (não use as duas formas juntas, senão o comando aparece duplicado).

Postagem em Instagram/TikTok/LinkedIn: skill `postiz` (plugin já disponível na conta).

## Atualizar as skills de terceiros

```bash
git clone --depth 1 https://github.com/AgriciDaniel/claude-youtube /tmp/cy && rsync -a --delete --exclude LICENSE /tmp/cy/skills/claude-youtube/ .claude/skills/youtube/
```

Revise o diff antes de commitar: skills executam instruções e scripts com as suas permissões.
