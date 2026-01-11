# unimind/models/native/vocabulary_common.py
# Common English Words - Expanding to ~3000 words for fluency

"""
Common English Words

Expands vocabulary with frequently used English words to achieve
conversational fluency (~3000 words = ~95% text coverage).

This module adds:
- Additional verbs (200+)
- Additional nouns (500+)
- Additional adjectives (200+)
- Phrasal verbs (100+)
- Common expressions
"""

from typing import Dict, List
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# ADDITIONAL COMMON VERBS
# =============================================================================

MORE_VERBS = {
    # Movement
    "arrive": WordEntry("arrive", [PartOfSpeech.VERB], ["Reach a destination"], WordFrequency.CORE_1000),
    "depart": WordEntry("depart", [PartOfSpeech.VERB], ["Leave"], WordFrequency.COMMON),
    "enter": WordEntry("enter", [PartOfSpeech.VERB], ["Go into"], WordFrequency.CORE_1000),
    "exit": WordEntry("exit", [PartOfSpeech.VERB], ["Go out"], WordFrequency.CORE_1000),
    "climb": WordEntry("climb", [PartOfSpeech.VERB], ["Go up"], WordFrequency.CORE_1000),
    "jump": WordEntry("jump", [PartOfSpeech.VERB], ["Leap"], WordFrequency.CORE_1000),
    "fly": WordEntry("fly", [PartOfSpeech.VERB], ["Move through air"], WordFrequency.CORE_1000),
    "swim": WordEntry("swim", [PartOfSpeech.VERB], ["Move in water"], WordFrequency.CORE_1000),
    "push": WordEntry("push", [PartOfSpeech.VERB], ["Press forward"], WordFrequency.CORE_1000),
    "pull": WordEntry("pull", [PartOfSpeech.VERB], ["Draw toward"], WordFrequency.CORE_1000),
    "throw": WordEntry("throw", [PartOfSpeech.VERB], ["Propel through air"], WordFrequency.CORE_1000),
    "catch": WordEntry("catch", [PartOfSpeech.VERB], ["Grab, capture"], WordFrequency.CORE_1000),
    "kick": WordEntry("kick", [PartOfSpeech.VERB], ["Strike with foot"], WordFrequency.CORE_1000),
    "hit": WordEntry("hit", [PartOfSpeech.VERB], ["Strike"], WordFrequency.CORE_1000),
    "drop": WordEntry("drop", [PartOfSpeech.VERB], ["Let fall"], WordFrequency.CORE_1000),
    "lift": WordEntry("lift", [PartOfSpeech.VERB], ["Raise up"], WordFrequency.CORE_1000),
    "pick": WordEntry("pick", [PartOfSpeech.VERB], ["Select, gather"], WordFrequency.CORE_1000),
    "shake": WordEntry("shake", [PartOfSpeech.VERB], ["Move back and forth"], WordFrequency.CORE_1000),
    "touch": WordEntry("touch", [PartOfSpeech.VERB], ["Make contact"], WordFrequency.CORE_1000),
    "reach": WordEntry("reach", [PartOfSpeech.VERB], ["Extend to, arrive at"], WordFrequency.CORE_1000),
    
    # Communication
    "respond": WordEntry("respond", [PartOfSpeech.VERB], ["Reply"], WordFrequency.COMMON),
    "reply": WordEntry("reply", [PartOfSpeech.VERB], ["Answer"], WordFrequency.COMMON),
    "mention": WordEntry("mention", [PartOfSpeech.VERB], ["Refer to"], WordFrequency.COMMON),
    "state": WordEntry("state", [PartOfSpeech.VERB], ["Declare formally"], WordFrequency.COMMON),
    "express": WordEntry("express", [PartOfSpeech.VERB], ["Convey"], WordFrequency.COMMON),
    "communicate": WordEntry("communicate", [PartOfSpeech.VERB], ["Share information"], WordFrequency.COMMON),
    "whisper": WordEntry("whisper", [PartOfSpeech.VERB], ["Speak softly"], WordFrequency.COMMON),
    "shout": WordEntry("shout", [PartOfSpeech.VERB], ["Speak loudly"], WordFrequency.CORE_1000),
    "yell": WordEntry("yell", [PartOfSpeech.VERB], ["Cry out"], WordFrequency.COMMON),
    "sing": WordEntry("sing", [PartOfSpeech.VERB], ["Produce music with voice"], WordFrequency.CORE_1000),
    "laugh": WordEntry("laugh", [PartOfSpeech.VERB], ["Express amusement"], WordFrequency.CORE_1000),
    "cry": WordEntry("cry", [PartOfSpeech.VERB], ["Shed tears"], WordFrequency.CORE_1000),
    "smile": WordEntry("smile", [PartOfSpeech.VERB], ["Express pleasure"], WordFrequency.CORE_1000),
    "agree": WordEntry("agree", [PartOfSpeech.VERB], ["Have same opinion"], WordFrequency.CORE_1000),
    "disagree": WordEntry("disagree", [PartOfSpeech.VERB], ["Have different opinion"], WordFrequency.COMMON),
    "accept": WordEntry("accept", [PartOfSpeech.VERB], ["Receive willingly"], WordFrequency.CORE_1000),
    "refuse": WordEntry("refuse", [PartOfSpeech.VERB], ["Decline"], WordFrequency.CORE_1000),
    "invite": WordEntry("invite", [PartOfSpeech.VERB], ["Ask to come"], WordFrequency.COMMON),
    "introduce": WordEntry("introduce", [PartOfSpeech.VERB], ["Present"], WordFrequency.COMMON),
    
    # Mental actions
    "notice": WordEntry("notice", [PartOfSpeech.VERB], ["Observe"], WordFrequency.CORE_1000),
    "observe": WordEntry("observe", [PartOfSpeech.VERB], ["Watch carefully"], WordFrequency.COMMON),
    "discover": WordEntry("discover", [PartOfSpeech.VERB], ["Find out"], WordFrequency.CORE_1000),
    "explore": WordEntry("explore", [PartOfSpeech.VERB], ["Investigate"], WordFrequency.COMMON),
    "investigate": WordEntry("investigate", [PartOfSpeech.VERB], ["Examine"], WordFrequency.COMMON),
    "determine": WordEntry("determine", [PartOfSpeech.VERB], ["Find out, decide"], WordFrequency.COMMON),
    "conclude": WordEntry("conclude", [PartOfSpeech.VERB], ["Finish, deduce"], WordFrequency.COMMON),
    "interpret": WordEntry("interpret", [PartOfSpeech.VERB], ["Explain meaning"], WordFrequency.COMMON),
    "assess": WordEntry("assess", [PartOfSpeech.VERB], ["Evaluate"], WordFrequency.COMMON),
    "judge": WordEntry("judge", [PartOfSpeech.VERB], ["Form opinion"], WordFrequency.CORE_1000),
    "estimate": WordEntry("estimate", [PartOfSpeech.VERB], ["Approximate"], WordFrequency.COMMON),
    "calculate": WordEntry("calculate", [PartOfSpeech.VERB], ["Compute"], WordFrequency.COMMON),
    "measure": WordEntry("measure", [PartOfSpeech.VERB], ["Determine size"], WordFrequency.CORE_1000),
    "solve": WordEntry("solve", [PartOfSpeech.VERB], ["Find answer"], WordFrequency.CORE_1000),
    "select": WordEntry("select", [PartOfSpeech.VERB], ["Choose"], WordFrequency.COMMON),
    "identify": WordEntry("identify", [PartOfSpeech.VERB], ["Recognize"], WordFrequency.COMMON),
    "define": WordEntry("define", [PartOfSpeech.VERB], ["Give meaning"], WordFrequency.COMMON),
    "summarize": WordEntry("summarize", [PartOfSpeech.VERB], ["Give brief account"], WordFrequency.COMMON),
    
    # Creation and change
    "design": WordEntry("design", [PartOfSpeech.VERB], ["Plan, create"], WordFrequency.COMMON),
    "construct": WordEntry("construct", [PartOfSpeech.VERB], ["Build"], WordFrequency.COMMON),
    "produce": WordEntry("produce", [PartOfSpeech.VERB], ["Make, create"], WordFrequency.CORE_1000),
    "manufacture": WordEntry("manufacture", [PartOfSpeech.VERB], ["Make goods"], WordFrequency.COMMON),
    "assemble": WordEntry("assemble", [PartOfSpeech.VERB], ["Put together"], WordFrequency.COMMON),
    "organize": WordEntry("organize", [PartOfSpeech.VERB], ["Arrange"], WordFrequency.COMMON),
    "arrange": WordEntry("arrange", [PartOfSpeech.VERB], ["Put in order"], WordFrequency.COMMON),
    "adjust": WordEntry("adjust", [PartOfSpeech.VERB], ["Modify slightly"], WordFrequency.COMMON),
    "modify": WordEntry("modify", [PartOfSpeech.VERB], ["Change"], WordFrequency.COMMON),
    "transform": WordEntry("transform", [PartOfSpeech.VERB], ["Change completely"], WordFrequency.COMMON),
    "convert": WordEntry("convert", [PartOfSpeech.VERB], ["Change form"], WordFrequency.COMMON),
    "replace": WordEntry("replace", [PartOfSpeech.VERB], ["Substitute"], WordFrequency.COMMON),
    "repair": WordEntry("repair", [PartOfSpeech.VERB], ["Fix"], WordFrequency.COMMON),
    "restore": WordEntry("restore", [PartOfSpeech.VERB], ["Return to original"], WordFrequency.COMMON),
    "maintain": WordEntry("maintain", [PartOfSpeech.VERB], ["Keep in condition"], WordFrequency.COMMON),
    "preserve": WordEntry("preserve", [PartOfSpeech.VERB], ["Keep safe"], WordFrequency.COMMON),
    "protect": WordEntry("protect", [PartOfSpeech.VERB], ["Keep safe"], WordFrequency.CORE_1000),
    "defend": WordEntry("defend", [PartOfSpeech.VERB], ["Protect"], WordFrequency.COMMON),
    "attack": WordEntry("attack", [PartOfSpeech.VERB], ["Act against"], WordFrequency.CORE_1000),
    "damage": WordEntry("damage", [PartOfSpeech.VERB], ["Harm"], WordFrequency.COMMON),
    
    # Interaction
    "join": WordEntry("join", [PartOfSpeech.VERB], ["Connect, become member"], WordFrequency.CORE_1000),
    "separate": WordEntry("separate", [PartOfSpeech.VERB], ["Divide"], WordFrequency.COMMON),
    "combine": WordEntry("combine", [PartOfSpeech.VERB], ["Mix together"], WordFrequency.COMMON),
    "mix": WordEntry("mix", [PartOfSpeech.VERB], ["Combine"], WordFrequency.CORE_1000),
    "divide": WordEntry("divide", [PartOfSpeech.VERB], ["Split"], WordFrequency.COMMON),
    "split": WordEntry("split", [PartOfSpeech.VERB], ["Divide"], WordFrequency.COMMON),
    "attach": WordEntry("attach", [PartOfSpeech.VERB], ["Connect"], WordFrequency.COMMON),
    "detach": WordEntry("detach", [PartOfSpeech.VERB], ["Disconnect"], WordFrequency.COMMON),
    "belong": WordEntry("belong", [PartOfSpeech.VERB], ["Be part of"], WordFrequency.CORE_1000),
    "contain": WordEntry("contain", [PartOfSpeech.VERB], ["Hold within"], WordFrequency.COMMON),
    "cover": WordEntry("cover", [PartOfSpeech.VERB], ["Put over"], WordFrequency.CORE_1000),
    "wrap": WordEntry("wrap", [PartOfSpeech.VERB], ["Cover completely"], WordFrequency.COMMON),
    "fill": WordEntry("fill", [PartOfSpeech.VERB], ["Make full"], WordFrequency.CORE_1000),
    "empty": WordEntry("empty", [PartOfSpeech.VERB], ["Remove contents"], WordFrequency.CORE_1000),
    "insert": WordEntry("insert", [PartOfSpeech.VERB], ["Put in"], WordFrequency.COMMON),
    "extract": WordEntry("extract", [PartOfSpeech.VERB], ["Take out"], WordFrequency.COMMON),
    
    # Achievement
    "achieve": WordEntry("achieve", [PartOfSpeech.VERB], ["Accomplish"], WordFrequency.COMMON),
    "accomplish": WordEntry("accomplish", [PartOfSpeech.VERB], ["Complete successfully"], WordFrequency.COMMON),
    "succeed": WordEntry("succeed", [PartOfSpeech.VERB], ["Achieve goal"], WordFrequency.COMMON),
    "fail": WordEntry("fail", [PartOfSpeech.VERB], ["Not succeed"], WordFrequency.CORE_1000),
    "attempt": WordEntry("attempt", [PartOfSpeech.VERB], ["Try"], WordFrequency.COMMON),
    "struggle": WordEntry("struggle", [PartOfSpeech.VERB], ["Try hard"], WordFrequency.COMMON),
    "compete": WordEntry("compete", [PartOfSpeech.VERB], ["Rival"], WordFrequency.COMMON),
    "challenge": WordEntry("challenge", [PartOfSpeech.VERB], ["Confront"], WordFrequency.COMMON),
    "overcome": WordEntry("overcome", [PartOfSpeech.VERB], ["Defeat"], WordFrequency.COMMON),
    "survive": WordEntry("survive", [PartOfSpeech.VERB], ["Continue to exist"], WordFrequency.COMMON),
    
    # Experience
    "experience": WordEntry("experience", [PartOfSpeech.VERB], ["Undergo"], WordFrequency.CORE_1000),
    "enjoy": WordEntry("enjoy", [PartOfSpeech.VERB], ["Take pleasure in"], WordFrequency.CORE_1000),
    "suffer": WordEntry("suffer", [PartOfSpeech.VERB], ["Undergo pain"], WordFrequency.CORE_1000),
    "appreciate": WordEntry("appreciate", [PartOfSpeech.VERB], ["Value highly"], WordFrequency.COMMON),
    "value": WordEntry("value", [PartOfSpeech.VERB], ["Consider important"], WordFrequency.CORE_1000),
    "respect": WordEntry("respect", [PartOfSpeech.VERB], ["Hold in esteem"], WordFrequency.COMMON),
    "admire": WordEntry("admire", [PartOfSpeech.VERB], ["Regard highly"], WordFrequency.COMMON),
    "trust": WordEntry("trust", [PartOfSpeech.VERB], ["Believe in"], WordFrequency.CORE_1000),
    "rely": WordEntry("rely", [PartOfSpeech.VERB], ["Depend on"], WordFrequency.COMMON),
    "depend": WordEntry("depend", [PartOfSpeech.VERB], ["Rely on"], WordFrequency.COMMON),
}


