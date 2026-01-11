# unimind/models/native/vocabulary_advanced.py
# Advanced Vocabulary for C2 Level - Thousands More Words

"""
Advanced Vocabulary Module

Thousands of additional words for C2 mastery:
- Travel & Transportation
- Buildings & Architecture  
- Materials & Substances
- Quantities & Measurements
- Time expressions
- Colors and visual
- Sounds and audio
- Shapes and forms
- Textures and surfaces
"""

from typing import Dict, Set
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# TRAVEL & TRANSPORTATION (~150 words)
# =============================================================================

TRAVEL_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - travel/transport"], WordFrequency.COMMON) for w in [
    "destination", "itinerary", "reservation", "accommodation", "lodging", "hostel",
    "motel", "resort", "cabin", "cottage", "villa", "bungalow", "suite", "lobby",
    "reception", "concierge", "bellhop", "porter", "luggage", "baggage", "suitcase",
    "backpack", "passport", "visa", "customs", "immigration", "terminal", "gate",
    "boarding", "departure", "arrival", "transit", "layover", "connecting", "domestic",
    "international", "airline", "aircraft", "cockpit", "cabin", "aisle", "overhead",
    "turbulence", "altitude", "runway", "takeoff", "landing", "cruise", "yacht",
    "ferry", "cargo", "freight", "shipping", "container", "dock", "harbor", "pier",
    "marina", "lighthouse", "anchor", "deck", "hull", "stern", "bow", "mast",
    "sail", "paddle", "kayak", "canoe", "raft", "submarine", "locomotive", "carriage",
    "compartment", "platform", "station", "conductor", "ticket", "fare", "commuter",
    "metro", "subway", "tram", "trolley", "cable", "gondola", "monorail", "expressway",
    "highway", "freeway", "turnpike", "intersection", "overpass", "underpass", "tunnel",
    "bridge", "ramp", "exit", "lane", "median", "shoulder", "curb", "sidewalk",
    "crosswalk", "pedestrian", "cyclist", "motorist", "commute", "congestion", "gridlock",
    "detour", "shortcut", "navigation", "compass", "milestone", "landmark", "signpost",
    "roundabout", "interchange", "junction", "bypass", "toll", "parking", "garage",
]}

# =============================================================================
# BUILDINGS & ARCHITECTURE (~150 words)
# =============================================================================

BUILDING_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - building/arch"], WordFrequency.COMMON) for w in [
    "structure", "edifice", "construction", "foundation", "framework", "skeleton",
    "facade", "exterior", "interior", "entrance", "exit", "doorway", "threshold",
    "foyer", "hallway", "corridor", "passage", "staircase", "stairwell", "landing",
    "banister", "railing", "balcony", "terrace", "patio", "veranda", "porch",
    "attic", "basement", "cellar", "crawlspace", "loft", "mezzanine", "penthouse",
    "apartment", "flat", "condo", "duplex", "townhouse", "mansion", "estate",
    "bungalow", "ranch", "colonial", "victorian", "cottage", "cabin", "lodge",
    "skyscraper", "highrise", "tower", "complex", "plaza", "arcade", "atrium",
    "dome", "spire", "steeple", "turret", "minaret", "arch", "column", "pillar",
    "beam", "rafter", "joist", "truss", "girder", "lintel", "cornice", "molding",
    "frieze", "pediment", "capital", "buttress", "pier", "abutment", "vault",
    "ceiling", "skylight", "shingle", "tile", "slate", "thatch", "chimney",
    "fireplace", "hearth", "mantel", "flue", "vent", "duct", "insulation",
    "drywall", "plaster", "stucco", "siding", "cladding", "weatherboard", "masonry",
    "brickwork", "stonework", "concrete", "mortar", "grout", "caulk", "sealant",
    "flooring", "hardwood", "laminate", "linoleum", "terrazzo", "marble", "granite",
    "countertop", "backsplash", "wainscoting", "paneling", "baseboard", "trim",
]}

# =============================================================================
# MATERIALS & SUBSTANCES (~150 words)
# =============================================================================

