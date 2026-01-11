# unimind/models/native/vocabulary_ultimate.py
# Ultimate Vocabulary Push for C1/C2 Level

"""
Ultimate Vocabulary Module

Push vocabulary to C1 level (8,000+) and beyond toward C2 (16,000+):
- Literary vocabulary
- Philosophical terms
- Artistic expressions
- Communication words
- Action and state words
"""

from typing import Dict
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


def _make_entries(words: list, pos: PartOfSpeech) -> Dict:
    return {w: WordEntry(w, [pos], [w], WordFrequency.COMMON) for w in words}


# =============================================================================
# LITERARY & PHILOSOPHICAL VOCABULARY (~300 words)
# =============================================================================

LITERARY_WORDS = [
    "allegory", "alliteration", "allusion", "ambiguity", "anachronism", "analogy",
    "antagonist", "anthropomorphism", "antithesis", "aphorism", "archetype", "assonance",
    "bildungsroman", "cacophony", "caesura", "catharsis", "characterization", "chiasmus",
    "climax", "colloquialism", "connotation", "consonance", "denouement", "deus",
    "diction", "didactic", "dystopia", "elegy", "ellipsis", "enjambment", "epigraph",
    "epilogue", "epiphany", "epistolary", "epithet", "euphemism", "exposition",
    "fable", "fallacy", "figurative", "flashback", "foil", "foreshadowing",
    "genre", "gothic", "grotesque", "haiku", "hamartia", "hubris", "hyperbole",
    "iambic", "idiom", "imagery", "innuendo", "irony", "juxtaposition", "lament",
    "limerick", "litotes", "malapropism", "melodrama", "memoir", "metaphor",
    "meter", "metonymy", "monologue", "mood", "morality", "motif", "muse",
    "narrative", "narrator", "naturalism", "nemesis", "neologism", "noir", "novella",
    "omniscient", "onomatopoeia", "oxymoron", "parable", "paradox", "parallelism",
    "parody", "pastoral", "pathos", "pentameter", "persona", "personification",
    "plot", "poetic", "point", "polemic", "postmodern", "prologue", "prose",
    "protagonist", "pun", "quatrain", "realism", "refrain", "rhetoric", "rhyme",
    "rhythm", "romanticism", "sarcasm", "satire", "scansion", "setting", "simile",
    "soliloquy", "sonnet", "stanza", "stream", "style", "subplot", "subtext",
    "surrealism", "suspense", "syllable", "symbol", "symbolism", "synecdoche",
    "syntax", "tautology", "theme", "thesis", "tone", "tragedy", "tragic",
    "transcendentalism", "trope", "understatement", "unreliable", "utopia", "verisimilitude",
    "vernacular", "verse", "vignette", "villanelle", "voice", "wit", "wordplay",
]

LITERARY_VOCAB = _make_entries(LITERARY_WORDS, PartOfSpeech.NOUN)


# =============================================================================
# PHILOSOPHICAL TERMS (~200 words)
# =============================================================================

PHILOSOPHY_WORDS = [
    "absolutism", "aestheticism", "agnosticism", "altruism", "anarchism", "animism",
    "anthropocentrism", "atheism", "atomism", "axiom", "behaviorism", "bioethics",
    "capitalism", "cartesian", "causality", "cognitivism", "collectivism", "communism",
    "compatibilism", "consequentialism", "constructivism", "contingency", "cosmology",
    "cynicism", "deduction", "deism", "deontology", "determinism", "dialectic",
    "dualism", "egoism", "emanationism", "emotivism", "empiricism", "enlightenment",
    "epicureanism", "epistemology", "essentialism", "eternalism", "ethics", "eudaimonia",
    "existentialism", "expressivism", "fallibilism", "fascism", "fatalism", "feminism",
    "foundationalism", "freewill", "functionalism", "hedonism", "hermeneutics",
    "historicism", "holism", "humanism", "idealism", "identity", "ideology",
    "immaterialism", "immortality", "imperialism", "indeterminism", "individualism",
    "inductivism", "instrumentalism", "intentionality", "internalism", "intuitionism",
    "kantian", "liberalism", "libertarianism", "logic", "logical", "marxism",
    "materialism", "mechanism", "mentalism", "metaethics", "metaphysics", "methodological",
    "monism", "moralism", "mysticism", "naturalism", "nihilism", "nominalism",
    "normativity", "objectivism", "occasionalism", "ontology", "optimism", "pantheism",
    "paradigm", "particularism", "paternalism", "perfectionism", "pessimism",
    "phenomenalism", "phenomenology", "physicalism", "platonism", "pluralism",
    "positivism", "postmodernism", "pragmatism", "predeterminism", "prescriptivism",
    "probabilism", "progressivism", "propertydualism", "quietism", "rationalism",
    "realism", "reductionism", "relativism", "reliabilism", "representationalism",
    "republicanism", "romanticism", "scholasticism", "scientism", "secularism",
    "semantics", "sensationalism", "sentimentalism", "skepticism", "socialism",
    "sociobiology", "solipsism", "sophism", "spiritualism", "stoicism", "structuralism",
    "subjectivism", "substance", "supernaturalism", "syllogism", "teleology",
    "theism", "theodicy", "thomism", "traditionalism", "transcendentalism",
    "universalism", "utilitarianism", "utopianism", "verificationism", "virtue",
    "vitalism", "voluntarism", "weltanschauung", "zeitgeist",
]

