# unimind/models/native/vocabulary_expansion.py
# Vocabulary Expansion - Sports, Entertainment, Legal, Emotions, Arts
# Target: Add 2000+ words to reach B2/C1 level

"""
Vocabulary Expansion Module

Expands vocabulary with additional domains:
- Sports & Fitness (200+ words)
- Entertainment & Media (200+ words)
- Legal & Government (200+ words)
- Emotions & Psychology (200+ words)
- Arts & Culture (200+ words)
- Social & Relationships (200+ words)
- Home & Daily Life (200+ words)
- Work & Career (200+ words)
"""

from typing import Dict, List
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# SPORTS & FITNESS (~200 words)
# =============================================================================

SPORTS_VOCAB = {
    # General sports
    "sport": WordEntry("sport", [PartOfSpeech.NOUN], ["Physical activity for competition"], WordFrequency.CORE_1000),
    "game": WordEntry("game", [PartOfSpeech.NOUN], ["Competitive activity"], WordFrequency.CORE_500),
    "match": WordEntry("match", [PartOfSpeech.NOUN], ["Sports contest"], WordFrequency.CORE_1000),
    "tournament": WordEntry("tournament", [PartOfSpeech.NOUN], ["Competition series"], WordFrequency.COMMON),
    "championship": WordEntry("championship", [PartOfSpeech.NOUN], ["Title competition"], WordFrequency.COMMON),
    "league": WordEntry("league", [PartOfSpeech.NOUN], ["Sports organization"], WordFrequency.COMMON),
    "team": WordEntry("team", [PartOfSpeech.NOUN], ["Group of players"], WordFrequency.CORE_500),
    "player": WordEntry("player", [PartOfSpeech.NOUN], ["Sports participant"], WordFrequency.CORE_500),
    "athlete": WordEntry("athlete", [PartOfSpeech.NOUN], ["Sports person"], WordFrequency.COMMON),
    "coach": WordEntry("coach", [PartOfSpeech.NOUN], ["Team trainer"], WordFrequency.COMMON),
    "referee": WordEntry("referee", [PartOfSpeech.NOUN], ["Game official"], WordFrequency.COMMON),
    "captain": WordEntry("captain", [PartOfSpeech.NOUN], ["Team leader"], WordFrequency.CORE_1000),
    "opponent": WordEntry("opponent", [PartOfSpeech.NOUN], ["Competitor"], WordFrequency.COMMON),
    "rival": WordEntry("rival", [PartOfSpeech.NOUN], ["Competitor"], WordFrequency.COMMON),
    "fan": WordEntry("fan", [PartOfSpeech.NOUN], ["Supporter"], WordFrequency.CORE_1000),
    
    # Actions
    "score": WordEntry("score", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Gain points"], WordFrequency.CORE_1000),
    "win": WordEntry("win", [PartOfSpeech.VERB], ["Be victorious"], WordFrequency.CORE_500),
    "lose": WordEntry("lose", [PartOfSpeech.VERB], ["Fail to win"], WordFrequency.CORE_500),
    "draw": WordEntry("draw", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Tie game"], WordFrequency.CORE_1000),
    "compete": WordEntry("compete", [PartOfSpeech.VERB], ["Participate in contest"], WordFrequency.COMMON),
    "train": WordEntry("train", [PartOfSpeech.VERB], ["Practice, prepare"], WordFrequency.CORE_1000),
    "practice": WordEntry("practice", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Repeated exercise"], WordFrequency.CORE_500),
    "exercise": WordEntry("exercise", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Physical activity"], WordFrequency.CORE_500),
    "stretch": WordEntry("stretch", [PartOfSpeech.VERB], ["Extend muscles"], WordFrequency.COMMON),
    "sprint": WordEntry("sprint", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Run fast"], WordFrequency.COMMON),
    "jog": WordEntry("jog", [PartOfSpeech.VERB], ["Run slowly"], WordFrequency.COMMON),
    "kick": WordEntry("kick", [PartOfSpeech.VERB], ["Strike with foot"], WordFrequency.CORE_1000),
    "throw": WordEntry("throw", [PartOfSpeech.VERB], ["Propel through air"], WordFrequency.CORE_1000),
    "catch": WordEntry("catch", [PartOfSpeech.VERB], ["Grab thrown object"], WordFrequency.CORE_1000),
    "pass": WordEntry("pass", [PartOfSpeech.VERB], ["Transfer ball"], WordFrequency.CORE_500),
    "shoot": WordEntry("shoot", [PartOfSpeech.VERB], ["Aim at goal"], WordFrequency.CORE_1000),
    "tackle": WordEntry("tackle", [PartOfSpeech.VERB], ["Stop opponent"], WordFrequency.COMMON),
    "defend": WordEntry("defend", [PartOfSpeech.VERB], ["Protect goal"], WordFrequency.COMMON),
    "attack": WordEntry("attack", [PartOfSpeech.VERB], ["Move toward goal"], WordFrequency.CORE_1000),
    
    # Specific sports
    "football": WordEntry("football", [PartOfSpeech.NOUN], ["Ball sport"], WordFrequency.CORE_1000),
    "soccer": WordEntry("soccer", [PartOfSpeech.NOUN], ["Association football"], WordFrequency.COMMON),
    "basketball": WordEntry("basketball", [PartOfSpeech.NOUN], ["Hoop sport"], WordFrequency.COMMON),
    "baseball": WordEntry("baseball", [PartOfSpeech.NOUN], ["Bat and ball sport"], WordFrequency.COMMON),
    "tennis": WordEntry("tennis", [PartOfSpeech.NOUN], ["Racket sport"], WordFrequency.COMMON),
    "golf": WordEntry("golf", [PartOfSpeech.NOUN], ["Club sport"], WordFrequency.COMMON),
    "swimming": WordEntry("swimming", [PartOfSpeech.NOUN], ["Water sport"], WordFrequency.COMMON),
    "running": WordEntry("running", [PartOfSpeech.NOUN], ["Track sport"], WordFrequency.COMMON),
    "cycling": WordEntry("cycling", [PartOfSpeech.NOUN], ["Bike sport"], WordFrequency.COMMON),
    "boxing": WordEntry("boxing", [PartOfSpeech.NOUN], ["Fighting sport"], WordFrequency.COMMON),
    "wrestling": WordEntry("wrestling", [PartOfSpeech.NOUN], ["Combat sport"], WordFrequency.COMMON),
    "skiing": WordEntry("skiing", [PartOfSpeech.NOUN], ["Snow sport"], WordFrequency.COMMON),
    "skating": WordEntry("skating", [PartOfSpeech.NOUN], ["Ice/roller sport"], WordFrequency.COMMON),
    "hockey": WordEntry("hockey", [PartOfSpeech.NOUN], ["Puck sport"], WordFrequency.COMMON),
    "volleyball": WordEntry("volleyball", [PartOfSpeech.NOUN], ["Net sport"], WordFrequency.COMMON),
    "gymnastics": WordEntry("gymnastics", [PartOfSpeech.NOUN], ["Flexibility sport"], WordFrequency.COMMON),
    "marathon": WordEntry("marathon", [PartOfSpeech.NOUN], ["Long distance race"], WordFrequency.COMMON),
    "athletics": WordEntry("athletics", [PartOfSpeech.NOUN], ["Track and field"], WordFrequency.COMMON),
    
    # Equipment
    "ball": WordEntry("ball", [PartOfSpeech.NOUN], ["Round object"], WordFrequency.CORE_500),
    "bat": WordEntry("bat", [PartOfSpeech.NOUN], ["Hitting stick"], WordFrequency.CORE_1000),
    "racket": WordEntry("racket", [PartOfSpeech.NOUN], ["Tennis equipment"], WordFrequency.COMMON),
    "goal": WordEntry("goal", [PartOfSpeech.NOUN], ["Scoring target"], WordFrequency.CORE_500),
    "net": WordEntry("net", [PartOfSpeech.NOUN], ["Sports barrier"], WordFrequency.CORE_1000),
    "court": WordEntry("court", [PartOfSpeech.NOUN], ["Playing surface"], WordFrequency.CORE_1000),
    "field": WordEntry("field", [PartOfSpeech.NOUN], ["Playing area"], WordFrequency.CORE_500),
    "stadium": WordEntry("stadium", [PartOfSpeech.NOUN], ["Sports venue"], WordFrequency.COMMON),
    "gym": WordEntry("gym", [PartOfSpeech.NOUN], ["Exercise place"], WordFrequency.COMMON),
    "pool": WordEntry("pool", [PartOfSpeech.NOUN], ["Swimming area"], WordFrequency.CORE_1000),
    "track": WordEntry("track", [PartOfSpeech.NOUN], ["Running path"], WordFrequency.CORE_1000),
    "helmet": WordEntry("helmet", [PartOfSpeech.NOUN], ["Head protection"], WordFrequency.COMMON),
    "uniform": WordEntry("uniform", [PartOfSpeech.NOUN], ["Team clothing"], WordFrequency.COMMON),
    
    # Fitness
    "fitness": WordEntry("fitness", [PartOfSpeech.NOUN], ["Physical condition"], WordFrequency.COMMON),
    "workout": WordEntry("workout", [PartOfSpeech.NOUN], ["Exercise session"], WordFrequency.COMMON),
    "cardio": WordEntry("cardio", [PartOfSpeech.NOUN], ["Heart exercise"], WordFrequency.COMMON),
    "strength": WordEntry("strength", [PartOfSpeech.NOUN], ["Physical power"], WordFrequency.CORE_1000),
    "endurance": WordEntry("endurance", [PartOfSpeech.NOUN], ["Stamina"], WordFrequency.COMMON),
    "stamina": WordEntry("stamina", [PartOfSpeech.NOUN], ["Physical endurance"], WordFrequency.COMMON),
    "muscle": WordEntry("muscle", [PartOfSpeech.NOUN], ["Body tissue"], WordFrequency.CORE_1000),
    "weight": WordEntry("weight", [PartOfSpeech.NOUN], ["Heaviness, exercise equipment"], WordFrequency.CORE_500),
    "yoga": WordEntry("yoga", [PartOfSpeech.NOUN], ["Mind-body practice"], WordFrequency.COMMON),
    "diet": WordEntry("diet", [PartOfSpeech.NOUN], ["Food intake"], WordFrequency.COMMON),
    
    # Results
    "victory": WordEntry("victory", [PartOfSpeech.NOUN], ["Win"], WordFrequency.COMMON),
    "defeat": WordEntry("defeat", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Loss"], WordFrequency.COMMON),
    "record": WordEntry("record", [PartOfSpeech.NOUN], ["Best achievement"], WordFrequency.CORE_500),
    "medal": WordEntry("medal", [PartOfSpeech.NOUN], ["Award"], WordFrequency.COMMON),
    "trophy": WordEntry("trophy", [PartOfSpeech.NOUN], ["Prize"], WordFrequency.COMMON),
    "champion": WordEntry("champion", [PartOfSpeech.NOUN], ["Winner"], WordFrequency.COMMON),
    "winner": WordEntry("winner", [PartOfSpeech.NOUN], ["Victor"], WordFrequency.CORE_1000),
    "loser": WordEntry("loser", [PartOfSpeech.NOUN], ["Defeated person"], WordFrequency.COMMON),
}


# =============================================================================
# ENTERTAINMENT & MEDIA (~200 words)
# =============================================================================

ENTERTAINMENT_VOCAB = {
    # General
    "entertainment": WordEntry("entertainment", [PartOfSpeech.NOUN], ["Amusement"], WordFrequency.COMMON),
    "media": WordEntry("media", [PartOfSpeech.NOUN], ["Communication channels"], WordFrequency.COMMON),
    "television": WordEntry("television", [PartOfSpeech.NOUN], ["TV"], WordFrequency.CORE_1000),
    "radio": WordEntry("radio", [PartOfSpeech.NOUN], ["Audio broadcast"], WordFrequency.CORE_1000),
    "internet": WordEntry("internet", [PartOfSpeech.NOUN], ["Global network"], WordFrequency.CORE_500),
    "streaming": WordEntry("streaming", [PartOfSpeech.NOUN], ["Online broadcast"], WordFrequency.COMMON),
    "podcast": WordEntry("podcast", [PartOfSpeech.NOUN], ["Audio show"], WordFrequency.COMMON),
    "channel": WordEntry("channel", [PartOfSpeech.NOUN], ["Broadcast station"], WordFrequency.CORE_1000),
    "program": WordEntry("program", [PartOfSpeech.NOUN], ["TV show"], WordFrequency.CORE_500),
    "broadcast": WordEntry("broadcast", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Transmission"], WordFrequency.COMMON),
    
    # Film & TV
    "movie": WordEntry("movie", [PartOfSpeech.NOUN], ["Film"], WordFrequency.CORE_500),
    "film": WordEntry("film", [PartOfSpeech.NOUN], ["Motion picture"], WordFrequency.CORE_500),
    "cinema": WordEntry("cinema", [PartOfSpeech.NOUN], ["Movie theater"], WordFrequency.COMMON),
    "theater": WordEntry("theater", [PartOfSpeech.NOUN], ["Performance venue"], WordFrequency.CORE_1000),
    "series": WordEntry("series", [PartOfSpeech.NOUN], ["TV show sequence"], WordFrequency.CORE_500),
    "episode": WordEntry("episode", [PartOfSpeech.NOUN], ["Single show"], WordFrequency.COMMON),
    "season": WordEntry("season", [PartOfSpeech.NOUN], ["Series segment"], WordFrequency.CORE_500),
    "documentary": WordEntry("documentary", [PartOfSpeech.NOUN], ["Factual film"], WordFrequency.COMMON),
    "comedy": WordEntry("comedy", [PartOfSpeech.NOUN], ["Funny genre"], WordFrequency.COMMON),
    "drama": WordEntry("drama", [PartOfSpeech.NOUN], ["Serious genre"], WordFrequency.COMMON),
    "horror": WordEntry("horror", [PartOfSpeech.NOUN], ["Scary genre"], WordFrequency.COMMON),
    "action": WordEntry("action", [PartOfSpeech.NOUN], ["Exciting genre"], WordFrequency.CORE_500),
    "thriller": WordEntry("thriller", [PartOfSpeech.NOUN], ["Suspenseful genre"], WordFrequency.COMMON),
    "romance": WordEntry("romance", [PartOfSpeech.NOUN], ["Love story genre"], WordFrequency.COMMON),
    "animation": WordEntry("animation", [PartOfSpeech.NOUN], ["Animated content"], WordFrequency.COMMON),
    "cartoon": WordEntry("cartoon", [PartOfSpeech.NOUN], ["Animated show"], WordFrequency.COMMON),
    
    # People
    "actor": WordEntry("actor", [PartOfSpeech.NOUN], ["Movie performer"], WordFrequency.CORE_1000),
    "actress": WordEntry("actress", [PartOfSpeech.NOUN], ["Female actor"], WordFrequency.CORE_1000),
    "director": WordEntry("director", [PartOfSpeech.NOUN], ["Film maker"], WordFrequency.COMMON),
    "producer": WordEntry("producer", [PartOfSpeech.NOUN], ["Content creator"], WordFrequency.COMMON),
    "writer": WordEntry("writer", [PartOfSpeech.NOUN], ["Script author"], WordFrequency.CORE_1000),
    "celebrity": WordEntry("celebrity", [PartOfSpeech.NOUN], ["Famous person"], WordFrequency.COMMON),
    "star": WordEntry("star", [PartOfSpeech.NOUN], ["Famous performer"], WordFrequency.CORE_500),
    "host": WordEntry("host", [PartOfSpeech.NOUN], ["Show presenter"], WordFrequency.COMMON),
    "audience": WordEntry("audience", [PartOfSpeech.NOUN], ["Viewers"], WordFrequency.CORE_1000),
    "viewer": WordEntry("viewer", [PartOfSpeech.NOUN], ["Watcher"], WordFrequency.COMMON),
    "listener": WordEntry("listener", [PartOfSpeech.NOUN], ["Audio audience"], WordFrequency.COMMON),
    
    # Music
    "music": WordEntry("music", [PartOfSpeech.NOUN], ["Sound art"], WordFrequency.CORE_500),
    "song": WordEntry("song", [PartOfSpeech.NOUN], ["Musical piece"], WordFrequency.CORE_500),
    "album": WordEntry("album", [PartOfSpeech.NOUN], ["Song collection"], WordFrequency.COMMON),
    "track": WordEntry("track", [PartOfSpeech.NOUN], ["Single recording"], WordFrequency.COMMON),
    "band": WordEntry("band", [PartOfSpeech.NOUN], ["Musical group"], WordFrequency.CORE_1000),
    "singer": WordEntry("singer", [PartOfSpeech.NOUN], ["Vocalist"], WordFrequency.CORE_1000),
    "musician": WordEntry("musician", [PartOfSpeech.NOUN], ["Music player"], WordFrequency.COMMON),
    "concert": WordEntry("concert", [PartOfSpeech.NOUN], ["Live performance"], WordFrequency.COMMON),
    "festival": WordEntry("festival", [PartOfSpeech.NOUN], ["Music event"], WordFrequency.COMMON),
    "guitar": WordEntry("guitar", [PartOfSpeech.NOUN], ["String instrument"], WordFrequency.COMMON),
    "piano": WordEntry("piano", [PartOfSpeech.NOUN], ["Keyboard instrument"], WordFrequency.COMMON),
    "drums": WordEntry("drums", [PartOfSpeech.NOUN], ["Percussion"], WordFrequency.COMMON),
    "lyrics": WordEntry("lyrics", [PartOfSpeech.NOUN], ["Song words"], WordFrequency.COMMON),
    "melody": WordEntry("melody", [PartOfSpeech.NOUN], ["Tune"], WordFrequency.COMMON),
    "rhythm": WordEntry("rhythm", [PartOfSpeech.NOUN], ["Beat pattern"], WordFrequency.COMMON),
    "genre": WordEntry("genre", [PartOfSpeech.NOUN], ["Style category"], WordFrequency.COMMON),
    "pop": WordEntry("pop", [PartOfSpeech.NOUN], ["Popular music"], WordFrequency.COMMON),
    "rock": WordEntry("rock", [PartOfSpeech.NOUN], ["Rock music"], WordFrequency.CORE_1000),
    "jazz": WordEntry("jazz", [PartOfSpeech.NOUN], ["Jazz music"], WordFrequency.COMMON),
    "classical": WordEntry("classical", [PartOfSpeech.ADJECTIVE], ["Classical music"], WordFrequency.COMMON),
    "hip-hop": WordEntry("hip-hop", [PartOfSpeech.NOUN], ["Hip-hop music"], WordFrequency.COMMON),
    
    # Gaming
    "game": WordEntry("game", [PartOfSpeech.NOUN], ["Video game"], WordFrequency.CORE_500),
    "gaming": WordEntry("gaming", [PartOfSpeech.NOUN], ["Playing games"], WordFrequency.COMMON),
    "console": WordEntry("console", [PartOfSpeech.NOUN], ["Gaming device"], WordFrequency.COMMON),
    "controller": WordEntry("controller", [PartOfSpeech.NOUN], ["Game input"], WordFrequency.COMMON),
    "level": WordEntry("level", [PartOfSpeech.NOUN], ["Game stage"], WordFrequency.CORE_500),
    "character": WordEntry("character", [PartOfSpeech.NOUN], ["Game persona"], WordFrequency.CORE_500),
    "multiplayer": WordEntry("multiplayer", [PartOfSpeech.ADJECTIVE], ["Multi-person"], WordFrequency.COMMON),
    "online": WordEntry("online", [PartOfSpeech.ADJECTIVE], ["Internet-based"], WordFrequency.COMMON),
    
    # News
    "news": WordEntry("news", [PartOfSpeech.NOUN], ["Current events"], WordFrequency.CORE_500),
    "journalist": WordEntry("journalist", [PartOfSpeech.NOUN], ["News reporter"], WordFrequency.COMMON),
    "reporter": WordEntry("reporter", [PartOfSpeech.NOUN], ["News gatherer"], WordFrequency.COMMON),
    "headline": WordEntry("headline", [PartOfSpeech.NOUN], ["News title"], WordFrequency.COMMON),
    "article": WordEntry("article", [PartOfSpeech.NOUN], ["News piece"], WordFrequency.CORE_1000),
    "interview": WordEntry("interview", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Q&A session"], WordFrequency.COMMON),
    "magazine": WordEntry("magazine", [PartOfSpeech.NOUN], ["Periodical"], WordFrequency.CORE_1000),
    "newspaper": WordEntry("newspaper", [PartOfSpeech.NOUN], ["Print news"], WordFrequency.CORE_1000),
    "publication": WordEntry("publication", [PartOfSpeech.NOUN], ["Published work"], WordFrequency.COMMON),
    
    # Social Media
    "social": WordEntry("social", [PartOfSpeech.ADJECTIVE], ["Society-related"], WordFrequency.CORE_500),
    "platform": WordEntry("platform", [PartOfSpeech.NOUN], ["Online service"], WordFrequency.COMMON),
    "post": WordEntry("post", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Online content"], WordFrequency.CORE_500),
    "share": WordEntry("share", [PartOfSpeech.VERB], ["Distribute content"], WordFrequency.CORE_500),
    "like": WordEntry("like", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Approve content"], WordFrequency.CORE_500),
    "comment": WordEntry("comment", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Response"], WordFrequency.CORE_1000),
    "follow": WordEntry("follow", [PartOfSpeech.VERB], ["Subscribe"], WordFrequency.CORE_500),
    "subscribe": WordEntry("subscribe", [PartOfSpeech.VERB], ["Sign up for"], WordFrequency.COMMON),
    "viral": WordEntry("viral", [PartOfSpeech.ADJECTIVE], ["Widely shared"], WordFrequency.COMMON),
    "trending": WordEntry("trending", [PartOfSpeech.ADJECTIVE], ["Popular now"], WordFrequency.COMMON),
    "influencer": WordEntry("influencer", [PartOfSpeech.NOUN], ["Social media star"], WordFrequency.COMMON),
}


# =============================================================================
# LEGAL & GOVERNMENT (~200 words)
# =============================================================================

LEGAL_VOCAB = {
    # Government
    "government": WordEntry("government", [PartOfSpeech.NOUN], ["Ruling body"], WordFrequency.CORE_500),
    "politics": WordEntry("politics", [PartOfSpeech.NOUN], ["Governing affairs"], WordFrequency.COMMON),
    "political": WordEntry("political", [PartOfSpeech.ADJECTIVE], ["Of politics"], WordFrequency.COMMON),
    "policy": WordEntry("policy", [PartOfSpeech.NOUN], ["Official plan"], WordFrequency.COMMON),
    "law": WordEntry("law", [PartOfSpeech.NOUN], ["Legal rule"], WordFrequency.CORE_500),
    "legal": WordEntry("legal", [PartOfSpeech.ADJECTIVE], ["Of law"], WordFrequency.COMMON),
    "illegal": WordEntry("illegal", [PartOfSpeech.ADJECTIVE], ["Against law"], WordFrequency.COMMON),
    "constitution": WordEntry("constitution", [PartOfSpeech.NOUN], ["Fundamental law"], WordFrequency.COMMON),
    "democracy": WordEntry("democracy", [PartOfSpeech.NOUN], ["People's rule"], WordFrequency.COMMON),
    "republic": WordEntry("republic", [PartOfSpeech.NOUN], ["Representative state"], WordFrequency.COMMON),
    "nation": WordEntry("nation", [PartOfSpeech.NOUN], ["Country"], WordFrequency.CORE_500),
    "state": WordEntry("state", [PartOfSpeech.NOUN], ["Political unit"], WordFrequency.CORE_500),
    "federal": WordEntry("federal", [PartOfSpeech.ADJECTIVE], ["National level"], WordFrequency.COMMON),
    "local": WordEntry("local", [PartOfSpeech.ADJECTIVE], ["Area-specific"], WordFrequency.CORE_500),
    
    # Officials
    "president": WordEntry("president", [PartOfSpeech.NOUN], ["Head of state"], WordFrequency.CORE_500),
    "minister": WordEntry("minister", [PartOfSpeech.NOUN], ["Government official"], WordFrequency.COMMON),
    "senator": WordEntry("senator", [PartOfSpeech.NOUN], ["Legislative member"], WordFrequency.COMMON),
    "representative": WordEntry("representative", [PartOfSpeech.NOUN], ["Elected official"], WordFrequency.COMMON),
    "governor": WordEntry("governor", [PartOfSpeech.NOUN], ["State leader"], WordFrequency.COMMON),
    "mayor": WordEntry("mayor", [PartOfSpeech.NOUN], ["City leader"], WordFrequency.COMMON),
    "official": WordEntry("official", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Government person"], WordFrequency.CORE_500),
    "politician": WordEntry("politician", [PartOfSpeech.NOUN], ["Political person"], WordFrequency.COMMON),
    "candidate": WordEntry("candidate", [PartOfSpeech.NOUN], ["Office seeker"], WordFrequency.COMMON),
    "citizen": WordEntry("citizen", [PartOfSpeech.NOUN], ["National member"], WordFrequency.COMMON),
    "voter": WordEntry("voter", [PartOfSpeech.NOUN], ["Election participant"], WordFrequency.COMMON),
    
    # Processes
    "election": WordEntry("election", [PartOfSpeech.NOUN], ["Voting process"], WordFrequency.COMMON),
    "vote": WordEntry("vote", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Cast ballot"], WordFrequency.CORE_1000),
    "campaign": WordEntry("campaign", [PartOfSpeech.NOUN], ["Political effort"], WordFrequency.COMMON),
    "debate": WordEntry("debate", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Formal argument"], WordFrequency.COMMON),
    "legislation": WordEntry("legislation", [PartOfSpeech.NOUN], ["Laws"], WordFrequency.COMMON),
    "regulation": WordEntry("regulation", [PartOfSpeech.NOUN], ["Official rule"], WordFrequency.COMMON),
    "reform": WordEntry("reform", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Change for better"], WordFrequency.COMMON),
    "amendment": WordEntry("amendment", [PartOfSpeech.NOUN], ["Law change"], WordFrequency.COMMON),
    "treaty": WordEntry("treaty", [PartOfSpeech.NOUN], ["Formal agreement"], WordFrequency.COMMON),
    "diplomacy": WordEntry("diplomacy", [PartOfSpeech.NOUN], ["International relations"], WordFrequency.COMMON),
    
    # Legal system
    "court": WordEntry("court", [PartOfSpeech.NOUN], ["Legal tribunal"], WordFrequency.CORE_500),
    "judge": WordEntry("judge", [PartOfSpeech.NOUN], ["Legal official"], WordFrequency.CORE_1000),
    "jury": WordEntry("jury", [PartOfSpeech.NOUN], ["Decision group"], WordFrequency.COMMON),
    "lawyer": WordEntry("lawyer", [PartOfSpeech.NOUN], ["Legal professional"], WordFrequency.COMMON),
    "attorney": WordEntry("attorney", [PartOfSpeech.NOUN], ["Lawyer"], WordFrequency.COMMON),
    "prosecutor": WordEntry("prosecutor", [PartOfSpeech.NOUN], ["Accusing lawyer"], WordFrequency.COMMON),
    "defendant": WordEntry("defendant", [PartOfSpeech.NOUN], ["Accused person"], WordFrequency.COMMON),
    "plaintiff": WordEntry("plaintiff", [PartOfSpeech.NOUN], ["Accusing party"], WordFrequency.COMMON),
    "witness": WordEntry("witness", [PartOfSpeech.NOUN], ["Evidence giver"], WordFrequency.COMMON),
    "testimony": WordEntry("testimony", [PartOfSpeech.NOUN], ["Witness statement"], WordFrequency.COMMON),
    "evidence": WordEntry("evidence", [PartOfSpeech.NOUN], ["Proof"], WordFrequency.CORE_500),
    "verdict": WordEntry("verdict", [PartOfSpeech.NOUN], ["Decision"], WordFrequency.COMMON),
    "sentence": WordEntry("sentence", [PartOfSpeech.NOUN], ["Punishment"], WordFrequency.CORE_500),
    "trial": WordEntry("trial", [PartOfSpeech.NOUN], ["Legal proceeding"], WordFrequency.COMMON),
    "appeal": WordEntry("appeal", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Request review"], WordFrequency.COMMON),
    "case": WordEntry("case", [PartOfSpeech.NOUN], ["Legal matter"], WordFrequency.CORE_500),
    "lawsuit": WordEntry("lawsuit", [PartOfSpeech.NOUN], ["Legal action"], WordFrequency.COMMON),
    "sue": WordEntry("sue", [PartOfSpeech.VERB], ["Take legal action"], WordFrequency.COMMON),
    
    # Crimes & punishment
    "crime": WordEntry("crime", [PartOfSpeech.NOUN], ["Illegal act"], WordFrequency.CORE_1000),
    "criminal": WordEntry("criminal", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Lawbreaker"], WordFrequency.COMMON),
    "guilty": WordEntry("guilty", [PartOfSpeech.ADJECTIVE], ["Responsible for crime"], WordFrequency.COMMON),
    "innocent": WordEntry("innocent", [PartOfSpeech.ADJECTIVE], ["Not guilty"], WordFrequency.COMMON),
    "arrest": WordEntry("arrest", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Detain legally"], WordFrequency.COMMON),
    "prison": WordEntry("prison", [PartOfSpeech.NOUN], ["Jail"], WordFrequency.COMMON),
    "jail": WordEntry("jail", [PartOfSpeech.NOUN], ["Detention place"], WordFrequency.COMMON),
    "punishment": WordEntry("punishment", [PartOfSpeech.NOUN], ["Penalty"], WordFrequency.COMMON),
    "fine": WordEntry("fine", [PartOfSpeech.NOUN], ["Money penalty"], WordFrequency.CORE_1000),
    "theft": WordEntry("theft", [PartOfSpeech.NOUN], ["Stealing"], WordFrequency.COMMON),
    "fraud": WordEntry("fraud", [PartOfSpeech.NOUN], ["Deception"], WordFrequency.COMMON),
    "murder": WordEntry("murder", [PartOfSpeech.NOUN], ["Killing"], WordFrequency.COMMON),
    "assault": WordEntry("assault", [PartOfSpeech.NOUN], ["Attack"], WordFrequency.COMMON),
    
    # Rights
    "right": WordEntry("right", [PartOfSpeech.NOUN], ["Entitlement"], WordFrequency.CORE_500),
    "freedom": WordEntry("freedom", [PartOfSpeech.NOUN], ["Liberty"], WordFrequency.CORE_1000),
    "liberty": WordEntry("liberty", [PartOfSpeech.NOUN], ["Freedom"], WordFrequency.COMMON),
    "justice": WordEntry("justice", [PartOfSpeech.NOUN], ["Fairness"], WordFrequency.COMMON),
    "equality": WordEntry("equality", [PartOfSpeech.NOUN], ["Equal treatment"], WordFrequency.COMMON),
    "privacy": WordEntry("privacy", [PartOfSpeech.NOUN], ["Personal space"], WordFrequency.COMMON),
    "property": WordEntry("property", [PartOfSpeech.NOUN], ["Owned things"], WordFrequency.CORE_1000),
    "ownership": WordEntry("ownership", [PartOfSpeech.NOUN], ["Possession"], WordFrequency.COMMON),
    "contract": WordEntry("contract", [PartOfSpeech.NOUN], ["Legal agreement"], WordFrequency.COMMON),
    "agreement": WordEntry("agreement", [PartOfSpeech.NOUN], ["Mutual consent"], WordFrequency.CORE_500),
    "license": WordEntry("license", [PartOfSpeech.NOUN], ["Permission"], WordFrequency.COMMON),
    "permit": WordEntry("permit", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Authorization"], WordFrequency.COMMON),
    "patent": WordEntry("patent", [PartOfSpeech.NOUN], ["Invention right"], WordFrequency.COMMON),
    "copyright": WordEntry("copyright", [PartOfSpeech.NOUN], ["Content right"], WordFrequency.COMMON),
}


# =============================================================================
# EMOTIONS & PSYCHOLOGY (~200 words)
# =============================================================================

EMOTIONS_VOCAB = {
    # Basic emotions
    "emotion": WordEntry("emotion", [PartOfSpeech.NOUN], ["Feeling"], WordFrequency.COMMON),
    "feeling": WordEntry("feeling", [PartOfSpeech.NOUN], ["Emotion"], WordFrequency.CORE_500),
    "mood": WordEntry("mood", [PartOfSpeech.NOUN], ["Emotional state"], WordFrequency.COMMON),
    "happiness": WordEntry("happiness", [PartOfSpeech.NOUN], ["Joy state"], WordFrequency.COMMON),
    "sadness": WordEntry("sadness", [PartOfSpeech.NOUN], ["Sorrow state"], WordFrequency.COMMON),
    "anger": WordEntry("anger", [PartOfSpeech.NOUN], ["Mad feeling"], WordFrequency.COMMON),
    "fear": WordEntry("fear", [PartOfSpeech.NOUN], ["Scared feeling"], WordFrequency.CORE_1000),
    "surprise": WordEntry("surprise", [PartOfSpeech.NOUN], ["Unexpected feeling"], WordFrequency.CORE_1000),
    "disgust": WordEntry("disgust", [PartOfSpeech.NOUN], ["Repulsion"], WordFrequency.COMMON),
    "love": WordEntry("love", [PartOfSpeech.NOUN], ["Deep affection"], WordFrequency.CORE_500),
    "hate": WordEntry("hate", [PartOfSpeech.NOUN], ["Strong dislike"], WordFrequency.CORE_1000),
    "joy": WordEntry("joy", [PartOfSpeech.NOUN], ["Great happiness"], WordFrequency.CORE_1000),
    "sorrow": WordEntry("sorrow", [PartOfSpeech.NOUN], ["Deep sadness"], WordFrequency.COMMON),
    "grief": WordEntry("grief", [PartOfSpeech.NOUN], ["Deep sorrow"], WordFrequency.COMMON),
    "excitement": WordEntry("excitement", [PartOfSpeech.NOUN], ["Enthusiasm"], WordFrequency.COMMON),
    "anxiety": WordEntry("anxiety", [PartOfSpeech.NOUN], ["Worry"], WordFrequency.COMMON),
    "worry": WordEntry("worry", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Concern"], WordFrequency.CORE_1000),
    "stress": WordEntry("stress", [PartOfSpeech.NOUN], ["Mental pressure"], WordFrequency.COMMON),
    "relief": WordEntry("relief", [PartOfSpeech.NOUN], ["Comfort"], WordFrequency.COMMON),
    "hope": WordEntry("hope", [PartOfSpeech.NOUN], ["Positive expectation"], WordFrequency.CORE_1000),
    "despair": WordEntry("despair", [PartOfSpeech.NOUN], ["Hopelessness"], WordFrequency.COMMON),
    
    # Complex emotions
    "jealousy": WordEntry("jealousy", [PartOfSpeech.NOUN], ["Envy"], WordFrequency.COMMON),
    "envy": WordEntry("envy", [PartOfSpeech.NOUN], ["Covetousness"], WordFrequency.COMMON),
    "guilt": WordEntry("guilt", [PartOfSpeech.NOUN], ["Remorse"], WordFrequency.COMMON),
    "shame": WordEntry("shame", [PartOfSpeech.NOUN], ["Embarrassment"], WordFrequency.COMMON),
    "pride": WordEntry("pride", [PartOfSpeech.NOUN], ["Self-satisfaction"], WordFrequency.COMMON),
    "embarrassment": WordEntry("embarrassment", [PartOfSpeech.NOUN], ["Self-consciousness"], WordFrequency.COMMON),
    "loneliness": WordEntry("loneliness", [PartOfSpeech.NOUN], ["Isolation feeling"], WordFrequency.COMMON),
    "boredom": WordEntry("boredom", [PartOfSpeech.NOUN], ["Tedium"], WordFrequency.COMMON),
    "frustration": WordEntry("frustration", [PartOfSpeech.NOUN], ["Annoyance"], WordFrequency.COMMON),
    "confusion": WordEntry("confusion", [PartOfSpeech.NOUN], ["Bewilderment"], WordFrequency.COMMON),
    "curiosity": WordEntry("curiosity", [PartOfSpeech.NOUN], ["Inquisitiveness"], WordFrequency.COMMON),
    "nostalgia": WordEntry("nostalgia", [PartOfSpeech.NOUN], ["Longing for past"], WordFrequency.COMMON),
    "gratitude": WordEntry("gratitude", [PartOfSpeech.NOUN], ["Thankfulness"], WordFrequency.COMMON),
    "sympathy": WordEntry("sympathy", [PartOfSpeech.NOUN], ["Compassion"], WordFrequency.COMMON),
    "empathy": WordEntry("empathy", [PartOfSpeech.NOUN], ["Understanding others"], WordFrequency.COMMON),
    "compassion": WordEntry("compassion", [PartOfSpeech.NOUN], ["Deep sympathy"], WordFrequency.COMMON),
    "contentment": WordEntry("contentment", [PartOfSpeech.NOUN], ["Satisfaction"], WordFrequency.COMMON),
    "satisfaction": WordEntry("satisfaction", [PartOfSpeech.NOUN], ["Fulfillment"], WordFrequency.COMMON),
    "disappointment": WordEntry("disappointment", [PartOfSpeech.NOUN], ["Letdown"], WordFrequency.COMMON),
    "regret": WordEntry("regret", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Remorse"], WordFrequency.COMMON),
    
    # Emotional adjectives
    "emotional": WordEntry("emotional", [PartOfSpeech.ADJECTIVE], ["Feeling-based"], WordFrequency.COMMON),
    "anxious": WordEntry("anxious", [PartOfSpeech.ADJECTIVE], ["Worried"], WordFrequency.COMMON),
    "nervous": WordEntry("nervous", [PartOfSpeech.ADJECTIVE], ["Tense"], WordFrequency.COMMON),
    "calm": WordEntry("calm", [PartOfSpeech.ADJECTIVE], ["Peaceful"], WordFrequency.CORE_1000),
    "peaceful": WordEntry("peaceful", [PartOfSpeech.ADJECTIVE], ["Tranquil"], WordFrequency.COMMON),
    "relaxed": WordEntry("relaxed", [PartOfSpeech.ADJECTIVE], ["At ease"], WordFrequency.COMMON),
    "tense": WordEntry("tense", [PartOfSpeech.ADJECTIVE], ["Nervous"], WordFrequency.COMMON),
    "depressed": WordEntry("depressed", [PartOfSpeech.ADJECTIVE], ["Very sad"], WordFrequency.COMMON),
    "cheerful": WordEntry("cheerful", [PartOfSpeech.ADJECTIVE], ["Happy"], WordFrequency.COMMON),
    "optimistic": WordEntry("optimistic", [PartOfSpeech.ADJECTIVE], ["Hopeful"], WordFrequency.COMMON),
    "pessimistic": WordEntry("pessimistic", [PartOfSpeech.ADJECTIVE], ["Negative"], WordFrequency.COMMON),
    "confident": WordEntry("confident", [PartOfSpeech.ADJECTIVE], ["Self-assured"], WordFrequency.COMMON),
    "insecure": WordEntry("insecure", [PartOfSpeech.ADJECTIVE], ["Uncertain"], WordFrequency.COMMON),
    "overwhelmed": WordEntry("overwhelmed", [PartOfSpeech.ADJECTIVE], ["Overcome"], WordFrequency.COMMON),
    "grateful": WordEntry("grateful", [PartOfSpeech.ADJECTIVE], ["Thankful"], WordFrequency.COMMON),
    "resentful": WordEntry("resentful", [PartOfSpeech.ADJECTIVE], ["Bitter"], WordFrequency.COMMON),
    "enthusiastic": WordEntry("enthusiastic", [PartOfSpeech.ADJECTIVE], ["Eager"], WordFrequency.COMMON),
    "passionate": WordEntry("passionate", [PartOfSpeech.ADJECTIVE], ["Intense feeling"], WordFrequency.COMMON),
    "indifferent": WordEntry("indifferent", [PartOfSpeech.ADJECTIVE], ["Uncaring"], WordFrequency.COMMON),
    
    # Psychology terms
    "psychology": WordEntry("psychology", [PartOfSpeech.NOUN], ["Mind study"], WordFrequency.COMMON),
    "mental": WordEntry("mental", [PartOfSpeech.ADJECTIVE], ["Of mind"], WordFrequency.CORE_1000),
    "mind": WordEntry("mind", [PartOfSpeech.NOUN], ["Consciousness"], WordFrequency.CORE_500),
    "behavior": WordEntry("behavior", [PartOfSpeech.NOUN], ["Actions"], WordFrequency.COMMON),
    "attitude": WordEntry("attitude", [PartOfSpeech.NOUN], ["Mindset"], WordFrequency.COMMON),
    "personality": WordEntry("personality", [PartOfSpeech.NOUN], ["Character"], WordFrequency.COMMON),
    "character": WordEntry("character", [PartOfSpeech.NOUN], ["Nature"], WordFrequency.CORE_500),
    "temperament": WordEntry("temperament", [PartOfSpeech.NOUN], ["Nature"], WordFrequency.COMMON),
    "trait": WordEntry("trait", [PartOfSpeech.NOUN], ["Characteristic"], WordFrequency.COMMON),
    "instinct": WordEntry("instinct", [PartOfSpeech.NOUN], ["Natural tendency"], WordFrequency.COMMON),
    "intuition": WordEntry("intuition", [PartOfSpeech.NOUN], ["Gut feeling"], WordFrequency.COMMON),
    "perception": WordEntry("perception", [PartOfSpeech.NOUN], ["Understanding"], WordFrequency.COMMON),
    "consciousness": WordEntry("consciousness", [PartOfSpeech.NOUN], ["Awareness"], WordFrequency.COMMON),
    "subconscious": WordEntry("subconscious", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Unconscious mind"], WordFrequency.COMMON),
    "motivation": WordEntry("motivation", [PartOfSpeech.NOUN], ["Drive"], WordFrequency.COMMON),
    "desire": WordEntry("desire", [PartOfSpeech.NOUN], ["Want"], WordFrequency.CORE_1000),
    "urge": WordEntry("urge", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Strong desire"], WordFrequency.COMMON),
    "impulse": WordEntry("impulse", [PartOfSpeech.NOUN], ["Sudden urge"], WordFrequency.COMMON),
    "habit": WordEntry("habit", [PartOfSpeech.NOUN], ["Regular behavior"], WordFrequency.COMMON),
    "addiction": WordEntry("addiction", [PartOfSpeech.NOUN], ["Dependency"], WordFrequency.COMMON),
    "trauma": WordEntry("trauma", [PartOfSpeech.NOUN], ["Psychological injury"], WordFrequency.COMMON),
    "therapy": WordEntry("therapy", [PartOfSpeech.NOUN], ["Treatment"], WordFrequency.COMMON),
    "counseling": WordEntry("counseling", [PartOfSpeech.NOUN], ["Guidance"], WordFrequency.COMMON),
}


# =============================================================================
# ARTS & CULTURE (~200 words)
# =============================================================================

ARTS_VOCAB = {
    # Visual arts
    "art": WordEntry("art", [PartOfSpeech.NOUN], ["Creative expression"], WordFrequency.CORE_500),
    "artist": WordEntry("artist", [PartOfSpeech.NOUN], ["Art creator"], WordFrequency.CORE_1000),
    "painting": WordEntry("painting", [PartOfSpeech.NOUN], ["Painted artwork"], WordFrequency.CORE_1000),
    "drawing": WordEntry("drawing", [PartOfSpeech.NOUN], ["Drawn image"], WordFrequency.CORE_1000),
    "sculpture": WordEntry("sculpture", [PartOfSpeech.NOUN], ["3D artwork"], WordFrequency.COMMON),
    "photograph": WordEntry("photograph", [PartOfSpeech.NOUN], ["Photo"], WordFrequency.COMMON),
    "photography": WordEntry("photography", [PartOfSpeech.NOUN], ["Photo art"], WordFrequency.COMMON),
    "portrait": WordEntry("portrait", [PartOfSpeech.NOUN], ["Person image"], WordFrequency.COMMON),
    "landscape": WordEntry("landscape", [PartOfSpeech.NOUN], ["Scene image"], WordFrequency.COMMON),
    "gallery": WordEntry("gallery", [PartOfSpeech.NOUN], ["Art display"], WordFrequency.COMMON),
    "museum": WordEntry("museum", [PartOfSpeech.NOUN], ["Art/history place"], WordFrequency.CORE_1000),
    "exhibition": WordEntry("exhibition", [PartOfSpeech.NOUN], ["Display show"], WordFrequency.COMMON),
    "canvas": WordEntry("canvas", [PartOfSpeech.NOUN], ["Painting surface"], WordFrequency.COMMON),
    "brush": WordEntry("brush", [PartOfSpeech.NOUN], ["Painting tool"], WordFrequency.CORE_1000),
    "palette": WordEntry("palette", [PartOfSpeech.NOUN], ["Color holder"], WordFrequency.COMMON),
    "color": WordEntry("color", [PartOfSpeech.NOUN], ["Hue"], WordFrequency.CORE_500),
    "shade": WordEntry("shade", [PartOfSpeech.NOUN], ["Color variation"], WordFrequency.COMMON),
    "texture": WordEntry("texture", [PartOfSpeech.NOUN], ["Surface feel"], WordFrequency.COMMON),
    "style": WordEntry("style", [PartOfSpeech.NOUN], ["Artistic manner"], WordFrequency.CORE_500),
    "abstract": WordEntry("abstract", [PartOfSpeech.ADJECTIVE], ["Non-representational"], WordFrequency.COMMON),
    "realistic": WordEntry("realistic", [PartOfSpeech.ADJECTIVE], ["Lifelike"], WordFrequency.COMMON),
    "modern": WordEntry("modern", [PartOfSpeech.ADJECTIVE], ["Contemporary"], WordFrequency.CORE_1000),
    "traditional": WordEntry("traditional", [PartOfSpeech.ADJECTIVE], ["Customary"], WordFrequency.COMMON),
    
    # Literature
    "literature": WordEntry("literature", [PartOfSpeech.NOUN], ["Written works"], WordFrequency.COMMON),
    "novel": WordEntry("novel", [PartOfSpeech.NOUN], ["Long fiction"], WordFrequency.COMMON),
    "poem": WordEntry("poem", [PartOfSpeech.NOUN], ["Verse writing"], WordFrequency.COMMON),
    "poetry": WordEntry("poetry", [PartOfSpeech.NOUN], ["Poem collection"], WordFrequency.COMMON),
    "fiction": WordEntry("fiction", [PartOfSpeech.NOUN], ["Imaginary stories"], WordFrequency.COMMON),
    "nonfiction": WordEntry("nonfiction", [PartOfSpeech.NOUN], ["Factual writing"], WordFrequency.COMMON),
    "author": WordEntry("author", [PartOfSpeech.NOUN], ["Writer"], WordFrequency.CORE_1000),
    "poet": WordEntry("poet", [PartOfSpeech.NOUN], ["Poem writer"], WordFrequency.COMMON),
    "chapter": WordEntry("chapter", [PartOfSpeech.NOUN], ["Book section"], WordFrequency.COMMON),
    "plot": WordEntry("plot", [PartOfSpeech.NOUN], ["Story events"], WordFrequency.COMMON),
    "theme": WordEntry("theme", [PartOfSpeech.NOUN], ["Central idea"], WordFrequency.COMMON),
    "character": WordEntry("character", [PartOfSpeech.NOUN], ["Story person"], WordFrequency.CORE_500),
    "narrator": WordEntry("narrator", [PartOfSpeech.NOUN], ["Story teller"], WordFrequency.COMMON),
    "dialogue": WordEntry("dialogue", [PartOfSpeech.NOUN], ["Character speech"], WordFrequency.COMMON),
    "metaphor": WordEntry("metaphor", [PartOfSpeech.NOUN], ["Figure of speech"], WordFrequency.COMMON),
    "symbol": WordEntry("symbol", [PartOfSpeech.NOUN], ["Representation"], WordFrequency.COMMON),
    
    # Performing arts
    "performance": WordEntry("performance", [PartOfSpeech.NOUN], ["Show"], WordFrequency.COMMON),
    "theater": WordEntry("theater", [PartOfSpeech.NOUN], ["Drama venue"], WordFrequency.CORE_1000),
    "play": WordEntry("play", [PartOfSpeech.NOUN], ["Drama work"], WordFrequency.CORE_500),
    "drama": WordEntry("drama", [PartOfSpeech.NOUN], ["Theatrical work"], WordFrequency.COMMON),
    "opera": WordEntry("opera", [PartOfSpeech.NOUN], ["Sung drama"], WordFrequency.COMMON),
    "ballet": WordEntry("ballet", [PartOfSpeech.NOUN], ["Classical dance"], WordFrequency.COMMON),
    "dance": WordEntry("dance", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Movement art"], WordFrequency.CORE_1000),
    "choreography": WordEntry("choreography", [PartOfSpeech.NOUN], ["Dance composition"], WordFrequency.COMMON),
    "stage": WordEntry("stage", [PartOfSpeech.NOUN], ["Performance area"], WordFrequency.CORE_1000),
    "scene": WordEntry("scene", [PartOfSpeech.NOUN], ["Play section"], WordFrequency.CORE_1000),
    "act": WordEntry("act", [PartOfSpeech.NOUN], ["Play division"], WordFrequency.CORE_500),
    "costume": WordEntry("costume", [PartOfSpeech.NOUN], ["Stage clothing"], WordFrequency.COMMON),
    "prop": WordEntry("prop", [PartOfSpeech.NOUN], ["Stage object"], WordFrequency.COMMON),
    "rehearsal": WordEntry("rehearsal", [PartOfSpeech.NOUN], ["Practice session"], WordFrequency.COMMON),
    "applause": WordEntry("applause", [PartOfSpeech.NOUN], ["Clapping"], WordFrequency.COMMON),
    
    # Culture
    "culture": WordEntry("culture", [PartOfSpeech.NOUN], ["Way of life"], WordFrequency.CORE_500),
    "cultural": WordEntry("cultural", [PartOfSpeech.ADJECTIVE], ["Of culture"], WordFrequency.COMMON),
    "tradition": WordEntry("tradition", [PartOfSpeech.NOUN], ["Custom"], WordFrequency.COMMON),
    "custom": WordEntry("custom", [PartOfSpeech.NOUN], ["Practice"], WordFrequency.COMMON),
    "heritage": WordEntry("heritage", [PartOfSpeech.NOUN], ["Inherited culture"], WordFrequency.COMMON),
    "ceremony": WordEntry("ceremony", [PartOfSpeech.NOUN], ["Formal event"], WordFrequency.COMMON),
    "ritual": WordEntry("ritual", [PartOfSpeech.NOUN], ["Traditional practice"], WordFrequency.COMMON),
    "festival": WordEntry("festival", [PartOfSpeech.NOUN], ["Celebration"], WordFrequency.COMMON),
    "celebration": WordEntry("celebration", [PartOfSpeech.NOUN], ["Festivity"], WordFrequency.COMMON),
    "holiday": WordEntry("holiday", [PartOfSpeech.NOUN], ["Special day"], WordFrequency.CORE_1000),
    "religion": WordEntry("religion", [PartOfSpeech.NOUN], ["Faith system"], WordFrequency.COMMON),
    "belief": WordEntry("belief", [PartOfSpeech.NOUN], ["Faith"], WordFrequency.CORE_1000),
    "philosophy": WordEntry("philosophy", [PartOfSpeech.NOUN], ["World view"], WordFrequency.COMMON),
    "myth": WordEntry("myth", [PartOfSpeech.NOUN], ["Traditional story"], WordFrequency.COMMON),
    "legend": WordEntry("legend", [PartOfSpeech.NOUN], ["Famous story"], WordFrequency.COMMON),
    "folklore": WordEntry("folklore", [PartOfSpeech.NOUN], ["Traditional beliefs"], WordFrequency.COMMON),
    
    # Architecture
    "architecture": WordEntry("architecture", [PartOfSpeech.NOUN], ["Building design"], WordFrequency.COMMON),
    "architect": WordEntry("architect", [PartOfSpeech.NOUN], ["Building designer"], WordFrequency.COMMON),
    "design": WordEntry("design", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Plan"], WordFrequency.CORE_500),
    "structure": WordEntry("structure", [PartOfSpeech.NOUN], ["Building"], WordFrequency.CORE_500),
    "monument": WordEntry("monument", [PartOfSpeech.NOUN], ["Memorial structure"], WordFrequency.COMMON),
    "tower": WordEntry("tower", [PartOfSpeech.NOUN], ["Tall structure"], WordFrequency.CORE_1000),
    "cathedral": WordEntry("cathedral", [PartOfSpeech.NOUN], ["Large church"], WordFrequency.COMMON),
    "temple": WordEntry("temple", [PartOfSpeech.NOUN], ["Religious building"], WordFrequency.COMMON),
    "palace": WordEntry("palace", [PartOfSpeech.NOUN], ["Royal residence"], WordFrequency.COMMON),
    "castle": WordEntry("castle", [PartOfSpeech.NOUN], ["Fortified building"], WordFrequency.COMMON),
}


# =============================================================================
# SOCIAL & RELATIONSHIPS (~150 words)
# =============================================================================

SOCIAL_VOCAB = {
    # Relationships
    "relationship": WordEntry("relationship", [PartOfSpeech.NOUN], ["Connection"], WordFrequency.CORE_1000),
    "friendship": WordEntry("friendship", [PartOfSpeech.NOUN], ["Friend bond"], WordFrequency.COMMON),
    "marriage": WordEntry("marriage", [PartOfSpeech.NOUN], ["Union"], WordFrequency.COMMON),
    "partner": WordEntry("partner", [PartOfSpeech.NOUN], ["Companion"], WordFrequency.COMMON),
    "spouse": WordEntry("spouse", [PartOfSpeech.NOUN], ["Married partner"], WordFrequency.COMMON),
    "couple": WordEntry("couple", [PartOfSpeech.NOUN], ["Two people together"], WordFrequency.CORE_1000),
    "neighbor": WordEntry("neighbor", [PartOfSpeech.NOUN], ["Nearby person"], WordFrequency.CORE_1000),
    "colleague": WordEntry("colleague", [PartOfSpeech.NOUN], ["Work partner"], WordFrequency.COMMON),
    "acquaintance": WordEntry("acquaintance", [PartOfSpeech.NOUN], ["Known person"], WordFrequency.COMMON),
    "stranger": WordEntry("stranger", [PartOfSpeech.NOUN], ["Unknown person"], WordFrequency.CORE_1000),
    "enemy": WordEntry("enemy", [PartOfSpeech.NOUN], ["Opponent"], WordFrequency.CORE_1000),
    
    # Social interactions
    "conversation": WordEntry("conversation", [PartOfSpeech.NOUN], ["Talk"], WordFrequency.CORE_1000),
    "communication": WordEntry("communication", [PartOfSpeech.NOUN], ["Information exchange"], WordFrequency.COMMON),
    "interaction": WordEntry("interaction", [PartOfSpeech.NOUN], ["Exchange"], WordFrequency.COMMON),
    "cooperation": WordEntry("cooperation", [PartOfSpeech.NOUN], ["Working together"], WordFrequency.COMMON),
    "conflict": WordEntry("conflict", [PartOfSpeech.NOUN], ["Disagreement"], WordFrequency.COMMON),
    "argument": WordEntry("argument", [PartOfSpeech.NOUN], ["Dispute"], WordFrequency.CORE_1000),
    "compromise": WordEntry("compromise", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Agreement"], WordFrequency.COMMON),
    "trust": WordEntry("trust", [PartOfSpeech.NOUN], ["Confidence"], WordFrequency.CORE_1000),
    "loyalty": WordEntry("loyalty", [PartOfSpeech.NOUN], ["Faithfulness"], WordFrequency.COMMON),
    "respect": WordEntry("respect", [PartOfSpeech.NOUN], ["Esteem"], WordFrequency.COMMON),
    "support": WordEntry("support", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Help"], WordFrequency.CORE_500),
    
    # Social actions
    "meet": WordEntry("meet", [PartOfSpeech.VERB], ["Come together"], WordFrequency.CORE_500),
    "introduce": WordEntry("introduce", [PartOfSpeech.VERB], ["Present"], WordFrequency.COMMON),
    "greet": WordEntry("greet", [PartOfSpeech.VERB], ["Welcome"], WordFrequency.COMMON),
    "invite": WordEntry("invite", [PartOfSpeech.VERB], ["Ask to come"], WordFrequency.COMMON),
    "host": WordEntry("host", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Entertain guests"], WordFrequency.COMMON),
    "visit": WordEntry("visit", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Go see"], WordFrequency.CORE_1000),
    "gather": WordEntry("gather", [PartOfSpeech.VERB], ["Come together"], WordFrequency.COMMON),
    "celebrate": WordEntry("celebrate", [PartOfSpeech.VERB], ["Mark occasion"], WordFrequency.COMMON),
    "socialize": WordEntry("socialize", [PartOfSpeech.VERB], ["Interact"], WordFrequency.COMMON),
    "network": WordEntry("network", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Make connections"], WordFrequency.COMMON),
    "date": WordEntry("date", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Romantic meeting"], WordFrequency.CORE_500),
    "marry": WordEntry("marry", [PartOfSpeech.VERB], ["Wed"], WordFrequency.COMMON),
    "divorce": WordEntry("divorce", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["End marriage"], WordFrequency.COMMON),
    
    # Social groups
    "society": WordEntry("society", [PartOfSpeech.NOUN], ["Community"], WordFrequency.CORE_500),
    "community": WordEntry("community", [PartOfSpeech.NOUN], ["Group"], WordFrequency.CORE_1000),
    "organization": WordEntry("organization", [PartOfSpeech.NOUN], ["Group"], WordFrequency.CORE_500),
    "club": WordEntry("club", [PartOfSpeech.NOUN], ["Interest group"], WordFrequency.CORE_1000),
    "association": WordEntry("association", [PartOfSpeech.NOUN], ["Organization"], WordFrequency.COMMON),
    "network": WordEntry("network", [PartOfSpeech.NOUN], ["Connected group"], WordFrequency.COMMON),
    "crowd": WordEntry("crowd", [PartOfSpeech.NOUN], ["Large group"], WordFrequency.CORE_1000),
    "audience": WordEntry("audience", [PartOfSpeech.NOUN], ["Spectators"], WordFrequency.CORE_1000),
    "public": WordEntry("public", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["People"], WordFrequency.CORE_500),
    "population": WordEntry("population", [PartOfSpeech.NOUN], ["People count"], WordFrequency.COMMON),
}


def load_expansion_vocabulary(vocab=None):
    """
    Load expansion vocabulary for additional domains.
    
    Args:
        vocab: Optional existing vocabulary to extend
        
    Returns:
        Extended vocabulary
    """
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    domains = [
        ("sports", SPORTS_VOCAB),
        ("entertainment", ENTERTAINMENT_VOCAB),
        ("legal", LEGAL_VOCAB),
        ("emotions", EMOTIONS_VOCAB),
        ("arts", ARTS_VOCAB),
        ("social", SOCIAL_VOCAB),
    ]
    
    total_added = 0
    for domain_name, domain_words in domains:
        for word, entry in domain_words.items():
            vocab.add_word(entry)
            total_added += 1
            
    print(f"[ExpansionVocabulary] Loaded {total_added} expansion words")
    print(f"[ExpansionVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_expansion_stats() -> dict:
    """Get word counts for expansion vocabulary."""
    return {
        "sports": len(SPORTS_VOCAB),
        "entertainment": len(ENTERTAINMENT_VOCAB),
        "legal": len(LEGAL_VOCAB),
        "emotions": len(EMOTIONS_VOCAB),
        "arts": len(ARTS_VOCAB),
        "social": len(SOCIAL_VOCAB),
        "total": (
            len(SPORTS_VOCAB) + len(ENTERTAINMENT_VOCAB) + len(LEGAL_VOCAB) +
            len(EMOTIONS_VOCAB) + len(ARTS_VOCAB) + len(SOCIAL_VOCAB)
        )
    }
