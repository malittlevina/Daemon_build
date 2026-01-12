# unimind/models/native/vocabulary_comprehensive.py
# Comprehensive Vocabulary for C2 Level - Thousands of Additional Words

"""
Comprehensive Vocabulary Module

Massive word collection covering:
- Everyday life (food, clothing, household)
- Nature and environment
- Body and health
- Professions and occupations
- Actions and behaviors
- Descriptive words
- Numbers and quantities
- And many more domains
"""

from typing import Dict, List, Set
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency

# =============================================================================
# FOOD & COOKING (~200 words)
# =============================================================================

FOOD_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - food item"], WordFrequency.COMMON) for w in [
    "ingredient", "recipe", "cuisine", "appetizer", "entree", "dessert", "beverage",
    "snack", "meal", "breakfast", "lunch", "dinner", "brunch", "feast", "picnic",
    "steak", "beef", "pork", "lamb", "veal", "bacon", "sausage", "ham", "turkey",
    "salmon", "tuna", "shrimp", "lobster", "crab", "oyster", "mussel", "squid",
    "pasta", "noodle", "spaghetti", "pizza", "burger", "sandwich", "taco", "burrito",
    "soup", "stew", "curry", "sauce", "gravy", "dressing", "marinade", "seasoning",
    "spice", "herb", "garlic", "onion", "pepper", "tomato", "potato", "carrot",
    "celery", "broccoli", "spinach", "lettuce", "cabbage", "cucumber", "mushroom",
    "bean", "pea", "corn", "olive", "avocado", "lemon", "lime", "grape", "berry",
    "strawberry", "blueberry", "raspberry", "cherry", "peach", "pear", "mango",
    "pineapple", "watermelon", "melon", "coconut", "almond", "walnut", "peanut",
    "chocolate", "candy", "cookie", "cake", "pie", "pastry", "bread", "toast",
    "cereal", "oatmeal", "pancake", "waffle", "muffin", "croissant", "bagel",
    "yogurt", "cream", "ice", "gelato", "pudding", "custard", "syrup", "honey",
    "jam", "jelly", "peanut", "butter", "margarine", "mayonnaise", "ketchup",
    "mustard", "vinegar", "oil", "flour", "yeast", "batter", "dough", "crust",
    "slice", "portion", "serving", "calorie", "protein", "carbohydrate", "fiber",
    "vitamin", "mineral", "nutrient", "organic", "vegetarian", "vegan", "gluten",
]}

# =============================================================================
# HOUSEHOLD & HOME (~200 words)
# =============================================================================

HOUSEHOLD_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - household item"], WordFrequency.COMMON) for w in [
    "furniture", "appliance", "fixture", "decoration", "carpet", "rug", "curtain",
    "blind", "sofa", "couch", "armchair", "recliner", "ottoman", "cushion", "pillow",
    "blanket", "sheet", "mattress", "headboard", "dresser", "nightstand", "wardrobe",
    "closet", "shelf", "bookcase", "cabinet", "drawer", "desk", "counter", "sink",
    "faucet", "toilet", "bathtub", "shower", "towel", "soap", "shampoo", "toothbrush",
    "razor", "comb", "brush", "hairdryer", "iron", "ironing", "laundry", "detergent",
    "bleach", "fabric", "washer", "dryer", "dishwasher", "refrigerator", "freezer",
    "oven", "stove", "microwave", "toaster", "blender", "mixer", "kettle", "coffeemaker",
    "pot", "pan", "skillet", "wok", "saucepan", "baking", "roasting", "cutting",
    "knife", "spoon", "fork", "spatula", "ladle", "whisk", "grater", "peeler",
    "colander", "strainer", "tray", "platter", "dish", "bowl", "mug", "pitcher",
    "vase", "candle", "lamp", "chandelier", "bulb", "switch", "outlet", "plug",
    "cord", "wire", "battery", "thermostat", "heater", "radiator", "fan", "ventilator",
    "humidifier", "dehumidifier", "purifier", "vacuum", "broom", "mop", "bucket",
    "sponge", "cloth", "rag", "duster", "polish", "wax", "cleaner", "disinfectant",
    "garbage", "trash", "recycling", "bin", "bag", "container", "storage", "organizer",
    "hook", "hanger", "rack", "stand", "mount", "bracket", "screw", "nail", "hammer",
    "screwdriver", "wrench", "pliers", "drill", "saw", "tape", "glue", "paint", "brush",
]}

# =============================================================================
# CLOTHING & FASHION (~150 words)
# =============================================================================

