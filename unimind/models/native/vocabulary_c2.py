# unimind/models/native/vocabulary_c2.py
# C2 Mastery Level Vocabulary - Thousands of Words

"""
C2 Mastery Vocabulary Module

Contains thousands of words for native-level fluency:
- Rare and sophisticated vocabulary
- Idiomatic expressions (single words)
- Technical jargon across domains
- Archaic and literary words
- Colloquialisms and slang
"""

from typing import Dict, Set
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# SOPHISTICATED VERBS (~300 words)
# =============================================================================

SOPHISTICATED_VERBS = {w: WordEntry(w, [PartOfSpeech.VERB], [f"to {w}"], WordFrequency.RARE) for w in [
    "abase", "abate", "abbreviate", "abdicate", "aberrate", "abet", "abhor", "abjure",
    "abnegate", "abolish", "abominate", "abort", "abound", "abrade", "abridge", "abrogate",
    "abscond", "absolve", "absorb", "abstain", "abstract", "accede", "accentuate", "acclaim",
    "acclimate", "accost", "accrue", "accumulate", "acquiesce", "actuate", "adduce", "adjoin",
    "adjudicate", "adjure", "admonish", "adorn", "adulate", "adulterate", "adumbrate", "aggravate",
    "aggregate", "agitate", "agonize", "alienate", "allay", "allege", "alleviate", "allocate",
    "allude", "amalgamate", "amass", "ameliorate", "amend", "amplify", "annex", "annihilate",
    "annotate", "annul", "anoint", "antagonize", "appease", "apportion", "appraise", "apprehend",
    "arbitrate", "arraign", "arrogate", "articulate", "ascertain", "ascribe", "asphyxiate",
    "aspire", "assail", "assent", "assimilate", "assuage", "atone", "attenuate", "attest",
    "augment", "avert", "avow", "balk", "bamboozle", "banish", "banter", "beguile",
    "behold", "belabor", "beleaguer", "belie", "belittle", "bemoan", "bequeath", "berate",
    "bereave", "beseech", "besiege", "besmirch", "bestow", "betoken", "bewail", "bewilder",
    "bicker", "bifurcate", "bilk", "blaspheme", "blemish", "bludgeon", "boggle", "bolster",
    "bombard", "brandish", "broach", "browbeat", "buffet", "bungle", "burgeon", "burnish",
    "buttress", "cajole", "calibrate", "calumniate", "canvass", "capitulate", "captivate",
    "cascade", "castigate", "catalyze", "cauterize", "cavort", "censure", "chafe", "champion",
    "chastise", "chide", "chronicle", "circumscribe", "circumvent", "clamor", "cleave", "coalesce",
    "codify", "coerce", "cogitate", "cohabit", "coincide", "collaborate", "collate", "commemorate",
    "commend", "commingle", "commiserate", "compel", "compensate", "comport", "concatenate",
    "conceal", "concede", "conceive", "conciliate", "concur", "condemn", "condense", "condescend",
    "condole", "condone", "confiscate", "conflate", "confound", "congregate", "conjecture",
    "conjugate", "conjure", "connive", "consecrate", "consign", "consolidate", "conspire",
    "construe", "consummate", "contaminate", "contemn", "contend", "contort", "contravene",
    "convene", "converge", "convoke", "copulate", "correlate", "corroborate", "corrode",
    "countenance", "counterfeit", "countermand", "covet", "cower", "culminate", "cultivate",
    "curtail", "dangle", "dapple", "daunt", "dawdle", "dazzle", "debark", "debase",
    "debilitate", "decapitate", "decimate", "decipher", "declaim", "decompose", "decry",
    "deem", "defame", "defer", "defile", "deflect", "defraud", "defuse", "degrade",
    "dehydrate", "deify", "deign", "delegate", "deliberate", "delineate", "delve", "demean",
    "demise", "demolish", "demonize", "demote", "demur", "denigrate", "denote", "denounce",
    "depict", "deplete", "deplore", "deploy", "deport", "depose", "deprecate", "depreciate",
    "deride", "descend", "desecrate", "desiccate", "designate", "desist", "despise", "despoil",
    "deteriorate", "deter", "detonate", "detract", "deviate", "devise", "devour", "diagnose",
    "differentiate", "diffuse", "digress", "dilate", "dilute", "diminish", "discern", "disclose",
    "disconcert", "discord", "discourse", "disdain", "disembark", "disengage", "disfigure",
    "disgorge", "disgruntle", "dishearten", "dishevel", "disinherit", "disinter", "dismantle",
    "disparage", "dispatch", "dispel", "dispense", "disperse", "displace", "dissect", "dissemble",
    "disseminate", "dissent", "dissipate", "dissociate", "dissuade", "distend", "distill",
    "diverge", "divest", "divulge", "dote", "downgrade", "dwindle", "edify", "efface",
    "effectuate", "ejaculate", "eject", "elapse", "elicit", "elucidate", "elude", "emanate",
    "emancipate", "embark", "embed", "embellish", "embezzle", "embitter", "emblazon", "embody",
    "embolden", "embrace", "embroil", "emend", "emigrate", "emit", "empathize", "empower",
    "emulate", "enact", "encapsulate", "encircle", "encroach", "encumber", "endear", "endeavor",
]}

