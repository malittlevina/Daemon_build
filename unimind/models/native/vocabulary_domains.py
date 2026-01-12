# unimind/models/native/vocabulary_domains.py
# Domain-Specific Vocabulary for Enhanced NLU

"""
Domain-Specific Vocabulary

Expands vocabulary with specialized terms for:
- Technology & Computing
- Science & Research
- Business & Finance
- Education & Learning
- Health & Medicine
- Arts & Entertainment
- Travel & Geography
- Food & Cooking
- Sports & Fitness
- Nature & Environment

Target: ~5000 total words for conversational fluency
"""

from typing import Dict, List
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# TECHNOLOGY & COMPUTING (~300 words)
# =============================================================================

TECHNOLOGY_VOCAB = {
    # Hardware
    "computer": WordEntry("computer", [PartOfSpeech.NOUN], ["Electronic computing device"], WordFrequency.CORE_500),
    "laptop": WordEntry("laptop", [PartOfSpeech.NOUN], ["Portable computer"], WordFrequency.COMMON),
    "tablet": WordEntry("tablet", [PartOfSpeech.NOUN], ["Touchscreen computer"], WordFrequency.COMMON),
    "phone": WordEntry("phone", [PartOfSpeech.NOUN], ["Telephone device"], WordFrequency.CORE_500),
    "smartphone": WordEntry("smartphone", [PartOfSpeech.NOUN], ["Mobile phone with computing"], WordFrequency.COMMON),
    "keyboard": WordEntry("keyboard", [PartOfSpeech.NOUN], ["Input device with keys"], WordFrequency.CORE_1000),
    "mouse": WordEntry("mouse", [PartOfSpeech.NOUN], ["Pointing device"], WordFrequency.CORE_1000),
    "monitor": WordEntry("monitor", [PartOfSpeech.NOUN], ["Display screen"], WordFrequency.CORE_1000),
    "screen": WordEntry("screen", [PartOfSpeech.NOUN], ["Display surface"], WordFrequency.CORE_500),
    "printer": WordEntry("printer", [PartOfSpeech.NOUN], ["Document output device"], WordFrequency.CORE_1000),
    "server": WordEntry("server", [PartOfSpeech.NOUN], ["Central computer providing services"], WordFrequency.COMMON),
    "router": WordEntry("router", [PartOfSpeech.NOUN], ["Network directing device"], WordFrequency.COMMON),
    "processor": WordEntry("processor", [PartOfSpeech.NOUN], ["CPU, computing unit"], WordFrequency.COMMON),
    "memory": WordEntry("memory", [PartOfSpeech.NOUN], ["Data storage, RAM"], WordFrequency.CORE_500),
    "storage": WordEntry("storage", [PartOfSpeech.NOUN], ["Data holding capacity"], WordFrequency.CORE_1000),
    "drive": WordEntry("drive", [PartOfSpeech.NOUN], ["Storage device"], WordFrequency.CORE_500),
    "chip": WordEntry("chip", [PartOfSpeech.NOUN], ["Integrated circuit"], WordFrequency.CORE_1000),
    "sensor": WordEntry("sensor", [PartOfSpeech.NOUN], ["Detection device"], WordFrequency.COMMON),
    "camera": WordEntry("camera", [PartOfSpeech.NOUN], ["Image capture device"], WordFrequency.CORE_500),
    "microphone": WordEntry("microphone", [PartOfSpeech.NOUN], ["Audio input device"], WordFrequency.CORE_1000),
    "speaker": WordEntry("speaker", [PartOfSpeech.NOUN], ["Audio output device"], WordFrequency.CORE_1000),
    "headphones": WordEntry("headphones", [PartOfSpeech.NOUN], ["Personal audio device"], WordFrequency.COMMON),
    "cable": WordEntry("cable", [PartOfSpeech.NOUN], ["Connecting wire"], WordFrequency.CORE_1000),
    "battery": WordEntry("battery", [PartOfSpeech.NOUN], ["Power storage device"], WordFrequency.CORE_1000),
    "charger": WordEntry("charger", [PartOfSpeech.NOUN], ["Power supply device"], WordFrequency.COMMON),
    
    # Software
    "software": WordEntry("software", [PartOfSpeech.NOUN], ["Computer programs"], WordFrequency.CORE_500),
    "hardware": WordEntry("hardware", [PartOfSpeech.NOUN], ["Physical computer components"], WordFrequency.CORE_1000),
    "program": WordEntry("program", [PartOfSpeech.NOUN], ["Software application"], WordFrequency.CORE_500),
    "application": WordEntry("application", [PartOfSpeech.NOUN], ["Software program"], WordFrequency.CORE_500, synonyms=["app"]),
    "app": WordEntry("app", [PartOfSpeech.NOUN], ["Software application"], WordFrequency.COMMON),
    "system": WordEntry("system", [PartOfSpeech.NOUN], ["Organized set of parts"], WordFrequency.CORE_500),
    "database": WordEntry("database", [PartOfSpeech.NOUN], ["Organized data collection"], WordFrequency.COMMON),
    "file": WordEntry("file", [PartOfSpeech.NOUN], ["Data storage unit"], WordFrequency.CORE_500),
    "folder": WordEntry("folder", [PartOfSpeech.NOUN], ["File container"], WordFrequency.CORE_1000),
    "document": WordEntry("document", [PartOfSpeech.NOUN], ["Written record"], WordFrequency.CORE_500),
    "code": WordEntry("code", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Programming instructions"], WordFrequency.CORE_500),
    "script": WordEntry("script", [PartOfSpeech.NOUN], ["Automated program"], WordFrequency.COMMON),
    "algorithm": WordEntry("algorithm", [PartOfSpeech.NOUN], ["Step-by-step procedure"], WordFrequency.COMMON),
    "function": WordEntry("function", [PartOfSpeech.NOUN], ["Reusable code block"], WordFrequency.CORE_500),
    "variable": WordEntry("variable", [PartOfSpeech.NOUN], ["Data container"], WordFrequency.COMMON),
    "interface": WordEntry("interface", [PartOfSpeech.NOUN], ["Interaction boundary"], WordFrequency.COMMON),
    "browser": WordEntry("browser", [PartOfSpeech.NOUN], ["Web viewing software"], WordFrequency.COMMON),
    "website": WordEntry("website", [PartOfSpeech.NOUN], ["Web pages collection"], WordFrequency.CORE_500),
    "webpage": WordEntry("webpage", [PartOfSpeech.NOUN], ["Single web document"], WordFrequency.COMMON),
    "link": WordEntry("link", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Connection, URL"], WordFrequency.CORE_500),
    "download": WordEntry("download", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Transfer from internet"], WordFrequency.COMMON),
    "upload": WordEntry("upload", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Transfer to internet"], WordFrequency.COMMON),
    "install": WordEntry("install", [PartOfSpeech.VERB], ["Set up software"], WordFrequency.CORE_1000),
    "update": WordEntry("update", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Make current"], WordFrequency.CORE_500),
    "upgrade": WordEntry("upgrade", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Improve version"], WordFrequency.COMMON),
    "backup": WordEntry("backup", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Copy for safety"], WordFrequency.COMMON),
    "crash": WordEntry("crash", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["System failure"], WordFrequency.CORE_1000),
    "bug": WordEntry("bug", [PartOfSpeech.NOUN], ["Software error"], WordFrequency.CORE_1000),
    "debug": WordEntry("debug", [PartOfSpeech.VERB], ["Fix errors"], WordFrequency.COMMON),
    "reboot": WordEntry("reboot", [PartOfSpeech.VERB], ["Restart computer"], WordFrequency.COMMON),
    "login": WordEntry("login", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Sign in"], WordFrequency.COMMON),
    "logout": WordEntry("logout", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Sign out"], WordFrequency.COMMON),
    "password": WordEntry("password", [PartOfSpeech.NOUN], ["Secret access code"], WordFrequency.COMMON),
    "username": WordEntry("username", [PartOfSpeech.NOUN], ["Account identifier"], WordFrequency.COMMON),
    "account": WordEntry("account", [PartOfSpeech.NOUN], ["User registration"], WordFrequency.CORE_500),
    "profile": WordEntry("profile", [PartOfSpeech.NOUN], ["User description"], WordFrequency.COMMON),
    "setting": WordEntry("setting", [PartOfSpeech.NOUN], ["Configuration option"], WordFrequency.CORE_500),
    "option": WordEntry("option", [PartOfSpeech.NOUN], ["Choice, selection"], WordFrequency.CORE_500),
    "feature": WordEntry("feature", [PartOfSpeech.NOUN], ["Characteristic, function"], WordFrequency.CORE_500),
    "tool": WordEntry("tool", [PartOfSpeech.NOUN], ["Utility, instrument"], WordFrequency.CORE_500),
    
    # Internet & Networking
    "internet": WordEntry("internet", [PartOfSpeech.NOUN], ["Global computer network"], WordFrequency.CORE_500),
    "network": WordEntry("network", [PartOfSpeech.NOUN], ["Connected system"], WordFrequency.CORE_500),
    "wifi": WordEntry("wifi", [PartOfSpeech.NOUN], ["Wireless internet"], WordFrequency.COMMON),
    "wireless": WordEntry("wireless", [PartOfSpeech.ADJECTIVE], ["Without wires"], WordFrequency.COMMON),
    "bluetooth": WordEntry("bluetooth", [PartOfSpeech.NOUN], ["Short-range wireless"], WordFrequency.COMMON),
    "connection": WordEntry("connection", [PartOfSpeech.NOUN], ["Link, relationship"], WordFrequency.CORE_500),
    "online": WordEntry("online", [PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB], ["Connected to internet"], WordFrequency.COMMON),
    "offline": WordEntry("offline", [PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB], ["Not connected"], WordFrequency.COMMON),
    "email": WordEntry("email", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Electronic mail"], WordFrequency.CORE_500),
    "message": WordEntry("message", [PartOfSpeech.NOUN], ["Communication"], WordFrequency.CORE_500),
    "chat": WordEntry("chat", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Online conversation"], WordFrequency.COMMON),
    "post": WordEntry("post", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Published content"], WordFrequency.CORE_500),
    "share": WordEntry("share", [PartOfSpeech.VERB], ["Distribute, give access"], WordFrequency.CORE_500),
    "stream": WordEntry("stream", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Continuous data flow"], WordFrequency.COMMON),
    "cloud": WordEntry("cloud", [PartOfSpeech.NOUN], ["Remote computing"], WordFrequency.COMMON),
    "server": WordEntry("server", [PartOfSpeech.NOUN], ["Host computer"], WordFrequency.COMMON),
    "domain": WordEntry("domain", [PartOfSpeech.NOUN], ["Web address space"], WordFrequency.COMMON),
    "bandwidth": WordEntry("bandwidth", [PartOfSpeech.NOUN], ["Data transfer capacity"], WordFrequency.COMMON),
    "firewall": WordEntry("firewall", [PartOfSpeech.NOUN], ["Security system"], WordFrequency.COMMON),
    "encryption": WordEntry("encryption", [PartOfSpeech.NOUN], ["Data encoding"], WordFrequency.COMMON),
    "privacy": WordEntry("privacy", [PartOfSpeech.NOUN], ["Personal data protection"], WordFrequency.COMMON),
    "security": WordEntry("security", [PartOfSpeech.NOUN], ["Protection measures"], WordFrequency.CORE_500),
    "virus": WordEntry("virus", [PartOfSpeech.NOUN], ["Malicious software"], WordFrequency.CORE_1000),
    "malware": WordEntry("malware", [PartOfSpeech.NOUN], ["Harmful software"], WordFrequency.COMMON),
    "spam": WordEntry("spam", [PartOfSpeech.NOUN], ["Unwanted messages"], WordFrequency.COMMON),
    "phishing": WordEntry("phishing", [PartOfSpeech.NOUN], ["Fraudulent attempts"], WordFrequency.COMMON),
    
    # AI & Modern Tech
    "artificial": WordEntry("artificial", [PartOfSpeech.ADJECTIVE], ["Made by humans"], WordFrequency.COMMON),
    "intelligence": WordEntry("intelligence", [PartOfSpeech.NOUN], ["Mental capability"], WordFrequency.CORE_1000),
    "machine": WordEntry("machine", [PartOfSpeech.NOUN], ["Mechanical device"], WordFrequency.CORE_500),
    "learning": WordEntry("learning", [PartOfSpeech.NOUN], ["Knowledge acquisition"], WordFrequency.CORE_500),
    "neural": WordEntry("neural", [PartOfSpeech.ADJECTIVE], ["Related to neurons"], WordFrequency.COMMON),
    "network": WordEntry("network", [PartOfSpeech.NOUN], ["Connected system"], WordFrequency.CORE_500),
    "model": WordEntry("model", [PartOfSpeech.NOUN], ["Representation"], WordFrequency.CORE_500),
    "training": WordEntry("training", [PartOfSpeech.NOUN], ["Teaching process"], WordFrequency.CORE_500),
    "data": WordEntry("data", [PartOfSpeech.NOUN], ["Information"], WordFrequency.CORE_500),
    "dataset": WordEntry("dataset", [PartOfSpeech.NOUN], ["Data collection"], WordFrequency.COMMON),
    "prediction": WordEntry("prediction", [PartOfSpeech.NOUN], ["Forecast"], WordFrequency.COMMON),
    "classification": WordEntry("classification", [PartOfSpeech.NOUN], ["Categorization"], WordFrequency.COMMON),
    "automation": WordEntry("automation", [PartOfSpeech.NOUN], ["Automatic operation"], WordFrequency.COMMON),
    "robot": WordEntry("robot", [PartOfSpeech.NOUN], ["Programmable machine"], WordFrequency.COMMON),
    "virtual": WordEntry("virtual", [PartOfSpeech.ADJECTIVE], ["Simulated, not physical"], WordFrequency.COMMON),
    "reality": WordEntry("reality", [PartOfSpeech.NOUN], ["What is real"], WordFrequency.CORE_500),
    "augmented": WordEntry("augmented", [PartOfSpeech.ADJECTIVE], ["Enhanced, added to"], WordFrequency.COMMON),
    "simulation": WordEntry("simulation", [PartOfSpeech.NOUN], ["Imitation of reality"], WordFrequency.COMMON),
    "digital": WordEntry("digital", [PartOfSpeech.ADJECTIVE], ["Using digits, electronic"], WordFrequency.COMMON),
    "analog": WordEntry("analog", [PartOfSpeech.ADJECTIVE], ["Continuous signal"], WordFrequency.COMMON),
}


# =============================================================================
# SCIENCE & RESEARCH (~200 words)
# =============================================================================

SCIENCE_VOCAB = {
    # Scientific Method
    "science": WordEntry("science", [PartOfSpeech.NOUN], ["Systematic study of nature"], WordFrequency.CORE_500),
    "research": WordEntry("research", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Systematic investigation"], WordFrequency.CORE_500),
    "experiment": WordEntry("experiment", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Scientific test"], WordFrequency.CORE_1000),
    "hypothesis": WordEntry("hypothesis", [PartOfSpeech.NOUN], ["Proposed explanation"], WordFrequency.COMMON),
    "theory": WordEntry("theory", [PartOfSpeech.NOUN], ["Explanation of phenomena"], WordFrequency.CORE_500),
    "evidence": WordEntry("evidence", [PartOfSpeech.NOUN], ["Supporting proof"], WordFrequency.CORE_500),
    "proof": WordEntry("proof", [PartOfSpeech.NOUN], ["Conclusive evidence"], WordFrequency.CORE_1000),
    "observation": WordEntry("observation", [PartOfSpeech.NOUN], ["Act of watching"], WordFrequency.CORE_1000),
    "analysis": WordEntry("analysis", [PartOfSpeech.NOUN], ["Detailed examination"], WordFrequency.CORE_500),
    "conclusion": WordEntry("conclusion", [PartOfSpeech.NOUN], ["Final result"], WordFrequency.CORE_500),
    "result": WordEntry("result", [PartOfSpeech.NOUN], ["Outcome"], WordFrequency.CORE_500),
    "discovery": WordEntry("discovery", [PartOfSpeech.NOUN], ["Finding something new"], WordFrequency.CORE_1000),
    "method": WordEntry("method", [PartOfSpeech.NOUN], ["Way of doing"], WordFrequency.CORE_500),
    "procedure": WordEntry("procedure", [PartOfSpeech.NOUN], ["Series of steps"], WordFrequency.CORE_1000),
    "variable": WordEntry("variable", [PartOfSpeech.NOUN], ["Changeable factor"], WordFrequency.COMMON),
    "constant": WordEntry("constant", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Unchanging value"], WordFrequency.COMMON),
    "sample": WordEntry("sample", [PartOfSpeech.NOUN], ["Representative portion"], WordFrequency.CORE_1000),
    "data": WordEntry("data", [PartOfSpeech.NOUN], ["Facts and statistics"], WordFrequency.CORE_500),
    "measurement": WordEntry("measurement", [PartOfSpeech.NOUN], ["Act of measuring"], WordFrequency.CORE_1000),
    "accuracy": WordEntry("accuracy", [PartOfSpeech.NOUN], ["Correctness"], WordFrequency.COMMON),
    
    # Physics
    "physics": WordEntry("physics", [PartOfSpeech.NOUN], ["Study of matter and energy"], WordFrequency.COMMON),
    "energy": WordEntry("energy", [PartOfSpeech.NOUN], ["Capacity to do work"], WordFrequency.CORE_500),
    "force": WordEntry("force", [PartOfSpeech.NOUN], ["Push or pull"], WordFrequency.CORE_500),
    "mass": WordEntry("mass", [PartOfSpeech.NOUN], ["Amount of matter"], WordFrequency.CORE_1000),
    "weight": WordEntry("weight", [PartOfSpeech.NOUN], ["Gravitational force"], WordFrequency.CORE_500),
    "velocity": WordEntry("velocity", [PartOfSpeech.NOUN], ["Speed with direction"], WordFrequency.COMMON),
    "acceleration": WordEntry("acceleration", [PartOfSpeech.NOUN], ["Rate of speed change"], WordFrequency.COMMON),
    "gravity": WordEntry("gravity", [PartOfSpeech.NOUN], ["Gravitational pull"], WordFrequency.CORE_1000),
    "momentum": WordEntry("momentum", [PartOfSpeech.NOUN], ["Mass in motion"], WordFrequency.COMMON),
    "friction": WordEntry("friction", [PartOfSpeech.NOUN], ["Resistance to motion"], WordFrequency.COMMON),
    "pressure": WordEntry("pressure", [PartOfSpeech.NOUN], ["Force per area"], WordFrequency.CORE_500),
    "temperature": WordEntry("temperature", [PartOfSpeech.NOUN], ["Heat level"], WordFrequency.CORE_500),
    "wave": WordEntry("wave", [PartOfSpeech.NOUN], ["Energy transfer"], WordFrequency.CORE_500),
    "light": WordEntry("light", [PartOfSpeech.NOUN], ["Visible radiation"], WordFrequency.CORE_500),
    "sound": WordEntry("sound", [PartOfSpeech.NOUN], ["Audible vibration"], WordFrequency.CORE_500),
    "electricity": WordEntry("electricity", [PartOfSpeech.NOUN], ["Electric charge flow"], WordFrequency.CORE_1000),
    "magnet": WordEntry("magnet", [PartOfSpeech.NOUN], ["Magnetic material"], WordFrequency.CORE_1000),
    "atom": WordEntry("atom", [PartOfSpeech.NOUN], ["Basic unit of matter"], WordFrequency.CORE_1000),
    "molecule": WordEntry("molecule", [PartOfSpeech.NOUN], ["Bonded atoms"], WordFrequency.COMMON),
    "electron": WordEntry("electron", [PartOfSpeech.NOUN], ["Negative particle"], WordFrequency.COMMON),
    
    # Chemistry
    "chemistry": WordEntry("chemistry", [PartOfSpeech.NOUN], ["Study of substances"], WordFrequency.COMMON),
    "element": WordEntry("element", [PartOfSpeech.NOUN], ["Basic substance"], WordFrequency.CORE_500),
    "compound": WordEntry("compound", [PartOfSpeech.NOUN], ["Combined elements"], WordFrequency.COMMON),
    "reaction": WordEntry("reaction", [PartOfSpeech.NOUN], ["Chemical change"], WordFrequency.CORE_500),
    "solution": WordEntry("solution", [PartOfSpeech.NOUN], ["Dissolved mixture"], WordFrequency.CORE_500),
    "mixture": WordEntry("mixture", [PartOfSpeech.NOUN], ["Combined substances"], WordFrequency.COMMON),
    "acid": WordEntry("acid", [PartOfSpeech.NOUN], ["Corrosive substance"], WordFrequency.CORE_1000),
    "base": WordEntry("base", [PartOfSpeech.NOUN], ["Alkaline substance"], WordFrequency.CORE_500),
    "gas": WordEntry("gas", [PartOfSpeech.NOUN], ["Gaseous state"], WordFrequency.CORE_500),
    "liquid": WordEntry("liquid", [PartOfSpeech.NOUN], ["Fluid state"], WordFrequency.CORE_500),
    "solid": WordEntry("solid", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Firm state"], WordFrequency.CORE_500),
    
    # Biology
    "biology": WordEntry("biology", [PartOfSpeech.NOUN], ["Study of life"], WordFrequency.COMMON),
    "cell": WordEntry("cell", [PartOfSpeech.NOUN], ["Basic unit of life"], WordFrequency.CORE_500),
    "organism": WordEntry("organism", [PartOfSpeech.NOUN], ["Living being"], WordFrequency.COMMON),
    "species": WordEntry("species", [PartOfSpeech.NOUN], ["Type of organism"], WordFrequency.COMMON),
    "evolution": WordEntry("evolution", [PartOfSpeech.NOUN], ["Gradual development"], WordFrequency.COMMON),
    "gene": WordEntry("gene", [PartOfSpeech.NOUN], ["Hereditary unit"], WordFrequency.COMMON),
    "dna": WordEntry("dna", [PartOfSpeech.NOUN], ["Genetic material"], WordFrequency.COMMON),
    "protein": WordEntry("protein", [PartOfSpeech.NOUN], ["Biological molecule"], WordFrequency.COMMON),
    "ecosystem": WordEntry("ecosystem", [PartOfSpeech.NOUN], ["Living system"], WordFrequency.COMMON),
    "habitat": WordEntry("habitat", [PartOfSpeech.NOUN], ["Natural home"], WordFrequency.COMMON),
}


# =============================================================================
# BUSINESS & FINANCE (~150 words)
# =============================================================================

BUSINESS_VOCAB = {
    "business": WordEntry("business", [PartOfSpeech.NOUN], ["Commercial activity"], WordFrequency.CORE_500),
    "company": WordEntry("company", [PartOfSpeech.NOUN], ["Business organization"], WordFrequency.CORE_500),
    "corporation": WordEntry("corporation", [PartOfSpeech.NOUN], ["Large company"], WordFrequency.COMMON),
    "organization": WordEntry("organization", [PartOfSpeech.NOUN], ["Structured group"], WordFrequency.CORE_500),
    "enterprise": WordEntry("enterprise", [PartOfSpeech.NOUN], ["Business venture"], WordFrequency.COMMON),
    "industry": WordEntry("industry", [PartOfSpeech.NOUN], ["Economic sector"], WordFrequency.CORE_500),
    "market": WordEntry("market", [PartOfSpeech.NOUN], ["Trading place"], WordFrequency.CORE_500),
    "customer": WordEntry("customer", [PartOfSpeech.NOUN], ["Buyer"], WordFrequency.CORE_500),
    "client": WordEntry("client", [PartOfSpeech.NOUN], ["Service user"], WordFrequency.COMMON),
    "consumer": WordEntry("consumer", [PartOfSpeech.NOUN], ["End user"], WordFrequency.COMMON),
    "product": WordEntry("product", [PartOfSpeech.NOUN], ["Manufactured item"], WordFrequency.CORE_500),
    "service": WordEntry("service", [PartOfSpeech.NOUN], ["Work for others"], WordFrequency.CORE_500),
    "sale": WordEntry("sale", [PartOfSpeech.NOUN], ["Exchange for money"], WordFrequency.CORE_500),
    "purchase": WordEntry("purchase", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Buy"], WordFrequency.CORE_1000),
    "revenue": WordEntry("revenue", [PartOfSpeech.NOUN], ["Income"], WordFrequency.COMMON),
    "profit": WordEntry("profit", [PartOfSpeech.NOUN], ["Financial gain"], WordFrequency.CORE_1000),
    "loss": WordEntry("loss", [PartOfSpeech.NOUN], ["Financial deficit"], WordFrequency.CORE_500),
    "cost": WordEntry("cost", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Price to pay"], WordFrequency.CORE_500),
    "price": WordEntry("price", [PartOfSpeech.NOUN], ["Amount charged"], WordFrequency.CORE_500),
    "budget": WordEntry("budget", [PartOfSpeech.NOUN], ["Financial plan"], WordFrequency.COMMON),
    "investment": WordEntry("investment", [PartOfSpeech.NOUN], ["Money put in"], WordFrequency.COMMON),
    "stock": WordEntry("stock", [PartOfSpeech.NOUN], ["Company shares"], WordFrequency.CORE_1000),
    "share": WordEntry("share", [PartOfSpeech.NOUN], ["Ownership portion"], WordFrequency.CORE_500),
    "bond": WordEntry("bond", [PartOfSpeech.NOUN], ["Debt security"], WordFrequency.COMMON),
    "asset": WordEntry("asset", [PartOfSpeech.NOUN], ["Valuable possession"], WordFrequency.COMMON),
    "liability": WordEntry("liability", [PartOfSpeech.NOUN], ["Debt obligation"], WordFrequency.COMMON),
    "capital": WordEntry("capital", [PartOfSpeech.NOUN], ["Financial resources"], WordFrequency.COMMON),
    "interest": WordEntry("interest", [PartOfSpeech.NOUN], ["Money charge"], WordFrequency.CORE_500),
    "loan": WordEntry("loan", [PartOfSpeech.NOUN], ["Borrowed money"], WordFrequency.CORE_1000),
    "debt": WordEntry("debt", [PartOfSpeech.NOUN], ["Money owed"], WordFrequency.CORE_1000),
    "credit": WordEntry("credit", [PartOfSpeech.NOUN], ["Borrowing capacity"], WordFrequency.CORE_1000),
    "bank": WordEntry("bank", [PartOfSpeech.NOUN], ["Financial institution"], WordFrequency.CORE_500),
    "account": WordEntry("account", [PartOfSpeech.NOUN], ["Financial record"], WordFrequency.CORE_500),
    "tax": WordEntry("tax", [PartOfSpeech.NOUN], ["Government charge"], WordFrequency.CORE_1000),
    "income": WordEntry("income", [PartOfSpeech.NOUN], ["Money earned"], WordFrequency.CORE_1000),
    "salary": WordEntry("salary", [PartOfSpeech.NOUN], ["Regular pay"], WordFrequency.COMMON),
    "wage": WordEntry("wage", [PartOfSpeech.NOUN], ["Payment for work"], WordFrequency.CORE_1000),
    "employee": WordEntry("employee", [PartOfSpeech.NOUN], ["Worker"], WordFrequency.CORE_1000),
    "employer": WordEntry("employer", [PartOfSpeech.NOUN], ["Hiring party"], WordFrequency.COMMON),
    "manager": WordEntry("manager", [PartOfSpeech.NOUN], ["Supervisor"], WordFrequency.CORE_1000),
    "executive": WordEntry("executive", [PartOfSpeech.NOUN], ["Senior leader"], WordFrequency.COMMON),
    "strategy": WordEntry("strategy", [PartOfSpeech.NOUN], ["Long-term plan"], WordFrequency.COMMON),
    "contract": WordEntry("contract", [PartOfSpeech.NOUN], ["Legal agreement"], WordFrequency.CORE_1000),
    "agreement": WordEntry("agreement", [PartOfSpeech.NOUN], ["Mutual understanding"], WordFrequency.CORE_500),
    "negotiation": WordEntry("negotiation", [PartOfSpeech.NOUN], ["Discussion to agree"], WordFrequency.COMMON),
    "competition": WordEntry("competition", [PartOfSpeech.NOUN], ["Rivalry"], WordFrequency.CORE_1000),
    "competitor": WordEntry("competitor", [PartOfSpeech.NOUN], ["Rival"], WordFrequency.COMMON),
    "marketing": WordEntry("marketing", [PartOfSpeech.NOUN], ["Promotion activities"], WordFrequency.COMMON),
    "advertising": WordEntry("advertising", [PartOfSpeech.NOUN], ["Public promotion"], WordFrequency.COMMON),
    "brand": WordEntry("brand", [PartOfSpeech.NOUN], ["Product identity"], WordFrequency.COMMON),
}


# =============================================================================
# EDUCATION & LEARNING (~100 words)
# =============================================================================

EDUCATION_VOCAB = {
    "education": WordEntry("education", [PartOfSpeech.NOUN], ["Learning process"], WordFrequency.CORE_500),
    "school": WordEntry("school", [PartOfSpeech.NOUN], ["Educational institution"], WordFrequency.CORE_500),
    "university": WordEntry("university", [PartOfSpeech.NOUN], ["Higher education"], WordFrequency.CORE_500),
    "college": WordEntry("college", [PartOfSpeech.NOUN], ["Educational institution"], WordFrequency.CORE_500),
    "class": WordEntry("class", [PartOfSpeech.NOUN], ["Group of students"], WordFrequency.CORE_500),
    "course": WordEntry("course", [PartOfSpeech.NOUN], ["Series of lessons"], WordFrequency.CORE_500),
    "lesson": WordEntry("lesson", [PartOfSpeech.NOUN], ["Teaching unit"], WordFrequency.CORE_1000),
    "lecture": WordEntry("lecture", [PartOfSpeech.NOUN], ["Educational talk"], WordFrequency.COMMON),
    "student": WordEntry("student", [PartOfSpeech.NOUN], ["Learner"], WordFrequency.CORE_500),
    "teacher": WordEntry("teacher", [PartOfSpeech.NOUN], ["Educator"], WordFrequency.CORE_500),
    "professor": WordEntry("professor", [PartOfSpeech.NOUN], ["University teacher"], WordFrequency.COMMON),
    "instructor": WordEntry("instructor", [PartOfSpeech.NOUN], ["Teacher"], WordFrequency.COMMON),
    "tutor": WordEntry("tutor", [PartOfSpeech.NOUN], ["Private teacher"], WordFrequency.COMMON),
    "degree": WordEntry("degree", [PartOfSpeech.NOUN], ["Academic qualification"], WordFrequency.CORE_500),
    "diploma": WordEntry("diploma", [PartOfSpeech.NOUN], ["Certificate"], WordFrequency.COMMON),
    "certificate": WordEntry("certificate", [PartOfSpeech.NOUN], ["Official document"], WordFrequency.COMMON),
    "exam": WordEntry("exam", [PartOfSpeech.NOUN], ["Test"], WordFrequency.CORE_1000),
    "test": WordEntry("test", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Examination"], WordFrequency.CORE_500),
    "quiz": WordEntry("quiz", [PartOfSpeech.NOUN], ["Short test"], WordFrequency.COMMON),
    "assignment": WordEntry("assignment", [PartOfSpeech.NOUN], ["Task given"], WordFrequency.COMMON),
    "homework": WordEntry("homework", [PartOfSpeech.NOUN], ["Home study"], WordFrequency.CORE_1000),
    "project": WordEntry("project", [PartOfSpeech.NOUN], ["Extended task"], WordFrequency.CORE_500),
    "essay": WordEntry("essay", [PartOfSpeech.NOUN], ["Written piece"], WordFrequency.COMMON),
    "thesis": WordEntry("thesis", [PartOfSpeech.NOUN], ["Academic paper"], WordFrequency.COMMON),
    "research": WordEntry("research", [PartOfSpeech.NOUN], ["Investigation"], WordFrequency.CORE_500),
    "study": WordEntry("study", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Learning activity"], WordFrequency.CORE_500),
    "learn": WordEntry("learn", [PartOfSpeech.VERB], ["Acquire knowledge"], WordFrequency.CORE_500),
    "teach": WordEntry("teach", [PartOfSpeech.VERB], ["Impart knowledge"], WordFrequency.CORE_500),
    "practice": WordEntry("practice", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Repeated exercise"], WordFrequency.CORE_500),
    "review": WordEntry("review", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Re-examine"], WordFrequency.CORE_500),
    "grade": WordEntry("grade", [PartOfSpeech.NOUN], ["Score level"], WordFrequency.CORE_1000),
    "score": WordEntry("score", [PartOfSpeech.NOUN], ["Points achieved"], WordFrequency.CORE_500),
    "curriculum": WordEntry("curriculum", [PartOfSpeech.NOUN], ["Course of study"], WordFrequency.COMMON),
    "syllabus": WordEntry("syllabus", [PartOfSpeech.NOUN], ["Course outline"], WordFrequency.COMMON),
    "textbook": WordEntry("textbook", [PartOfSpeech.NOUN], ["Study book"], WordFrequency.COMMON),
    "library": WordEntry("library", [PartOfSpeech.NOUN], ["Book collection"], WordFrequency.CORE_1000),
    "knowledge": WordEntry("knowledge", [PartOfSpeech.NOUN], ["Understanding"], WordFrequency.CORE_500),
    "skill": WordEntry("skill", [PartOfSpeech.NOUN], ["Learned ability"], WordFrequency.CORE_500),
    "ability": WordEntry("ability", [PartOfSpeech.NOUN], ["Capability"], WordFrequency.CORE_500),
    "comprehension": WordEntry("comprehension", [PartOfSpeech.NOUN], ["Understanding"], WordFrequency.COMMON),
    "vocabulary": WordEntry("vocabulary", [PartOfSpeech.NOUN], ["Word collection"], WordFrequency.COMMON),
    "grammar": WordEntry("grammar", [PartOfSpeech.NOUN], ["Language rules"], WordFrequency.COMMON),
    "spelling": WordEntry("spelling", [PartOfSpeech.NOUN], ["Word formation"], WordFrequency.COMMON),
    "reading": WordEntry("reading", [PartOfSpeech.NOUN], ["Text interpretation"], WordFrequency.CORE_500),
    "writing": WordEntry("writing", [PartOfSpeech.NOUN], ["Text creation"], WordFrequency.CORE_500),
    "mathematics": WordEntry("mathematics", [PartOfSpeech.NOUN], ["Number science"], WordFrequency.COMMON),
    "math": WordEntry("math", [PartOfSpeech.NOUN], ["Mathematics"], WordFrequency.COMMON),
    "science": WordEntry("science", [PartOfSpeech.NOUN], ["Study of nature"], WordFrequency.CORE_500),
    "history": WordEntry("history", [PartOfSpeech.NOUN], ["Past events"], WordFrequency.CORE_500),
    "geography": WordEntry("geography", [PartOfSpeech.NOUN], ["Earth study"], WordFrequency.COMMON),
}


# =============================================================================
# HEALTH & MEDICINE (~100 words)
# =============================================================================

HEALTH_VOCAB = {
    "health": WordEntry("health", [PartOfSpeech.NOUN], ["Physical condition"], WordFrequency.CORE_500),
    "medicine": WordEntry("medicine", [PartOfSpeech.NOUN], ["Healing science"], WordFrequency.CORE_500),
    "doctor": WordEntry("doctor", [PartOfSpeech.NOUN], ["Medical professional"], WordFrequency.CORE_500),
    "nurse": WordEntry("nurse", [PartOfSpeech.NOUN], ["Healthcare worker"], WordFrequency.CORE_1000),
    "patient": WordEntry("patient", [PartOfSpeech.NOUN], ["Person receiving care"], WordFrequency.CORE_500),
    "hospital": WordEntry("hospital", [PartOfSpeech.NOUN], ["Medical facility"], WordFrequency.CORE_500),
    "clinic": WordEntry("clinic", [PartOfSpeech.NOUN], ["Medical office"], WordFrequency.COMMON),
    "treatment": WordEntry("treatment", [PartOfSpeech.NOUN], ["Medical care"], WordFrequency.CORE_1000),
    "therapy": WordEntry("therapy", [PartOfSpeech.NOUN], ["Treatment method"], WordFrequency.COMMON),
    "surgery": WordEntry("surgery", [PartOfSpeech.NOUN], ["Medical operation"], WordFrequency.COMMON),
    "operation": WordEntry("operation", [PartOfSpeech.NOUN], ["Surgical procedure"], WordFrequency.CORE_500),
    "disease": WordEntry("disease", [PartOfSpeech.NOUN], ["Illness"], WordFrequency.CORE_1000),
    "illness": WordEntry("illness", [PartOfSpeech.NOUN], ["Sickness"], WordFrequency.CORE_1000),
    "condition": WordEntry("condition", [PartOfSpeech.NOUN], ["Health state"], WordFrequency.CORE_500),
    "symptom": WordEntry("symptom", [PartOfSpeech.NOUN], ["Disease sign"], WordFrequency.COMMON),
    "diagnosis": WordEntry("diagnosis", [PartOfSpeech.NOUN], ["Illness identification"], WordFrequency.COMMON),
    "prescription": WordEntry("prescription", [PartOfSpeech.NOUN], ["Medicine order"], WordFrequency.COMMON),
    "medication": WordEntry("medication", [PartOfSpeech.NOUN], ["Medicine"], WordFrequency.COMMON),
    "drug": WordEntry("drug", [PartOfSpeech.NOUN], ["Medicine"], WordFrequency.CORE_500),
    "pill": WordEntry("pill", [PartOfSpeech.NOUN], ["Medicine tablet"], WordFrequency.CORE_1000),
    "vaccine": WordEntry("vaccine", [PartOfSpeech.NOUN], ["Disease prevention"], WordFrequency.COMMON),
    "injection": WordEntry("injection", [PartOfSpeech.NOUN], ["Shot"], WordFrequency.COMMON),
    "pain": WordEntry("pain", [PartOfSpeech.NOUN], ["Physical discomfort"], WordFrequency.CORE_500),
    "fever": WordEntry("fever", [PartOfSpeech.NOUN], ["High temperature"], WordFrequency.CORE_1000),
    "headache": WordEntry("headache", [PartOfSpeech.NOUN], ["Head pain"], WordFrequency.COMMON),
    "cold": WordEntry("cold", [PartOfSpeech.NOUN], ["Common illness"], WordFrequency.CORE_500),
    "flu": WordEntry("flu", [PartOfSpeech.NOUN], ["Influenza"], WordFrequency.COMMON),
    "infection": WordEntry("infection", [PartOfSpeech.NOUN], ["Disease invasion"], WordFrequency.COMMON),
    "allergy": WordEntry("allergy", [PartOfSpeech.NOUN], ["Immune reaction"], WordFrequency.COMMON),
    "injury": WordEntry("injury", [PartOfSpeech.NOUN], ["Harm, damage"], WordFrequency.CORE_1000),
    "wound": WordEntry("wound", [PartOfSpeech.NOUN], ["Body damage"], WordFrequency.CORE_1000),
    "recovery": WordEntry("recovery", [PartOfSpeech.NOUN], ["Healing process"], WordFrequency.COMMON),
    "healthy": WordEntry("healthy", [PartOfSpeech.ADJECTIVE], ["In good health"], WordFrequency.CORE_500),
    "sick": WordEntry("sick", [PartOfSpeech.ADJECTIVE], ["Ill"], WordFrequency.CORE_500),
    "exercise": WordEntry("exercise", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Physical activity"], WordFrequency.CORE_500),
    "diet": WordEntry("diet", [PartOfSpeech.NOUN], ["Food intake"], WordFrequency.COMMON),
    "nutrition": WordEntry("nutrition", [PartOfSpeech.NOUN], ["Nourishment"], WordFrequency.COMMON),
    "vitamin": WordEntry("vitamin", [PartOfSpeech.NOUN], ["Nutrient"], WordFrequency.COMMON),
    "sleep": WordEntry("sleep", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Rest"], WordFrequency.CORE_500),
    "stress": WordEntry("stress", [PartOfSpeech.NOUN], ["Mental tension"], WordFrequency.COMMON),
    "mental": WordEntry("mental", [PartOfSpeech.ADJECTIVE], ["Of the mind"], WordFrequency.CORE_1000),
    "physical": WordEntry("physical", [PartOfSpeech.ADJECTIVE], ["Of the body"], WordFrequency.CORE_500),
}


# =============================================================================
# LOADING FUNCTION
# =============================================================================

def load_domain_vocabulary(vocab=None):
    """
    Load all domain-specific vocabulary.
    
    Args:
        vocab: Optional existing vocabulary to extend
        
    Returns:
        Extended vocabulary with domain words
    """
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    domains = [
        ("technology", TECHNOLOGY_VOCAB),
        ("science", SCIENCE_VOCAB),
        ("business", BUSINESS_VOCAB),
        ("education", EDUCATION_VOCAB),
        ("health", HEALTH_VOCAB),
    ]
    
    total_added = 0
    for domain_name, domain_words in domains:
        for word, entry in domain_words.items():
            vocab.add_word(entry)
            total_added += 1
            
    print(f"[DomainVocabulary] Loaded {total_added} domain-specific words")
    print(f"[DomainVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_domain_stats() -> Dict[str, int]:
    """Get word counts per domain."""
    return {
        "technology": len(TECHNOLOGY_VOCAB),
        "science": len(SCIENCE_VOCAB),
        "business": len(BUSINESS_VOCAB),
        "education": len(EDUCATION_VOCAB),
        "health": len(HEALTH_VOCAB),
        "total": (
            len(TECHNOLOGY_VOCAB) + len(SCIENCE_VOCAB) + 
            len(BUSINESS_VOCAB) + len(EDUCATION_VOCAB) + len(HEALTH_VOCAB)
        )
    }