CLOTHING_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - clothing item"], WordFrequency.COMMON) for w in [
    "garment", "outfit", "attire", "apparel", "wardrobe", "fashion", "style", "trend",
    "blouse", "sweater", "cardigan", "hoodie", "vest", "blazer", "suit", "tuxedo",
    "jeans", "trousers", "shorts", "skirt", "leggings", "stockings", "tights", "socks",
    "underwear", "bra", "panties", "boxers", "briefs", "pajamas", "nightgown", "robe",
    "swimsuit", "bikini", "trunks", "wetsuit", "raincoat", "parka", "windbreaker",
    "scarf", "glove", "mitten", "earmuff", "beanie", "cap", "beret", "fedora",
    "sneaker", "sandal", "flip-flop", "slipper", "heel", "pump", "loafer", "oxford",
    "boot", "ankle", "knee", "thigh", "leather", "suede", "canvas", "rubber",
    "belt", "suspender", "tie", "bowtie", "cufflink", "button", "zipper", "buckle",
    "pocket", "collar", "sleeve", "cuff", "hem", "seam", "stitch", "thread",
    "fabric", "cotton", "silk", "wool", "linen", "polyester", "nylon", "denim",
    "velvet", "satin", "lace", "chiffon", "tweed", "flannel", "fleece", "cashmere",
    "pattern", "stripe", "plaid", "polka", "floral", "solid", "print", "embroidery",
    "accessory", "jewelry", "necklace", "bracelet", "earring", "brooch", "watch",
    "sunglasses", "handbag", "purse", "wallet", "backpack", "luggage", "suitcase",
]}

# =============================================================================
# NATURE & ENVIRONMENT (~200 words)
# =============================================================================

NATURE_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - nature term"], WordFrequency.COMMON) for w in [
    "environment", "ecosystem", "habitat", "biome", "wilderness", "landscape",
    "terrain", "geography", "topography", "altitude", "elevation", "slope",
    "peak", "summit", "ridge", "cliff", "canyon", "gorge", "ravine", "cave",
    "cavern", "waterfall", "spring", "stream", "creek", "brook", "pond", "lagoon",
    "marsh", "swamp", "wetland", "meadow", "prairie", "savanna", "tundra", "glacier",
    "iceberg", "volcano", "lava", "magma", "crater", "geyser", "hot", "mineral",
    "rock", "stone", "boulder", "pebble", "gravel", "sand", "dirt", "mud", "clay",
    "soil", "sediment", "fossil", "crystal", "gemstone", "diamond", "ruby", "emerald",
    "vegetation", "flora", "fauna", "wildlife", "species", "mammal", "reptile",
    "amphibian", "insect", "butterfly", "bee", "ant", "spider", "worm", "snail",
    "wolf", "bear", "deer", "moose", "elk", "fox", "rabbit", "squirrel", "raccoon",
    "eagle", "hawk", "owl", "crow", "sparrow", "robin", "hummingbird", "penguin",
    "whale", "dolphin", "shark", "seal", "turtle", "frog", "snake", "lizard",
    "oak", "pine", "maple", "birch", "cedar", "willow", "palm", "bamboo", "fern",
    "moss", "algae", "fungus", "mushroom", "lichen", "vine", "shrub", "bush", "hedge",
    "bloom", "blossom", "petal", "stem", "leaf", "branch", "trunk", "bark", "root",
    "seed", "nut", "cone", "pollen", "nectar", "photosynthesis", "chlorophyll",
    "oxygen", "carbon", "nitrogen", "hydrogen", "ozone", "atmosphere", "climate",
    "weather", "precipitation", "humidity", "fog", "mist", "dew", "frost", "hail",
    "thunder", "lightning", "rainbow", "sunset", "sunrise", "dawn", "dusk", "twilight",
]}

# =============================================================================
# BODY & ANATOMY (~150 words)
# =============================================================================

BODY_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - body part/term"], WordFrequency.COMMON) for w in [
    "anatomy", "physiology", "organ", "tissue", "muscle", "bone", "joint", "tendon",
    "ligament", "cartilage", "spine", "vertebra", "skull", "rib", "pelvis", "femur",
    "skeleton", "marrow", "blood", "vein", "artery", "capillary", "plasma", "cell",
    "nerve", "neuron", "synapse", "reflex", "sensation", "perception", "stimulus",
    "lung", "liver", "kidney", "stomach", "intestine", "colon", "bladder", "pancreas",
    "spleen", "appendix", "gallbladder", "esophagus", "trachea", "larynx", "pharynx",
    "diaphragm", "thyroid", "adrenal", "pituitary", "hormone", "enzyme", "protein",
    "forehead", "temple", "cheek", "chin", "jaw", "eyebrow", "eyelash", "eyelid",
    "pupil", "iris", "cornea", "retina", "lens", "nostril", "lip", "tongue", "palate",
    "gum", "tooth", "molar", "wisdom", "throat", "neck", "shoulder", "elbow", "wrist",
    "palm", "finger", "thumb", "knuckle", "nail", "hip", "thigh", "knee", "calf",
    "ankle", "heel", "toe", "sole", "arch", "chest", "breast", "abdomen", "waist",
    "back", "buttock", "groin", "armpit", "skin", "pore", "wrinkle", "freckle", "mole",
    "hair", "scalp", "beard", "mustache", "eyebrow", "lash", "follicle", "strand",
    "pulse", "heartbeat", "breath", "respiration", "digestion", "metabolism", "circulation",
]}

