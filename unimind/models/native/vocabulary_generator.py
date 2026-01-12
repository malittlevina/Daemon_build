# unimind/models/native/vocabulary_generator.py
# Massive Vocabulary Generator - Generate thousands of words for C2 level

"""
Vocabulary Generator Module

Generates comprehensive vocabulary lists including:
- Verb conjugations and variations
- Noun plurals and derivatives
- Adjective comparatives and superlatives
- Word families (derive, derivation, derivative, etc.)
- Common prefixes and suffixes
- Compound words
"""

from typing import Dict, List, Set
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# BASE WORD LISTS - Core words to expand
# =============================================================================

# Common English verbs (base forms)
BASE_VERBS = [
    "accept", "achieve", "act", "add", "admit", "affect", "afford", "agree", "allow",
    "answer", "appear", "apply", "argue", "arrange", "arrive", "assume", "attend",
    "avoid", "base", "bear", "beat", "become", "begin", "believe", "belong", "break",
    "build", "burn", "buy", "call", "care", "carry", "catch", "cause", "change",
    "charge", "check", "choose", "claim", "clean", "clear", "climb", "close", "collect",
    "compare", "complete", "concern", "confirm", "connect", "consider", "contain",
    "continue", "control", "cook", "copy", "correct", "cost", "count", "cover",
    "create", "cross", "cut", "damage", "dance", "deal", "decide", "deliver",
    "demand", "deny", "depend", "describe", "design", "destroy", "develop", "die",
    "direct", "discover", "discuss", "divide", "doubt", "draw", "dress", "drink",
    "drive", "drop", "eat", "enable", "encourage", "end", "enjoy", "enter", "examine",
    "exist", "expect", "experience", "explain", "express", "extend", "face", "fail",
    "fall", "fear", "feed", "feel", "fight", "fill", "find", "finish", "fit",
    "fix", "fly", "focus", "follow", "force", "forget", "form", "function", "gain",
    "gather", "generate", "give", "grow", "guess", "handle", "hang", "happen", "hate",
    "hear", "help", "hide", "hit", "hold", "hope", "hurt", "identify", "ignore",
    "imagine", "improve", "include", "increase", "indicate", "influence", "inform",
    "insist", "install", "intend", "introduce", "invite", "join", "jump", "keep",
    "kick", "kill", "knock", "know", "lack", "last", "laugh", "lay", "lead",
    "learn", "leave", "lend", "let", "lie", "lift", "light", "limit", "link",
    "listen", "live", "lock", "look", "lose", "love", "maintain", "make", "manage",
    "mark", "marry", "match", "matter", "mean", "measure", "meet", "mention", "mind",
    "miss", "mix", "move", "name", "need", "notice", "obtain", "occur", "offer",
    "open", "operate", "order", "organize", "own", "pass", "pay", "perform", "permit",
    "pick", "place", "plan", "play", "please", "point", "pour", "prefer", "prepare",
    "present", "press", "prevent", "produce", "promise", "protect", "prove", "provide",
    "publish", "pull", "push", "put", "raise", "reach", "read", "realize", "receive",
    "recognize", "record", "reduce", "refer", "reflect", "refuse", "regard", "relate",
    "release", "remain", "remember", "remove", "repeat", "replace", "reply", "report",
    "represent", "require", "rest", "result", "retain", "return", "reveal", "ride",
    "ring", "rise", "risk", "roll", "rule", "run", "rush", "save", "say",
    "search", "seem", "sell", "send", "separate", "serve", "set", "settle", "shake",
    "shape", "share", "shift", "shine", "shoot", "shop", "shout", "show", "shut",
    "sign", "sing", "sit", "sleep", "slide", "smile", "smoke", "solve", "sort",
    "sound", "speak", "spend", "spread", "stand", "start", "state", "stay", "steal",
    "step", "stick", "stop", "store", "study", "succeed", "suffer", "suggest", "suit",
    "supply", "support", "suppose", "survive", "swim", "switch", "take", "talk",
    "taste", "teach", "tear", "tell", "tend", "test", "thank", "think", "throw",
    "tie", "touch", "train", "travel", "treat", "trouble", "trust", "turn", "type",
    "understand", "use", "vary", "view", "visit", "vote", "wait", "wake", "walk",
    "want", "warn", "wash", "watch", "wear", "win", "wish", "wonder", "work",
    "worry", "write",
]

