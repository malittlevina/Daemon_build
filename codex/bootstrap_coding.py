import json
import os
from codex.curriculum import CurriculumManager

def bootstrap_coding_knowledge():
    manager = CurriculumManager()
    
    # Create the MasterCoding Curriculum
    coding = manager.create_pack("MasterCoding", "SoftwareEngineering")
    
    # 1. Design Patterns (Gang of Four)
    coding.add_topic(
        "singleton_pattern", 
        "Singleton Pattern", 
        "Ensure a class has only one instance and provide a global point of access to it. Use when exactly one instance of a class is needed to coordinate actions across the system.",
        ["pattern", "creational", "structure"]
    )
    coding.add_topic(
        "factory_pattern", 
        "Factory Method Pattern", 
        "Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.",
        ["pattern", "creational", "polymorphism"]
    )
    coding.add_topic(
        "observer_pattern", 
        "Observer Pattern", 
        "Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically. Key for event-driven systems.",
        ["pattern", "behavioral", "events"]
    )
    coding.add_topic(
        "strategy_pattern", 
        "Strategy Pattern", 
        "Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.",
        ["pattern", "behavioral", "algorithms"]
    )
    
    # 2. SOLID Principles
    coding.add_topic(
        "solid_srp", 
        "Single Responsibility Principle (SRP)", 
        "A class should have one, and only one, reason to change. It should do one thing and do it well.",
        ["principle", "solid", "clean_code"]
    )
    coding.add_topic(
        "solid_ocp", 
        "Open/Closed Principle (OCP)", 
        "Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification.",
        ["principle", "solid", "extensibility"]
    )
    
    # 3. Clean Code
    coding.add_topic(
        "clean_functions", 
        "Clean Functions", 
        "Functions should be small. They should do one thing. They should have descriptive names. They should have few arguments (ideally niladic, monadic, or dyadic).",
        ["clean_code", "refactoring", "readability"]
    )
    
    manager.save_pack("MasterCoding")
    print("[KnowledgeBootstrap] MasterCoding curriculum created.")

if __name__ == "__main__":
    bootstrap_coding_knowledge()
