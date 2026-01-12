# unimind/models/native/vocabulary_c1_push.py
# Final Push to C1 Level and Beyond

"""
C1 Push Vocabulary Module

Additional vocabulary to definitely reach C1 (8,000+) and push toward C2:
- Technology terms
- Business jargon
- Legal terminology
- More everyday words
"""

from typing import Dict
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


def _make_entries(words: list, pos: PartOfSpeech) -> Dict:
    return {w: WordEntry(w, [pos], [w], WordFrequency.COMMON) for w in words}


# =============================================================================
# MORE TECHNOLOGY TERMS (~200 words)
# =============================================================================

TECH_MORE = [
    "accessibility", "adware", "agile", "analytics", "android", "anonymizer",
    "api", "applet", "archiving", "authentication", "autoresponder", "backend",
    "bandwidth", "beta", "bigdata", "binary", "biometric", "bitcoin", "bitrate",
    "blockchain", "blog", "blogger", "bluetooth", "bookmark", "boolean", "boot",
    "bot", "broadband", "browser", "buffer", "bug", "byte", "cache", "captcha",
    "chatbot", "chip", "clickthrough", "clipboard", "cloud", "codec", "compiler",
    "compression", "computing", "connectivity", "cookie", "crowdsourcing", "cryptocurrency",
    "css", "cursor", "cybersecurity", "daemon", "dashboard", "datacenter", "dataset",
    "debugging", "decompression", "defragmentation", "deployment", "desktop", "developer",
    "devops", "digital", "digitization", "disk", "dns", "docker", "domain", "download",
    "downtime", "driver", "dropdown", "e-commerce", "ecosystem", "email", "embedded",
    "emoji", "emulator", "encryption", "endpoint", "ethernet", "executable", "extension",
    "extraction", "failover", "favicon", "feedback", "fiber", "file", "fintech",
    "firewall", "firmware", "flash", "folder", "font", "formatting", "framework",
    "freeware", "frontend", "ftp", "gateway", "geolocation", "gigabyte", "github",
    "gpu", "graphics", "gui", "hacker", "hacking", "hardware", "hashtag", "hdmi",
    "header", "helpdesk", "hexadecimal", "hibernate", "homepage", "hosting", "hotspot",
    "html", "http", "hyperlink", "hypertext", "icon", "ide", "import", "inbox",
    "indexing", "informatics", "infrastructure", "inline", "input", "instagram",
    "installation", "instance", "integration", "interface", "internet", "intranet",
    "ios", "ip", "isp", "iteration", "java", "javascript", "json", "kernel",
    "keyboard", "kilobyte", "kubernetes", "lan", "laptop", "latency", "layer",
    "legacy", "library", "license", "link", "linux", "localhost", "log", "login",
    "logout", "loop", "machine", "macro", "mainframe", "malware", "markup", "megabyte",
    "memory", "metadata", "microchip", "microprocessor", "middleware", "migration",
    "mobile", "modem", "module", "monitor", "motherboard", "mouse", "multitasking",
    "mysql", "namespace", "navigation", "nesting", "netiquette", "network", "neural",
    "node", "notification", "npm", "object", "offline", "onboarding", "online",
    "opensource", "operating", "optimization", "os", "outage", "output", "overflow",
    "packet", "pagination", "parameter", "parsing", "partition", "password", "patch",
    "path", "payload", "pdf", "peer", "performance", "peripheral", "permission",
    "phishing", "php", "ping", "pipeline", "pixel", "placeholder", "plaintext",
    "platform", "plugin", "podcast", "pointer", "popup", "port", "portal", "post",
    "preprocessing", "printer", "privacy", "procedural", "processing", "processor",
    "profile", "programming", "prompt", "protocol", "provider", "proxy", "python",
    "query", "queue", "quicksort", "ram", "ransomware", "rdbms", "readme", "realtime",
    "reboot", "recursion", "redirect", "redundancy", "refresh", "regex", "registry",
    "relational", "release", "remote", "rendering", "repository", "request", "resolution",
    "responsive", "restore", "retrieval", "rgb", "robotics", "rollback", "rom",
    "router", "routing", "runtime", "saas", "sandbox", "scalability", "scanner",
    "scheduling", "schema", "screenshot", "script", "scripting", "scroll", "sdk",
    "search", "security", "segmentation", "selector", "semiconductor", "serial",
    "server", "serverless", "session", "shareware", "shell", "shortcut", "sidebar",
    "signup", "simulation", "sitemap", "smartphone", "snippet", "socket", "software",
]

TECH_VOCAB = _make_entries(TECH_MORE, PartOfSpeech.NOUN)


# =============================================================================
# MORE BUSINESS TERMS (~200 words)
# =============================================================================