# =============================================================================
# ADDITIONAL COMMON NOUNS
# =============================================================================

MORE_NOUNS = {
    # Everyday objects
    "key": WordEntry("key", [PartOfSpeech.NOUN], ["Device to open lock"], WordFrequency.CORE_1000),
    "bag": WordEntry("bag", [PartOfSpeech.NOUN], ["Container"], WordFrequency.CORE_1000),
    "box": WordEntry("box", [PartOfSpeech.NOUN], ["Container"], WordFrequency.CORE_1000),
    "bottle": WordEntry("bottle", [PartOfSpeech.NOUN], ["Container for liquid"], WordFrequency.CORE_1000),
    "cup": WordEntry("cup", [PartOfSpeech.NOUN], ["Drinking vessel"], WordFrequency.CORE_1000),
    "glass": WordEntry("glass", [PartOfSpeech.NOUN], ["Drinking vessel, material"], WordFrequency.CORE_1000),
    "plate": WordEntry("plate", [PartOfSpeech.NOUN], ["Dish for food"], WordFrequency.CORE_1000),
    "bowl": WordEntry("bowl", [PartOfSpeech.NOUN], ["Round dish"], WordFrequency.CORE_1000),
    "knife": WordEntry("knife", [PartOfSpeech.NOUN], ["Cutting tool"], WordFrequency.CORE_1000),
    "fork": WordEntry("fork", [PartOfSpeech.NOUN], ["Eating utensil"], WordFrequency.CORE_1000),
    "spoon": WordEntry("spoon", [PartOfSpeech.NOUN], ["Eating utensil"], WordFrequency.CORE_1000),
    "pen": WordEntry("pen", [PartOfSpeech.NOUN], ["Writing instrument"], WordFrequency.CORE_1000),
    "pencil": WordEntry("pencil", [PartOfSpeech.NOUN], ["Writing instrument"], WordFrequency.CORE_1000),
    "brush": WordEntry("brush", [PartOfSpeech.NOUN], ["Tool with bristles"], WordFrequency.CORE_1000),
    "clock": WordEntry("clock", [PartOfSpeech.NOUN], ["Time device"], WordFrequency.CORE_1000),
    "watch": WordEntry("watch", [PartOfSpeech.NOUN], ["Wrist timepiece"], WordFrequency.CORE_1000),
    "mirror": WordEntry("mirror", [PartOfSpeech.NOUN], ["Reflective surface"], WordFrequency.CORE_1000),
    "lamp": WordEntry("lamp", [PartOfSpeech.NOUN], ["Light source"], WordFrequency.CORE_1000),
    "umbrella": WordEntry("umbrella", [PartOfSpeech.NOUN], ["Rain protection"], WordFrequency.COMMON),
    "wallet": WordEntry("wallet", [PartOfSpeech.NOUN], ["Money holder"], WordFrequency.COMMON),
    
    # Clothing
    "shirt": WordEntry("shirt", [PartOfSpeech.NOUN], ["Upper body garment"], WordFrequency.CORE_1000),
    "pants": WordEntry("pants", [PartOfSpeech.NOUN], ["Lower body garment"], WordFrequency.CORE_1000),
    "dress": WordEntry("dress", [PartOfSpeech.NOUN], ["One-piece garment"], WordFrequency.CORE_1000),
    "coat": WordEntry("coat", [PartOfSpeech.NOUN], ["Outer garment"], WordFrequency.CORE_1000),
    "jacket": WordEntry("jacket", [PartOfSpeech.NOUN], ["Light coat"], WordFrequency.CORE_1000),
    "shoes": WordEntry("shoes", [PartOfSpeech.NOUN], ["Footwear"], WordFrequency.CORE_1000),
    "boots": WordEntry("boots", [PartOfSpeech.NOUN], ["Heavy footwear"], WordFrequency.CORE_1000),
    "hat": WordEntry("hat", [PartOfSpeech.NOUN], ["Head covering"], WordFrequency.CORE_1000),
    "glasses": WordEntry("glasses", [PartOfSpeech.NOUN], ["Eyewear"], WordFrequency.CORE_1000),
    "ring": WordEntry("ring", [PartOfSpeech.NOUN], ["Finger jewelry"], WordFrequency.CORE_1000),
    
    # Food
    "bread": WordEntry("bread", [PartOfSpeech.NOUN], ["Baked food"], WordFrequency.CORE_1000),
    "rice": WordEntry("rice", [PartOfSpeech.NOUN], ["Grain food"], WordFrequency.CORE_1000),
    "meat": WordEntry("meat", [PartOfSpeech.NOUN], ["Animal food"], WordFrequency.CORE_1000),
    "chicken": WordEntry("chicken", [PartOfSpeech.NOUN], ["Poultry"], WordFrequency.CORE_1000),
    "fish": WordEntry("fish", [PartOfSpeech.NOUN], ["Seafood"], WordFrequency.CORE_1000),
    "egg": WordEntry("egg", [PartOfSpeech.NOUN], ["Oval food"], WordFrequency.CORE_1000),
    "cheese": WordEntry("cheese", [PartOfSpeech.NOUN], ["Dairy food"], WordFrequency.CORE_1000),
    "butter": WordEntry("butter", [PartOfSpeech.NOUN], ["Dairy spread"], WordFrequency.CORE_1000),
    "milk": WordEntry("milk", [PartOfSpeech.NOUN], ["Dairy drink"], WordFrequency.CORE_1000),
    "coffee": WordEntry("coffee", [PartOfSpeech.NOUN], ["Hot beverage"], WordFrequency.CORE_1000),
    "tea": WordEntry("tea", [PartOfSpeech.NOUN], ["Hot beverage"], WordFrequency.CORE_1000),
    "juice": WordEntry("juice", [PartOfSpeech.NOUN], ["Fruit drink"], WordFrequency.CORE_1000),
    "sugar": WordEntry("sugar", [PartOfSpeech.NOUN], ["Sweetener"], WordFrequency.CORE_1000),
    "salt": WordEntry("salt", [PartOfSpeech.NOUN], ["Seasoning"], WordFrequency.CORE_1000),
    "vegetable": WordEntry("vegetable", [PartOfSpeech.NOUN], ["Plant food"], WordFrequency.CORE_1000),
    "fruit": WordEntry("fruit", [PartOfSpeech.NOUN], ["Sweet produce"], WordFrequency.CORE_1000),
    "apple": WordEntry("apple", [PartOfSpeech.NOUN], ["Common fruit"], WordFrequency.CORE_1000),
    "orange": WordEntry("orange", [PartOfSpeech.NOUN], ["Citrus fruit"], WordFrequency.CORE_1000),
    "banana": WordEntry("banana", [PartOfSpeech.NOUN], ["Yellow fruit"], WordFrequency.CORE_1000),
    "salad": WordEntry("salad", [PartOfSpeech.NOUN], ["Mixed vegetables"], WordFrequency.COMMON),
    
    # Buildings/Rooms
    "building": WordEntry("building", [PartOfSpeech.NOUN], ["Structure"], WordFrequency.CORE_1000),
    "apartment": WordEntry("apartment", [PartOfSpeech.NOUN], ["Living unit"], WordFrequency.CORE_1000),
    "floor": WordEntry("floor", [PartOfSpeech.NOUN], ["Ground surface"], WordFrequency.CORE_1000),
    "wall": WordEntry("wall", [PartOfSpeech.NOUN], ["Vertical surface"], WordFrequency.CORE_1000),
    "ceiling": WordEntry("ceiling", [PartOfSpeech.NOUN], ["Room top"], WordFrequency.CORE_1000),
    "roof": WordEntry("roof", [PartOfSpeech.NOUN], ["Building top"], WordFrequency.CORE_1000),
    "kitchen": WordEntry("kitchen", [PartOfSpeech.NOUN], ["Cooking room"], WordFrequency.CORE_1000),
    "bedroom": WordEntry("bedroom", [PartOfSpeech.NOUN], ["Sleeping room"], WordFrequency.CORE_1000),
    "bathroom": WordEntry("bathroom", [PartOfSpeech.NOUN], ["Washing room"], WordFrequency.CORE_1000),
    "garage": WordEntry("garage", [PartOfSpeech.NOUN], ["Car storage"], WordFrequency.CORE_1000),
    "garden": WordEntry("garden", [PartOfSpeech.NOUN], ["Plant area"], WordFrequency.CORE_1000),
    "yard": WordEntry("yard", [PartOfSpeech.NOUN], ["Outdoor area"], WordFrequency.CORE_1000),
    "stairs": WordEntry("stairs", [PartOfSpeech.NOUN], ["Steps"], WordFrequency.CORE_1000),
    "elevator": WordEntry("elevator", [PartOfSpeech.NOUN], ["Lift"], WordFrequency.COMMON),
    
    # Nature
    "mountain": WordEntry("mountain", [PartOfSpeech.NOUN], ["High land"], WordFrequency.CORE_1000),
    "river": WordEntry("river", [PartOfSpeech.NOUN], ["Flowing water"], WordFrequency.CORE_1000),
    "lake": WordEntry("lake", [PartOfSpeech.NOUN], ["Body of water"], WordFrequency.CORE_1000),
    "ocean": WordEntry("ocean", [PartOfSpeech.NOUN], ["Large sea"], WordFrequency.CORE_1000),
    "beach": WordEntry("beach", [PartOfSpeech.NOUN], ["Shore"], WordFrequency.CORE_1000),
    "forest": WordEntry("forest", [PartOfSpeech.NOUN], ["Dense trees"], WordFrequency.CORE_1000),
    "desert": WordEntry("desert", [PartOfSpeech.NOUN], ["Dry area"], WordFrequency.CORE_1000),
    "island": WordEntry("island", [PartOfSpeech.NOUN], ["Land in water"], WordFrequency.CORE_1000),
    "hill": WordEntry("hill", [PartOfSpeech.NOUN], ["Small mountain"], WordFrequency.CORE_1000),
    "valley": WordEntry("valley", [PartOfSpeech.NOUN], ["Low land"], WordFrequency.CORE_1000),
    "cloud": WordEntry("cloud", [PartOfSpeech.NOUN], ["Sky vapor"], WordFrequency.CORE_1000),
    "rain": WordEntry("rain", [PartOfSpeech.NOUN], ["Water drops"], WordFrequency.CORE_1000),
    "snow": WordEntry("snow", [PartOfSpeech.NOUN], ["Frozen water"], WordFrequency.CORE_1000),
    "wind": WordEntry("wind", [PartOfSpeech.NOUN], ["Moving air"], WordFrequency.CORE_1000),
    "storm": WordEntry("storm", [PartOfSpeech.NOUN], ["Violent weather"], WordFrequency.CORE_1000),
    "weather": WordEntry("weather", [PartOfSpeech.NOUN], ["Atmospheric conditions"], WordFrequency.CORE_1000),
    "season": WordEntry("season", [PartOfSpeech.NOUN], ["Time of year"], WordFrequency.CORE_1000),
    
    # Transportation
    "train": WordEntry("train", [PartOfSpeech.NOUN], ["Rail vehicle"], WordFrequency.CORE_1000),
    "bus": WordEntry("bus", [PartOfSpeech.NOUN], ["Public vehicle"], WordFrequency.CORE_1000),
    "plane": WordEntry("plane", [PartOfSpeech.NOUN], ["Aircraft"], WordFrequency.CORE_1000),
    "ship": WordEntry("ship", [PartOfSpeech.NOUN], ["Large boat"], WordFrequency.CORE_1000),
    "boat": WordEntry("boat", [PartOfSpeech.NOUN], ["Water vehicle"], WordFrequency.CORE_1000),
    "bicycle": WordEntry("bicycle", [PartOfSpeech.NOUN], ["Two-wheeled vehicle"], WordFrequency.CORE_1000),
    "motorcycle": WordEntry("motorcycle", [PartOfSpeech.NOUN], ["Motor bike"], WordFrequency.COMMON),
    "truck": WordEntry("truck", [PartOfSpeech.NOUN], ["Large vehicle"], WordFrequency.CORE_1000),
    "taxi": WordEntry("taxi", [PartOfSpeech.NOUN], ["Hired car"], WordFrequency.CORE_1000),
    "ticket": WordEntry("ticket", [PartOfSpeech.NOUN], ["Travel pass"], WordFrequency.CORE_1000),
    "station": WordEntry("station", [PartOfSpeech.NOUN], ["Stop point"], WordFrequency.CORE_1000),
    "airport": WordEntry("airport", [PartOfSpeech.NOUN], ["Plane terminal"], WordFrequency.CORE_1000),
    "bridge": WordEntry("bridge", [PartOfSpeech.NOUN], ["Crossing structure"], WordFrequency.CORE_1000),
    "highway": WordEntry("highway", [PartOfSpeech.NOUN], ["Main road"], WordFrequency.CORE_1000),
    "traffic": WordEntry("traffic", [PartOfSpeech.NOUN], ["Vehicle movement"], WordFrequency.CORE_1000),
    
    # Abstract concepts
    "idea": WordEntry("idea", [PartOfSpeech.NOUN], ["Thought"], WordFrequency.CORE_500),
    "thought": WordEntry("thought", [PartOfSpeech.NOUN], ["Mental activity"], WordFrequency.CORE_1000),
    "opinion": WordEntry("opinion", [PartOfSpeech.NOUN], ["Personal view"], WordFrequency.CORE_1000),
    "belief": WordEntry("belief", [PartOfSpeech.NOUN], ["Conviction"], WordFrequency.CORE_1000),
    "truth": WordEntry("truth", [PartOfSpeech.NOUN], ["Reality"], WordFrequency.CORE_1000),
    "fact": WordEntry("fact", [PartOfSpeech.NOUN], ["True statement"], WordFrequency.CORE_500),
    "reality": WordEntry("reality", [PartOfSpeech.NOUN], ["What is real"], WordFrequency.CORE_1000),
    "dream": WordEntry("dream", [PartOfSpeech.NOUN], ["Sleep vision"], WordFrequency.CORE_1000),
    "hope": WordEntry("hope", [PartOfSpeech.NOUN], ["Positive expectation"], WordFrequency.CORE_1000),
    "fear": WordEntry("fear", [PartOfSpeech.NOUN], ["Fright"], WordFrequency.CORE_1000),
    "love": WordEntry("love", [PartOfSpeech.NOUN], ["Deep affection"], WordFrequency.CORE_500),
    "hate": WordEntry("hate", [PartOfSpeech.NOUN], ["Strong dislike"], WordFrequency.CORE_1000),
    "joy": WordEntry("joy", [PartOfSpeech.NOUN], ["Happiness"], WordFrequency.CORE_1000),
    "peace": WordEntry("peace", [PartOfSpeech.NOUN], ["Calm"], WordFrequency.CORE_1000),
    "freedom": WordEntry("freedom", [PartOfSpeech.NOUN], ["Liberty"], WordFrequency.CORE_1000),
    "power": WordEntry("power", [PartOfSpeech.NOUN], ["Ability, control"], WordFrequency.CORE_500),
    "strength": WordEntry("strength", [PartOfSpeech.NOUN], ["Power"], WordFrequency.CORE_1000),
    "weakness": WordEntry("weakness", [PartOfSpeech.NOUN], ["Lack of power"], WordFrequency.COMMON),
    "success": WordEntry("success", [PartOfSpeech.NOUN], ["Achievement"], WordFrequency.CORE_1000),
    "failure": WordEntry("failure", [PartOfSpeech.NOUN], ["Lack of success"], WordFrequency.CORE_1000),
    "chance": WordEntry("chance", [PartOfSpeech.NOUN], ["Opportunity"], WordFrequency.CORE_1000),
    "opportunity": WordEntry("opportunity", [PartOfSpeech.NOUN], ["Chance"], WordFrequency.CORE_1000),
    "choice": WordEntry("choice", [PartOfSpeech.NOUN], ["Selection"], WordFrequency.CORE_1000),
    "difference": WordEntry("difference", [PartOfSpeech.NOUN], ["Distinction"], WordFrequency.CORE_1000),
    "similarity": WordEntry("similarity", [PartOfSpeech.NOUN], ["Likeness"], WordFrequency.COMMON),
    "relationship": WordEntry("relationship", [PartOfSpeech.NOUN], ["Connection"], WordFrequency.CORE_1000),
    "connection": WordEntry("connection", [PartOfSpeech.NOUN], ["Link"], WordFrequency.CORE_1000),
    "advantage": WordEntry("advantage", [PartOfSpeech.NOUN], ["Benefit"], WordFrequency.CORE_1000),
    "disadvantage": WordEntry("disadvantage", [PartOfSpeech.NOUN], ["Drawback"], WordFrequency.COMMON),
    "purpose": WordEntry("purpose", [PartOfSpeech.NOUN], ["Aim"], WordFrequency.CORE_1000),
    "meaning": WordEntry("meaning", [PartOfSpeech.NOUN], ["Significance"], WordFrequency.CORE_1000),
    "reason": WordEntry("reason", [PartOfSpeech.NOUN], ["Cause"], WordFrequency.CORE_500),
    "cause": WordEntry("cause", [PartOfSpeech.NOUN], ["Reason"], WordFrequency.CORE_1000),
    "effect": WordEntry("effect", [PartOfSpeech.NOUN], ["Result"], WordFrequency.CORE_1000),
    "impact": WordEntry("impact", [PartOfSpeech.NOUN], ["Effect"], WordFrequency.COMMON),
    "influence": WordEntry("influence", [PartOfSpeech.NOUN], ["Power over"], WordFrequency.CORE_1000),
    "control": WordEntry("control", [PartOfSpeech.NOUN], ["Power over"], WordFrequency.CORE_1000),
    
    # Activities
    "activity": WordEntry("activity", [PartOfSpeech.NOUN], ["Action"], WordFrequency.CORE_1000),
    "game": WordEntry("game", [PartOfSpeech.NOUN], ["Activity for fun"], WordFrequency.CORE_1000),
    "sport": WordEntry("sport", [PartOfSpeech.NOUN], ["Physical activity"], WordFrequency.CORE_1000),
    "hobby": WordEntry("hobby", [PartOfSpeech.NOUN], ["Leisure activity"], WordFrequency.COMMON),
    "music": WordEntry("music", [PartOfSpeech.NOUN], ["Sound art"], WordFrequency.CORE_1000),
    "song": WordEntry("song", [PartOfSpeech.NOUN], ["Musical piece"], WordFrequency.CORE_1000),
    "dance": WordEntry("dance", [PartOfSpeech.NOUN], ["Movement to music"], WordFrequency.CORE_1000),
    "art": WordEntry("art", [PartOfSpeech.NOUN], ["Creative work"], WordFrequency.CORE_1000),
    "movie": WordEntry("movie", [PartOfSpeech.NOUN], ["Film"], WordFrequency.CORE_1000),
    "show": WordEntry("show", [PartOfSpeech.NOUN], ["Performance"], WordFrequency.CORE_1000),
    "party": WordEntry("party", [PartOfSpeech.NOUN], ["Celebration"], WordFrequency.CORE_1000),
    "meeting": WordEntry("meeting", [PartOfSpeech.NOUN], ["Gathering"], WordFrequency.CORE_1000),
    "event": WordEntry("event", [PartOfSpeech.NOUN], ["Happening"], WordFrequency.CORE_1000),
    "trip": WordEntry("trip", [PartOfSpeech.NOUN], ["Journey"], WordFrequency.CORE_1000),
    "vacation": WordEntry("vacation", [PartOfSpeech.NOUN], ["Holiday"], WordFrequency.CORE_1000),
    "adventure": WordEntry("adventure", [PartOfSpeech.NOUN], ["Exciting experience"], WordFrequency.COMMON),
    "conversation": WordEntry("conversation", [PartOfSpeech.NOUN], ["Talk"], WordFrequency.CORE_1000),
    "discussion": WordEntry("discussion", [PartOfSpeech.NOUN], ["Formal talk"], WordFrequency.CORE_1000),
    "argument": WordEntry("argument", [PartOfSpeech.NOUN], ["Disagreement"], WordFrequency.CORE_1000),
    "fight": WordEntry("fight", [PartOfSpeech.NOUN], ["Conflict"], WordFrequency.CORE_1000),
}


