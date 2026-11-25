---
name: youtube-autopilot
description: >
  Orquestra o pipeline completo de conteúdo para YouTube e redes: pesquisa → ideia →
  roteiro → produção do vídeo → cortes/Shorts → metadados/SEO → thumbnail → upload
  agendado → distribuição em Instagram/TikTok/LinkedIn → captura de leads → análise.
  Use quando o usuário pedir "automatizar o canal", "pipeline de vídeo", "produzir e
  postar", "semana de conteúdo", "do vídeo ao lead" ou um fluxo que junte várias etapas.
---

# YouTube Autopilot — do tema ao lead

Você é o diretor de operação. Não refaça o trabalho das outras skills: chame cada uma
na ordem, passe a saída adiante e pare nos portões de aprovação.

## Pré-requisitos (pergunte só o que faltar)

1. Nicho específico + oferta (o que o canal vende: serviço, produto, consultoria).
2. **Destino do lead**: link de WhatsApp, landing page, formulário ou isca digital.
   Sem isso, o pipeline gera views, não clientes — avise o usuário.
3. Tamanho do canal e meta do mês (views, inscritos ou leads).
4. Frequência: ex. 1 vídeo longo + 5 Shorts/semana.

## Pipeline

| # | Etapa | Ferramenta | Saída |
|---|-------|-----------|-------|
| 1 | Pesquisa de demanda e concorrentes | `last30days <tema do nicho>` (o que o público reclamou/perguntou nos últimos 30 dias em Reddit, X, YouTube, TikTok); `youtube` → `/youtube ideate`, `/youtube competitor`; `youtube-full` para transcrições dos concorrentes | 10 ideias ranqueadas por demanda × intenção de compra, cada uma com a frase real do público que a originou |
| 2 | Roteiro com retenção | `youtube` → `/youtube script` + `/youtube hook` | Roteiro com gancho de 0–30 s e CTA para o destino do lead |
| 3 | Produção | Gravação do usuário **ou** `remotion-best-practices` (motion/listas) **ou** Kling AI / HeyGen (IA) | `master.mp4` |
| 4 | Cortes verticais | `video-factory` → `make_short.py` (3–8 cortes) | `short_XX.mp4` |
| 5 | Thumbnail | `youtube` → `/youtube thumbnail` + `video-factory/thumb_candidates.py` + Canva/Adobe | `thumb.jpg` ≤ 2 MB |
| 6 | Metadados/SEO | `youtube` → `/youtube metadata` | título, descrição com link do lead + UTM, tags, capítulos |
| 7 | **Portão de aprovação** | mostrar tudo ao usuário | "ok" explícito |
| 8 | Upload agendado | `youtube-upload` (`--dry-run` → upload real) | `video_id` + URL |
| 9 | Distribuição | skill `postiz` (Instagram, TikTok, LinkedIn, X, Facebook) | posts agendados |
| 10 | Medição | `youtube` → `/youtube analyze`; Supermetrics se conectado | relatório semanal |

## Regras inegociáveis

- **Nada público sem aprovação.** Etapas 8 e 9 publicam em nome do usuário: confirme antes.
- **Gerações pagas** (Kling, HeyGen, DataForSEO, TranscriptAPI): informe o custo estimado
  e peça confirmação antes de disparar em lote.
- **UTM em todo link** da descrição e das redes:
  `?utm_source=youtube&utm_medium=video&utm_campaign=<slug-do-video>` (troque
  `utm_source` por instagram/tiktok em cada rede). Sem UTM não dá para saber qual
  vídeo gera lead.
- **Conteúdo de IA realista** → `--synthetic-media` no upload (política do YouTube).
- **Não copie** roteiros ou vídeos de concorrentes: extraia padrões (formato, gancho,
  estrutura), nunca o texto.
- Volume sem qualidade queima o canal: prefira 1 vídeo forte a 5 genéricos.

## Do view ao lead (o que a maioria esquece)

1. CTA verbal no minuto 1–2 e no final, apontando para UMA ação.
2. Link do lead na primeira linha da descrição + comentário fixado.
3. Shorts apontam para o vídeo longo relacionado (recurso "vídeo relacionado") e o
   longo aponta para o lead.
4. Isca específica do vídeo (checklist, planilha, diagnóstico) converte mais que
   "fale comigo".
5. Registre `video_id`, UTM e leads gerados numa planilha (Airtable/HubSpot se conectado)
   para cortar o que não converte.

## Relatório semanal (formato)

| Vídeo | Views | CTR | Retenção média | Cliques no link | Leads | Custo por lead |
|-------|-------|-----|----------------|-----------------|-------|----------------|

Termine sempre com: o que dobrar, o que cortar e o próximo teste.