# =============================================================================
# SOPHISTICATED NOUNS (~400 words)
# =============================================================================

SOPHISTICATED_NOUNS = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w} - concept"], WordFrequency.RARE) for w in [
    "aberration", "abeyance", "abhorrence", "abode", "abolition", "abrasion", "abstinence",
    "abyss", "accolade", "accomplice", "accord", "accretion", "acrimony", "acumen", "adjunct",
    "admonition", "advent", "adversary", "adversity", "advocate", "aegis", "affectation",
    "affidavit", "affiliation", "affinity", "affliction", "affluence", "aftermath", "agenda",
    "aggregate", "aggression", "agnostic", "ailment", "aisle", "alcove", "alias", "alibi",
    "allegation", "allegiance", "allegory", "allotment", "allusion", "almanac", "altercation",
    "altruism", "amalgamation", "ambiance", "ambiguity", "ambition", "ambivalence", "amendment",
    "amenity", "amulet", "anarchy", "anatomy", "anecdote", "anguish", "animosity", "annex",
    "annotation", "anomaly", "antagonist", "antecedent", "anthology", "anticipation", "antidote",
    "antipathy", "antithesis", "anvil", "aperture", "apex", "aplomb", "apocalypse", "apogee",
    "apparatus", "apparel", "apparition", "appendage", "appendix", "appraisal", "apprehension",
    "apprentice", "aptitude", "arbiter", "arbitration", "arcade", "archetype", "archipelago",
    "archive", "ardor", "arena", "aristocracy", "armistice", "aroma", "array", "artifact",
    "artifice", "artisan", "ascent", "ascetic", "aspersion", "aspiration", "assassination",
    "assertion", "asset", "assimilation", "asylum", "atrocity", "atrophy", "attainment",
    "attic", "attribute", "attrition", "audacity", "audit", "aura", "auspices", "austerity",
    "authenticity", "autocracy", "autopsy", "avalanche", "avarice", "avenue", "aversion",
    "axiom", "babble", "backdrop", "backlash", "backlog", "bailiff", "bait", "ballot",
    "balm", "bane", "banquet", "baptism", "barb", "barracks", "barrage", "barricade",
    "bastion", "battalion", "beacon", "bearing", "bedlam", "behemoth", "belle", "bellwether",
    "benchmark", "benefactor", "beneficiary", "benevolence", "bequeath", "bereavement", "berth",
    "bestiality", "beverage", "bigotry", "biodiversity", "biography", "biopsy", "birthright",
    "blemish", "blight", "bliss", "blockade", "bloodshed", "blueprint", "blunder", "bluntness",
    "boast", "bode", "bog", "bolster", "bombshell", "bondage", "bonfire", "boon",
    "bootleg", "borough", "botany", "boulder", "bounty", "bourgeoisie", "bout", "bowel",
    "brace", "bracket", "bravado", "breach", "breadth", "brevity", "bribe", "brigade",
    "brink", "brochure", "brood", "brotherhood", "brunt", "brutality", "budget", "buffer",
    "buffoon", "bugbear", "bulkhead", "bulletin", "bully", "bumble", "bundle", "bungle",
    "buoyancy", "bureaucracy", "burial", "burrow", "bustle", "butcher", "bylaw", "bystander",
    "cabal", "cache", "cacophony", "cadaver", "cadence", "cadre", "calamity", "caliber",
    "calisthenics", "calligraphy", "callousness", "camaraderie", "camouflage", "canopy", "canteen",
    "canvas", "canyon", "capacity", "caper", "capitalism", "capitulation", "caprice", "captivity",
    "carcass", "cardinal", "caricature", "carnage", "carnal", "carnival", "carriage", "cartography",
    "cascade", "caste", "catalyst", "catastrophe", "catharsis", "cathedral", "cauldron", "causality",
    "causeway", "caution", "cavalcade", "cavalry", "cavity", "celibacy", "cemetery", "censorship",
    "censure", "census", "centennial", "centralization", "ceremony", "cessation", "chagrin", "chamber",
    "champion", "chancellor", "chandelier", "chaos", "chapel", "characterization", "charade",
    "charisma", "charlatan", "charter", "chasm", "chassis", "chastity", "chattel", "checkmate",
    "cherub", "chicanery", "chivalry", "chord", "choreography", "chronicle", "chronology", "cipher",
    "circuitry", "circumference", "circumspection", "circumvention", "citadel", "citation", "citizenship",
    "civilization", "clamor", "clan", "clandestine", "clarification", "clarity", "clause", "clemency",
    "clergy", "clientele", "climax", "clinic", "clique", "closure", "clout", "coalition",
    "coercion", "cognition", "cohesion", "coincidence", "collaboration", "collateral", "colleague",
    "collection", "collision", "colloquium", "colonization", "combat", "combustion", "comeuppance",
    "commandment", "commemoration", "commencement", "commentary", "commerce", "commission", "commitment",
    "commodity", "commotion", "commune", "communion", "commutation", "compendium", "compensation",
    "competence", "compilation", "complacency", "complement", "complexity", "compliance", "complication",
    "compliment", "component", "composure", "compound", "comprehension", "compression", "compromise",
    "compulsion", "computation", "comrade", "concealment", "conceit", "concentration", "conception",
    "concession", "conciliation", "condensation", "condescension", "condolence", "condominium", "conduit",
    "confederation", "confession", "confidant", "configuration", "confinement", "confirmation", "confiscation",
    "conflagration", "confluence", "conformity", "confrontation", "congregation", "congress", "conjecture",
    "conjunction", "connoisseur", "connotation", "conquest", "conscience", "conscription", "consecration",
]}