BUSINESS_MORE = [
    "accountability", "acquisition", "advertising", "affiliate", "agenda", "agreement",
    "allowance", "ambassador", "amortization", "analysis", "analyst", "annual",
    "announcement", "appreciation", "arbitration", "assessment", "assignment", "association",
    "audit", "authority", "automation", "balance", "banking", "bankruptcy", "benchmark",
    "beneficiary", "bidding", "billing", "blueprint", "bonus", "bookkeeping", "branding",
    "breakeven", "briefing", "brokerage", "budget", "bureaucracy", "buyout", "campaign",
    "candidate", "capacity", "capitalism", "capitalization", "career", "cashflow",
    "certification", "chairman", "channel", "charter", "clearance", "client", "closing",
    "coaching", "collaboration", "collateral", "collection", "commerce", "commission",
    "commitment", "committee", "commodity", "communication", "compensation", "competition",
    "competitive", "compliance", "conference", "confidentiality", "conglomerate",
    "consensus", "consolidation", "consultant", "consulting", "consumer", "contingency",
    "contracting", "contractor", "contribution", "controlling", "conversion", "cooperation",
    "coordination", "copyright", "corporate", "corporation", "correlation", "correspondence",
    "counterpart", "coverage", "creativity", "credibility", "creditor", "criteria",
    "customer", "deadline", "dealership", "debriefing", "decentralization", "decision",
    "delegation", "delivery", "demographic", "department", "depreciation", "derivative",
    "designation", "development", "differentiation", "director", "disbursement", "disclosure",
    "discount", "discrimination", "dismissal", "disruption", "distribution", "diversification",
    "dividend", "documentation", "downsizing", "downtrend", "downturn", "draft",
    "drawdown", "earnings", "economy", "effectiveness", "efficiency", "elasticity",
    "embargo", "employee", "employer", "employment", "empowerment", "endorsement",
    "engagement", "enterprise", "entrepreneur", "entrepreneurship", "entry", "environment",
    "equilibrium", "equity", "escalation", "estimate", "evaluation", "evolution",
    "excellence", "exchange", "exclusivity", "execution", "executive", "exemption",
    "exit", "expansion", "expectation", "expenditure", "expertise", "export",
    "exposure", "facilitation", "facility", "factoring", "feasibility", "feedback",
    "fiduciary", "finance", "financing", "fiscal", "flexibility", "fluctuation",
    "forecast", "forfeiture", "formation", "franchise", "franchising", "freelance",
    "fulfillment", "functionality", "funding", "fundraising", "futures", "globalization",
    "governance", "grant", "gross", "growth", "guarantee", "guidance", "guideline",
    "headquarters", "hedging", "hierarchy", "hiring", "holding", "hospitality",
    "human", "impact", "implementation", "import", "improvement", "incentive",
    "incidence", "income", "incorporation", "increment", "incubator", "independence",
    "index", "indication", "indicator", "industry", "inflation", "influence",
    "infrastructure", "initiative", "innovation", "input", "inquiry", "insider",
    "insolvency", "inspection", "installation", "institution", "instruction", "insurance",
    "integration", "integrity", "intellectual", "intelligence", "intensity", "interaction",
    "interest", "interference", "intermediary", "internship", "interpretation", "intervention",
]

BUSINESS_VOCAB = _make_entries(BUSINESS_MORE, PartOfSpeech.NOUN)


# =============================================================================
# EVEN MORE WORDS (~400 words)
# =============================================================================

