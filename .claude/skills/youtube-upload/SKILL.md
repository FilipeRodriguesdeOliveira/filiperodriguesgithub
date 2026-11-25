---
name: youtube-upload
description: >
  Publica e agenda vídeos no YouTube pela YouTube Data API v3 (upload resumível,
  título, descrição, tags, categoria, idioma, privacidade, agendamento publishAt,
  thumbnail customizada, playlist, made-for-kids, conteúdo sintético/IA).
  Use quando o usuário pedir para "subir", "postar", "publicar", "agendar" ou
  "fazer upload" de um vídeo ou Short no YouTube, ou trocar a thumbnail de um vídeo.
---

# YouTube Upload — publicação e agendamento

Script: `scripts/upload.py` (Python 3.9+). Dependências: `pip install -r scripts/requirements.txt`.

## Regra de ouro (NÃO pule)

1. **Nunca publique sem aprovação explícita do usuário.** Antes do upload, mostre o
   pacote final (arquivo, título, descrição, tags, privacidade, data de agendamento,
   thumbnail, playlist) e peça "ok". Upload é ação pública e difícil de desfazer.
2. Padrão é `--privacy private`. Só use `public` se o usuário pedir. Para agendar,
   use `--publish-at` (o script força `private` + publishAt, exigência da API).
3. Rode sempre `--dry-run` primeiro: valida arquivo, metadados e limites sem gastar cota.
4. Nunca imprima, comite ou cole tokens/segredos no chat. `client_secret.json` e
   `token.json` ficam fora do repositório (já cobertos pelo `.gitignore`).

## Credenciais (uma vez)

1. Google Cloud Console → crie um projeto → ative **YouTube Data API v3**.
2. Tela de consentimento OAuth (tipo External, adicione seu e-mail como test user).
3. Credenciais → **OAuth client ID → Desktop app** → baixe o JSON.
4. Salve em `~/.config/youtube-upload/client_secret.json` (ou passe `--client-secrets`).
5. Primeira execução abre o fluxo OAuth (escopos `youtube.upload` + `youtube`);
   o token fica em `~/.config/youtube-upload/token.json`.

Em ambiente sem navegador (sessão na nuvem) o fluxo OAuth não completa: rode a
primeira autenticação na máquina do usuário e depois reutilize o `token.json`.

**Atenção a projetos não verificados:** enquanto o app OAuth não passar pela auditoria
do Google, vídeos enviados pela API por projetos criados após 28/07/2020 ficam
travados como privados. Para uso próprio, peça a auditoria (API Services Audit) ou
publique manualmente a partir do privado no YouTube Studio.

## Uso

```bash
python scripts/upload.py --file video.mp4 \
  --title "Título com a keyword no início" \
  --description-file descricao.txt \
  --tags "tag1,tag2,tag3" --category 22 --language pt-BR \
  --privacy private --publish-at 2026-11-20T18:00:00-03:00 \
  --thumbnail thumb.jpg --playlist PLxxxxxxxx \
  --dry-run
```

Remova `--dry-run` após aprovação. Para trocar só a thumbnail de um vídeo existente:
`python scripts/upload.py --set-thumbnail VIDEO_ID --thumbnail thumb.jpg`.

Flags úteis: `--made-for-kids`, `--synthetic-media` (declara conteúdo alterado/gerado
por IA realista — obrigatório pelas políticas do YouTube quando aplicável),
`--notify-subscribers false`, `--license creativeCommon`.

## Limites que o script valida

| Item | Limite |
|------|--------|
| Título | 100 caracteres, sem `<` `>` |
| Descrição | 5000 bytes, sem `<` `>` |
| Tags | soma ~500 caracteres |
| Thumbnail | JPG/PNG, ≤ 2 MB (ideal 1280×720) |
| publishAt | futuro, ISO 8601 com fuso |

## Cota

Cota padrão: 10.000 unidades/dia por projeto. `videos.insert` é a operação mais cara
(historicamente 1.600 unidades; o Google revisou custos em 2025 — confira a tabela
oficial "Quota Calculator" antes de planejar volume). `thumbnails.set` ≈ 50,
`playlistItems.insert` ≈ 50. Planeje lotes de uploads de acordo.

## Shorts

Não existe flag de Short na API: o YouTube classifica como Short o vídeo vertical
(9:16 ou quadrado) com até 3 minutos. Inclua `#Shorts` no título ou descrição só como
reforço. Gere o corte com a skill `video-factory`.

## Saída

O script imprime JSON com `video_id`, `url`, `privacy`, `publish_at`. Registre isso
para o relatório/planilha de conteúdo.
