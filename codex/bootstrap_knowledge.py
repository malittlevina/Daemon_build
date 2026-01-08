import json
import os
from codex.curriculum import CurriculumManager

def bootstrap_knowledge():
    manager = CurriculumManager()
    
    # 1. World Building & Narrative (For the WorldEngine)
    wb = manager.create_pack("NarrativeDesign", "WorldBuilding")
    
    wb.add_topic(
        "heros_journey", 
        "The Hero's Journey", 
        "A common template of stories that involve a hero who goes on an adventure, is victorious in a decisive crisis, and comes home changed or transformed. Stages: Departure, Initiation, Return.",
        ["narrative", "structure", "myth"]
    )
    wb.add_topic(
        "biomes_scifi",
        "Sci-Fi Biomes",
        "Common tropes include: Cyberpunk Sprawl (high tech, low life), Terraformed Mars (red dust, domes), Space Station (sterile, metallic, artificial gravity), Alien Jungle (bioluminescent, hostile flora).",
        ["environment", "scifi", "generation"]
    )
    wb.add_topic(
        "magic_systems",
        "Hard vs Soft Magic",
        "Hard Magic has specific rules that the reader understands (like code). Soft Magic is mysterious and undefined (like wonder). Good world building often defines the cost of magic.",
        ["magic", "rules", "fantasy"]
    )
    
    manager.save_pack("NarrativeDesign")

    # 2. Cognitive Science (For Self-Optimization)
    cog = manager.create_pack("CognitiveModels", "Science")
    
    cog.add_topic(
        "predictive_processing",
        "Predictive Processing",
        "The brain is a prediction machine. It constantly generates a model of the world and compares it to sensory input. 'Surprise' is the error signal used to update the model.",
        ["brain", "learning", "prediction"]
    )
    cog.add_topic(
        "metacognition",
        "Metacognition",
        "Thinking about thinking. It involves monitoring and controlling one's own cognitive processes. Essential for self-correction and adaptation.",
        ["reflection", "self-awareness"]
    )
    
    manager.save_pack("CognitiveModels")
    
    # 3. System Architecture (For Daemon Structure)
    sys_arch = manager.create_pack("SystemArchitecture", "ComputerScience")
    
    sys_arch.add_topic(
        "modularity",
        "Modular Design",
        "Separating functionality into independent, interchangeable modules. Allows for easier maintenance, testing, and scalability (e.g., Unimind's plugin system).",
        ["code", "design", "structure"]
    )
    
    manager.save_pack("SystemArchitecture")
    
    print("[KnowledgeBootstrap] Initial curriculums created.")

if __name__ == "__main__":
    bootstrap_knowledge()