EXTRA_WORDS = [
    # More nouns
    "abstraction", "acceleration", "accommodation", "accumulation", "acknowledgment",
    "acquisition", "activation", "adaptation", "adjustment", "administration",
    "admission", "adoption", "advancement", "advertisement", "affirmation",
    "aggregation", "agitation", "allocation", "alteration", "amplification",
    "annotation", "anticipation", "appreciation", "appropriation", "approximation",
    "articulation", "aspiration", "assassination", "assertion", "assessment",
    "assimilation", "association", "assumption", "attestation", "attribution",
    "authorization", "automation", "calculation", "calibration", "cancellation",
    "capitalization", "categorization", "celebration", "centralization", "certification",
    "characterization", "circulation", "clarification", "classification", "collaboration",
    "collection", "colonization", "combination", "commemoration", "commercialization",
    "communication", "compensation", "compilation", "completion", "complication",
    "composition", "comprehension", "computation", "concentration", "conceptualization",
    "condemnation", "condensation", "configuration", "confirmation", "confrontation",
    "congregation", "conjugation", "connection", "consecration", "conservation",
    "consideration", "consolidation", "consultation", "contamination", "contemplation",
    "continuation", "contradiction", "contribution", "conversation", "conversion",
    "conviction", "cooperation", "coordination", "corporation", "correlation",
    "corruption", "creation", "cultivation", "customization", "decentralization",
    "declaration", "decomposition", "decoration", "dedication", "deduction",
    "defamation", "definition", "degradation", "delegation", "deliberation",
    "delineation", "demonstration", "denomination", "denunciation", "depiction",
    "depopulation", "deportation", "depreciation", "depression", "derivation",
    "description", "desegregation", "designation", "destination", "destruction",
    "deterioration", "determination", "devaluation", "devastation", "deviation",
    "differentiation", "digitization", "discrimination", "dislocation", "dispensation",
    "displacement", "disposition", "disqualification", "dissemination", "dissertation",
    "dissolution", "distinction", "distortion", "distribution", "diversification",
    "documentation", "domestication", "domination", "donation", "dramatization",
    "duplication", "duration", "dysfunction", "education", "elaboration",
    "electrification", "elevation", "elimination", "emanation", "emancipation",
    "embarkation", "emigration", "emission", "emotion", "emphasis", "emulation",
    "encapsulation", "encryption", "enumeration", "equation", "eradication",
    "erosion", "eruption", "escalation", "estimation", "evacuation", "evaluation",
    "evaporation", "evolution", "exaggeration", "examination", "excavation",
    "exclamation", "exclusion", "execution", "exemption", "exhibition",
    "exhortation", "expectation", "expedition", "experimentation", "expiration",
    "explanation", "exploitation", "exploration", "exportation", "exposition",
    "expropriation", "expulsion", "extension", "extermination", "extraction",
    "extrapolation", "fabrication", "facilitation", "falsification", "fascination",
    "federation", "fermentation", "fertilization", "figuration", "filtration",
    "finalization", "fluctuation", "formalization", "formation", "formulation",
    "fortification", "foundation", "fragmentation", "frustration", "fumigation",
    "generalization", "generation", "gentrification", "germination", "globalization",
    "glorification", "graduation", "gratification", "gravitation", "hallucination",
    "harmonization", "hesitation", "hibernation", "homogenization", "hospitalization",
    "humanization", "humiliation", "hybridization", "hydrogenation", "hyphenation",
    "identification", "illumination", "illustration", "imagination", "imitation",
    "immigration", "immunization", "implementation", "implication", "importation",
    "imposition", "imprecision", "improvisation", "inactivation", "inauguration",
    "incarceration", "incarnation", "inclination", "incorporation", "incrimination",
    "indemnification", "indication", "indoctrination", "industrialization", "infiltration",
    "inflammation", "inflation", "information", "inhalation", "initialization",
    "initiation", "injection", "innovation", "inoculation", "inscription",
    "installation", "instigation", "institutionalization", "instruction", "instrumentation",
    "insulation", "integration", "intensification", "interaction", "interception",
    "interconnection", "interpretation", "interrogation", "interruption", "intersection",
    "intervention", "intimidation", "intonation", "intoxication", "introduction",
    "intuition", "invasion", "investigation", "invitation", "invocation",
    "ionization", "irrigation", "irritation", "isolation", "iteration",
    "justification", "legislation", "legitimation", "liberation", "limitation",
    "liquidation", "litigation", "localization", "locomotion", "lubrication",
    "magnetization", "magnification", "manifestation", "manipulation", "marginalization",
    "materialization", "maturation", "maximization", "mechanization", "mediation",
    "medication", "meditation", "memorization", "mention", "migration",
    "militarization", "minimization", "misrepresentation", "mobilization", "moderation",
    "modernization", "modification", "modulation", "monetization", "monopolization",
    "motivation", "multiplication", "mutation", "narration", "nationalization",
    "naturalization", "navigation", "negotiation", "neutralization", "nomination",
    "normalization", "notation", "notification", "nutrition", "obligation",
    "observation", "obstruction", "occupation", "operation", "optimization",
    "orchestration", "ordination", "organization", "orientation", "origination",
    "oscillation", "ostracization", "oxidation", "oxygenation", "pacification",
    "pagination", "participation", "partition", "pasteurization", "penetration",
    "perception", "perfection", "perforation", "perpetuation", "personalization",
    "personification", "persuasion", "perturbation", "petition", "plantation",
    "polarization", "pollenization", "pollution", "population", "position",
    "possession", "potentiation", "precipitation", "predetermination", "prediction",
    "predomination", "preoccupation", "preparation", "prescription", "presentation",
    "preservation", "presumption", "prevention", "privatization", "probation",
    "proclamation", "procrastination", "production", "professionalization", "progression",
    "prohibition", "projection", "proliferation", "prolongation", "promotion",
]

EXTRA_VOCAB = _make_entries(EXTRA_WORDS, PartOfSpeech.NOUN)


def load_c1_push_vocabulary(vocab=None):
    """Load C1 push vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in TECH_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in BUSINESS_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in EXTRA_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[C1PushVocabulary] Loaded {total_added} additional words")
    print(f"[C1PushVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_c1_push_stats() -> dict:
    """Get C1 push vocabulary statistics."""
    return {
        "tech": len(TECH_VOCAB),
        "business": len(BUSINESS_VOCAB),
        "extra": len(EXTRA_VOCAB),
        "total": len(TECH_VOCAB) + len(BUSINESS_VOCAB) + len(EXTRA_VOCAB)
    }