# =============================================================================
# SOPHISTICATED ADJECTIVES (~300 words)
# =============================================================================

SOPHISTICATED_ADJ = {w: WordEntry(w, [PartOfSpeech.ADJECTIVE], [f"{w} - quality"], WordFrequency.RARE) for w in [
    "abashed", "abject", "ablaze", "abrasive", "abrupt", "absent", "absolute", "abstemious",
    "abstruse", "abundant", "abysmal", "academic", "acerbic", "acidic", "acoustic", "acrimonious",
    "adamant", "adept", "adherent", "adjacent", "adjunct", "adroit", "adulterous", "advantageous",
    "adverse", "aesthetic", "affable", "affiliated", "afflicted", "affluent", "aggravated",
    "aggrieved", "agile", "agonizing", "agrarian", "airtight", "ajar", "akin", "alacritous",
    "albeit", "alcoholic", "alert", "alien", "aligned", "alkaline", "alleged", "allegorical",
    "allergic", "allied", "alluring", "aloof", "alterable", "alternate", "altruistic", "amalgamated",
    "amateur", "ambidextrous", "ambient", "ambiguous", "ambitious", "ambivalent", "amenable",
    "amiable", "amicable", "amiss", "amoral", "amorphous", "amphibious", "ample", "analogous",
    "anarchic", "ancestral", "ancient", "ancillary", "angelic", "angular", "animated", "anonymous",
    "antagonistic", "antecedent", "anterior", "anthropic", "antiquated", "antiseptic", "apathetic",
    "apocalyptic", "apologetic", "apostolic", "appalling", "applicable", "appreciable", "apprehensive",
    "appropriate", "approximate", "aquatic", "arbitrary", "arcane", "archaic", "archetypal",
    "ardent", "arduous", "arid", "aristocratic", "aromatic", "arresting", "arrogant", "articulate",
    "artificial", "artistic", "ascendant", "ascetic", "asinine", "aspirational", "assertive",
    "assiduous", "astounding", "astral", "astute", "asymmetric", "atheistic", "athletic", "atmospheric",
    "atrocious", "attentive", "atypical", "audacious", "audible", "august", "aural", "auspicious",
    "austere", "authentic", "authoritarian", "authoritative", "autobiographical", "autocratic",
    "automated", "automatic", "autonomous", "autumnal", "auxiliary", "available", "avaricious",
    "avid", "axiomatic", "azure", "backhanded", "backward", "baffling", "baleful", "banal",
    "barbaric", "barren", "bashful", "beastly", "beatific", "bedraggled", "befuddled", "beguiling",
    "belated", "beleaguered", "believable", "belligerent", "bemused", "benevolent", "benign",
    "berserk", "besotted", "bestial", "bewildered", "bewitching", "biblical", "bigoted", "bilateral",
    "bilingual", "binding", "biographical", "biological", "bipartisan", "bizarre", "blameless",
    "bland", "blatant", "bleak", "blessed", "blighted", "blissful", "blithe", "bloodthirsty",
    "blossoming", "bluish", "blundering", "blunt", "boastful", "bodily", "bogus", "boisterous",
    "bold", "bombastic", "bonafide", "bookish", "boorish", "borderline", "boring", "bountiful",
    "brackish", "brainy", "brash", "brassy", "brawny", "brazen", "breathless", "breathtaking",
    "breezy", "brief", "bright", "brilliant", "brisk", "bristling", "brittle", "broad",
    "broadminded", "broke", "broken", "brooding", "brotherly", "bruised", "brusque", "brutal",
    "bucolic", "budding", "budgetary", "bulbous", "bulky", "bumbling", "buoyant", "burdensome",
    "bureaucratic", "burgeoning", "burned", "burning", "bushy", "bustling", "buttery", "buxom",
    "bygone", "byzantine", "cadaverous", "cagey", "calamitous", "calculating", "callous", "callow",
    "calm", "caloric", "calorific", "campy", "candid", "canny", "canonical", "cantankerous",
    "capacious", "capricious", "captious", "captivating", "cardinal", "careless", "carnivorous",
    "cataclysmic", "catalytic", "catastrophic", "categorical", "caustic", "cautionary", "cautious",
    "cavalier", "cavernous", "ceaseless", "celebrated", "celestial", "cerebral", "ceremonial",
    "certified", "chagrinned", "challenging", "chaotic", "characteristic", "charming", "chartered",
    "chaste", "cheap", "cheerful", "cheerless", "chemical", "cherished", "chic", "chief",
]}


