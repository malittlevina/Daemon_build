# unimind/models/native/vocabulary_final.py
# Final Massive Vocabulary Push for C2 Level

"""
Final Vocabulary Module - Massive Additional Words

Contains thousands more words to push toward C2 level:
- Scientific terminology
- Medical vocabulary
- Financial terms
- Technical jargon
- Literary vocabulary
- Additional everyday words
"""

from typing import Dict, Set
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# Quick word list generator for common patterns
def _make_entries(words: list, pos: PartOfSpeech, freq=WordFrequency.COMMON) -> Dict:
    return {w: WordEntry(w, [pos], [w], freq) for w in words}


# =============================================================================
# SCIENTIFIC VOCABULARY (~400 words)
# =============================================================================

SCIENCE_WORDS = [
    "acceleration", "adaptation", "adhesion", "aerobic", "aerodynamic", "affinity",
    "aggregate", "algorithm", "allele", "allergy", "allotrope", "amino", "ampere",
    "amplitude", "anaerobic", "anatomy", "anion", "anode", "antibiotic", "antibody",
    "antigen", "antimatter", "antiseptic", "aqueous", "archaeology", "arthropod",
    "asteroid", "astrophysics", "atmospheric", "atomic", "autonomic", "axon",
    "bacteria", "bacterium", "barometer", "biennial", "binary", "biochemistry",
    "biodegradable", "bioethics", "biological", "biomass", "biome", "biosphere",
    "biotechnology", "boiling", "bonding", "botany", "buoyancy", "calibration",
    "calorie", "capacitor", "capillary", "carbohydrate", "carbonate", "catalyst",
    "cathode", "cation", "cavity", "celestial", "cellular", "celsius", "centrifugal",
    "centripetal", "cerebral", "chromosome", "circuit", "circulation", "classification",
    "coagulation", "coefficient", "cohesion", "combustion", "compound", "compression",
    "condensation", "conduction", "conductor", "conservation", "constellation",
    "convection", "corrosion", "cosmic", "covalent", "crystalline", "cytoplasm",
    "decomposition", "deduction", "deformation", "degradation", "dehydration",
    "density", "depolarization", "derivative", "desalination", "deterioration",
    "diffraction", "diffusion", "digestion", "dilution", "displacement", "dissociation",
    "dissolution", "distillation", "diversity", "dominant", "doppler", "dynamics",
    "earthquake", "eclipse", "ecological", "ecosystem", "efficiency", "elasticity",
    "electrode", "electrolysis", "electrolyte", "electromagnetic", "electron",
    "element", "embryo", "emission", "empirical", "endocrine", "endothermic",
    "entropy", "enzyme", "epidemic", "epidermis", "equilibrium", "erosion",
    "evaporation", "evolution", "excretion", "exothermic", "experiment", "exponential",
    "extinction", "extraction", "fahrenheit", "famine", "fauna", "fermentation",
    "fertilization", "fetus", "filtration", "fission", "flora", "fluorescence",
    "fossil", "fracture", "frequency", "friction", "fulcrum", "function", "fusion",
    "galaxy", "gamma", "gaseous", "gene", "genetic", "genome", "genus", "geochemistry",
    "geologic", "geophysics", "geothermal", "germination", "glacier", "gland",
    "glucose", "gravitation", "greenhouse", "habitat", "halogen", "hemisphere",
    "hereditary", "heredity", "heterogeneous", "hibernate", "homogeneous", "hormone",
    "humidity", "hydraulic", "hydrocarbon", "hydrodynamic", "hydrogen", "hydrolysis",
    "hydrophobic", "hypothesis", "igneous", "immune", "immunology", "impermeable",
    "incubation", "induction", "inertia", "infection", "inflammation", "infrared",
    "inheritance", "inhibitor", "inoculation", "inorganic", "insecticide", "insulation",
    "insulin", "integral", "interaction", "interference", "interstellar", "invertebrate",
    "ionization", "irradiation", "isotope", "joule", "kelvin", "kinetic", "laboratory",
    "laser", "latitude", "lava", "leukocyte", "lever", "ligament", "lipid", "liquid",
    "lithosphere", "longitude", "luminescence", "lunar", "lymph", "magma", "magnetic",
    "magnetism", "mammal", "mantle", "mass", "matrix", "matter", "mechanics",
    "meiosis", "membrane", "meniscus", "metabolism", "metamorphic", "metamorphosis",
    "meteor", "meteorology", "microbe", "microbiology", "microscope", "microscopic",
    "migration", "mineral", "mitochondria", "mitosis", "mixture", "molecular",
    "molecule", "momentum", "monomer", "morphology", "multicellular", "mutation",
    "nanotechnology", "nebula", "negative", "nervous", "neurology", "neuron",
    "neutralization", "neutron", "newton", "nitrogen", "nomenclature", "nuclear",
    "nucleic", "nucleus", "nutrient", "observation", "ohm", "opaque", "optics",
    "orbital", "organ", "organic", "organism", "oscillation", "osmosis", "oxidation",
    "oxide", "oxygen", "ozone", "paleontology", "pandemic", "parasite", "particle",
    "pathogen", "periodic", "permeability", "pesticide", "petroleum", "phenomenon",
    "phosphorus", "photon", "photosynthesis", "physics", "physiology", "pigment",
    "plasma", "plate", "pneumatic", "pollen", "pollination", "pollution", "polymer",
    "population", "positive", "potassium", "potential", "precipitation", "predator",
    "pressure", "prey", "primate", "probability", "prokaryote", "propagation",
    "protein", "proton", "protoplasm", "protozoa", "pulley", "pulsar", "quantum",
    "quark", "quasar", "radiation", "radioactive", "radioisotope", "radius",
    "reactant", "reaction", "reagent", "receptor", "recessive", "recombination",
    "reduction", "reflection", "refraction", "regeneration", "relativity", "reproduction",
    "reptile", "resistance", "resonance", "respiration", "retina", "ribonucleic",
    "ribosome", "rotation", "saccharide", "salinity", "satellite", "saturation",
    "sediment", "semiconductor", "seismology", "selection", "semiconductor", "sensory",
    "sepsis", "serum", "silicon", "simulation", "sinus", "skeletal", "sodium",
    "solar", "solubility", "solute", "solution", "solvent", "sonar", "sonic",
    "speciation", "species", "specimen", "spectroscopy", "spectrum", "spore",
    "stamen", "stationary", "statistics", "stimulus", "stoichiometry", "strain",
    "stratosphere", "subatomic", "sublimation", "substrate", "sulfur", "supernova",
    "symbiosis", "synapse", "synthesis", "systematic", "taxonomy", "tectonic",
    "temperature", "terrestrial", "thermal", "thermodynamics", "thermostat", "tissue",
    "titration", "topography", "toxicology", "toxin", "trajectory", "translucent",
    "transmit", "transparent", "transpiration", "tropism", "troposphere", "tsunami",
    "turbulence", "ultraviolet", "unicellular", "uranium", "vaccination", "vaccine",
    "vacuum", "valence", "vapor", "vascular", "vector", "velocity", "ventricle",
    "vertebrate", "virology", "virus", "viscosity", "vitamin", "volcano", "volt",
    "watt", "wavelength", "zoology", "zygote",
]