# Common English nouns
BASE_NOUNS = [
    "ability", "absence", "access", "account", "act", "action", "activity", "adult",
    "advantage", "advice", "affair", "age", "agency", "agent", "agreement", "aim",
    "air", "amount", "analysis", "animal", "answer", "appearance", "application",
    "approach", "area", "argument", "arm", "army", "art", "article", "aspect",
    "association", "attention", "attitude", "audience", "authority", "baby", "back",
    "background", "balance", "band", "bank", "bar", "base", "basis", "battle",
    "beach", "bed", "behavior", "belief", "benefit", "bill", "birth", "bit",
    "blood", "board", "boat", "body", "book", "border", "boss", "bottle", "bottom",
    "box", "boy", "brain", "branch", "bread", "break", "bridge", "brother", "budget",
    "building", "bus", "bush", "business", "cabinet", "call", "camera", "camp",
    "campaign", "cancer", "candidate", "capacity", "capital", "car", "card", "care",
    "career", "case", "cash", "cat", "category", "cause", "cell", "center", "century",
    "chair", "chairman", "challenge", "chamber", "champion", "chance", "change",
    "channel", "chapter", "character", "charge", "charity", "check", "chest", "chief",
    "child", "choice", "church", "circle", "circumstance", "citizen", "city", "claim",
    "class", "client", "climate", "club", "coach", "coal", "coast", "code", "coffee",
    "college", "color", "column", "combination", "command", "comment", "commission",
    "committee", "communication", "community", "company", "comparison", "competition",
    "complaint", "computer", "concept", "concern", "conclusion", "condition",
    "conference", "confidence", "conflict", "connection", "consequence", "consideration",
    "construction", "consumer", "contact", "content", "context", "contract", "contrast",
    "contribution", "control", "conversation", "copy", "corner", "cost", "council",
    "count", "country", "county", "couple", "course", "court", "cover", "credit",
    "crime", "crisis", "criticism", "crowd", "culture", "cup", "currency", "customer",
    "cut", "damage", "dance", "danger", "data", "date", "daughter", "day", "deal",
    "death", "debate", "debt", "decade", "decision", "defence", "definition", "degree",
    "demand", "democracy", "department", "design", "desire", "desk", "detail",
    "development", "device", "difference", "difficulty", "dinner", "direction",
    "director", "discipline", "discussion", "disease", "distance", "distribution",
    "district", "division", "doctor", "document", "dog", "dollar", "door", "doubt",
    "dress", "drink", "driver", "drug", "duty", "ear", "earth", "economy", "edge",
    "editor", "education", "effect", "efficiency", "effort", "egg", "election",
    "element", "emergency", "emotion", "emphasis", "employee", "employer", "employment",
    "end", "enemy", "energy", "engine", "engineering", "enterprise", "entertainment",
    "entry", "environment", "equipment", "error", "escape", "estate", "estimate",
    "europe", "evaluation", "evening", "event", "evidence", "evolution", "examination",
    "example", "exchange", "exercise", "exhibition", "existence", "expansion",
    "expectation", "expenditure", "experience", "experiment", "expert", "explanation",
    "expression", "extension", "extent", "eye", "face", "facility", "fact", "factor",
    "factory", "failure", "faith", "fall", "family", "farm", "farmer", "fashion",
    "fat", "father", "fault", "favor", "fear", "feature", "fee", "feeling", "field",
    "figure", "file", "film", "finance", "finding", "finger", "fire", "firm", "fish",
    "floor", "flow", "flower", "focus", "food", "foot", "football", "force", "forest",
    "form", "format", "former", "fortune", "foundation", "frame", "freedom", "friend",
    "front", "fruit", "fuel", "function", "fund", "furniture", "future", "gain",
    "gallery", "game", "gap", "garden", "gas", "gate", "gene", "generation", "girl",
    "glass", "goal", "gold", "golf", "good", "goods", "government", "governor", "grade",
    "grant", "grass", "ground", "group", "growth", "guard", "guest", "guide", "gun",
    "guy", "hair", "half", "hall", "hand", "handle", "harbour", "head", "health",
    "heart", "heat", "height", "help", "hero", "hill", "history", "hole", "holiday",
    "home", "hope", "horse", "hospital", "host", "hotel", "hour", "house", "housing",
    "human", "ice", "idea", "identity", "image", "imagination", "impact", "implication",
    "importance", "impression", "improvement", "incident", "income", "increase",
    "independence", "index", "individual", "industry", "inflation", "influence",
    "information", "initiative", "injury", "input", "inquiry", "instance", "institution",
    "instruction", "instrument", "insurance", "intelligence", "intention", "interest",
    "internet", "interpretation", "intervention", "interview", "introduction",
    "investigation", "investment", "investor", "iron", "island", "issue", "item",
    "jacket", "job", "joint", "joke", "journal", "journalist", "journey", "judge",
    "judgment", "juice", "jump", "jury", "justice", "key", "kid", "king", "kitchen",
    "knee", "knife", "knowledge", "lab", "label", "labor", "lack", "lady", "lake",
    "land", "landscape", "language", "laugh", "launch", "law", "lawyer", "layer",
    "lead", "leader", "leadership", "leaf", "league", "learning", "leather", "leave",
    "lecture", "leg", "legislation", "length", "lesson", "letter", "level", "library",
    "license", "lie", "life", "lift", "light", "limit", "line", "link", "lip",
    "list", "literature", "living", "loan", "location", "lock", "logic", "look",
    "lord", "loss", "lot", "love", "luck", "lunch", "machine", "magazine", "mail",
    "maintenance", "majority", "man", "management", "manager", "manner", "map",
    "margin", "mark", "market", "marriage", "mass", "master", "match", "material",
    "matter", "meal", "meaning", "measure", "meat", "mechanism", "media", "medicine",
    "medium", "meeting", "member", "membership", "memory", "mental", "mention",
    "message", "metal", "method", "middle", "mile", "milk", "mind", "mine", "minister",
    "ministry", "minute", "mirror", "mission", "mistake", "mix", "mixture", "model",
    "moment", "money", "month", "mood", "moon", "morning", "mortgage", "mother",
    "motion", "motor", "mountain", "mouse", "mouth", "move", "movement", "movie",
    "murder", "museum", "music", "name", "nation", "nature", "neck", "need",
    "negotiation", "neighbor", "neighborhood", "nerve", "network", "news", "newspaper",
    "night", "noise", "north", "nose", "note", "notice", "notion", "novel", "nuclear",
    "number", "nurse", "object", "objective", "obligation", "observation", "observer",
    "occasion", "occupation", "ocean", "offer", "office", "officer", "oil", "operation",
    "operator", "opinion", "opportunity", "opposition", "option", "orange", "order",
    "organisation", "origin", "outcome", "output", "outside", "owner", "pace", "pack",
    "package", "page", "pain", "pair", "palace", "panel", "paper", "parent", "park",
    "parliament", "part", "participant", "participation", "partner", "partnership",
    "party", "passage", "passenger", "past", "path", "patience", "patient", "pattern",
    "pay", "payment", "peace", "peak", "pen", "pension", "people", "perception",
    "performance", "period", "permission", "person", "personality", "perspective",
    "phase", "phenomenon", "philosophy", "phone", "photograph", "phrase", "physics",
    "piano", "picture", "piece", "pilot", "pipe", "pitch", "place", "plain", "plan",
    "plane", "planet", "planning", "plant", "plastic", "plate", "platform", "play",
    "player", "pleasure", "plenty", "plot", "pocket", "poem", "poet", "poetry",
    "point", "police", "policy", "politics", "poll", "pollution", "pool", "population",
    "port", "portion", "position", "possession", "possibility", "post", "pot",
    "potential", "pound", "poverty", "powder", "power", "practice", "prayer", "premium",
    "presence", "present", "presentation", "president", "press", "pressure", "price",
    "pride", "priest", "prince", "princess", "principle", "print", "priority", "prison",
    "privacy", "prize", "problem", "procedure", "process", "producer", "product",
    "production", "profession", "professional", "professor", "profit", "program",
    "progress", "project", "promise", "promotion", "proof", "property", "proportion",
    "proposal", "prospect", "protection", "protein", "protest", "provision", "pub",
    "public", "publication", "publicity", "publisher", "punishment", "pupil", "purchase",
    "purpose", "quality", "quantity", "quarter", "queen", "question", "queue", "race",
    "radio", "rail", "railway", "rain", "range", "rank", "rate", "ratio", "reaction",
    "reader", "reading", "reality", "reason", "recall", "receipt", "recognition",
    "recommendation", "record", "recording", "recovery", "reduction", "reference",
    "reflection", "reform", "region", "register", "regulation", "rejection", "relation",
    "relationship", "release", "relief", "religion", "remark", "rent", "repeat",
    "replacement", "reply", "report", "reporter", "representation", "representative",
    "republic", "reputation", "request", "requirement", "rescue", "research", "reserve",
    "resident", "resistance", "resolution", "resource", "respect", "response",
    "responsibility", "rest", "restaurant", "result", "return", "revenue", "review",
    "revolution", "reward", "rice", "right", "ring", "rise", "risk", "river", "road",
    "rock", "role", "roof", "room", "root", "rose", "round", "route", "routine",
    "row", "rule", "run", "safety", "sail", "salary", "sale", "sample", "sand",
    "satisfaction", "saving", "scale", "scene", "scheme", "school", "science",
    "scientist", "scope", "score", "screen", "sea", "search", "season", "seat",
    "secretary", "section", "sector", "security", "seed", "selection", "self", "seller",
    "sense", "sentence", "sequence", "series", "servant", "service", "session", "set",
    "setting", "settlement", "sex", "shade", "shadow", "shape", "share", "sheet",
    "shelf", "shell", "shelter", "shift", "ship", "shirt", "shock", "shoe", "shop",
    "shopping", "shore", "shot", "shoulder", "show", "shower", "side", "sight", "sign",
    "signal", "significance", "silence", "silver", "sin", "singer", "single", "sister",
    "site", "situation", "size", "skill", "skin", "sky", "slave", "sleep", "slice",
    "smile", "smoke", "snow", "society", "software", "soil", "soldier", "solicitor",
    "solution", "son", "song", "sort", "soul", "sound", "source", "south", "space",
    "speaker", "specialist", "species", "speech", "speed", "spirit", "spokesman",
    "sport", "spot", "spring", "square", "stability", "staff", "stage", "stake",
    "stand", "standard", "star", "start", "state", "statement", "station", "statistics",
    "status", "stay", "steel", "step", "stick", "stock", "stomach", "stone", "stop",
    "storage", "store", "storm", "story", "stranger", "strategy", "stream", "street",
    "strength", "stress", "strike", "structure", "struggle", "student", "studio",
    "study", "stuff", "style", "subject", "substance", "success", "sugar", "suggestion",
    "suit", "sum", "summer", "summit", "sun", "supply", "support", "supporter",
    "surface", "surgery", "surplus", "surprise", "survey", "survival", "suspect",
    "symbol", "sympathy", "symptom", "system", "table", "tail", "tale", "talent",
    "talk", "tank", "tape", "target", "task", "taste", "tax", "tea", "teacher",
    "teaching", "team", "tear", "technique", "technology", "telephone", "television",
    "temperature", "temple", "tendency", "tension", "tent", "term", "terms", "territory",
    "terror", "test", "text", "thanks", "theatre", "theme", "theory", "therapy",
    "thing", "thinking", "thought", "threat", "throat", "ticket", "tie", "time",
    "tip", "title", "today", "toe", "toilet", "tomorrow", "tone", "tongue", "tonight",
    "tool", "tooth", "top", "topic", "total", "touch", "tour", "tourist", "tournament",
    "tower", "town", "track", "trade", "tradition", "traffic", "train", "trainer",
    "training", "transfer", "transition", "transport", "travel", "treaty", "treatment",
    "tree", "trend", "trial", "trick", "trip", "troop", "trouble", "truck", "trust",
    "truth", "tube", "turn", "type", "uncle", "understanding", "unemployment", "union",
    "unit", "universe", "university", "use", "user", "valley", "value", "van",
    "variety", "vegetable", "vehicle", "version", "victim", "victory", "video", "view",
    "village", "violence", "vision", "visit", "visitor", "voice", "volume", "vote",
    "wage", "wait", "walk", "wall", "war", "ward", "warning", "wash", "waste",
    "watch", "water", "wave", "way", "weakness", "wealth", "weapon", "weather",
    "web", "wedding", "week", "weekend", "weight", "welcome", "welfare", "west",
    "wheat", "wheel", "wife", "will", "wind", "window", "wine", "wing", "winner",
    "winter", "wire", "wish", "witness", "woman", "wonder", "wood", "wool", "word",
    "work", "worker", "works", "workshop", "world", "worry", "worth", "wound", "writer",
    "writing", "yard", "year", "yesterday", "youth", "zone",
]