# =============================================================================
# PROFESSIONS & OCCUPATIONS (~200 words)
# =============================================================================

PROFESSION_VOCAB = {w: WordEntry(w, [PartOfSpeech.NOUN], [f"{w.title()} - profession"], WordFrequency.COMMON) for w in [
    "profession", "occupation", "career", "vocation", "trade", "craft", "specialty",
    "accountant", "actuary", "administrator", "analyst", "architect", "artist",
    "attorney", "auditor", "banker", "barber", "bartender", "biologist", "broker",
    "butcher", "carpenter", "cashier", "chef", "chemist", "chiropractor", "clerk",
    "coach", "consultant", "contractor", "counselor", "curator", "dentist", "designer",
    "detective", "dietitian", "director", "economist", "editor", "electrician",
    "engineer", "entrepreneur", "executive", "farmer", "firefighter", "florist",
    "geologist", "graphic", "hairdresser", "historian", "illustrator", "inspector",
    "interpreter", "investigator", "jeweler", "janitor", "journalist", "judge",
    "landscaper", "lawyer", "lecturer", "librarian", "lifeguard", "locksmith",
    "machinist", "magician", "manager", "manufacturer", "marketer", "mechanic",
    "mediator", "meteorologist", "midwife", "miner", "musician", "nanny", "navigator",
    "neurologist", "notary", "novelist", "nutritionist", "obstetrician", "optician",
    "optometrist", "orthodontist", "painter", "paralegal", "paramedic", "pastor",
    "pathologist", "pediatrician", "pharmacist", "philosopher", "photographer",
    "physician", "physicist", "pilot", "plumber", "podiatrist", "politician",
    "priest", "principal", "producer", "professor", "programmer", "psychiatrist",
    "psychologist", "publisher", "radiologist", "realtor", "receptionist", "recruiter",
    "reporter", "researcher", "restaurateur", "retailer", "salesperson", "scientist",
    "sculptor", "secretary", "security", "senator", "sergeant", "sociologist",
    "soldier", "solicitor", "sommelier", "specialist", "spokesperson", "statistician",
    "steward", "stockbroker", "strategist", "surgeon", "surveyor", "tailor",
    "technician", "therapist", "trainer", "translator", "treasurer", "tutor",
    "underwriter", "undertaker", "urologist", "veterinarian", "videographer",
    "waiter", "waitress", "warden", "welder", "wholesaler", "writer", "zoologist",
]}

# =============================================================================
# ADJECTIVES - DESCRIPTIVE (~300 words)
# =============================================================================