SCIENCE_VOCAB = _make_entries(SCIENCE_WORDS, PartOfSpeech.NOUN)


# =============================================================================
# MEDICAL VOCABULARY (~300 words)
# =============================================================================

MEDICAL_WORDS = [
    "abdomen", "abnormality", "abortion", "abscess", "acute", "addiction", "adhesion",
    "adipose", "adrenal", "adverse", "aetiology", "ailment", "allergy", "amputation",
    "anaemia", "anaesthetic", "analgesic", "aneurysm", "angina", "angioplasty",
    "antibiotic", "antidepressant", "antidote", "antigen", "antiseptic", "anxiety",
    "appendectomy", "appendix", "arrhythmia", "artery", "arthritis", "asthma",
    "atrophy", "autopsy", "benign", "bile", "biopsy", "bladder", "bleeding",
    "blood", "bone", "bowel", "brain", "breast", "bronchitis", "bruise", "burn",
    "bypass", "cancer", "cardiac", "cardiovascular", "cartilage", "cataract",
    "catheter", "cerebral", "chemotherapy", "cholesterol", "chronic", "circulation",
    "cirrhosis", "clot", "colon", "coma", "complication", "concussion", "congenital",
    "congestive", "constipation", "contagious", "contraception", "convulsion",
    "coronary", "cortex", "cough", "cranial", "critical", "cyst", "defibrillator",
    "dehydration", "dementia", "dengue", "dental", "depression", "dermatitis",
    "diabetes", "diagnosis", "dialysis", "diarrhea", "diastolic", "disability",
    "disease", "dislocation", "disorder", "dissection", "dosage", "dysfunction",
    "eczema", "edema", "electrocardiogram", "embolism", "emergency", "emphysema",
    "encephalitis", "endoscopy", "epidemic", "epilepsy", "esophagus", "examination",
    "excision", "exhaustion", "fatigue", "femur", "fever", "fibrosis", "flu",
    "fracture", "gallbladder", "gangrene", "gastric", "gastritis", "gastrointestinal",
    "genetic", "geriatric", "gland", "glaucoma", "glucose", "gynecology", "headache",
    "healthcare", "heartburn", "hemoglobin", "hemorrhage", "hepatitis", "hernia",
    "hormone", "hospice", "hospital", "hypertension", "hyperthyroidism", "hypoglycemia",
    "hypothermia", "hypothyroidism", "hysterectomy", "immunity", "immunization",
    "implant", "incision", "incubation", "indigestion", "infection", "infertility",
    "inflammation", "influenza", "injection", "injury", "inpatient", "insomnia",
    "insulin", "intensive", "intestine", "intravenous", "jaundice", "kidney",
    "laryngitis", "lesion", "leukemia", "ligament", "liver", "lobe", "lung",
    "lymph", "malaria", "malignant", "malnutrition", "mammogram", "mastectomy",
    "measles", "medication", "melanoma", "membrane", "meningitis", "menopause",
    "menstruation", "metabolism", "metastasis", "migraine", "miscarriage", "molecule",
    "mucus", "mumps", "muscle", "nausea", "neonatal", "nephritis", "nerve",
    "neurology", "neuropathy", "nicotine", "nutrition", "obesity", "obstetrics",
    "oncology", "ophthalmology", "organ", "orthopedic", "osteoporosis", "outpatient",
    "ovary", "overdose", "oxygen", "pacemaker", "pain", "palliative", "palpitation",
    "pancreas", "pandemic", "paralysis", "parasite", "pathology", "patient",
    "pediatric", "pelvis", "penicillin", "peptic", "pharyngitis", "phlebotomy",
    "physical", "physician", "physiology", "placebo", "placenta", "plasma", "platelet",
    "pneumonia", "poisoning", "polio", "pregnancy", "prenatal", "prescription",
    "prevention", "prognosis", "prolapse", "prostate", "prosthesis", "protein",
    "psychiatry", "psychology", "pulmonary", "pulse", "quarantine", "rabies",
    "radiology", "rash", "receptor", "recovery", "rectum", "rehabilitation", "relapse",
    "renal", "respiratory", "resuscitation", "rheumatism", "rupture", "saliva",
    "sclerosis", "screening", "seizure", "sepsis", "serum", "shock", "sinus",
    "skeleton", "skin", "skull", "spasm", "specimen", "spinal", "spine", "spleen",
    "sprain", "sterilization", "steroid", "stomach", "strain", "stroke", "surgery",
    "symptom", "syndrome", "systemic", "systolic", "tendon", "terminal", "testicle",
    "therapy", "thorax", "thrombosis", "thyroid", "tissue", "tonsillitis", "toxin",
    "trachea", "transfusion", "transplant", "trauma", "treatment", "tremor", "tumor",
    "typhoid", "ulcer", "ultrasound", "urine", "urology", "uterus", "vaccination",
    "vaccine", "vascular", "vein", "ventilator", "vertebra", "viral", "virus",
    "vitamin", "vomiting", "wheelchair", "wound", "xray",
]

