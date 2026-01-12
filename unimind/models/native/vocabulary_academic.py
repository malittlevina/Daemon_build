# unimind/models/native/vocabulary_academic.py
# Academic and Advanced Vocabulary for C1/C2 Level

"""
Academic Vocabulary Module

Contains academic and advanced vocabulary for C1/C2 level fluency:
- Academic Word List (AWL) words
- Formal vocabulary
- Abstract concepts
- Discourse markers
- Transition words
"""

from typing import Dict
from .vocabulary import WordEntry, PartOfSpeech, WordFrequency


# =============================================================================
# ACADEMIC WORD LIST - Core Academic Vocabulary (~500 words)
# =============================================================================

ACADEMIC_CORE = {
    # Analysis & Research
    "analyze": WordEntry("analyze", [PartOfSpeech.VERB], ["Examine in detail"], WordFrequency.COMMON),
    "analysis": WordEntry("analysis", [PartOfSpeech.NOUN], ["Detailed examination"], WordFrequency.COMMON),
    "analytical": WordEntry("analytical", [PartOfSpeech.ADJECTIVE], ["Using analysis"], WordFrequency.COMMON),
    "assess": WordEntry("assess", [PartOfSpeech.VERB], ["Evaluate"], WordFrequency.COMMON),
    "assessment": WordEntry("assessment", [PartOfSpeech.NOUN], ["Evaluation"], WordFrequency.COMMON),
    "concept": WordEntry("concept", [PartOfSpeech.NOUN], ["Abstract idea"], WordFrequency.COMMON),
    "conceptual": WordEntry("conceptual", [PartOfSpeech.ADJECTIVE], ["Relating to concepts"], WordFrequency.COMMON),
    "context": WordEntry("context", [PartOfSpeech.NOUN], ["Circumstances"], WordFrequency.COMMON),
    "contextual": WordEntry("contextual", [PartOfSpeech.ADJECTIVE], ["In context"], WordFrequency.COMMON),
    "data": WordEntry("data", [PartOfSpeech.NOUN], ["Information"], WordFrequency.CORE_500),
    "define": WordEntry("define", [PartOfSpeech.VERB], ["Give meaning"], WordFrequency.COMMON),
    "definition": WordEntry("definition", [PartOfSpeech.NOUN], ["Meaning statement"], WordFrequency.COMMON),
    "derive": WordEntry("derive", [PartOfSpeech.VERB], ["Obtain from source"], WordFrequency.COMMON),
    "derivation": WordEntry("derivation", [PartOfSpeech.NOUN], ["Process of deriving"], WordFrequency.COMMON),
    "establish": WordEntry("establish", [PartOfSpeech.VERB], ["Set up, prove"], WordFrequency.COMMON),
    "established": WordEntry("established", [PartOfSpeech.ADJECTIVE], ["Accepted"], WordFrequency.COMMON),
    "estimate": WordEntry("estimate", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Approximate"], WordFrequency.COMMON),
    "evaluate": WordEntry("evaluate", [PartOfSpeech.VERB], ["Assess value"], WordFrequency.COMMON),
    "evaluation": WordEntry("evaluation", [PartOfSpeech.NOUN], ["Assessment"], WordFrequency.COMMON),
    "evident": WordEntry("evident", [PartOfSpeech.ADJECTIVE], ["Clear, obvious"], WordFrequency.COMMON),
    "evidence": WordEntry("evidence", [PartOfSpeech.NOUN], ["Proof"], WordFrequency.CORE_500),
    "export": WordEntry("export", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Send abroad"], WordFrequency.COMMON),
    "factor": WordEntry("factor", [PartOfSpeech.NOUN], ["Contributing element"], WordFrequency.COMMON),
    "formula": WordEntry("formula", [PartOfSpeech.NOUN], ["Mathematical expression"], WordFrequency.COMMON),
    "formulate": WordEntry("formulate", [PartOfSpeech.VERB], ["Create, devise"], WordFrequency.COMMON),
    "function": WordEntry("function", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Purpose, work"], WordFrequency.CORE_500),
    "functional": WordEntry("functional", [PartOfSpeech.ADJECTIVE], ["Working, practical"], WordFrequency.COMMON),
    "identify": WordEntry("identify", [PartOfSpeech.VERB], ["Recognize"], WordFrequency.COMMON),
    "identification": WordEntry("identification", [PartOfSpeech.NOUN], ["Recognition"], WordFrequency.COMMON),
    "indicate": WordEntry("indicate", [PartOfSpeech.VERB], ["Show, suggest"], WordFrequency.COMMON),
    "indication": WordEntry("indication", [PartOfSpeech.NOUN], ["Sign"], WordFrequency.COMMON),
    "individual": WordEntry("individual", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Single person"], WordFrequency.COMMON),
    "interpret": WordEntry("interpret", [PartOfSpeech.VERB], ["Explain meaning"], WordFrequency.COMMON),
    "interpretation": WordEntry("interpretation", [PartOfSpeech.NOUN], ["Explanation"], WordFrequency.COMMON),
    "involve": WordEntry("involve", [PartOfSpeech.VERB], ["Include, engage"], WordFrequency.COMMON),
    "involvement": WordEntry("involvement", [PartOfSpeech.NOUN], ["Participation"], WordFrequency.COMMON),
    "issue": WordEntry("issue", [PartOfSpeech.NOUN], ["Topic, problem"], WordFrequency.CORE_500),
    "major": WordEntry("major", [PartOfSpeech.ADJECTIVE], ["Main, significant"], WordFrequency.COMMON),
    "majority": WordEntry("majority", [PartOfSpeech.NOUN], ["Greater part"], WordFrequency.COMMON),
    "method": WordEntry("method", [PartOfSpeech.NOUN], ["Way of doing"], WordFrequency.COMMON),
    "methodology": WordEntry("methodology", [PartOfSpeech.NOUN], ["System of methods"], WordFrequency.COMMON),
    "occur": WordEntry("occur", [PartOfSpeech.VERB], ["Happen"], WordFrequency.COMMON),
    "occurrence": WordEntry("occurrence", [PartOfSpeech.NOUN], ["Event"], WordFrequency.COMMON),
    "percent": WordEntry("percent", [PartOfSpeech.NOUN], ["Per hundred"], WordFrequency.COMMON),
    "percentage": WordEntry("percentage", [PartOfSpeech.NOUN], ["Proportion"], WordFrequency.COMMON),
    "period": WordEntry("period", [PartOfSpeech.NOUN], ["Time span"], WordFrequency.COMMON),
    "policy": WordEntry("policy", [PartOfSpeech.NOUN], ["Plan of action"], WordFrequency.COMMON),
    "principle": WordEntry("principle", [PartOfSpeech.NOUN], ["Fundamental rule"], WordFrequency.COMMON),
    "principled": WordEntry("principled", [PartOfSpeech.ADJECTIVE], ["Based on principles"], WordFrequency.COMMON),
    "procedure": WordEntry("procedure", [PartOfSpeech.NOUN], ["Process"], WordFrequency.COMMON),
    "procedural": WordEntry("procedural", [PartOfSpeech.ADJECTIVE], ["Of procedure"], WordFrequency.COMMON),
    "process": WordEntry("process", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Series of steps"], WordFrequency.CORE_500),
    "require": WordEntry("require", [PartOfSpeech.VERB], ["Need"], WordFrequency.COMMON),
    "requirement": WordEntry("requirement", [PartOfSpeech.NOUN], ["Necessity"], WordFrequency.COMMON),
    "research": WordEntry("research", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Investigation"], WordFrequency.CORE_500),
    "researcher": WordEntry("researcher", [PartOfSpeech.NOUN], ["One who researches"], WordFrequency.COMMON),
    "respond": WordEntry("respond", [PartOfSpeech.VERB], ["Reply"], WordFrequency.COMMON),
    "response": WordEntry("response", [PartOfSpeech.NOUN], ["Answer"], WordFrequency.COMMON),
    "role": WordEntry("role", [PartOfSpeech.NOUN], ["Function, part"], WordFrequency.COMMON),
    "section": WordEntry("section", [PartOfSpeech.NOUN], ["Part"], WordFrequency.COMMON),
    "sector": WordEntry("sector", [PartOfSpeech.NOUN], ["Area, division"], WordFrequency.COMMON),
    "significant": WordEntry("significant", [PartOfSpeech.ADJECTIVE], ["Important"], WordFrequency.COMMON),
    "significance": WordEntry("significance", [PartOfSpeech.NOUN], ["Importance"], WordFrequency.COMMON),
    "similar": WordEntry("similar", [PartOfSpeech.ADJECTIVE], ["Alike"], WordFrequency.COMMON),
    "similarity": WordEntry("similarity", [PartOfSpeech.NOUN], ["Likeness"], WordFrequency.COMMON),
    "source": WordEntry("source", [PartOfSpeech.NOUN], ["Origin"], WordFrequency.COMMON),
    "specific": WordEntry("specific", [PartOfSpeech.ADJECTIVE], ["Particular"], WordFrequency.COMMON),
    "specifically": WordEntry("specifically", [PartOfSpeech.ADVERB], ["In particular"], WordFrequency.COMMON),
    "structure": WordEntry("structure", [PartOfSpeech.NOUN], ["Organization"], WordFrequency.COMMON),
    "structural": WordEntry("structural", [PartOfSpeech.ADJECTIVE], ["Of structure"], WordFrequency.COMMON),
    "theory": WordEntry("theory", [PartOfSpeech.NOUN], ["Explanation"], WordFrequency.COMMON),
    "theoretical": WordEntry("theoretical", [PartOfSpeech.ADJECTIVE], ["Of theory"], WordFrequency.COMMON),
    "vary": WordEntry("vary", [PartOfSpeech.VERB], ["Change"], WordFrequency.COMMON),
    "variable": WordEntry("variable", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Changeable"], WordFrequency.COMMON),
    "variation": WordEntry("variation", [PartOfSpeech.NOUN], ["Difference"], WordFrequency.COMMON),
    
    # Discourse & Argumentation
    "achieve": WordEntry("achieve", [PartOfSpeech.VERB], ["Accomplish"], WordFrequency.COMMON),
    "achievement": WordEntry("achievement", [PartOfSpeech.NOUN], ["Accomplishment"], WordFrequency.COMMON),
    "acquire": WordEntry("acquire", [PartOfSpeech.VERB], ["Obtain"], WordFrequency.COMMON),
    "acquisition": WordEntry("acquisition", [PartOfSpeech.NOUN], ["Obtaining"], WordFrequency.COMMON),
    "adapt": WordEntry("adapt", [PartOfSpeech.VERB], ["Adjust"], WordFrequency.COMMON),
    "adaptation": WordEntry("adaptation", [PartOfSpeech.NOUN], ["Adjustment"], WordFrequency.COMMON),
    "adequate": WordEntry("adequate", [PartOfSpeech.ADJECTIVE], ["Sufficient"], WordFrequency.COMMON),
    "adequately": WordEntry("adequately", [PartOfSpeech.ADVERB], ["Sufficiently"], WordFrequency.COMMON),
    "affect": WordEntry("affect", [PartOfSpeech.VERB], ["Influence"], WordFrequency.COMMON),
    "alternative": WordEntry("alternative", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Other option"], WordFrequency.COMMON),
    "apparent": WordEntry("apparent", [PartOfSpeech.ADJECTIVE], ["Obvious"], WordFrequency.COMMON),
    "apparently": WordEntry("apparently", [PartOfSpeech.ADVERB], ["Seemingly"], WordFrequency.COMMON),
    "approach": WordEntry("approach", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Method, come near"], WordFrequency.COMMON),
    "appropriate": WordEntry("appropriate", [PartOfSpeech.ADJECTIVE], ["Suitable"], WordFrequency.COMMON),
    "appropriately": WordEntry("appropriately", [PartOfSpeech.ADVERB], ["Suitably"], WordFrequency.COMMON),
    "aspect": WordEntry("aspect", [PartOfSpeech.NOUN], ["Feature"], WordFrequency.COMMON),
    "assume": WordEntry("assume", [PartOfSpeech.VERB], ["Suppose"], WordFrequency.COMMON),
    "assumption": WordEntry("assumption", [PartOfSpeech.NOUN], ["Supposition"], WordFrequency.COMMON),
    "attribute": WordEntry("attribute", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Assign, quality"], WordFrequency.COMMON),
    "benefit": WordEntry("benefit", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Advantage"], WordFrequency.COMMON),
    "beneficial": WordEntry("beneficial", [PartOfSpeech.ADJECTIVE], ["Advantageous"], WordFrequency.COMMON),
    "category": WordEntry("category", [PartOfSpeech.NOUN], ["Classification"], WordFrequency.COMMON),
    "categorize": WordEntry("categorize", [PartOfSpeech.VERB], ["Classify"], WordFrequency.COMMON),
    "chapter": WordEntry("chapter", [PartOfSpeech.NOUN], ["Book section"], WordFrequency.COMMON),
    "circumstance": WordEntry("circumstance", [PartOfSpeech.NOUN], ["Condition"], WordFrequency.COMMON),
    "cite": WordEntry("cite", [PartOfSpeech.VERB], ["Quote, mention"], WordFrequency.COMMON),
    "citation": WordEntry("citation", [PartOfSpeech.NOUN], ["Reference"], WordFrequency.COMMON),
    "clarify": WordEntry("clarify", [PartOfSpeech.VERB], ["Make clear"], WordFrequency.COMMON),
    "clarification": WordEntry("clarification", [PartOfSpeech.NOUN], ["Explanation"], WordFrequency.COMMON),
    "classify": WordEntry("classify", [PartOfSpeech.VERB], ["Categorize"], WordFrequency.COMMON),
    "classification": WordEntry("classification", [PartOfSpeech.NOUN], ["Categorization"], WordFrequency.COMMON),
    "clause": WordEntry("clause", [PartOfSpeech.NOUN], ["Sentence part, provision"], WordFrequency.COMMON),
    "code": WordEntry("code", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["System of rules"], WordFrequency.COMMON),
    "coherent": WordEntry("coherent", [PartOfSpeech.ADJECTIVE], ["Logical, consistent"], WordFrequency.COMMON),
    "coherence": WordEntry("coherence", [PartOfSpeech.NOUN], ["Logical connection"], WordFrequency.COMMON),
    "colleague": WordEntry("colleague", [PartOfSpeech.NOUN], ["Co-worker"], WordFrequency.COMMON),
    "commission": WordEntry("commission", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Committee, authorize"], WordFrequency.COMMON),
    "commit": WordEntry("commit", [PartOfSpeech.VERB], ["Dedicate, pledge"], WordFrequency.COMMON),
    "commitment": WordEntry("commitment", [PartOfSpeech.NOUN], ["Dedication"], WordFrequency.COMMON),
    "commodity": WordEntry("commodity", [PartOfSpeech.NOUN], ["Tradeable good"], WordFrequency.COMMON),
    "communicate": WordEntry("communicate", [PartOfSpeech.VERB], ["Convey information"], WordFrequency.COMMON),
    "communication": WordEntry("communication", [PartOfSpeech.NOUN], ["Information exchange"], WordFrequency.COMMON),
    "community": WordEntry("community", [PartOfSpeech.NOUN], ["Group of people"], WordFrequency.COMMON),
    "compatible": WordEntry("compatible", [PartOfSpeech.ADJECTIVE], ["Able to work together"], WordFrequency.COMMON),
    "compensate": WordEntry("compensate", [PartOfSpeech.VERB], ["Make up for"], WordFrequency.COMMON),
    "compensation": WordEntry("compensation", [PartOfSpeech.NOUN], ["Recompense"], WordFrequency.COMMON),
    "complex": WordEntry("complex", [PartOfSpeech.ADJECTIVE], ["Complicated"], WordFrequency.COMMON),
    "complexity": WordEntry("complexity", [PartOfSpeech.NOUN], ["Complication"], WordFrequency.COMMON),
    "component": WordEntry("component", [PartOfSpeech.NOUN], ["Part"], WordFrequency.COMMON),
    "comprehensive": WordEntry("comprehensive", [PartOfSpeech.ADJECTIVE], ["Complete, thorough"], WordFrequency.COMMON),
    "comprise": WordEntry("comprise", [PartOfSpeech.VERB], ["Consist of"], WordFrequency.COMMON),
    "compute": WordEntry("compute", [PartOfSpeech.VERB], ["Calculate"], WordFrequency.COMMON),
    "computation": WordEntry("computation", [PartOfSpeech.NOUN], ["Calculation"], WordFrequency.COMMON),
    "concentrate": WordEntry("concentrate", [PartOfSpeech.VERB], ["Focus"], WordFrequency.COMMON),
    "concentration": WordEntry("concentration", [PartOfSpeech.NOUN], ["Focus"], WordFrequency.COMMON),
    "conclude": WordEntry("conclude", [PartOfSpeech.VERB], ["End, deduce"], WordFrequency.COMMON),
    "conclusion": WordEntry("conclusion", [PartOfSpeech.NOUN], ["End, deduction"], WordFrequency.COMMON),
    "concurrent": WordEntry("concurrent", [PartOfSpeech.ADJECTIVE], ["Simultaneous"], WordFrequency.COMMON),
    "conduct": WordEntry("conduct", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Carry out, behavior"], WordFrequency.COMMON),
    "confer": WordEntry("confer", [PartOfSpeech.VERB], ["Discuss, grant"], WordFrequency.COMMON),
    "conference": WordEntry("conference", [PartOfSpeech.NOUN], ["Meeting"], WordFrequency.COMMON),
    "confine": WordEntry("confine", [PartOfSpeech.VERB], ["Limit"], WordFrequency.COMMON),
    "confirm": WordEntry("confirm", [PartOfSpeech.VERB], ["Verify"], WordFrequency.COMMON),
    "confirmation": WordEntry("confirmation", [PartOfSpeech.NOUN], ["Verification"], WordFrequency.COMMON),
    "conflict": WordEntry("conflict", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Disagreement"], WordFrequency.COMMON),
    "conform": WordEntry("conform", [PartOfSpeech.VERB], ["Comply"], WordFrequency.COMMON),
    "consent": WordEntry("consent", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Agreement"], WordFrequency.COMMON),
    "consequent": WordEntry("consequent", [PartOfSpeech.ADJECTIVE], ["Following as result"], WordFrequency.COMMON),
    "consequence": WordEntry("consequence", [PartOfSpeech.NOUN], ["Result"], WordFrequency.COMMON),
    "consequently": WordEntry("consequently", [PartOfSpeech.ADVERB], ["As a result"], WordFrequency.COMMON),
    "considerable": WordEntry("considerable", [PartOfSpeech.ADJECTIVE], ["Significant"], WordFrequency.COMMON),
    "considerably": WordEntry("considerably", [PartOfSpeech.ADVERB], ["Significantly"], WordFrequency.COMMON),
    "consist": WordEntry("consist", [PartOfSpeech.VERB], ["Be composed of"], WordFrequency.COMMON),
    "consistent": WordEntry("consistent", [PartOfSpeech.ADJECTIVE], ["Uniform"], WordFrequency.COMMON),
    "consistently": WordEntry("consistently", [PartOfSpeech.ADVERB], ["Uniformly"], WordFrequency.COMMON),
    "constant": WordEntry("constant", [PartOfSpeech.ADJECTIVE, PartOfSpeech.NOUN], ["Unchanging"], WordFrequency.COMMON),
    "constantly": WordEntry("constantly", [PartOfSpeech.ADVERB], ["Continuously"], WordFrequency.COMMON),
    "constitute": WordEntry("constitute", [PartOfSpeech.VERB], ["Form, make up"], WordFrequency.COMMON),
    "constitution": WordEntry("constitution", [PartOfSpeech.NOUN], ["Composition, law"], WordFrequency.COMMON),
    "constrain": WordEntry("constrain", [PartOfSpeech.VERB], ["Limit"], WordFrequency.COMMON),
    "constraint": WordEntry("constraint", [PartOfSpeech.NOUN], ["Limitation"], WordFrequency.COMMON),
    "construct": WordEntry("construct", [PartOfSpeech.VERB], ["Build"], WordFrequency.COMMON),
    "construction": WordEntry("construction", [PartOfSpeech.NOUN], ["Building"], WordFrequency.COMMON),
    "consult": WordEntry("consult", [PartOfSpeech.VERB], ["Seek advice"], WordFrequency.COMMON),
    "consultation": WordEntry("consultation", [PartOfSpeech.NOUN], ["Advisory meeting"], WordFrequency.COMMON),
    "consume": WordEntry("consume", [PartOfSpeech.VERB], ["Use up"], WordFrequency.COMMON),
    "consumption": WordEntry("consumption", [PartOfSpeech.NOUN], ["Using up"], WordFrequency.COMMON),
    "contact": WordEntry("contact", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Communication"], WordFrequency.COMMON),
    "contemporary": WordEntry("contemporary", [PartOfSpeech.ADJECTIVE, PartOfSpeech.NOUN], ["Modern"], WordFrequency.COMMON),
    "contrast": WordEntry("contrast", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Difference"], WordFrequency.COMMON),
    "contribute": WordEntry("contribute", [PartOfSpeech.VERB], ["Give"], WordFrequency.COMMON),
    "contribution": WordEntry("contribution", [PartOfSpeech.NOUN], ["Gift, addition"], WordFrequency.COMMON),
    "controversy": WordEntry("controversy", [PartOfSpeech.NOUN], ["Dispute"], WordFrequency.COMMON),
    "controversial": WordEntry("controversial", [PartOfSpeech.ADJECTIVE], ["Disputed"], WordFrequency.COMMON),
    "convention": WordEntry("convention", [PartOfSpeech.NOUN], ["Custom, meeting"], WordFrequency.COMMON),
    "conventional": WordEntry("conventional", [PartOfSpeech.ADJECTIVE], ["Traditional"], WordFrequency.COMMON),
    "convert": WordEntry("convert", [PartOfSpeech.VERB], ["Change"], WordFrequency.COMMON),
    "conversion": WordEntry("conversion", [PartOfSpeech.NOUN], ["Change"], WordFrequency.COMMON),
    "convince": WordEntry("convince", [PartOfSpeech.VERB], ["Persuade"], WordFrequency.COMMON),
    "cooperate": WordEntry("cooperate", [PartOfSpeech.VERB], ["Work together"], WordFrequency.COMMON),
    "cooperation": WordEntry("cooperation", [PartOfSpeech.NOUN], ["Collaboration"], WordFrequency.COMMON),
    "coordinate": WordEntry("coordinate", [PartOfSpeech.VERB], ["Organize together"], WordFrequency.COMMON),
    "coordination": WordEntry("coordination", [PartOfSpeech.NOUN], ["Organization"], WordFrequency.COMMON),
    "core": WordEntry("core", [PartOfSpeech.NOUN, PartOfSpeech.ADJECTIVE], ["Central part"], WordFrequency.COMMON),
    "corporate": WordEntry("corporate", [PartOfSpeech.ADJECTIVE], ["Of corporations"], WordFrequency.COMMON),
    "correspond": WordEntry("correspond", [PartOfSpeech.VERB], ["Match, communicate"], WordFrequency.COMMON),
    "correspondence": WordEntry("correspondence", [PartOfSpeech.NOUN], ["Communication"], WordFrequency.COMMON),
    "criterion": WordEntry("criterion", [PartOfSpeech.NOUN], ["Standard"], WordFrequency.COMMON),
    "criteria": WordEntry("criteria", [PartOfSpeech.NOUN], ["Standards (plural)"], WordFrequency.COMMON),
    "crucial": WordEntry("crucial", [PartOfSpeech.ADJECTIVE], ["Critical"], WordFrequency.COMMON),
    "cultural": WordEntry("cultural", [PartOfSpeech.ADJECTIVE], ["Of culture"], WordFrequency.COMMON),
    "culture": WordEntry("culture", [PartOfSpeech.NOUN], ["Society customs"], WordFrequency.COMMON),
    "cycle": WordEntry("cycle", [PartOfSpeech.NOUN], ["Recurring sequence"], WordFrequency.COMMON),
    "debate": WordEntry("debate", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Discussion"], WordFrequency.COMMON),
    "decade": WordEntry("decade", [PartOfSpeech.NOUN], ["Ten years"], WordFrequency.COMMON),
    "decline": WordEntry("decline", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Decrease"], WordFrequency.COMMON),
    "deduce": WordEntry("deduce", [PartOfSpeech.VERB], ["Conclude logically"], WordFrequency.COMMON),
    "deduction": WordEntry("deduction", [PartOfSpeech.NOUN], ["Logical conclusion"], WordFrequency.COMMON),
    "demonstrate": WordEntry("demonstrate", [PartOfSpeech.VERB], ["Show, prove"], WordFrequency.COMMON),
    "demonstration": WordEntry("demonstration", [PartOfSpeech.NOUN], ["Showing"], WordFrequency.COMMON),
    "denote": WordEntry("denote", [PartOfSpeech.VERB], ["Indicate"], WordFrequency.COMMON),
    "deny": WordEntry("deny", [PartOfSpeech.VERB], ["Refuse, reject"], WordFrequency.COMMON),
    "depress": WordEntry("depress", [PartOfSpeech.VERB], ["Reduce, sadden"], WordFrequency.COMMON),
    "depression": WordEntry("depression", [PartOfSpeech.NOUN], ["Downturn, sadness"], WordFrequency.COMMON),
    "despite": WordEntry("despite", [PartOfSpeech.PREPOSITION], ["In spite of"], WordFrequency.COMMON),
    "detect": WordEntry("detect", [PartOfSpeech.VERB], ["Discover"], WordFrequency.COMMON),
    "detection": WordEntry("detection", [PartOfSpeech.NOUN], ["Discovery"], WordFrequency.COMMON),
    "device": WordEntry("device", [PartOfSpeech.NOUN], ["Tool, gadget"], WordFrequency.COMMON),
    "devote": WordEntry("devote", [PartOfSpeech.VERB], ["Dedicate"], WordFrequency.COMMON),
    "devotion": WordEntry("devotion", [PartOfSpeech.NOUN], ["Dedication"], WordFrequency.COMMON),
    "differentiate": WordEntry("differentiate", [PartOfSpeech.VERB], ["Distinguish"], WordFrequency.COMMON),
    "dimension": WordEntry("dimension", [PartOfSpeech.NOUN], ["Aspect, size"], WordFrequency.COMMON),
    "diminish": WordEntry("diminish", [PartOfSpeech.VERB], ["Reduce"], WordFrequency.COMMON),
    "discrete": WordEntry("discrete", [PartOfSpeech.ADJECTIVE], ["Separate"], WordFrequency.COMMON),
    "discrimination": WordEntry("discrimination", [PartOfSpeech.NOUN], ["Distinction, bias"], WordFrequency.COMMON),
    "displace": WordEntry("displace", [PartOfSpeech.VERB], ["Move, replace"], WordFrequency.COMMON),
    "displacement": WordEntry("displacement", [PartOfSpeech.NOUN], ["Moving"], WordFrequency.COMMON),
    "display": WordEntry("display", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["Show"], WordFrequency.COMMON),
    "dispose": WordEntry("dispose", [PartOfSpeech.VERB], ["Arrange, discard"], WordFrequency.COMMON),
    "distinct": WordEntry("distinct", [PartOfSpeech.ADJECTIVE], ["Different, clear"], WordFrequency.COMMON),
    "distinction": WordEntry("distinction", [PartOfSpeech.NOUN], ["Difference"], WordFrequency.COMMON),
    "distort": WordEntry("distort", [PartOfSpeech.VERB], ["Twist, misrepresent"], WordFrequency.COMMON),
    "distortion": WordEntry("distortion", [PartOfSpeech.NOUN], ["Twisting"], WordFrequency.COMMON),
    "distribute": WordEntry("distribute", [PartOfSpeech.VERB], ["Spread, give out"], WordFrequency.COMMON),
    "distribution": WordEntry("distribution", [PartOfSpeech.NOUN], ["Spreading"], WordFrequency.COMMON),
    "diverse": WordEntry("diverse", [PartOfSpeech.ADJECTIVE], ["Varied"], WordFrequency.COMMON),
    "diversity": WordEntry("diversity", [PartOfSpeech.NOUN], ["Variety"], WordFrequency.COMMON),
    "document": WordEntry("document", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Record"], WordFrequency.COMMON),
    "documentation": WordEntry("documentation", [PartOfSpeech.NOUN], ["Records"], WordFrequency.COMMON),
    "domain": WordEntry("domain", [PartOfSpeech.NOUN], ["Area, field"], WordFrequency.COMMON),
    "domestic": WordEntry("domestic", [PartOfSpeech.ADJECTIVE], ["Home-related, national"], WordFrequency.COMMON),
    "dominate": WordEntry("dominate", [PartOfSpeech.VERB], ["Control"], WordFrequency.COMMON),
    "dominant": WordEntry("dominant", [PartOfSpeech.ADJECTIVE], ["Controlling"], WordFrequency.COMMON),
    "draft": WordEntry("draft", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Preliminary version"], WordFrequency.COMMON),
    "drama": WordEntry("drama", [PartOfSpeech.NOUN], ["Play, intense situation"], WordFrequency.COMMON),
    "dramatic": WordEntry("dramatic", [PartOfSpeech.ADJECTIVE], ["Striking"], WordFrequency.COMMON),
    "duration": WordEntry("duration", [PartOfSpeech.NOUN], ["Length of time"], WordFrequency.COMMON),
    "dynamic": WordEntry("dynamic", [PartOfSpeech.ADJECTIVE], ["Active, changing"], WordFrequency.COMMON),
}


# =============================================================================
# TRANSITION WORDS & DISCOURSE MARKERS
# =============================================================================

DISCOURSE_MARKERS = {
    # Addition
    "furthermore": WordEntry("furthermore", [PartOfSpeech.ADVERB], ["In addition"], WordFrequency.COMMON),
    "moreover": WordEntry("moreover", [PartOfSpeech.ADVERB], ["Besides"], WordFrequency.COMMON),
    "additionally": WordEntry("additionally", [PartOfSpeech.ADVERB], ["Also"], WordFrequency.COMMON),
    "likewise": WordEntry("likewise", [PartOfSpeech.ADVERB], ["Similarly"], WordFrequency.COMMON),
    
    # Contrast
    "however": WordEntry("however", [PartOfSpeech.ADVERB], ["But"], WordFrequency.COMMON),
    "nevertheless": WordEntry("nevertheless", [PartOfSpeech.ADVERB], ["Even so"], WordFrequency.COMMON),
    "nonetheless": WordEntry("nonetheless", [PartOfSpeech.ADVERB], ["Even so"], WordFrequency.COMMON),
    "conversely": WordEntry("conversely", [PartOfSpeech.ADVERB], ["On the other hand"], WordFrequency.COMMON),
    "whereas": WordEntry("whereas", [PartOfSpeech.CONJUNCTION], ["While"], WordFrequency.COMMON),
    "alternatively": WordEntry("alternatively", [PartOfSpeech.ADVERB], ["Or else"], WordFrequency.COMMON),
    
    # Cause/Effect
    "therefore": WordEntry("therefore", [PartOfSpeech.ADVERB], ["Thus"], WordFrequency.COMMON),
    "thus": WordEntry("thus", [PartOfSpeech.ADVERB], ["Therefore"], WordFrequency.COMMON),
    "hence": WordEntry("hence", [PartOfSpeech.ADVERB], ["Therefore"], WordFrequency.COMMON),
    "accordingly": WordEntry("accordingly", [PartOfSpeech.ADVERB], ["As a result"], WordFrequency.COMMON),
    
    # Emphasis
    "indeed": WordEntry("indeed", [PartOfSpeech.ADVERB], ["In fact"], WordFrequency.COMMON),
    "certainly": WordEntry("certainly", [PartOfSpeech.ADVERB], ["Definitely"], WordFrequency.COMMON),
    "undoubtedly": WordEntry("undoubtedly", [PartOfSpeech.ADVERB], ["Certainly"], WordFrequency.COMMON),
    "notably": WordEntry("notably", [PartOfSpeech.ADVERB], ["Especially"], WordFrequency.COMMON),
    "particularly": WordEntry("particularly", [PartOfSpeech.ADVERB], ["Especially"], WordFrequency.COMMON),
    
    # Sequence
    "subsequently": WordEntry("subsequently", [PartOfSpeech.ADVERB], ["After that"], WordFrequency.COMMON),
    "previously": WordEntry("previously", [PartOfSpeech.ADVERB], ["Before"], WordFrequency.COMMON),
    "meanwhile": WordEntry("meanwhile", [PartOfSpeech.ADVERB], ["At the same time"], WordFrequency.COMMON),
    "simultaneously": WordEntry("simultaneously", [PartOfSpeech.ADVERB], ["At the same time"], WordFrequency.COMMON),
    "ultimately": WordEntry("ultimately", [PartOfSpeech.ADVERB], ["Finally"], WordFrequency.COMMON),
    
    # Summary
    "overall": WordEntry("overall", [PartOfSpeech.ADVERB], ["In general"], WordFrequency.COMMON),
    "primarily": WordEntry("primarily", [PartOfSpeech.ADVERB], ["Mainly"], WordFrequency.COMMON),
    "essentially": WordEntry("essentially", [PartOfSpeech.ADVERB], ["Basically"], WordFrequency.COMMON),
    "fundamentally": WordEntry("fundamentally", [PartOfSpeech.ADVERB], ["Basically"], WordFrequency.COMMON),
    "predominantly": WordEntry("predominantly", [PartOfSpeech.ADVERB], ["Mainly"], WordFrequency.COMMON),
}


def load_academic_vocabulary(vocab=None):
    """Load academic vocabulary."""
    from .vocabulary import get_vocabulary
    
    if vocab is None:
        vocab = get_vocabulary()
        
    total_added = 0
    
    for word, entry in ACADEMIC_CORE.items():
        vocab.add_word(entry)
        total_added += 1
        
    for word, entry in DISCOURSE_MARKERS.items():
        vocab.add_word(entry)
        total_added += 1
        
    print(f"[AcademicVocabulary] Loaded {total_added} academic words")
    print(f"[AcademicVocabulary] Total vocabulary: {vocab.vocabulary_size()} words")
    
    return vocab


def get_academic_stats() -> dict:
    """Get academic vocabulary statistics."""
    return {
        "academic_core": len(ACADEMIC_CORE),
        "discourse_markers": len(DISCOURSE_MARKERS),
        "total": len(ACADEMIC_CORE) + len(DISCOURSE_MARKERS)
    }
