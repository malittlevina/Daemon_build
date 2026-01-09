from __future__ import annotations

from typing import List, Tuple

from daemon.unimind.knowledge_store import ConceptCard, KnowledgeStore
from daemon.unimind.mind_palace import MindPalace


def seed_k12(store: KnowledgeStore, palace: MindPalace) -> None:
    """
    Seed a compact K-12 core so recall works immediately.

    This intentionally stays small and structured (cards, not essays).
    """

    cards: List[ConceptCard] = []

    # ---- Math ----
    cards += [
        ConceptCard(
            id="k12.math.fractions",
            title="Fractions",
            definition="A fraction represents a part of a whole: numerator/denominator.",
            constraints=["Denominator cannot be 0"],
            tags=["k12", "math", "arithmetic"],
            examples=["3/4 means 3 parts out of 4 equal parts."],
            related=["k12.math.ratios"],
        ),
        ConceptCard(
            id="k12.math.ratios",
            title="Ratios",
            definition="A ratio compares quantities (a:b). A proportion is an equality of ratios.",
            tags=["k12", "math", "arithmetic"],
            examples=["If 2 apples cost $4, then cost ratio is 2:4 = 1:2."],
            related=["k12.math.fractions"],
        ),
        ConceptCard(
            id="k12.math.linear_equation",
            title="Linear Equations",
            definition="An equation where variables have exponent 1 (e.g., ax + b = c).",
            tags=["k12", "math", "algebra"],
            examples=["Solve 2x + 3 = 11 → x = 4."],
            related=["k12.math.order_of_operations"],
        ),
        ConceptCard(
            id="k12.math.order_of_operations",
            title="Order of Operations (PEMDAS)",
            definition="Rules for evaluating expressions: parentheses, exponents, multiplication/division, addition/subtraction.",
            tags=["k12", "math", "arithmetic"],
            examples=["3 + 2×5 = 13 (multiply before add)."],
        ),
        ConceptCard(
            id="k12.math.pythagorean_theorem",
            title="Pythagorean Theorem",
            definition="In a right triangle, a² + b² = c² (c is the hypotenuse).",
            tags=["k12", "math", "geometry", "geometry.math"],
            examples=["If legs are 3 and 4, hypotenuse is 5."],
        ),
        ConceptCard(
            id="k12.math.mean_median_mode",
            title="Mean, Median, Mode",
            definition="Mean = average; median = middle value; mode = most frequent value.",
            tags=["k12", "math", "statistics"],
            examples=["For 1,2,2,10: mean=3.75, median=2, mode=2."],
        ),
    ]

    # ---- Science ----
    cards += [
        ConceptCard(
            id="k12.science.scientific_method",
            title="Scientific Method",
            definition="Ask a question, form a hypothesis, test with experiments, analyze results, conclude, and iterate.",
            tags=["k12", "science", "earth_science"],
            examples=["Hypothesis: plants grow faster with more light → test with controlled groups."],
        ),
        ConceptCard(
            id="k12.science.cell",
            title="Cell (Basic Biology)",
            definition="The cell is the basic unit of life. Cells have membranes and internal structures that perform functions.",
            tags=["k12", "science", "biology"],
            related=["k12.science.dna"],
        ),
        ConceptCard(
            id="k12.science.dna",
            title="DNA",
            definition="DNA stores genetic information. Genes are segments of DNA that influence traits.",
            tags=["k12", "science", "biology"],
        ),
        ConceptCard(
            id="k12.science.photosynthesis",
            title="Photosynthesis",
            definition="Plants convert light energy into chemical energy: CO₂ + H₂O → glucose + O₂ (simplified).",
            tags=["k12", "science", "biology"],
            examples=["Occurs mainly in chloroplasts in plant cells."],
        ),
        ConceptCard(
            id="k12.science.newtons_laws",
            title="Newton’s Laws of Motion",
            definition="1) Inertia; 2) F=ma; 3) equal and opposite reactions.",
            tags=["k12", "science", "physics"],
            examples=["Doubling mass doubles required force for same acceleration."],
        ),
        ConceptCard(
            id="k12.science.states_of_matter",
            title="States of Matter",
            definition="Common states: solid, liquid, gas (and plasma). Temperature and pressure affect state.",
            tags=["k12", "science", "chemistry"],
        ),
        ConceptCard(
            id="k12.science.water_cycle",
            title="Water Cycle",
            definition="Evaporation → condensation → precipitation → collection/runoff.",
            tags=["k12", "science", "earth_science"],
        ),
    ]

    # ---- History / Civics ----
    cards += [
        ConceptCard(
            id="k12.history.ancient_egypt",
            title="Ancient Egypt (Overview)",
            definition="Ancient civilization along the Nile River known for pharaohs, pyramids, and hieroglyphics.",
            tags=["k12", "history", "ancient"],
        ),
        ConceptCard(
            id="k12.history.industrial_revolution",
            title="Industrial Revolution",
            definition="Period of major industrialization (machines, factories) that changed economies and societies.",
            tags=["k12", "history", "modern"],
        ),
        ConceptCard(
            id="k12.history.american_civil_war",
            title="American Civil War (1861–1865)",
            definition="Conflict between Union and Confederacy; central issues included slavery and states’ rights.",
            tags=["k12", "history", "modern"],
        ),
        ConceptCard(
            id="k12.history.world_war_2",
            title="World War II (1939–1945)",
            definition="Global war involving Axis and Allies; ended with Allied victory and major geopolitical change.",
            tags=["k12", "history", "modern"],
        ),
        ConceptCard(
            id="k12.history.us_constitution",
            title="U.S. Constitution (Basics)",
            definition="Foundational legal document; defines government structure, powers, and rights (via amendments).",
            tags=["k12", "history", "civics"],
        ),
        ConceptCard(
            id="k12.history.branches_of_government",
            title="Branches of Government",
            definition="Legislative makes laws, executive enforces laws, judicial interprets laws (checks and balances).",
            tags=["k12", "history", "civics"],
            related=["k12.history.us_constitution"],
        ),
    ]

    # ---- English / Grammar / Writing ----
    cards += [
        ConceptCard(
            id="k12.english.parts_of_speech",
            title="Parts of Speech",
            definition="Noun, verb, adjective, adverb, pronoun, preposition, conjunction, interjection.",
            tags=["k12", "english", "grammar"],
            examples=["Quickly (adverb) modifies a verb: ran quickly."],
        ),
        ConceptCard(
            id="k12.english.subject_verb_agreement",
            title="Subject–Verb Agreement",
            definition="Singular subjects take singular verbs; plural subjects take plural verbs.",
            tags=["k12", "english", "grammar"],
            examples=["The list of items is on the table (subject: list)."],
        ),
        ConceptCard(
            id="k12.english.punctuation_basics",
            title="Punctuation Basics",
            definition="Periods end statements, commas separate clauses/items, apostrophes show possession or contractions.",
            tags=["k12", "english", "grammar"],
        ),
        ConceptCard(
            id="k12.english.paragraph_structure",
            title="Paragraph Structure",
            definition="A paragraph often has a topic sentence, supporting details, and a concluding/transition sentence.",
            tags=["k12", "english", "writing"],
        ),
        ConceptCard(
            id="k12.english.thesis_statement",
            title="Thesis Statement",
            definition="A concise claim that guides an essay’s argument and structure.",
            tags=["k12", "english", "writing"],
        ),
    ]

    for c in cards:
        out = store.upsert_concept(c)
        palace.place(out.id, tags=out.tags)