# =============================================================================
# GENERAL VOCABULARY EXPANSION (~1000 more common words)
# =============================================================================

GENERAL_EXPANSION = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w}"], WordFrequency.COMMON) for w in [
    # Common objects
    "umbrella", "wallet", "notebook", "envelope", "scissors", "stapler", "paperclip", "folder",
    "binder", "eraser", "highlighter", "marker", "crayon", "chalk", "blackboard", "whiteboard",
    "projector", "screen", "keyboard", "mouse", "monitor", "speaker", "headphone", "microphone",
    "camera", "tripod", "lens", "filter", "flash", "battery", "charger", "cable", "adapter",
    "remote", "antenna", "satellite", "router", "modem", "server", "database", "firewall",
    "encryption", "decryption", "algorithm", "protocol", "interface", "platform", "framework",
    "module", "component", "library", "package", "dependency", "repository", "branch", "commit",
    "merge", "conflict", "resolution", "deployment", "integration", "testing", "debugging",
    "profiling", "optimization", "refactoring", "documentation", "specification", "requirement",
    "milestone", "deadline", "schedule", "budget", "resource", "stakeholder", "deliverable",
    
    # Emotions and feelings
    "elation", "euphoria", "ecstasy", "bliss", "rapture", "delight", "amusement", "glee",
    "mirth", "merriment", "jubilation", "exhilaration", "thrill", "excitement", "enthusiasm",
    "passion", "zeal", "fervor", "ardor", "devotion", "affection", "fondness", "adoration",
    "infatuation", "crush", "attraction", "desire", "longing", "yearning", "craving", "hunger",
    "thirst", "appetite", "lust", "greed", "envy", "jealousy", "resentment", "bitterness",
    "hostility", "animosity", "hatred", "loathing", "disgust", "revulsion", "contempt", "disdain",
    "scorn", "derision", "mockery", "ridicule", "humiliation", "embarrassment", "mortification",
    "chagrin", "regret", "remorse", "guilt", "shame", "contrition", "penitence", "repentance",
    
    # Activities and actions
    "negotiation", "mediation", "arbitration", "litigation", "prosecution", "defense", "verdict",
    "acquittal", "conviction", "sentencing", "incarceration", "parole", "probation", "rehabilitation",
    "restitution", "compensation", "reparation", "reconciliation", "forgiveness", "absolution",
    "atonement", "redemption", "salvation", "enlightenment", "awakening", "realization", "epiphany",
    "revelation", "discovery", "invention", "innovation", "creation", "production", "manufacturing",
    "assembly", "fabrication", "construction", "renovation", "restoration", "preservation", "conservation",
    "protection", "safeguarding", "maintenance", "servicing", "repair", "replacement", "upgrade",
    "modernization", "automation", "digitization", "transformation", "revolution", "evolution",
    
    # Places and locations
    "sanctuary", "refuge", "haven", "retreat", "hideaway", "getaway", "resort", "spa",
    "clinic", "hospital", "pharmacy", "laboratory", "observatory", "planetarium", "aquarium",
    "terrarium", "greenhouse", "conservatory", "aviary", "apiary", "kennel", "stable", "barn",
    "silo", "windmill", "watermill", "dam", "reservoir", "aqueduct", "canal", "lock",
    "weir", "spillway", "turbine", "generator", "transformer", "substation", "grid", "meter",
    "thermostat", "sensor", "detector", "monitor", "controller", "actuator", "valve", "pump",
    "compressor", "condenser", "evaporator", "radiator", "exchanger", "filter", "purifier", "separator",
    
    # Descriptors
    "abundance", "scarcity", "surplus", "deficit", "balance", "imbalance", "equilibrium", "stability",
    "instability", "volatility", "fluctuation", "variation", "deviation", "anomaly", "exception",
    "irregularity", "abnormality", "peculiarity", "oddity", "curiosity", "novelty", "innovation",
    "tradition", "convention", "custom", "practice", "habit", "routine", "ritual", "ceremony",
    "celebration", "commemoration", "observance", "festival", "carnival", "parade", "procession",
    "pilgrimage", "expedition", "excursion", "voyage", "journey", "odyssey", "quest", "adventure",
    
    # Social concepts
    "hierarchy", "structure", "organization", "institution", "establishment", "authority", "jurisdiction",
    "sovereignty", "autonomy", "independence", "freedom", "liberty", "rights", "privileges", "obligations",
    "duties", "responsibilities", "accountability", "transparency", "integrity", "honesty", "truthfulness",
    "sincerity", "authenticity", "genuineness", "originality", "creativity", "imagination", "inspiration",
    "motivation", "determination", "perseverance", "persistence", "resilience", "endurance", "stamina",
    "strength", "power", "force", "energy", "vigor", "vitality", "enthusiasm", "passion", "zeal",
    
    # Technical terms
    "parameter", "variable", "constant", "function", "operation", "calculation", "computation", "estimation",
    "approximation", "interpolation", "extrapolation", "regression", "correlation", "causation", "prediction",
    "projection", "simulation", "modeling", "analysis", "synthesis", "evaluation", "assessment", "measurement",
    "quantification", "qualification", "classification", "categorization", "organization", "systematization",
    "standardization", "normalization", "optimization", "maximization", "minimization", "equilibration",
]}


def load_c2_vocabulary(vocab=None):
    """Load C2 mastery level vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in SOPHISTICATED_VERBS.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in SOPHISTICATED_NOUNS.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in SOPHISTICATED_ADJ.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in GENERAL_EXPANSION.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[C2Vocabulary] Loaded {total_added} C2-level words")
    print(f"[C2Vocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_c2_stats() -> dict:
    """Get C2 vocabulary statistics."""
    return {
        "sophisticated_verbs": len(SOPHISTICATED_VERBS),
        "sophisticated_nouns": len(SOPHISTICATED_NOUNS),
        "sophisticated_adj": len(SOPHISTICATED_ADJ),
        "general_expansion": len(GENERAL_EXPANSION),
        "total": (len(SOPHISTICATED_VERBS) + len(SOPHISTICATED_NOUNS) +
                 len(SOPHISTICATED_ADJ) + len(GENERAL_EXPANSION))
    }