PHILOSOPHY_VOCAB = _make_entries(PHILOSOPHY_WORDS, PartOfSpeech.NOUN)


# =============================================================================
# ADDITIONAL COMMON VERBS (~400 words)
# =============================================================================

MORE_COMMON_VERBS = [
    "abolish", "abridge", "absolve", "abstain", "abuse", "accede", "accelerate",
    "accent", "accentuate", "access", "accessorize", "acclaim", "acclimate",
    "accommodate", "accompany", "accomplish", "accost", "account", "accredit",
    "accrue", "accumulate", "accuse", "accustom", "ache", "achieve", "acidify",
    "acknowledge", "acquaint", "acquiesce", "acquire", "acquit", "activate",
    "actualize", "actuate", "adapt", "addict", "address", "adhere", "adjoin",
    "adjourn", "adjudicate", "adjust", "administer", "admire", "admit", "admonish",
    "adopt", "adore", "adorn", "adulterate", "advance", "advantage", "adventure",
    "advertise", "advise", "advocate", "aerate", "affect", "affiliate", "affirm",
    "affix", "afflict", "afford", "affront", "age", "aggravate", "aggregate",
    "agitate", "agonize", "agree", "aid", "aim", "air", "alarm", "alert",
    "alienate", "align", "allay", "allege", "alleviate", "allocate", "allot",
    "allow", "alloy", "allude", "ally", "alphabetize", "alter", "alternate",
    "amalgamate", "amass", "amaze", "ambush", "ameliorate", "amend", "amplify",
    "amputate", "amuse", "analyze", "anchor", "anger", "angle", "animate",
    "annex", "annihilate", "annotate", "announce", "annoy", "annul", "anoint",
    "answer", "antagonize", "anticipate", "ape", "apologize", "appall", "appeal",
    "appear", "appease", "append", "applaud", "apply", "appoint", "apportion",
    "appraise", "appreciate", "apprehend", "apprentice", "approach", "appropriate",
    "approve", "approximate", "arbitrate", "arch", "archive", "argue", "arise",
    "arm", "arouse", "arraign", "arrange", "array", "arrest", "arrive", "arrogate",
    "articulate", "ascend", "ascertain", "ascribe", "aspire", "assail", "assassinate",
    "assault", "assay", "assemble", "assent", "assert", "assess", "assign",
    "assimilate", "assist", "associate", "assuage", "assume", "assure", "astonish",
    "astound", "attach", "attack", "attain", "attempt", "attend", "attest",
    "attract", "attribute", "auction", "audit", "augment", "authenticate",
    "author", "authorize", "automate", "avenge", "aver", "avert", "avoid",
    "await", "awaken", "award", "babble", "back", "backfire", "backtrack",
    "badger", "baffle", "bail", "bait", "bake", "balance", "balk", "ban",
    "bandage", "bang", "banish", "bank", "bankrupt", "bar", "barbarize", "bare",
    "bargain", "bark", "barricade", "barter", "base", "bash", "bask", "batch",
    "bathe", "batter", "battle", "beam", "bear", "beat", "beautify", "beckon",
    "become", "bedevil", "beef", "beg", "beget", "begin", "begrudge", "beguile",
    "behave", "behead", "behold", "belabor", "belch", "belie", "believe", "belittle",
    "bellow", "belong", "belt", "bemoan", "benchmark", "bend", "benefit",
    "bequeath", "berate", "bereave", "beseech", "beset", "besiege", "besmirch",
    "bestow", "bet", "betray", "better", "bewail", "bewilder", "bias", "bicycle",
    "bid", "bilk", "bill", "bind", "bite", "blacken", "blacklist", "blackmail",
    "blame", "blanch", "blank", "blanket", "blaspheme", "blast", "blaze", "bleach",
    "bleat", "bleed", "blemish", "blend", "bless", "blight", "blind", "blindfold",
    "blink", "blister", "bloat", "block", "blockade", "blog", "bloom", "blossom",
    "blot", "blow", "bludgeon", "bluff", "blunder", "blunt", "blur", "blurt",
    "blush", "board", "boast", "boat", "bob", "bode", "bog", "boil", "bolster",
    "bolt", "bomb", "bombard", "bond", "bone", "book", "boom", "boost", "boot",
    "border", "bore", "borrow", "boss", "botch", "bother", "bottle", "bottom",
    "bounce", "bound", "bow", "bowl", "box", "boycott", "brace", "bracket",
    "brag", "braid", "brain", "brainwash", "brake", "branch", "brand", "brandish",
    "brave", "brawl", "breach", "break", "breakfast", "breathe", "breed", "brew",
    "bribe", "brick", "bridge", "brief", "brighten", "bring", "bristle", "broach",
    "broadcast", "broaden", "broil", "broker", "brood", "broom", "browse", "bruise",
    "brush", "brutalize", "bubble", "buck", "buckle", "bud", "budget", "buffer",
    "buffet", "bug", "build", "bulge", "bulk", "bulldoze", "bully", "bump",
    "bunch", "bundle", "bungle", "buoy", "burden", "burglarize", "burn", "burnish",
    "burrow", "burst", "bury", "bus", "bushwhack", "bustle", "busy", "butcher",
    "butt", "butter", "button", "buttonhole", "buttress", "buy", "buzz", "bypass",
]