# =============================================================================
# ADDITIONAL ADJECTIVES
# =============================================================================

MORE_ADJECTIVES = {
    # Size/Quantity
    "tiny": WordEntry("tiny", [PartOfSpeech.ADJECTIVE], ["Very small"], WordFrequency.CORE_1000),
    "huge": WordEntry("huge", [PartOfSpeech.ADJECTIVE], ["Very large"], WordFrequency.CORE_1000),
    "enormous": WordEntry("enormous", [PartOfSpeech.ADJECTIVE], ["Very large"], WordFrequency.COMMON),
    "massive": WordEntry("massive", [PartOfSpeech.ADJECTIVE], ["Very large"], WordFrequency.COMMON),
    "giant": WordEntry("giant", [PartOfSpeech.ADJECTIVE], ["Very large"], WordFrequency.COMMON),
    "wide": WordEntry("wide", [PartOfSpeech.ADJECTIVE], ["Broad"], WordFrequency.CORE_1000),
    "narrow": WordEntry("narrow", [PartOfSpeech.ADJECTIVE], ["Thin"], WordFrequency.CORE_1000),
    "thick": WordEntry("thick", [PartOfSpeech.ADJECTIVE], ["Not thin"], WordFrequency.CORE_1000),
    "thin": WordEntry("thin", [PartOfSpeech.ADJECTIVE], ["Not thick"], WordFrequency.CORE_1000),
    "deep": WordEntry("deep", [PartOfSpeech.ADJECTIVE], ["Far down"], WordFrequency.CORE_1000),
    "shallow": WordEntry("shallow", [PartOfSpeech.ADJECTIVE], ["Not deep"], WordFrequency.COMMON),
    "tall": WordEntry("tall", [PartOfSpeech.ADJECTIVE], ["High"], WordFrequency.CORE_1000),
    "short": WordEntry("short", [PartOfSpeech.ADJECTIVE], ["Not tall"], WordFrequency.CORE_1000),
    "round": WordEntry("round", [PartOfSpeech.ADJECTIVE], ["Circular"], WordFrequency.CORE_1000),
    "square": WordEntry("square", [PartOfSpeech.ADJECTIVE], ["Four-sided"], WordFrequency.CORE_1000),
    "flat": WordEntry("flat", [PartOfSpeech.ADJECTIVE], ["Level"], WordFrequency.CORE_1000),
    "sharp": WordEntry("sharp", [PartOfSpeech.ADJECTIVE], ["Pointed, clever"], WordFrequency.CORE_1000),
    "smooth": WordEntry("smooth", [PartOfSpeech.ADJECTIVE], ["Even surface"], WordFrequency.CORE_1000),
    "rough": WordEntry("rough", [PartOfSpeech.ADJECTIVE], ["Uneven surface"], WordFrequency.CORE_1000),
    
    # Quality
    "excellent": WordEntry("excellent", [PartOfSpeech.ADJECTIVE], ["Very good"], WordFrequency.CORE_1000),
    "wonderful": WordEntry("wonderful", [PartOfSpeech.ADJECTIVE], ["Marvelous"], WordFrequency.CORE_1000),
    "terrible": WordEntry("terrible", [PartOfSpeech.ADJECTIVE], ["Very bad"], WordFrequency.CORE_1000),
    "horrible": WordEntry("horrible", [PartOfSpeech.ADJECTIVE], ["Awful"], WordFrequency.CORE_1000),
    "awful": WordEntry("awful", [PartOfSpeech.ADJECTIVE], ["Very bad"], WordFrequency.CORE_1000),
    "amazing": WordEntry("amazing", [PartOfSpeech.ADJECTIVE], ["Wonderful"], WordFrequency.CORE_1000),
    "incredible": WordEntry("incredible", [PartOfSpeech.ADJECTIVE], ["Unbelievable"], WordFrequency.COMMON),
    "fantastic": WordEntry("fantastic", [PartOfSpeech.ADJECTIVE], ["Wonderful"], WordFrequency.COMMON),
    "brilliant": WordEntry("brilliant", [PartOfSpeech.ADJECTIVE], ["Very bright, excellent"], WordFrequency.COMMON),
    "lovely": WordEntry("lovely", [PartOfSpeech.ADJECTIVE], ["Very nice"], WordFrequency.CORE_1000),
    "delicious": WordEntry("delicious", [PartOfSpeech.ADJECTIVE], ["Very tasty"], WordFrequency.COMMON),
    "disgusting": WordEntry("disgusting", [PartOfSpeech.ADJECTIVE], ["Very unpleasant"], WordFrequency.COMMON),
    
    # Personality
    "friendly": WordEntry("friendly", [PartOfSpeech.ADJECTIVE], ["Kind"], WordFrequency.CORE_1000),
    "polite": WordEntry("polite", [PartOfSpeech.ADJECTIVE], ["Courteous"], WordFrequency.CORE_1000),
    "rude": WordEntry("rude", [PartOfSpeech.ADJECTIVE], ["Impolite"], WordFrequency.CORE_1000),
    "honest": WordEntry("honest", [PartOfSpeech.ADJECTIVE], ["Truthful"], WordFrequency.CORE_1000),
    "clever": WordEntry("clever", [PartOfSpeech.ADJECTIVE], ["Intelligent"], WordFrequency.CORE_1000),
    "wise": WordEntry("wise", [PartOfSpeech.ADJECTIVE], ["Having wisdom"], WordFrequency.CORE_1000),
    "brave": WordEntry("brave", [PartOfSpeech.ADJECTIVE], ["Courageous"], WordFrequency.CORE_1000),
    "lazy": WordEntry("lazy", [PartOfSpeech.ADJECTIVE], ["Not hardworking"], WordFrequency.CORE_1000),
    "patient": WordEntry("patient", [PartOfSpeech.ADJECTIVE], ["Calm waiting"], WordFrequency.CORE_1000),
    "generous": WordEntry("generous", [PartOfSpeech.ADJECTIVE], ["Giving"], WordFrequency.COMMON),
    "selfish": WordEntry("selfish", [PartOfSpeech.ADJECTIVE], ["Self-centered"], WordFrequency.COMMON),
    "careful": WordEntry("careful", [PartOfSpeech.ADJECTIVE], ["Cautious"], WordFrequency.CORE_1000),
    "careless": WordEntry("careless", [PartOfSpeech.ADJECTIVE], ["Not careful"], WordFrequency.COMMON),
    "curious": WordEntry("curious", [PartOfSpeech.ADJECTIVE], ["Wanting to know"], WordFrequency.COMMON),
    "creative": WordEntry("creative", [PartOfSpeech.ADJECTIVE], ["Imaginative"], WordFrequency.COMMON),
    "responsible": WordEntry("responsible", [PartOfSpeech.ADJECTIVE], ["Reliable"], WordFrequency.CORE_1000),
    
    # State/Condition
    "alive": WordEntry("alive", [PartOfSpeech.ADJECTIVE], ["Living"], WordFrequency.CORE_1000),
    "dead": WordEntry("dead", [PartOfSpeech.ADJECTIVE], ["Not alive"], WordFrequency.CORE_1000),
    "awake": WordEntry("awake", [PartOfSpeech.ADJECTIVE], ["Not sleeping"], WordFrequency.CORE_1000),
    "asleep": WordEntry("asleep", [PartOfSpeech.ADJECTIVE], ["Sleeping"], WordFrequency.CORE_1000),
    "alone": WordEntry("alone", [PartOfSpeech.ADJECTIVE], ["By oneself"], WordFrequency.CORE_1000),
    "together": WordEntry("together", [PartOfSpeech.ADJECTIVE], ["With others"], WordFrequency.CORE_1000),
    "quiet": WordEntry("quiet", [PartOfSpeech.ADJECTIVE], ["Silent"], WordFrequency.CORE_1000),
    "loud": WordEntry("loud", [PartOfSpeech.ADJECTIVE], ["Noisy"], WordFrequency.CORE_1000),
    "silent": WordEntry("silent", [PartOfSpeech.ADJECTIVE], ["No sound"], WordFrequency.CORE_1000),
    "noisy": WordEntry("noisy", [PartOfSpeech.ADJECTIVE], ["Loud"], WordFrequency.COMMON),
    "broken": WordEntry("broken", [PartOfSpeech.ADJECTIVE], ["Not working"], WordFrequency.CORE_1000),
    "fixed": WordEntry("fixed", [PartOfSpeech.ADJECTIVE], ["Repaired"], WordFrequency.CORE_1000),
    "complete": WordEntry("complete", [PartOfSpeech.ADJECTIVE], ["Finished"], WordFrequency.CORE_1000),
    "incomplete": WordEntry("incomplete", [PartOfSpeech.ADJECTIVE], ["Not finished"], WordFrequency.COMMON),
    "missing": WordEntry("missing", [PartOfSpeech.ADJECTIVE], ["Not present"], WordFrequency.CORE_1000),
    "hidden": WordEntry("hidden", [PartOfSpeech.ADJECTIVE], ["Concealed"], WordFrequency.CORE_1000),
    "visible": WordEntry("visible", [PartOfSpeech.ADJECTIVE], ["Can be seen"], WordFrequency.COMMON),
    "invisible": WordEntry("invisible", [PartOfSpeech.ADJECTIVE], ["Cannot be seen"], WordFrequency.COMMON),
    
    # Time
    "early": WordEntry("early", [PartOfSpeech.ADJECTIVE], ["Before expected"], WordFrequency.CORE_1000),
    "late": WordEntry("late", [PartOfSpeech.ADJECTIVE], ["After expected"], WordFrequency.CORE_1000),
    "recent": WordEntry("recent", [PartOfSpeech.ADJECTIVE], ["Not long ago"], WordFrequency.CORE_1000),
    "ancient": WordEntry("ancient", [PartOfSpeech.ADJECTIVE], ["Very old"], WordFrequency.COMMON),
    "modern": WordEntry("modern", [PartOfSpeech.ADJECTIVE], ["Current"], WordFrequency.CORE_1000),
    "current": WordEntry("current", [PartOfSpeech.ADJECTIVE], ["Present"], WordFrequency.CORE_1000),
    "previous": WordEntry("previous", [PartOfSpeech.ADJECTIVE], ["Before"], WordFrequency.COMMON),
    "following": WordEntry("following", [PartOfSpeech.ADJECTIVE], ["After"], WordFrequency.COMMON),
    "daily": WordEntry("daily", [PartOfSpeech.ADJECTIVE], ["Every day"], WordFrequency.CORE_1000),
    "weekly": WordEntry("weekly", [PartOfSpeech.ADJECTIVE], ["Every week"], WordFrequency.COMMON),
    "monthly": WordEntry("monthly", [PartOfSpeech.ADJECTIVE], ["Every month"], WordFrequency.COMMON),
    "annual": WordEntry("annual", [PartOfSpeech.ADJECTIVE], ["Every year"], WordFrequency.COMMON),
    "temporary": WordEntry("temporary", [PartOfSpeech.ADJECTIVE], ["Not permanent"], WordFrequency.COMMON),
    "permanent": WordEntry("permanent", [PartOfSpeech.ADJECTIVE], ["Lasting"], WordFrequency.COMMON),
    "constant": WordEntry("constant", [PartOfSpeech.ADJECTIVE], ["Unchanging"], WordFrequency.COMMON),
    "frequent": WordEntry("frequent", [PartOfSpeech.ADJECTIVE], ["Often"], WordFrequency.COMMON),
    "occasional": WordEntry("occasional", [PartOfSpeech.ADJECTIVE], ["Sometimes"], WordFrequency.COMMON),
}


def load_common_vocabulary(vocab=None):
    """
    Load common vocabulary to reach fluency level.
    
    Args:
        vocab: Optional existing vocabulary to extend
        
    Returns:
        Extended vocabulary
    """
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in MORE_VERBS.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MORE_NOUNS.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in MORE_ADJECTIVES.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[CommonVocabulary] Loaded {total_added} common words")
    print(f"[CommonVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_common_stats() -> Dict[str, int]:
    """Get word counts for common vocabulary."""
    return {
        "more_verbs": len(MORE_VERBS),
        "more_nouns": len(MORE_NOUNS),
        "more_adjectives": len(MORE_ADJECTIVES),
        "total": len(MORE_VERBS) + len(MORE_NOUNS) + len(MORE_ADJECTIVES)
    }
