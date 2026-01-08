## Daemon Dictionary (pronunciation + enunciation training data)

This folder is a **human-curated lexicon** for daemon names, subsystems, rituals, and other “high value” tokens that speech-to-text often mishears.

It serves two practical purposes:

- **Transcription biasing**: generate a prompt for Whisper (“these are important words/phrases”).
- **Post-processing normalization**: map common variants/mishearings to canonical forms before routing into NLU / rituals.

### Files

- `lexicon.jsonl`: one JSON object per line; easy to append/merge in git.
- `whisper_prompt.txt`: generated from `lexicon.jsonl` (optional, but recommended).

### `lexicon.jsonl` schema (per line)

Each line is a standalone JSON object:

```json
{
  "term": "Prometheus",
  "aliases": ["promethius", "pro meteus"],
  "pronunciation": {
    "ipa": "prəˈmiːθiəs",
    "arpabet": "P R AH0 M IY1 TH IY0 AH0 S"
  },
  "enunciation": {
    "syllables": ["pro", "MEE", "thee", "us"],
    "stress_hint": "primary stress on MEE"
  },
  "domain": "hotword",
  "notes": "Daemon name / invocation keyword"
}
```

Guidance:

- **`term`**: canonical casing (what you want downstream systems to see).
- **`aliases`**: common mishearings or alternate spellings; keep them lowercase if possible.
- **`pronunciation.ipa`**: good for humans; **`arpabet`** is useful if you later adopt a phoneme-based lexicon.
- **`enunciation`**: optional coaching metadata (stress, syllable splits, pacing cues).

### How it plugs into the system

- `voice/voice_listener.py`: normalizes recognized phrases (aliases → canonical term) and can strip a hotword prefix.
- `voice/transcriber.py`: optionally injects `whisper_prompt.txt` as Whisper’s `initial_prompt` to bias recognition toward your daemon vocabulary.

### Updating the prompt (optional)

Generate/refresh `whisper_prompt.txt` from your lexicon:

```bash
python -m daemon_dictionary.build_whisper_prompt
```