MORE_VERBS_VOCAB = _make_entries(MORE_COMMON_VERBS, PartOfSpeech.VERB)


# =============================================================================
# ADDITIONAL NOUNS (~500 words)
# =============================================================================

MORE_COMMON_NOUNS = [
    "abbey", "abbreviation", "abdomen", "aberration", "abhorrence", "abode",
    "abolition", "aborigine", "abortion", "abrasion", "abyss", "academia",
    "acceleration", "accent", "acceptability", "acceptance", "accessibility",
    "accident", "acclaim", "acclamation", "accommodation", "accompaniment",
    "accomplice", "accomplishment", "accord", "accordance", "accordion", "accountant",
    "accountability", "accreditation", "accretion", "accuracy", "accusation",
    "acetone", "achievement", "achilles", "acknowledgement", "acne", "acorn",
    "acoustics", "acquaintance", "acquiescence", "acquisition", "acre", "acrobat",
    "acrobatics", "acronym", "acrylic", "acting", "activism", "activist",
    "actuality", "acumen", "acupuncture", "adage", "adapter", "addiction",
    "additive", "addressee", "adequacy", "adherence", "adherent", "adhesive",
    "adjacency", "adjective", "adjustment", "administrator", "admiralty", "admiration",
    "admirer", "admissibility", "admission", "admittance", "adolescence", "adolescent",
    "adoption", "adoration", "adrenaline", "adulthood", "advancement", "adventurer",
    "adverb", "adversary", "advertisement", "advertiser", "advocacy", "aerobics",
    "aerosol", "aesthetics", "affability", "affection", "affidavit", "affiliation",
    "affliction", "affluence", "aftermath", "afterthought", "aggression", "aggressor",
    "agility", "agitation", "agitator", "agnostic", "agony", "agrarian",
    "agriculturalist", "agronomist", "aide", "ailment", "airborne", "aircraft",
    "airfare", "airline", "airliner", "airmail", "airplane", "airport", "airship",
    "airspace", "airstrip", "aisle", "alarm", "album", "alchemy", "alcohol",
    "alcoholism", "alcove", "alderman", "alertness", "algebra", "algorithm",
    "alias", "alibi", "alien", "alienation", "alignment", "alimentary", "alimony",
    "alkalinity", "allegation", "allegiance", "allegory", "allergen", "allergist",
    "alleviation", "alley", "alliance", "alligator", "allocation", "allotment",
    "allowance", "alloy", "allure", "allusion", "ally", "almanac", "almighty",
    "almond", "alms", "alphabet", "alpine", "altar", "alteration", "altercation",
    "alternation", "alternative", "altitude", "alto", "altruism", "aluminum",
    "alumnus", "amateur", "amazement", "ambassador", "ambiance", "ambiguity",
    "ambition", "ambulance", "ambush", "amendment", "amenity", "amiability",
    "amity", "ammonia", "ammunition", "amnesia", "amnesty", "amoeba", "amphibian",
    "amphitheater", "amplification", "amplifier", "amplitude", "amulet", "amusement",
    "anagram", "analgesia", "analgesic", "analog", "analogue", "analyst",
    "analytics", "anarchism", "anarchist", "anarchy", "ancestor", "ancestry",
    "anchor", "anchorage", "anchorman", "anecdote", "anemia", "anesthesia",
    "anesthesiologist", "anesthetic", "anew", "angel", "anger", "angioplasty",
    "angle", "angler", "anguish", "animation", "animator", "animosity", "ankle",
    "annex", "annexation", "anniversary", "annotation", "announcement", "announcer",
    "annoyance", "annual", "annuity", "annulment", "anomaly", "anonymity",
    "antagonism", "antagonist", "antecedent", "antelope", "antenna", "anthem",
    "anthology", "anthropologist", "anthropology", "antibiotic", "anticipation",
    "antidepressant", "antidote", "antiquarian", "antique", "antiquity", "antithesis",
    "antivirus", "antler", "anvil", "anxiety", "apartment", "apathy", "ape",
    "aperitif", "aperture", "apex", "aphrodisiac", "apiary", "apocalypse",
    "apologist", "apology", "apostle", "apparatus", "apparel", "apparition",
    "appeal", "appearance", "appeasement", "appellate", "appendage", "appendix",
    "appetite", "appetizer", "applause", "applicability", "applicant", "application",
    "appointment", "apportionment", "appraisal", "appraiser", "appreciation",
    "apprehension", "apprentice", "apprenticeship", "approval", "approximation",
    "apricot", "apron", "aptitude", "aquarium", "aqueduct", "arbitrage",
    "arbitration", "arbitrator", "arcade", "arch", "archaeologist", "archaeology",
    "archbishop", "archer", "archery", "archipelago", "architect", "architecture",
    "archive", "archivist", "ardor", "arena", "argument", "aria", "aristocracy",
    "aristocrat", "arithmetic", "ark", "armada", "armament", "armchair", "armistice",
    "armor", "armory", "armpit", "army", "aroma", "aromatherapy", "arraignment",
    "arrangement", "arrears", "arrest", "arrival", "arrogance", "arrow", "arsenal",
    "arson", "arsonist", "artery", "artichoke", "article", "articulation",
    "artifact", "artifice", "artificer", "artisan", "artistry", "artwork",
    "asbestos", "ascent", "asceticism", "ash", "ashram", "ashtray", "aspen",
    "asphalt", "aspiration", "aspirin", "assailant", "assassin", "assassination",
    "assault", "assemblage", "assembler", "assembly", "assertion", "assessor",
    "asset", "assignment", "assimilation", "assistance", "assistant", "associate",
    "association", "assortment", "assumption", "assurance", "asteroid", "asthma",
    "astonishment", "astrology", "astronaut", "astronomer", "astronomy", "astrophysics",
    "astuteness", "asylum", "atheism", "atheist", "athlete", "athletics",
    "atlas", "atmosphere", "atoll", "atom", "atrocity", "attachment", "attacker",
    "attainment", "attempt", "attendance", "attendant", "attention", "attic",
    "attire", "attorney", "attraction", "attractiveness", "attribute", "attribution",
    "attrition", "auction", "auctioneer", "audacity", "audience", "audio",
    "audiology", "audit", "audition", "auditor", "auditorium", "augmentation",
    "aunt", "aura", "austerity", "authenticity", "author", "authoritarianism",
    "authority", "authorization", "autobiography", "autocracy", "autograph",
    "automaker", "automation", "automobile", "autonomy", "autopsy", "autumn",
    "availability", "avalanche", "avenue", "average", "aviation", "aviator",
    "avidity", "avocation", "avoidance", "awakening", "awareness", "awe", "axiom",
    "axis", "axle", "azalea", "bachelor", "backlash", "backlog", "backpack",
    "backside", "backstage", "backstroke", "backup", "backyard", "bacon",
    "bacteria", "bacterium", "badge", "badger", "badminton", "bag", "bagel",
    "baggage", "bagpipe", "bail", "bailiff", "bait", "baker", "bakery",
    "balance", "balcony", "baldness", "bale", "ball", "ballad", "ballerina",
    "ballet", "balloon", "ballot", "ballpark", "ballpoint", "ballroom", "balm",
    "bamboo", "ban", "banana", "band", "bandage", "bandit", "bandwidth",
    "bane", "bang", "bangle", "banishment", "banister", "banjo", "bank",
    "banker", "banking", "bankruptcy", "banner", "banquet", "baptism", "baptist",
]

MORE_NOUNS_VOCAB = _make_entries(MORE_COMMON_NOUNS, PartOfSpeech.NOUN)


def load_ultimate_vocabulary(vocab=None):
    """Load ultimate vocabulary to push toward C2."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in LITERARY_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in PHILOSOPHY_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MORE_VERBS_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MORE_NOUNS_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[UltimateVocabulary] Loaded {total_added} additional words")
    print(f"[UltimateVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_ultimate_stats() -> dict:
    """Get ultimate vocabulary statistics."""
    return {
        "literary": len(LITERARY_VOCAB),
        "philosophy": len(PHILOSOPHY_VOCAB),
        "verbs": len(MORE_VERBS_VOCAB),
        "nouns": len(MORE_NOUNS_VOCAB),
        "total": (len(LITERARY_VOCAB) + len(PHILOSOPHY_VOCAB) + 
                 len(MORE_VERBS_VOCAB) + len(MORE_NOUNS_VOCAB))
    }
