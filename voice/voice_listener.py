# voice/voice_listener.py

from __future__ import annotations

from rituals.ritual_registry import RitualRegistry


def start_voice_listener():
    """
    Cross-platform safe entrypoint.

    On systems without `speech_recognition` / audio devices, this returns a
    descriptive string rather than crashing the daemon.
    """
    try:
        import speech_recognition as sr
    except Exception as e:
        return f"[VoiceListener] Disabled (speech_recognition unavailable): {e}"

    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
    except Exception as e:
        return f"[VoiceListener] Disabled (microphone unavailable): {e}"

    rituals = RitualRegistry()

    print("[VoiceListener] Listening for ritual invocation...")
    with microphone as source:
        audio = recognizer.listen(source)

    try:
        phrase = recognizer.recognize_google(audio).lower()
        print(f"[VoiceListener] Heard phrase: {phrase}")
        return rituals.cast_ritual(phrase)
    except sr.UnknownValueError:
        return "[VoiceListener] Could not understand audio."
    except sr.RequestError as e:
        return f"[VoiceListener] API error: {e}"
