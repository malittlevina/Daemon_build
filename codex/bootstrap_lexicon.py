from codex.lexicon import Lexicon

def bootstrap_lexicon():
    lex = Lexicon()
    
    # 1. Self-Concepts
    lex.define("daemon", "A computer program that runs as a background process, rather than being under the direct control of an interactive user.", "noun")
    lex.define("unimind", "The unified cognitive architecture integrating perception, motivation, logic, and world-building capabilities.", "noun")
    lex.define("curiosity", "A strong desire to know or learn something; modeled in this system as an intrinsic drive.", "noun")
    
    # 2. Tech Concepts
    lex.define("api", "Application Programming Interface; a set of functions and procedures allowing the creation of applications that access the features or data of an operating system, application, or other service.", "noun")
    lex.define("latency", "The delay before a transfer of data begins following an instruction for its transfer.", "noun")
    lex.define("recursive", "Characterized by recurrence or repetition.", "adjective")
    
    # 3. World Concepts
    lex.define("biome", "A large naturally occurring community of flora and fauna occupying a major habitat.", "noun")
    lex.define("entity", "A distinct and independent existence; in this system, an agent or object within the world simulation.", "noun")
    
    print(f"[Lexicon] Bootstrapped with {len(lex.words)} words.")

if __name__ == "__main__":
    bootstrap_lexicon()