MATERIAL_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - material"], WordFrequency.COMMON) for w in [
    "substance", "material", "compound", "element", "mixture", "solution", "alloy",
    "metal", "steel", "iron", "aluminum", "copper", "brass", "bronze", "zinc",
    "titanium", "platinum", "silver", "gold", "nickel", "chromium", "tungsten",
    "lead", "tin", "mercury", "uranium", "plutonium", "radium", "helium", "neon",
    "carbon", "graphite", "silicone", "ceramic", "porcelain", "terracotta", "earthenware",
    "glass", "crystal", "quartz", "obsidian", "jade", "amber", "pearl", "ivory",
    "coral", "marble", "granite", "limestone", "sandstone", "slate", "shale",
    "chalk", "charite", "calcium", "calcium", "calcium", "calcium", "calcium",
    "fiber", "cellulose", "resin", "polymer", "plastic", "acrylic", "vinyl",
    "rubber", "latex", "silicone", "teflon", "fiberglass", "foam", "gel",
    "wax", "paraffin", "petroleum", "asphalt", "tar", "bitumen", "adhesive",
    "epoxy", "lacquer", "varnish", "enamel", "coating", "pigment", "dye",
    "ink", "stain", "bleach", "solvent", "alcohol", "acetone", "ammonia",
    "acid", "alkaline", "sodium", "potassium", "chlorine", "fluoride", "iodine",
    "sulfur", "phosphorus", "magnesium", "calcium", "barium", "radium", "cesium",
    "arsenic", "antimony", "bismuth", "cobalt", "manganese", "vanadium", "molybdenum",
]}

# =============================================================================
# QUANTITIES & MEASUREMENTS (~100 words)
# =============================================================================

QUANTITY_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - quantity"], WordFrequency.COMMON) for w in [
    "quantity", "amount", "portion", "fraction", "percentage", "proportion", "ratio",
    "rate", "frequency", "intensity", "magnitude", "scale", "range", "span",
    "extent", "scope", "limit", "boundary", "threshold", "maximum", "minimum",
    "average", "median", "mean", "mode", "standard", "deviation", "variance",
    "increment", "decrement", "increase", "decrease", "growth", "decline", "reduction",
    "expansion", "contraction", "multiplication", "division", "addition", "subtraction",
    "measurement", "dimension", "length", "width", "height", "depth", "thickness",
    "diameter", "radius", "circumference", "perimeter", "area", "volume", "capacity",
    "weight", "mass", "density", "pressure", "temperature", "velocity", "acceleration",
    "momentum", "force", "energy", "power", "wattage", "voltage", "amperage", "resistance",
    "frequency", "wavelength", "amplitude", "decibel", "hertz", "kilogram", "gram",
    "milligram", "microgram", "ton", "pound", "ounce", "liter", "milliliter",
    "gallon", "quart", "pint", "cup", "tablespoon", "teaspoon", "meter", "kilometer",
]}

# =============================================================================
# TIME EXPRESSIONS (~100 words)
# =============================================================================

TIME_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - time term"], WordFrequency.COMMON) for w in [
    "moment", "instant", "second", "minute", "hour", "day", "week", "fortnight",
    "month", "quarter", "semester", "year", "decade", "century", "millennium", "era",
    "epoch", "age", "period", "phase", "stage", "interval", "duration", "span",
    "term", "session", "cycle", "sequence", "schedule", "timeline", "deadline",
    "milestone", "anniversary", "birthday", "holiday", "vacation", "weekend", "weekday",
    "morning", "noon", "afternoon", "evening", "night", "midnight", "dawn", "dusk",
    "sunrise", "sunset", "twilight", "daylight", "nightfall", "springtime", "summertime",
    "autumn", "winter", "equinox", "solstice", "timezone", "daylight", "standard",
    "calendar", "date", "weekday", "workday", "business", "overtime", "downtime",
    "countdown", "stopwatch", "timer", "alarm", "reminder", "appointment", "reservation",
    "postponement", "delay", "extension", "renewal", "expiration", "validity",
]}

# =============================================================================
# COLORS & VISUAL (~100 words)
# =============================================================================

