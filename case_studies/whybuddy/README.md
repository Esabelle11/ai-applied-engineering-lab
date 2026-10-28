# WhyBuddy — Question to Learning Video

WhyBuddy has two complete modes:

```text
--live:   question -> LLM lesson -> Stable Diffusion slides -> TTS narration -> MP4
--replay: saved bee lesson -> saved PNGs + MP3 + completed MP4
```

## Replay the supplied lesson

```sh
uv run python -m case_studies.whybuddy.run --replay
```

This makes no model, image, or TTS request. It returns the supplied lesson for
“Why do bees make honey?” and its finished video:

[final_eebf368b7c694705b673059aa602c7a3.mp4](data/bee_honey_replay/final_eebf368b7c694705b673059aa602c7a3.mp4)

The replay bundle also contains the seven individual slide PNGs, narration MP3,
and the intermediate no-audio slideshow MP4 from the supplied `results` folder.

## Create a live video

Set a live LLM provider/model and `TTS_AI_KEY` in `.env`, then install the
optional image dependencies:

```sh
uv sync --extra media --extra providers
uv run --extra media --extra providers python -m case_studies.whybuddy.run --live \
  --question "Why do bees make honey?"
```

One `--live` command runs the entire workflow. It creates a new directory such
as `artifacts/whybuddy/<id>/` containing:

- `lesson.json` — the LLM question, narration, image prompts, provider, and model;
- `slide_0.png`, `slide_1.png`, … — one DreamShaper image per prompt;
- `narration.mp3` — the full narration from the SDK’s tts.ai adapter;
- `lesson.mp4` — the PNGs and MP3 combined with `ffmpeg`.

Pass `--output-dir path/to/new-folder` to select a folder. It must not already
exist, so a live run cannot overwrite a previous lesson accidentally.

The default image model is `Lykon/dreamshaper-7`, following the supplied
notebook. Its weights are downloaded by Diffusers on first use. `ffmpeg` must
be installed and available on `PATH`.

## Limits

This is a learning reference, not a production child-safety system. Review
generated explanations and imagery, follow the selected model and voice
provider licenses, and apply appropriate moderation before showing content to
children.