MEDICAL_VOCAB = _make_entries(MEDICAL_WORDS, PartOfSpeech.NOUN)


# =============================================================================
# FINANCIAL VOCABULARY (~200 words)
# =============================================================================

FINANCIAL_WORDS = [
    "account", "accounting", "acquisition", "actuary", "allocation", "amortization",
    "annuity", "appreciation", "arbitrage", "asset", "audit", "balance", "bankruptcy",
    "benchmark", "beneficiary", "bond", "bookkeeping", "brokerage", "budget",
    "bullish", "buyout", "capital", "capitalization", "cashflow", "collateral",
    "commodity", "compound", "consolidation", "contingency", "contribution",
    "convertible", "corporation", "correlation", "coverage", "credit", "creditor",
    "currency", "debenture", "debit", "debt", "default", "deferral", "deficit",
    "deflation", "depreciation", "derivative", "devaluation", "disclosure", "discount",
    "diversification", "dividend", "downturn", "earnings", "economy", "efficiency",
    "elasticity", "embezzlement", "endowment", "enterprise", "entitlement", "entrepreneur",
    "equity", "escrow", "estate", "exchange", "excise", "exemption", "expenditure",
    "expense", "export", "exposure", "factoring", "fiduciary", "finance", "fiscal",
    "foreclosure", "forex", "franchise", "fraud", "fund", "futures", "gain",
    "garnishment", "goodwill", "grant", "gross", "growth", "guarantee", "hedge",
    "holding", "hyperinflation", "illiquid", "import", "income", "incorporation",
    "index", "indicator", "inflation", "inheritance", "insolvency", "insurance",
    "interest", "inventory", "investment", "investor", "invoice", "ipo", "irr",
    "issuer", "joint", "journal", "jurisdiction", "lease", "ledger", "leverage",
    "liability", "lien", "liquidation", "liquidity", "listing", "litigation", "loan",
    "loss", "margin", "markdown", "markup", "maturity", "merger", "microfinance",
    "monetary", "mortgage", "mutual", "nasdaq", "negotiable", "networth", "nominal",
    "nonprofit", "obligation", "offering", "offshore", "option", "outstanding",
    "overdraft", "overhead", "ownership", "partnership", "patent", "payable",
    "payment", "payroll", "pension", "portfolio", "position", "premium", "prepayment",
    "principal", "privatization", "procurement", "profit", "projection", "promissory",
    "property", "prospectus", "provision", "proxy", "quarter", "quota", "quotation",
    "rally", "rate", "rating", "ratio", "real", "realization", "receivable",
    "recession", "reconciliation", "recovery", "redemption", "refinancing", "refund",
    "regulation", "reimbursement", "reinvestment", "remittance", "rental", "repayment",
    "reserve", "residual", "restructuring", "retail", "retention", "retirement",
    "return", "revenue", "reverse", "risk", "rollover", "royalty", "salary",
    "savings", "securities", "securitization", "shareholder", "shares", "shortfall",
    "solvency", "speculation", "spread", "stakeholder", "startup", "statement",
    "stimulus", "stock", "strategy", "subprime", "subsidiary", "subsidy", "surplus",
    "swap", "syndication", "takeover", "tariff", "taxation", "tender", "tenure",
    "term", "ticker", "trade", "trader", "trading", "transaction", "transfer",
    "treasury", "trend", "trust", "trustee", "turnover", "underwriting", "unemployment",
    "valuation", "value", "variable", "variance", "venture", "volatility", "volume",
    "warrant", "wealth", "wholesale", "withdrawal", "writeoff", "yield",
]