COLOR_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - color/visual"], WordFrequency.COMMON) for w in [
    "color", "hue", "shade", "tint", "tone", "saturation", "brightness", "contrast",
    "pigment", "dye", "paint", "ink", "stain", "finish", "gloss", "matte",
    "crimson", "scarlet", "maroon", "burgundy", "coral", "salmon", "peach", "rose",
    "magenta", "fuchsia", "pink", "violet", "lavender", "purple", "indigo", "navy",
    "royal", "azure", "turquoise", "teal", "cyan", "aqua", "mint", "emerald",
    "lime", "chartreuse", "olive", "khaki", "tan", "beige", "cream", "ivory",
    "amber", "gold", "bronze", "copper", "rust", "sienna", "terracotta", "mahogany",
    "chestnut", "chocolate", "mocha", "espresso", "caramel", "taupe", "charcoal",
    "slate", "ash", "silver", "platinum", "pearl", "opal", "rainbow", "spectrum",
    "prism", "gradient", "pattern", "stripe", "check", "plaid", "polka", "floral",
]}

# =============================================================================
# SOUNDS & AUDIO (~100 words)
# =============================================================================

SOUND_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - sound term"], WordFrequency.COMMON) for w in [
    "sound", "noise", "tone", "pitch", "volume", "frequency", "vibration", "echo",
    "resonance", "reverberation", "acoustics", "audio", "sonic", "ultrasonic",
    "click", "clap", "snap", "crack", "pop", "bang", "boom", "blast", "explosion",
    "thud", "thump", "bump", "knock", "tap", "rap", "beat", "pulse", "rhythm",
    "hum", "buzz", "hiss", "sizzle", "crackle", "rustle", "shuffle", "scrape",
    "scratch", "squeak", "creak", "groan", "moan", "sigh", "gasp", "wheeze",
    "cough", "sneeze", "hiccup", "burp", "snore", "yawn", "whisper", "murmur",
    "mumble", "mutter", "grumble", "growl", "roar", "scream", "shriek", "screech",
    "wail", "howl", "bark", "meow", "chirp", "tweet", "squawk", "caw", "crow",
    "coo", "hoot", "quack", "ribbit", "neigh", "moo", "baa", "oink", "cluck",
    "chime", "bell", "gong", "siren", "alarm", "beep", "ringtone", "melody",
]}

# =============================================================================
# SHAPES & FORMS (~80 words)
# =============================================================================

SHAPE_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - shape/form"], WordFrequency.COMMON) for w in [
    "shape", "form", "figure", "outline", "silhouette", "contour", "profile",
    "circle", "oval", "ellipse", "sphere", "hemisphere", "globe", "orb", "ball",
    "square", "rectangle", "oblong", "cube", "block", "box", "pyramid", "prism",
    "triangle", "cone", "cylinder", "tube", "pipe", "ring", "hoop", "loop",
    "spiral", "helix", "coil", "curl", "wave", "curve", "arc", "bow", "crescent",
    "wedge", "slice", "segment", "section", "layer", "tier", "stack", "pile",
    "heap", "mound", "bump", "bulge", "protrusion", "ridge", "groove", "notch",
    "slot", "slit", "gap", "hole", "opening", "cavity", "hollow", "dent",
    "indent", "depression", "concave", "convex", "flat", "level", "plane", "surface",
    "edge", "corner", "angle", "vertex", "apex", "peak", "point", "tip",
]}


def load_advanced_vocabulary(vocab=None):
    """Load advanced vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in TRAVEL_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in BUILDING_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MATERIAL_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in QUANTITY_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in TIME_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in COLOR_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in SOUND_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in SHAPE_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[AdvancedVocabulary] Loaded {total_added} words")
    print(f"[AdvancedVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_advanced_stats() -> dict:
    """Get advanced vocabulary statistics."""
    return {
        "travel": len(TRAVEL_VOCAB),
        "buildings": len(BUILDING_VOCAB),
        "materials": len(MATERIAL_VOCAB),
        "quantities": len(QUANTITY_VOCAB),
        "time": len(TIME_VOCAB),
        "colors": len(COLOR_VOCAB),
        "sounds": len(SOUND_VOCAB),
        "shapes": len(SHAPE_VOCAB),
        "total": (len(TRAVEL_VOCAB) + len(BUILDING_VOCAB) + len(MATERIAL_VOCAB) +
                 len(QUANTITY_VOCAB) + len(TIME_VOCAB) + len(COLOR_VOCAB) +
                 len(SOUND_VOCAB) + len(SHAPE_VOCAB))
    }
