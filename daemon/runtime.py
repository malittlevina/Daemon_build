from __future__ import annotations

from dataclasses import dataclass

from emotion.emotion_engine import EmotionEngine
from guardian.ethical_core import EthicalCore
from memory_tree.memory_logger import MemoryLogger
from nlu.nlu_engine import NLUEngine
from scrolls.scroll_engine import ScrollEngine
from unimind.core import Unimind
from unimind.modules.emotion_module import EmotionModule
from unimind.modules.ethics_guard import EthicsGuardModule
from unimind.modules.language_nlu import LanguageNLUModule
from unimind.modules.logic_scroll_router import ScrollRouterModule
from unimind.modules.memory_module import MemoryModule


@dataclass
class DaemonRuntime:
    unimind: Unimind
    scrolls: ScrollEngine
    nlu: NLUEngine
    emotions: EmotionEngine
    ethics: EthicalCore
    memory: MemoryLogger


def build_daemon_runtime(use_ollama_fallback: bool = False) -> DaemonRuntime:
    """
    Construct the daemon's end-to-end query pipeline.
    """
    scrolls = ScrollEngine()
    nlu = NLUEngine(scrolls, use_ollama_fallback=use_ollama_fallback)

    emotions = EmotionEngine()
    ethics = EthicalCore()
    memory = MemoryLogger()

    unimind = Unimind()
    unimind.register("language", LanguageNLUModule(nlu))
    unimind.register("ethics", EthicsGuardModule(ethics))
    unimind.register("logic", ScrollRouterModule(scrolls))
    unimind.register("emotion", EmotionModule(emotions))
    unimind.register("memory", MemoryModule(memory))

    return DaemonRuntime(
        unimind=unimind,
        scrolls=scrolls,
        nlu=nlu,
        emotions=emotions,
        ethics=ethics,
        memory=memory,
    )