FINANCIAL_VOCAB = _make_entries(FINANCIAL_WORDS, PartOfSpeech.NOUN)


# =============================================================================
# EVERYDAY WORDS (~500 more common words)
# =============================================================================

EVERYDAY_WORDS = [
    # Verbs
    "abandon", "absorb", "accelerate", "accommodate", "accompany", "accomplish",
    "accumulate", "accuse", "adapt", "adhere", "admire", "adopt", "advertise",
    "advocate", "alert", "align", "allocate", "alter", "amend", "amplify",
    "animate", "anticipate", "apologize", "applaud", "appreciate", "approve",
    "arouse", "assemble", "assign", "associate", "astonish", "attach", "attain",
    "attract", "audit", "awaken", "backfire", "backup", "ban", "bargain",
    "behave", "benchmark", "bless", "boast", "boost", "bother", "brake",
    "breach", "brighten", "broadcast", "broaden", "browse", "bubble", "budget",
    "bundle", "burden", "bury", "calculate", "campaign", "cancel", "capture",
    "categorize", "cater", "cease", "celebrate", "certify", "challenge", "chase",
    "circulate", "clap", "clarify", "clash", "classify", "cleanse", "click",
    "cling", "clone", "cluster", "coach", "coincide", "collapse", "combat",
    "combine", "comment", "commercialize", "commission", "compel", "compile",
    "complain", "complement", "complicate", "comply", "compose", "compound",
    "compress", "compromise", "conceal", "concentrate", "conceptualize", "conclude",
    "condemn", "condense", "conduct", "confer", "confine", "confiscate", "confront",
    "congratulate", "connect", "conquer", "conserve", "consult", "consume",
    "contaminate", "contemplate", "contest", "contradict", "contrast", "contribute",
    "converge", "converse", "convert", "convey", "cooperate", "cope", "copyright",
    "correlate", "correspond", "corrupt", "counsel", "counter", "couple", "crack",
    "craft", "crash", "crawl", "criticize", "crop", "crush", "cultivate", "cure",
    "curl", "customize", "cycle", "dare", "dazzle", "deactivate", "debrief",
    "decay", "deceive", "decentralize", "declare", "decode", "decompose", "decorate",
    "decrease", "dedicate", "deduct", "deem", "deepen", "default", "defeat",
    "defend", "defer", "define", "deflect", "degrade", "delay", "delegate",
    "delete", "delight", "demolish", "demote", "denounce", "depart", "depict",
    "deplete", "deploy", "deposit", "depreciate", "depress", "deprive", "derive",
    "descend", "designate", "desire", "destabilize", "detach", "detain", "deter",
    "deteriorate", "determine", "detest", "develop", "devise", "devote", "diagnose",
    "dictate", "differ", "differentiate", "dig", "digest", "digitize", "dilute",
    "dim", "diminish", "dine", "dip", "disable", "disagree", "disappear",
    "disappoint", "disapprove", "disarm", "discard", "discharge", "disclaim",
    "disclose", "discount", "discourage", "discover", "discriminate", "discuss",
    "disguise", "disgust", "dislike", "dislocate", "dismiss", "disorder", "dispatch",
    "dispel", "disperse", "displace", "display", "dispose", "disprove", "dispute",
    "disregard", "disrupt", "disseminate", "dissent", "dissolve", "dissuade",
    "distance", "distill", "distinguish", "distort", "distract", "distribute",
    "disturb", "diverge", "diversify", "divert", "divide", "divorce", "dock",
    "document", "dodge", "dominate", "donate", "doom", "double", "download",
    "downplay", "draft", "drag", "drain", "dramatize", "drape", "drift", "drill",
    "drip", "drown", "dry", "dump", "duplicate", "dwell", "dye", "ease",
    "echo", "edit", "educate", "eject", "elaborate", "elapse", "elect", "electrify",
    "elevate", "eliminate", "elongate", "elude", "emanate", "embark", "embed",
    "embody", "embrace", "emerge", "emigrate", "emit", "emphasize", "employ",
    "empower", "empty", "enable", "enact", "encounter", "encourage", "encrypt",
    "endanger", "endeavor", "endorse", "endure", "energize", "engage", "engineer",
    "enhance", "enlighten", "enlist", "enrich", "enroll", "ensure", "entail",
    "entertain", "enthuse", "entice", "entitle", "entrust", "enumerate", "envy",
    "equalize", "equate", "equip", "eradicate", "erect", "erode", "err",
    "erupt", "escalate", "escape", "escort", "establish", "estimate", "evacuate",
    "evade", "evaluate", "evaporate", "evolve", "exacerbate", "exaggerate", "examine",
    "exceed", "excel", "exchange", "excite", "exclude", "excuse", "execute",
    "exempt", "exert", "exhaust", "exhibit", "exile", "expand", "expedite",
    "expel", "experiment", "expire", "exploit", "explore", "export", "expose",
    "extend", "extinguish", "extract", "fabricate", "facilitate", "factor",
    "fade", "fake", "falsify", "familiarize", "fancy", "fascinate", "fashion",
    "fasten", "fatten", "favor", "fax", "feast", "feature", "feed", "fertilize",
    "fetch", "filter", "finalize", "finance", "fire", "firm", "fish", "flag",
    "flash", "flatten", "flavor", "flee", "flex", "flip", "flood", "flourish",
    "fluctuate", "flush", "foam", "fold", "forbid", "forecast", "foresee",
    "forge", "forgive", "formalize", "format", "formulate", "foster", "found",
    "frame", "franchise", "free", "freeze", "frequent", "freshen", "frighten",
    "frost", "frustrate", "fulfill", "fume", "function", "furnish", "fuse",
]