# Common adjectives
BASE_ADJECTIVES = [
    "able", "absolute", "academic", "acceptable", "accessible", "active", "actual",
    "additional", "adequate", "administrative", "adult", "advanced", "afraid",
    "aggressive", "agricultural", "alive", "alone", "alternative", "amazing", "ancient",
    "angry", "annual", "anxious", "apparent", "appropriate", "armed", "artificial",
    "artistic", "ashamed", "asleep", "attractive", "automatic", "available", "average",
    "aware", "awful", "bad", "basic", "beautiful", "big", "bitter", "blind", "blue",
    "bold", "boring", "brave", "brief", "bright", "brilliant", "broad", "brown",
    "busy", "calm", "capable", "capital", "careful", "central", "certain", "cheap",
    "chemical", "chief", "civil", "classical", "clean", "clear", "clever", "clinical",
    "close", "closed", "cold", "comfortable", "commercial", "common", "competitive",
    "complete", "complex", "comprehensive", "concerned", "confident", "conscious",
    "considerable", "consistent", "constant", "constitutional", "contemporary",
    "content", "continuous", "convenient", "conventional", "cool", "corporate",
    "correct", "creative", "criminal", "critical", "crucial", "cultural", "curious",
    "current", "daily", "dangerous", "dark", "dead", "dear", "decent", "deep",
    "defensive", "definite", "deliberate", "delicate", "democratic", "dependent",
    "desperate", "detailed", "determined", "different", "difficult", "digital",
    "direct", "dirty", "disabled", "disappointed", "distinct", "domestic", "double",
    "dramatic", "drunk", "dry", "due", "dull", "eager", "early", "easy", "economic",
    "educational", "effective", "efficient", "elderly", "electoral", "electric",
    "electronic", "elegant", "emotional", "empty", "encouraging", "english", "enormous",
    "entire", "environmental", "equal", "equivalent", "essential", "eternal", "ethnic",
    "european", "even", "eventual", "everyday", "evident", "evil", "exact", "excellent",
    "exceptional", "excited", "exciting", "executive", "existing", "expensive",
    "experienced", "experimental", "expert", "explicit", "extensive", "external",
    "extra", "extraordinary", "extreme", "fair", "false", "familiar", "famous",
    "fantastic", "far", "fast", "fat", "fatal", "favorable", "favorite", "federal",
    "female", "few", "fierce", "final", "financial", "fine", "firm", "fit", "fixed",
    "flat", "flexible", "following", "fond", "foreign", "formal", "former", "fortunate",
    "forward", "free", "frequent", "fresh", "friendly", "front", "frozen", "full",
    "fun", "functional", "fundamental", "funny", "furious", "future", "gay", "general",
    "generous", "gentle", "genuine", "german", "giant", "glad", "global", "golden",
    "good", "gorgeous", "grand", "grateful", "great", "green", "grey", "gross",
    "growing", "guilty", "happy", "hard", "harmful", "harsh", "healthy", "heavy",
    "helpful", "hidden", "high", "historic", "historical", "holy", "honest", "horrible",
    "hot", "huge", "human", "hungry", "ideal", "ill", "illegal", "immediate",
    "immense", "immune", "important", "impossible", "impressed", "impressive",
    "inadequate", "inappropriate", "inc", "incident", "incredible", "independent",
    "indirect", "individual", "industrial", "inevitable", "inferior", "infinite",
    "influential", "informal", "initial", "inland", "inner", "innocent", "innovative",
    "instant", "institutional", "insufficient", "intellectual", "intelligent",
    "intense", "intensive", "interested", "interesting", "interim", "internal",
    "international", "intimate", "involved", "joint", "keen", "key", "kind", "known",
    "labour", "lacking", "large", "late", "lateral", "latest", "latter", "lazy",
    "leading", "lean", "left", "legal", "legitimate", "lengthy", "less", "lesser",
    "level", "liable", "liberal", "light", "likely", "limited", "linear", "linguistic",
    "liquid", "literary", "little", "live", "living", "local", "logical", "lone",
    "lonely", "long", "loose", "lost", "loud", "lovely", "low", "lower", "loyal",
    "lucky", "mad", "magic", "magical", "magnetic", "magnificent", "main", "major",
    "male", "manual", "marine", "marked", "married", "massive", "master", "material",
    "mature", "maximum", "meaningful", "mechanical", "medical", "medieval", "medium",
    "mental", "mere", "middle", "mild", "military", "minimal", "minimum", "minor",
    "miserable", "missing", "mixed", "mobile", "moderate", "modern", "modest",
    "molecular", "moral", "multiple", "municipal", "musical", "mutual", "mysterious",
    "naked", "narrow", "nasty", "national", "native", "natural", "naval", "near",
    "nearby", "neat", "necessary", "negative", "nervous", "net", "neutral", "new",
    "nice", "noble", "normal", "northern", "notable", "nuclear", "numerous", "objective",
    "obvious", "occasional", "odd", "offensive", "official", "ok", "okay", "old",
    "ongoing", "only", "open", "opening", "operational", "opposite", "optical",
    "optimistic", "oral", "orange", "ordinary", "organic", "organizational", "oriental",
    "original", "other", "outdoor", "outer", "outside", "outstanding", "overall",
    "overseas", "overwhelming", "own", "painful", "pale", "parallel", "parliamentary",
    "partial", "particular", "passionate", "passive", "past", "patient", "payable",
    "peaceful", "peculiar", "perfect", "permanent", "personal", "petty", "philosophical",
    "physical", "pink", "plain", "plastic", "pleasant", "pleased", "plenty", "plus",
    "pointed", "polar", "polite", "political", "poor", "popular", "positive", "possible",
    "potential", "powerful", "practical", "precious", "precise", "pregnant", "premier",
    "prepared", "present", "presidential", "pretty", "previous", "primary", "prime",
    "primitive", "principal", "prior", "private", "probable", "productive", "professional",
    "profitable", "profound", "progressive", "prominent", "promising", "proper",
    "proposed", "prospective", "protective", "protestant", "proud", "provincial",
    "psychological", "public", "pure", "purple", "qualified", "quick", "quiet",
    "racial", "radical", "random", "rapid", "rare", "rational", "raw", "ready",
    "real", "realistic", "reasonable", "recent", "red", "reduced", "regional",
    "regular", "regulatory", "related", "relative", "relaxed", "relevant", "reliable",
    "religious", "reluctant", "remaining", "remarkable", "remote", "renewed",
    "representative", "republican", "residential", "resistant", "resolved", "respectable",
    "respective", "responsible", "restricted", "resulting", "retired", "revolutionary",
    "rich", "ridiculous", "right", "rigid", "rising", "risky", "rival", "romantic",
    "rough", "round", "royal", "ruling", "rural", "russian", "sacred", "sad",
    "safe", "same", "satisfied", "scared", "scientific", "scottish", "secondary",
    "secret", "secure", "select", "selected", "selective", "senior", "sensible",
    "sensitive", "separate", "serious", "severe", "sexual", "shallow", "sharp",
    "sheer", "short", "shy", "sick", "significant", "silent", "silly", "silver",
    "similar", "simple", "simultaneous", "single", "skilled", "slight", "slim",
    "slow", "small", "smart", "smooth", "so", "social", "socialist", "soft", "solar",
    "sole", "solid", "sophisticated", "sorry", "sound", "sour", "south", "southern",
    "soviet", "spare", "special", "specific", "spectacular", "spiritual", "splendid",
    "spoken", "sporting", "stable", "standard", "static", "statistical", "steady",
    "steep", "sticky", "stiff", "still", "straight", "strange", "strategic", "strict",
    "striking", "strong", "structural", "stupid", "subject", "subsequent", "substantial",
    "subtle", "successful", "successive", "sudden", "sufficient", "suitable", "sunny",
    "super", "superb", "superior", "supporting", "supreme", "sure", "surprised",
    "surprising", "surrounding", "suspicious", "sustainable", "sweet", "swift",
    "symbolic", "sympathetic", "systematic", "tall", "technical", "teenage", "temporary",
    "tender", "terrible", "terrific", "territorial", "thick", "thin", "thorough",
    "tight", "tiny", "tired", "top", "total", "tough", "toxic", "traditional",
    "tremendous", "tricky", "tropical", "troubled", "true", "typical", "ugly",
    "ultimate", "unable", "uncertain", "uncomfortable", "underlying", "understanding",
    "unexpected", "unfair", "unfortunate", "unhappy", "uniform", "unique", "united",
    "universal", "unknown", "unlikely", "unnecessary", "unusual", "upper", "upset",
    "urban", "urgent", "used", "useful", "useless", "usual", "valid", "valuable",
    "variable", "various", "vast", "verbal", "vertical", "very", "viable", "violent",
    "virtual", "visible", "visual", "vital", "voluntary", "vulnerable", "warm",
    "weak", "wealthy", "weekly", "weird", "welcome", "well", "welsh", "western",
    "wet", "white", "whole", "wicked", "wide", "widespread", "wild", "willing",
    "wise", "wonderful", "wooden", "working", "worldwide", "worried", "worse",
    "worst", "worth", "worthwhile", "worthy", "wrong", "yellow", "young",
]


