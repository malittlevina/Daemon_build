# Daemon Dictionary Training Data

This directory contains resources for training and maintaining the daemon's vocabulary, specifically focusing on pronunciation and enunciation of system-specific terminology.

## Files

- **`pronunciation_dictionary.json`**: The core dataset containing terms, phonetic spellings (IPA and simple), stress patterns, and enunciation guides.
- **`vocabulary_manager.py`**: A Python class (`VocabularyManager`) to programmatically interface with the dictionary.

## Usage

### Adding new terms

You can manually edit `pronunciation_dictionary.json` or use the `VocabularyManager` class:

```python
from daemon.training_data.vocabulary_manager import VocabularyManager

vocab = VocabularyManager()
vocab.add_entry(
    term="NewModule",
    phonetic="NOO-mod-yool",
    ipa="/nuːˈmɒdjuːl/",
    category="Extension",
    enunciation="Standard pronunciation"
)
```

### JSON Structure

Each entry in the dictionary has the following fields:

- `term`: The word or phrase.
- `phonetic`: A user-friendly phonetic spelling (e.g., "YOU-nih-mind").
- `ipa`: International Phonetic Alphabet representation.
- `stress_pattern`: Digital representation of stress (1=primary, 0=unstressed).
- `category`: Classification of the term.
- `enunciation_guide`: Human-readable tips for correct speech synthesis or correction.
- `usage_context`: Brief description of what the term refers to.