DESCRIPTIVE_ADJ = {w: WordEntry(w, [PartOfSpeech.ADJECTIVE], [f"{w.title()} - descriptive"], WordFrequency.COMMON) for w in [
    # Physical properties
    "absurd", "acute", "adjacent", "ample", "angular", "apparent", "approximate",
    "arbitrary", "authentic", "barren", "bleak", "blunt", "bold", "brisk", "broad",
    "bulky", "bumpy", "clumsy", "coarse", "compact", "concise", "concrete", "crude",
    "damp", "delicate", "dense", "dim", "dull", "elaborate", "elegant", "erratic",
    "extensive", "faint", "feasible", "fierce", "flexible", "fluent", "fragile",
    "frail", "frank", "frequent", "fuzzy", "gentle", "genuine", "gloomy", "glossy",
    "graceful", "gradual", "grand", "grave", "greasy", "grim", "gross", "harsh",
    "hasty", "hazy", "hefty", "hollow", "humble", "immense", "implicit", "inherent",
    "intact", "intense", "intricate", "keen", "lean", "lengthy", "literal", "lofty",
    "lucid", "magnificent", "meager", "mellow", "mere", "mild", "miniature", "minute",
    "moist", "modest", "mute", "naked", "neat", "noble", "obscure", "odd", "opaque",
    "ornate", "pale", "partial", "passive", "peculiar", "petty", "plain", "plausible",
    "plentiful", "plump", "polished", "potent", "precise", "preliminary", "premier",
    "premium", "primitive", "pristine", "profound", "prominent", "prompt", "prone",
    "proper", "prosperous", "provisional", "prudent", "quaint", "radiant", "random",
    "rapid", "rational", "raw", "reckless", "refined", "reluctant", "remote",
    "renowned", "rigid", "robust", "rough", "rugged", "rustic", "sacred", "savage",
    "scarce", "scattered", "scenic", "serene", "severe", "shabby", "sheer", "shrewd",
    "shrill", "sincere", "singular", "skeptical", "slender", "slick", "slight",
    "slim", "slippery", "sluggish", "sober", "solemn", "solid", "solitary", "somber",
    "sophisticated", "sour", "sparse", "spectacular", "spontaneous", "stable",
    "stale", "stark", "static", "steady", "steep", "sterile", "stern", "stiff",
    "striking", "stubborn", "sturdy", "subdued", "sublime", "subtle", "successive",
    "sufficient", "superficial", "superior", "supreme", "surplus", "susceptible",
    "suspicious", "swift", "synthetic", "tangible", "tedious", "tender", "tense",
    "tentative", "terminal", "terrific", "thorough", "thoughtful", "thrifty", "tidy",
    "timid", "tolerant", "tough", "toxic", "tragic", "tranquil", "transparent",
    "tremendous", "trivial", "tropical", "turbulent", "ultimate", "unanimous",
    "unaware", "uncertain", "uncomfortable", "underlying", "unique", "universal",
    "unprecedented", "unstable", "urgent", "utmost", "utter", "vacant", "vague",
    "valid", "valuable", "variable", "vast", "verbal", "versatile", "vertical",
    "viable", "vibrant", "vicious", "vigorous", "viral", "virtual", "visible",
    "vital", "vivid", "volatile", "voluntary", "vulnerable", "weird", "wicked",
    "widespread", "witty", "worthy", "zealous",
]}

# =============================================================================
# ADVERBS - MANNER (~100 words)
# =============================================================================

MANNER_ADV = {w: WordEntry(w, [PartOfSpeech.ADVERB], [f"{w.title()} - manner adverb"], WordFrequency.COMMON) for w in [
    "abruptly", "accidentally", "actively", "adequately", "aggressively", "allegedly",
    "annually", "anxiously", "apparently", "approximately", "arbitrarily", "arguably",
    "automatically", "barely", "briefly", "broadly", "carelessly", "casually",
    "cautiously", "chronologically", "collectively", "commonly", "comparatively",
    "consistently", "continuously", "correctly", "critically", "currently", "daily",
    "deliberately", "desperately", "differently", "diligently", "dramatically",
    "drastically", "eagerly", "economically", "effectively", "efficiently", "elsewhere",
    "enormously", "enthusiastically", "entirely", "equally", "essentially", "eventually",
    "evidently", "exclusively", "explicitly", "externally", "fairly", "faithfully",
    "famously", "firmly", "formally", "formerly", "fortunately", "frankly", "freely",
    "frequently", "genuinely", "globally", "gradually", "greatly", "happily", "hardly",
    "hastily", "heavily", "hopefully", "ideally", "identically", "illegally",
    "immediately", "immensely", "implicitly", "importantly", "increasingly",
    "independently", "individually", "inevitably", "infinitely", "informally",
    "initially", "innocently", "instantly", "intensely", "internally", "ironically",
    "jointly", "largely", "lately", "legally", "legitimately", "literally", "locally",
    "logically", "loosely", "loudly", "mainly", "marginally", "markedly", "massively",
    "meaningfully", "mentally", "merely", "mildly", "minimally", "mistakenly",
]}


def load_comprehensive_vocabulary(vocab=None):
    """Load comprehensive vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in FOOD_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in HOUSEHOLD_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in CLOTHING_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in NATURE_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in BODY_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in PROFESSION_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in DESCRIPTIVE_ADJ.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MANNER_ADV.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[ComprehensiveVocabulary] Loaded {total_added} words")
    print(f"[ComprehensiveVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_comprehensive_stats() -> dict:
    """Get comprehensive vocabulary statistics."""
    return {
        "food": len(FOOD_VOCAB),
        "household": len(HOUSEHOLD_VOCAB),
        "clothing": len(CLOTHING_VOCAB),
        "nature": len(NATURE_VOCAB),
        "body": len(BODY_VOCAB),
        "professions": len(PROFESSION_VOCAB),
        "adjectives": len(DESCRIPTIVE_ADJ),
        "adverbs": len(MANNER_ADV),
        "total": (len(FOOD_VOCAB) + len(HOUSEHOLD_VOCAB) + len(CLOTHING_VOCAB) +
                 len(NATURE_VOCAB) + len(BODY_VOCAB) + len(PROFESSION_VOCAB) +
                 len(DESCRIPTIVE_ADJ) + len(MANNER_ADV))
    }