def generate_vocabulary(vocab=None):
    """
    Generate comprehensive vocabulary from base word lists.
    
    Creates:
    - All base verbs, nouns, and adjectives
    - Common variations and forms
    """
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
    
    total_added = 0
    
    # Add all base verbs
    for verb in BASE_VERBS:
        entry = WordEntry(verb, [PartOfSpeech.VERB], [f"to {verb}"], WordFrequency.COMMON)
        vocab.add_word(entry)
        total_added += 1
        
        # Add -ing form
        if verb.endswith('e'):
            ing_form = verb[:-1] + 'ing'
        elif verb.endswith('ie'):
            ing_form = verb[:-2] + 'ying'
        elif len(verb) > 2 and verb[-1] not in 'aeiou' and verb[-2] in 'aeiou' and verb[-3] not in 'aeiou':
            ing_form = verb + verb[-1] + 'ing'
        else:
            ing_form = verb + 'ing'
        vocab.add_word(WordEntry(ing_form, [PartOfSpeech.VERB], [f"{verb} (present)"], WordFrequency.COMMON))
        total_added += 1
        
    # Add all base nouns
    for noun in BASE_NOUNS:
        entry = WordEntry(noun, [PartOfSpeech.NOUN], [f"{noun}"], WordFrequency.COMMON)
        vocab.add_word(entry)
        total_added += 1
        
    # Add all base adjectives
    for adj in BASE_ADJECTIVES:
        entry = WordEntry(adj, [PartOfSpeech.ADJECTIVE], [f"{adj}"], WordFrequency.COMMON)
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[VocabularyGenerator] Generated {total_added} words from base lists")
    print(f"[VocabularyGenerator] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_generator_stats() -> dict:
    """Get generator vocabulary statistics."""
    return {
        "base_verbs": len(BASE_VERBS),
        "base_nouns": len(BASE_NOUNS),
        "base_adjectives": len(BASE_ADJECTIVES),
        "total_base": len(BASE_VERBS) + len(BASE_NOUNS) + len(BASE_ADJECTIVES),
        "estimated_expansion": (len(BASE_VERBS) * 2) + len(BASE_NOUNS) + len(BASE_ADJECTIVES)
    }
