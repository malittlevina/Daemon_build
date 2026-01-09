from __future__ import annotations

from typing import List, Tuple

from daemon.unimind.knowledge_store import ConceptCard, KnowledgeStore, SkillRecipe
from daemon.unimind.mind_palace import MindPalace


def seed_k12(store: KnowledgeStore, palace: MindPalace) -> None:
    """
    Seed a compact K-12 core so recall works immediately.

    This intentionally stays small and structured (cards, not essays).
    """

    cards: List[ConceptCard] = []
    recipes: List[SkillRecipe] = []

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

    # ---- K-12 procedural recipes (small, reusable) ----
    recipes += [
        SkillRecipe(
            id="k12.recipe.solve_linear_equations",
            goal="Solve a one-variable linear equation (ax + b = c).",
            steps=[
                "Simplify both sides (combine like terms).",
                "Move variable terms to one side (add/subtract the same value on both sides).",
                "Move constants to the other side.",
                "Divide both sides by the coefficient of x.",
                "Check by substituting the solution back into the original equation.",
            ],
            quality_checks=["solution satisfies original equation"],
            failure_modes=["forgetting to apply an operation to both sides", "sign errors when moving terms"],
            tags=["k12", "math", "algebra", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.add_fractions",
            goal="Add or subtract fractions.",
            steps=[
                "Find a common denominator (least common multiple is ideal).",
                "Rewrite each fraction with the common denominator.",
                "Add/subtract numerators; keep the denominator the same.",
                "Simplify the resulting fraction (reduce by greatest common factor).",
                "Convert to a mixed number if needed.",
            ],
            quality_checks=["fraction reduced/simplified"],
            failure_modes=["adding denominators directly", "not simplifying"],
            tags=["k12", "math", "arithmetic", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.use_pythagorean_theorem",
            goal="Use the Pythagorean theorem to find a missing side in a right triangle.",
            steps=[
                "Identify the hypotenuse (side opposite the right angle).",
                "Assign legs as a and b, hypotenuse as c.",
                "Use a² + b² = c² and plug in known values.",
                "Solve for the unknown (square root if needed).",
                "Check if the result is reasonable for triangle side lengths.",
            ],
            quality_checks=["used hypotenuse correctly", "units consistent"],
            failure_modes=["mixing up hypotenuse vs legs", "forgetting square root"],
            tags=["k12", "math", "geometry", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.scientific_method",
            goal="Design a simple experiment using the scientific method.",
            steps=[
                "Ask a clear, testable question.",
                "Write a hypothesis (If… then… because…).",
                "Identify variables: independent, dependent, and controlled.",
                "Run the experiment and record observations/data.",
                "Analyze results and decide whether they support the hypothesis.",
                "Write a conclusion and propose next questions.",
            ],
            quality_checks=["controls identified", "measurements recorded"],
            failure_modes=["changing multiple variables at once", "small sample/biased observations"],
            tags=["k12", "science", "earth_science", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.write_paragraph",
            goal="Write a clear academic paragraph.",
            steps=[
                "Write a topic sentence that states the main point.",
                "Add 2–4 supporting sentences (facts, reasoning, examples).",
                "Use transitions for flow (however, therefore, for example).",
                "Write a concluding/bridge sentence that links to the next idea.",
                "Revise for clarity, grammar, and concision.",
            ],
            quality_checks=["single main idea", "topic sentence matches support"],
            failure_modes=["multiple topics in one paragraph", "no evidence/examples"],
            tags=["k12", "english", "writing", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.subject_verb_agreement_check",
            goal="Check subject–verb agreement in a sentence.",
            steps=[
                "Find the main verb.",
                "Ask 'who/what is doing the action?' to find the subject.",
                "Ignore prepositional phrases between subject and verb (e.g., 'of the…').",
                "Make the verb match the subject (singular vs plural).",
                "Re-read the sentence for meaning and correctness.",
            ],
            quality_checks=["main subject identified", "verb matches subject number"],
            failure_modes=["agreeing with a nearby noun instead of the true subject"],
            tags=["k12", "english", "grammar", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.read_history_timeline",
            goal="Summarize a historical period as a simple timeline.",
            steps=[
                "Identify the start/end dates (or approximate era).",
                "List key events in chronological order.",
                "Add causes and effects for major events (1–2 lines each).",
                "Note important people/locations involved.",
                "Write a brief summary of what changed over the period.",
            ],
            quality_checks=["events in chronological order", "cause/effect included"],
            failure_modes=["mixing up event order", "listing facts without explaining impact"],
            tags=["k12", "history", "modern", "recipe"],
        ),
        SkillRecipe(
            id="k12.recipe.explain_branches_government",
            goal="Explain the three branches of government and checks/balances.",
            steps=[
                "Name each branch: legislative, executive, judicial.",
                "State each branch’s main role (make/enforce/interpret laws).",
                "Give 1–2 examples of checks and balances (e.g., veto, judicial review).",
                "Explain why checks and balances matter (prevent abuse of power).",
            ],
            quality_checks=["roles correct", "at least one check/balance example"],
            failure_modes=["mixing roles of branches", "missing how they constrain each other"],
            tags=["k12", "history", "civics", "recipe"],
        ),
    ]

    for r in recipes:
        out = store.upsert_recipe(r)
        palace.place(out.id, tags=out.tags)

