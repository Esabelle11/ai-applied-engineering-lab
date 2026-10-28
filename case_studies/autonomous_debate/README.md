# Autonomous Debate — grounded podcast replay

This is a compact version of the attached Agent Podcast debate system. It keeps the engineering boundaries that matter without retaining the research, embedding, graph-analysis, TTS, or audio-rendering pipelines:

```text
reviewed research brief -> fixed debate director -> bounded speaker turns -> transcript
                                                    \
                                                     -> optional saved audio replay
```

The saved replay uses the supplied Hackaday research record, the first episode from `episodes.json`, and its matching MP3. They are copied into `data/`, so replay is self-contained and never makes a provider or network call.

```sh
uv run python -m case_studies.autonomous_debate.run --replay
uv run python -m case_studies.autonomous_debate.run --live
uv run --extra providers python -m case_studies.autonomous_debate.run \
  --live --synthesize-audio
```

`--live` makes seven explicit LLM-provider calls using the fixed moderator/Alex/Sarah schedule. Each prompt gets only the reviewed source facts, requires uncertainty to be labelled, and rejects empty turns.

`--synthesize-audio` is a second, explicit network action for a newly generated `--live` transcript. It sends each ordered transcript line to tts.ai's Kokoro endpoint, using `Marcus → am_adam`, `Alex → bm_george`, and `Sarah → af_bella`; it polls unfinished jobs, measures each returned MP3 with `ffprobe`, and writes one concatenated MP3 plus a speaker timeline. Set `TTS_AI_KEY` in `.env` (or the environment). The default output is `artifacts/autonomous_debate/rendered-debate.mp3`; a pre-existing file requires `--overwrite-audio`. `--replay` already has a bundled captured MP3 and therefore rejects `--synthesize-audio`.

`data/` contains:

- `research_disk_polishing_replay.json` — the selected “Disk Polishing Goes Open Source - Hackaday” record;
- `episode_replay.json` — the first captured episode, trimmed to its relevant fields;
- `18ad16d6-8341-4b76-bb61-ed65ef4a1a94.mp3` — that episode’s captured audio.

## Full application reference

For the complete debate-podcast application, see [Autonomous Debate
Ecosystem](https://github.com/Esabelle11/Autonomous-Debate-Ecosystem). It extends
this intentionally small example into an automated, multi-agent editorial and
podcast-production workflow:

```text
Daily news
  → Editorial intelligence and debate selection
  → Topic-specific debate director
  → Phase-driven multi-agent debate
  → Semantic argument graph and analytics
  → Voice production
  → Podcast episode and interactive visualization
```

The full application includes news collection, fact extraction, editorial
scoring, dynamic role briefings, phase-aware memory, semantic relationship
analysis, debate visualization, and automated voice production. This case
study focuses on the smaller, auditable boundary around a reviewed research
brief, a fixed debate schedule, captured replay data, and explicitly authorized
live generation or TTS calls.

The replay transcript is historical model output, not a verified technical recommendation. In particular, claims made by individual speakers beyond the captured research facts should be treated as debate positions, not evidence.
