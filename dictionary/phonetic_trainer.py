# dictionary/phonetic_trainer.py
"""
Phonetic Trainer for Daemon Dictionary

Provides utilities for pronunciation training, validation, and generating
audio training datasets. Integrates with the lexicon for pronunciation
guidance and speech synthesis preparation.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from dictionary.lexicon_loader import get_lexicon, LexiconLoader


class PhoneticTrainer:
    """
    Training utility for daemon pronunciation and enunciation.
    Supports drill generation, progress tracking, and audio sample management.
    """
    
    def __init__(self, progress_file: str = "dictionary/training_progress.json"):
        self.lexicon = get_lexicon()
        self.progress_file = progress_file
        self.progress = self._load_progress()
        print("[PhoneticTrainer] Initialized.")
    
    def _load_progress(self) -> Dict:
        """Load training progress from file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "sessions": [],
            "word_scores": {},
            "drill_completions": {},
            "total_practice_minutes": 0
        }
    
    def _save_progress(self):
        """Save training progress to file."""
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2)
    
    # ========== Pronunciation Guides ==========
    
    def get_pronunciation_guide(self, word: str) -> Optional[Dict]:
        """
        Get a comprehensive pronunciation guide for a word.
        
        Args:
            word: The word to get guidance for
            
        Returns:
            Dictionary with pronunciation details and tips
        """
        entry = self.lexicon.lookup(word)
        if not entry:
            return None
            
        guide = {
            "word": word,
            "ipa": entry.get("ipa"),
            "phonetic_spelling": entry.get("phonetic_spelling"),
            "syllables": entry.get("syllables"),
            "stress_pattern": entry.get("stress"),
            "emphasis": entry.get("emphasis"),
            "tips": self._generate_pronunciation_tips(word, entry)
        }
        
        return guide
    
    def _generate_pronunciation_tips(self, word: str, entry: Dict) -> List[str]:
        """Generate pronunciation tips based on word characteristics."""
        tips = []
        
        # Stress tips
        stress = entry.get("stress", [])
        syllables = entry.get("syllables", [])
        if stress and syllables:
            stressed_idx = [i for i, s in enumerate(stress) if s == 1]
            for idx in stressed_idx:
                if idx < len(syllables):
                    tips.append(f"Emphasize the syllable '{syllables[idx].upper()}'")
        
        # Special sound tips
        ipa = entry.get("ipa", "")
        if "θ" in ipa:
            tips.append("Contains voiceless 'th' - tongue between teeth, no vibration")
        if "ð" in ipa:
            tips.append("Contains voiced 'th' - tongue between teeth with vibration")
        if "ə" in ipa:
            tips.append("Contains schwa sound - unstressed, neutral vowel like 'uh'")
        if "ʃ" in ipa:
            tips.append("Contains 'sh' sound - lips slightly rounded")
        if "ʒ" in ipa:
            tips.append("Contains 'zh' sound - like 's' in 'measure'")
            
        # Category-specific tips
        category = entry.get("category", "")
        if category == "proper_noun":
            tips.append("Proper noun - maintain consistent pronunciation")
        if category == "verb":
            tips.append("As a verb, may have different stress than noun form")
            
        return tips
    
    def get_syllable_breakdown(self, word: str) -> Optional[str]:
        """
        Get a visual syllable breakdown with stress markers.
        
        Args:
            word: The word to break down
            
        Returns:
            String like "pro-MEE-thee-us" showing syllables and stress
        """
        entry = self.lexicon.lookup(word)
        if not entry:
            return None
            
        syllables = entry.get("syllables", [])
        stress = entry.get("stress", [])
        
        if not syllables:
            return None
            
        result_parts = []
        for i, syllable in enumerate(syllables):
            if i < len(stress) and stress[i] == 1:
                result_parts.append(syllable.upper())
            else:
                result_parts.append(syllable.lower())
                
        return "-".join(result_parts)
    
    # ========== Drill Generation ==========
    
    def generate_drill_session(self, 
                               drill_type: str = "mixed",
                               num_items: int = 10) -> List[Dict]:
        """
        Generate a practice drill session.
        
        Args:
            drill_type: 'words', 'rituals', 'scrolls', 'phrases', or 'mixed'
            num_items: Number of items in the drill
            
        Returns:
            List of drill items with pronunciation data
        """
        drills = []
        
        if drill_type == "words" or drill_type == "mixed":
            drills.extend(self._generate_word_drills(
                num_items if drill_type == "words" else num_items // 3
            ))
            
        if drill_type == "rituals" or drill_type == "mixed":
            drills.extend(self._generate_ritual_drills(
                num_items if drill_type == "rituals" else num_items // 3
            ))
            
        if drill_type == "scrolls" or drill_type == "mixed":
            drills.extend(self._generate_scroll_drills(
                num_items if drill_type == "scrolls" else num_items // 3
            ))
            
        if drill_type == "phrases" or drill_type == "mixed":
            drills.extend(self._generate_phrase_drills(
                num_items if drill_type == "phrases" else num_items // 4
            ))
        
        # Shuffle for variety
        random.shuffle(drills)
        return drills[:num_items]
    
    def _generate_word_drills(self, count: int) -> List[Dict]:
        """Generate word pronunciation drills."""
        drills = []
        words = list(self.lexicon.word_index.keys())
        selected = random.sample(words, min(count, len(words)))
        
        for word in selected:
            entry = self.lexicon.lookup(word)
            if entry:
                drills.append({
                    "type": "word",
                    "text": word,
                    "ipa": entry.get("ipa"),
                    "phonetic": entry.get("phonetic_spelling"),
                    "syllable_breakdown": self.get_syllable_breakdown(word),
                    "instruction": f"Pronounce: {word}"
                })
        return drills
    
    def _generate_ritual_drills(self, count: int) -> List[Dict]:
        """Generate ritual phrase pronunciation drills."""
        drills = []
        rituals = self.lexicon.get_all_rituals()
        selected = random.sample(rituals, min(count, len(rituals)))
        
        training = self.lexicon.training.get("ritual_training", {})
        for ritual in selected:
            data = training.get(ritual, {})
            drills.append({
                "type": "ritual",
                "text": data.get("canonical", ritual),
                "ipa": data.get("ipa"),
                "phonetic": data.get("phonetic_spelling"),
                "pause_pattern": data.get("pause_pattern"),
                "instruction": f"Invoke ritual: {data.get('canonical', ritual)}"
            })
        return drills
    
    def _generate_scroll_drills(self, count: int) -> List[Dict]:
        """Generate scroll command pronunciation drills."""
        drills = []
        scrolls = self.lexicon.get_all_scrolls()
        selected = random.sample(scrolls, min(count, len(scrolls)))
        
        training = self.lexicon.training.get("scroll_training", {})
        for scroll in selected:
            data = training.get(scroll, {})
            # Use an example completion if available
            examples = data.get("example_completions", [])
            text = examples[0] if examples else data.get("canonical", scroll)
            drills.append({
                "type": "scroll",
                "text": text,
                "canonical": data.get("canonical"),
                "ipa": data.get("ipa"),
                "phonetic": data.get("phonetic_spelling"),
                "instruction": f"Cast scroll: {text}"
            })
        return drills
    
    def _generate_phrase_drills(self, count: int) -> List[Dict]:
        """Generate practice phrase drills from pronunciation exercises."""
        drills = []
        
        # Get drills from training data
        pronunciation_drills = self.lexicon.training.get("pronunciation_drills", {})
        
        all_exercises = []
        for drill_type in ["consonant_clusters", "vowel_precision", "rhythm_exercises"]:
            exercises = pronunciation_drills.get(drill_type, [])
            for ex in exercises:
                all_exercises.append({
                    "drill_type": drill_type,
                    **ex
                })
        
        selected = random.sample(all_exercises, min(count, len(all_exercises)))
        
        for ex in selected:
            drills.append({
                "type": "phrase",
                "drill_category": ex.get("drill_type"),
                "text": ex.get("practice_phrase") or ex.get("sentence"),
                "focus": ex.get("cluster") or ex.get("vowel") or ex.get("pattern"),
                "words": ex.get("words", []),
                "instruction": f"Practice phrase (focus: {ex.get('cluster') or ex.get('vowel') or ex.get('pattern')})"
            })
        return drills
    
    # ========== Progress Tracking ==========
    
    def record_practice(self, word: str, score: float, notes: str = ""):
        """
        Record a practice attempt for a word.
        
        Args:
            word: The practiced word
            score: Score from 0.0 to 1.0
            notes: Optional notes about the attempt
        """
        if word not in self.progress["word_scores"]:
            self.progress["word_scores"][word] = {
                "attempts": [],
                "best_score": 0.0,
                "average_score": 0.0
            }
            
        attempt = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "notes": notes
        }
        
        self.progress["word_scores"][word]["attempts"].append(attempt)
        
        # Update stats
        scores = [a["score"] for a in self.progress["word_scores"][word]["attempts"]]
        self.progress["word_scores"][word]["best_score"] = max(scores)
        self.progress["word_scores"][word]["average_score"] = sum(scores) / len(scores)
        
        self._save_progress()
    
    def complete_drill(self, drill_type: str, score: float):
        """Record completion of a drill session."""
        if drill_type not in self.progress["drill_completions"]:
            self.progress["drill_completions"][drill_type] = []
            
        self.progress["drill_completions"][drill_type].append({
            "timestamp": datetime.now().isoformat(),
            "score": score
        })
        
        self._save_progress()
    
    def get_weak_words(self, threshold: float = 0.7) -> List[str]:
        """Get words that need more practice (below threshold)."""
        weak = []
        for word, data in self.progress.get("word_scores", {}).items():
            if data.get("average_score", 0) < threshold:
                weak.append(word)
        return weak
    
    def get_progress_summary(self) -> Dict:
        """Get overall training progress summary."""
        word_scores = self.progress.get("word_scores", {})
        drill_completions = self.progress.get("drill_completions", {})
        
        total_words = len(word_scores)
        total_attempts = sum(
            len(w.get("attempts", [])) 
            for w in word_scores.values()
        )
        avg_score = 0.0
        if word_scores:
            avg_score = sum(
                w.get("average_score", 0) 
                for w in word_scores.values()
            ) / len(word_scores)
        
        return {
            "total_words_practiced": total_words,
            "total_attempts": total_attempts,
            "overall_average_score": round(avg_score, 2),
            "weak_words": self.get_weak_words(),
            "drill_types_completed": list(drill_completions.keys()),
            "total_drill_sessions": sum(
                len(d) for d in drill_completions.values()
            )
        }
    
    # ========== Audio Training Data ==========
    
    def generate_audio_manifest(self, output_dir: str = "dictionary/audio_samples") -> Dict:
        """
        Generate a manifest for audio training data collection.
        
        Args:
            output_dir: Directory where audio samples will be stored
            
        Returns:
            Manifest dictionary with all required audio samples
        """
        os.makedirs(output_dir, exist_ok=True)
        
        manifest = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "output_directory": output_dir,
            "format_requirements": self.lexicon.training.get(
                "audio_sample_requirements", {}
            ),
            "samples": {
                "hotword": [],
                "rituals": [],
                "scrolls": [],
                "vocabulary": []
            }
        }
        
        # Hotword samples
        hotword = self.lexicon.get_hotword()
        if hotword:
            hotword_data = self.lexicon.training.get("hotword_training", {})
            for sample in hotword_data.get("training_samples", []):
                for variation in sample.get("variations", []):
                    manifest["samples"]["hotword"].append({
                        "text": variation["text"],
                        "expected_confidence": variation["confidence"],
                        "filename_pattern": f"hotword_{variation['text'].replace(' ', '_')}_{{speaker}}_{{take}}.wav"
                    })
                for context in sample.get("context_phrases", []):
                    manifest["samples"]["hotword"].append({
                        "text": context,
                        "type": "context_phrase",
                        "filename_pattern": f"hotword_context_{context.replace(' ', '_')}_{{speaker}}_{{take}}.wav"
                    })
        
        # Ritual samples
        for ritual_name in self.lexicon.get_all_rituals():
            ritual_data = self.lexicon.training.get("ritual_training", {}).get(ritual_name, {})
            manifest["samples"]["rituals"].append({
                "name": ritual_name,
                "canonical": ritual_data.get("canonical"),
                "ipa": ritual_data.get("ipa"),
                "variations": [v["text"] for v in ritual_data.get("variations", [])],
                "filename_pattern": f"ritual_{ritual_name}_{{speaker}}_{{take}}.wav"
            })
        
        # Scroll samples
        for scroll_name in self.lexicon.get_all_scrolls():
            scroll_data = self.lexicon.training.get("scroll_training", {}).get(scroll_name, {})
            manifest["samples"]["scrolls"].append({
                "name": scroll_name,
                "canonical": scroll_data.get("canonical"),
                "ipa": scroll_data.get("ipa"),
                "example_completions": scroll_data.get("example_completions", []),
                "filename_pattern": f"scroll_{scroll_name}_{{speaker}}_{{take}}.wav"
            })
        
        # Vocabulary samples
        for word, entry in self.lexicon.word_index.items():
            if not entry.get("alias_of"):  # Skip aliases
                manifest["samples"]["vocabulary"].append({
                    "word": word,
                    "ipa": entry.get("ipa"),
                    "category": entry.get("category"),
                    "filename_pattern": f"vocab_{word}_{{speaker}}_{{take}}.wav"
                })
        
        # Save manifest
        manifest_path = os.path.join(output_dir, "audio_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"[PhoneticTrainer] Audio manifest saved to {manifest_path}")
        return manifest
    
    def validate_audio_sample(self, audio_path: str, expected_text: str) -> Dict:
        """
        Validate an audio sample against expected pronunciation.
        
        Note: This is a placeholder that returns structure for integration
        with actual speech recognition validation.
        
        Args:
            audio_path: Path to audio file
            expected_text: Expected transcription
            
        Returns:
            Validation result dictionary
        """
        # This would integrate with whisper/speech recognition
        # For now, return a structure template
        return {
            "audio_path": audio_path,
            "expected_text": expected_text,
            "validated": False,
            "transcription": None,
            "confidence": 0.0,
            "pronunciation_score": 0.0,
            "issues": [],
            "note": "Integrate with voice/transcriber.py for actual validation"
        }
    
    # ========== SSML Generation ==========
    
    def generate_tts_script(self, text: str, style: str = "neutral") -> str:
        """
        Generate SSML-formatted script for text-to-speech.
        
        Args:
            text: Text to convert
            style: Speaking style ('neutral', 'ritual', 'command')
            
        Returns:
            SSML-formatted string
        """
        # Start SSML document
        ssml_parts = ['<speak>']
        
        # Style-specific prosody
        if style == "ritual":
            ssml_parts.append('<prosody rate="slow" pitch="low">')
        elif style == "command":
            ssml_parts.append('<prosody rate="medium" pitch="medium">')
        else:
            ssml_parts.append('<prosody rate="medium">')
        
        # Format text with phoneme tags
        formatted = self.lexicon.format_for_tts(text)
        ssml_parts.append(formatted)
        
        ssml_parts.append('</prosody>')
        ssml_parts.append('</speak>')
        
        return "".join(ssml_parts)
    
    def get_pronunciation_card(self, word: str) -> Optional[str]:
        """
        Generate a formatted pronunciation card for display.
        
        Args:
            word: Word to generate card for
            
        Returns:
            Formatted string for display
        """
        guide = self.get_pronunciation_guide(word)
        if not guide:
            return None
            
        lines = [
            f"╔══════════════════════════════════════╗",
            f"║  {word.upper():^34}  ║",
            f"╠══════════════════════════════════════╣",
            f"║  IPA: {guide['ipa'] or 'N/A':<30}  ║",
            f"║  Phonetic: {guide['phonetic_spelling'] or 'N/A':<25}  ║",
            f"║  Syllables: {self.get_syllable_breakdown(word) or 'N/A':<24}  ║",
            f"╠══════════════════════════════════════╣",
        ]
        
        for tip in guide.get("tips", [])[:3]:
            # Truncate long tips
            tip_display = tip[:34] if len(tip) <= 34 else tip[:31] + "..."
            lines.append(f"║  • {tip_display:<33} ║")
        
        lines.append(f"╚══════════════════════════════════════╝")
        
        return "\n".join(lines)


# Convenience function
def get_trainer() -> PhoneticTrainer:
    """Get a phonetic trainer instance."""
    return PhoneticTrainer()


if __name__ == "__main__":
    print("\n=== Daemon Phonetic Trainer Test ===\n")
    
    trainer = PhoneticTrainer()
    
    # Test pronunciation guide
    print("Pronunciation Guide for 'prometheus':")
    guide = trainer.get_pronunciation_guide("prometheus")
    if guide:
        print(f"  IPA: {guide['ipa']}")
        print(f"  Phonetic: {guide['phonetic_spelling']}")
        print(f"  Syllables: {trainer.get_syllable_breakdown('prometheus')}")
        print(f"  Tips: {guide['tips']}")
    
    # Test pronunciation card
    print("\nPronunciation Card:")
    card = trainer.get_pronunciation_card("daemon")
    if card:
        print(card)
    
    # Generate drill session
    print("\nGenerated Drill Session (5 items):")
    drills = trainer.generate_drill_session(drill_type="mixed", num_items=5)
    for i, drill in enumerate(drills, 1):
        print(f"  {i}. [{drill['type']}] {drill['instruction']}")
        print(f"     Text: {drill['text']}")
        if drill.get('phonetic'):
            print(f"     Phonetic: {drill['phonetic']}")
    
    # Test TTS script generation
    print("\nTTS Script Generation:")
    test_text = "Prometheus invoke the codex ritual"
    ssml = trainer.generate_tts_script(test_text, style="ritual")
    print(f"  Input: {test_text}")
    print(f"  SSML: {ssml[:150]}...")
    
    # Generate audio manifest
    print("\nGenerating Audio Training Manifest...")
    manifest = trainer.generate_audio_manifest()
    print(f"  Hotword samples: {len(manifest['samples']['hotword'])}")
    print(f"  Ritual samples: {len(manifest['samples']['rituals'])}")
    print(f"  Scroll samples: {len(manifest['samples']['scrolls'])}")
    print(f"  Vocabulary samples: {len(manifest['samples']['vocabulary'])}")
    
    print("\n=== Test Complete ===")