EVERYDAY_VOCAB = _make_entries(EVERYDAY_WORDS, PartOfSpeech.VERB)


# =============================================================================
# ADDITIONAL ADJECTIVES (~300 words)
# =============================================================================

MORE_ADJECTIVES = [
    "abandoned", "abrupt", "absent", "absolute", "abstract", "abundant", "academic",
    "acceptable", "accessible", "accidental", "acclaimed", "accountable", "accurate",
    "accused", "acknowledged", "acoustic", "active", "actual", "acute", "adaptable",
    "addictive", "additional", "adequate", "adjacent", "administrative", "admirable",
    "adorable", "advanced", "advantageous", "adventurous", "adverse", "aesthetic",
    "affectionate", "affordable", "aggressive", "agile", "agreeable", "alarming",
    "alcoholic", "alert", "alien", "alike", "alkaline", "alleged", "allergic",
    "allied", "allowable", "alternate", "alternative", "amateur", "amazing",
    "ambiguous", "ambitious", "ample", "amusing", "analytical", "ancient", "animated",
    "annual", "anonymous", "anticipated", "anxious", "apologetic", "apparent",
    "appealing", "applicable", "appreciative", "appropriate", "approximate", "arbitrary",
    "architectural", "ardent", "arguable", "aristocratic", "aromatic", "arranged",
    "artificial", "artistic", "ascending", "ashamed", "aspiring", "assertive",
    "astonishing", "astronomical", "athletic", "atmospheric", "attached", "attainable",
    "attentive", "attractive", "authentic", "authoritative", "automatic", "autonomous",
    "available", "average", "avid", "awake", "aware", "awesome", "awful", "awkward",
    "bacterial", "balanced", "bare", "basic", "beautiful", "behavioral", "believable",
    "beloved", "beneficial", "benevolent", "best", "better", "binding", "biographical",
    "biological", "bitter", "bizarre", "blank", "bleak", "blessed", "blind",
    "blissful", "blonde", "bloody", "boiling", "bold", "boring", "botanical",
    "bound", "brave", "breakable", "breathtaking", "brief", "bright", "brilliant",
    "broad", "broken", "bronze", "brutal", "bureaucratic", "burning", "busy",
    "calculated", "calm", "capable", "capital", "captive", "careful", "careless",
    "caring", "casual", "catastrophic", "categorical", "cautious", "celebrated",
    "celestial", "central", "ceremonial", "certain", "challenging", "changeable",
    "chaotic", "characteristic", "charitable", "charming", "cheap", "cheerful",
    "chemical", "chief", "childish", "chronic", "circular", "civic", "civil",
    "civilized", "classic", "classical", "clean", "clear", "clever", "clinical",
    "close", "closed", "cloudy", "coastal", "cognitive", "coherent", "coincidental",
    "cold", "collaborative", "collective", "colonial", "colorful", "colossal",
    "combined", "comfortable", "comic", "coming", "commanding", "commemorative",
    "commercial", "committed", "common", "communal", "communicative", "compact",
    "comparable", "comparative", "compassionate", "compatible", "compelling",
    "compensatory", "competent", "competitive", "complementary", "complete",
    "complex", "complicated", "complimentary", "comprehensive", "compulsory",
    "computational", "concealed", "concentrated", "conceptual", "concerned",
    "concrete", "concurrent", "conditional", "confident", "confidential",
    "confined", "confirmed", "conflicting", "confusing", "congressional", "connected",
    "consecutive", "consensual", "consequent", "conservative", "considerable",
    "considerate", "consistent", "consolidated", "constant", "constitutional",
    "constructive", "consultative", "contemporary", "content", "continental",
    "continual", "continuous", "contradictory", "contrary", "contributing",
    "controversial", "convenient", "conventional", "conversational", "convincing",
    "cooperative", "coordinated", "corporate", "correct", "corresponding", "corrupt",
    "costly", "countless", "courteous", "cozy", "cracked", "crafty", "cramped",
    "crazy", "creative", "credible", "criminal", "crippled", "crisp", "critical",
    "crooked", "crowded", "crucial", "crude", "cruel", "crushing", "cultural",
    "cumulative", "cunning", "curious", "current", "customary", "cute", "cynical",
    "daily", "damaged", "damp", "dangerous", "daring", "dark", "dazzling",
    "dead", "deadly", "dear", "debatable", "decent", "decisive", "declining",
    "decorative", "dedicated", "deep", "defective", "defensive", "defiant",
    "definite", "definitive", "degraded", "delayed", "deliberate", "delicate",
    "delicious", "delighted", "delightful", "democratic", "demographic", "demonstrative",
    "dense", "dental", "dependent", "depressed", "depressing", "descriptive",
    "deserted", "deserving", "desirable", "desired", "desolate", "desperate",
    "destined", "destructive", "detailed", "determined", "detrimental", "developmental",
    "devoted", "diagnostic", "diagonal", "dietary", "different", "differential",
]

MORE_ADJ_VOCAB = _make_entries(MORE_ADJECTIVES, PartOfSpeech.ADJECTIVE)


def load_final_vocabulary(vocab=None):
    """Load final massive vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in SCIENCE_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MEDICAL_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in FINANCIAL_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in EVERYDAY_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MORE_ADJ_VOCAB.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[FinalVocabulary] Loaded {total_added} additional words")
    print(f"[FinalVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_final_stats() -> dict:
    """Get final vocabulary statistics."""
    return {
        "science": len(SCIENCE_VOCAB),
        "medical": len(MEDICAL_VOCAB),
        "financial": len(FINANCIAL_VOCAB),
        "everyday": len(EVERYDAY_VOCAB),
        "adjectives": len(MORE_ADJ_VOCAB),
        "total": (len(SCIENCE_VOCAB) + len(MEDICAL_VOCAB) + len(FINANCIAL_VOCAB) +
                 len(EVERYDAY_VOCAB) + len(MORE_ADJ_VOCAB))
    }
