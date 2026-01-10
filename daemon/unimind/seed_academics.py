from __future__ import annotations

from typing import List

from daemon.unimind.knowledge_store import ConceptCard, KnowledgeStore, SkillRecipe
from daemon.unimind.mind_palace import MindPalace


def _upsert_all(store: KnowledgeStore, palace: MindPalace, *, cards: List[ConceptCard], recipes: List[SkillRecipe]) -> None:
    for c in cards:
        out = store.upsert_concept(c)
        palace.place(out.id, tags=out.tags)
    for r in recipes:
        out = store.upsert_recipe(r)
        palace.place(out.id, tags=out.tags)


def seed_geometry_worldbuilding(store: KnowledgeStore, palace: MindPalace) -> None:
    """
    Geometry/worldbuilding fundamentals used for shaping objects and scenes.
    """
    cards: List[ConceptCard] = [
        ConceptCard(
            id="wb.geometry.primitives",
            title="Geometric Primitives",
            definition="Basic shapes used as building blocks: points, lines, planes, triangles, boxes, spheres, cylinders.",
            constraints=["Triangles are the fundamental unit of real-time meshes."],
            tags=["geometry", "worldbuilding", "undergrad", "engineering"],
            examples=["A box primitive can be beveled and hollowed to form a crate."],
            related=["shape.extrude", "shape.bevel"],
        ),
        ConceptCard(
            id="wb.geometry.transforms",
            title="Transforms (Translation/Rotation/Scale)",
            definition="A transform maps points from one coordinate frame to another; commonly represented by 4×4 matrices.",
            constraints=["Non-uniform scale can distort normals; recompute normals or use correct normal matrix."],
            tags=["geometry", "worldbuilding", "undergrad", "engineering", "math"],
            examples=["Rotate 90° around Z to align a doorway on a wall."],
            related=["wb.geometry.coordinate_systems"],
        ),
        ConceptCard(
            id="wb.geometry.coordinate_systems",
            title="Coordinate Systems",
            definition="A coordinate system defines axes and units. World, local, and camera coordinates are common.",
            constraints=["Be consistent about handedness (right-hand vs left-hand) across tools/pipelines."],
            tags=["geometry", "worldbuilding", "undergrad", "engineering"],
            examples=["Local coordinates simplify placing parts relative to a parent object."],
            related=["wb.geometry.transforms"],
        ),
        ConceptCard(
            id="wb.geometry.units_scale",
            title="Units and Scale",
            definition="A consistent unit scale (e.g., 1 unit = 1 meter) prevents physics, animation, and camera issues.",
            constraints=["Physics stability and collision tolerances depend on scale."],
            tags=["geometry", "worldbuilding", "engineering", "undergrad", "physics"],
            examples=["If a character is 1.8m tall, a door might be ~2.1m."],
        ),
        ConceptCard(
            id="wb.geometry.mesh_vs_solid",
            title="Meshes vs Solids (Watertightness)",
            definition="A solid model is 'watertight' (closed surface). Many operations (booleans) assume watertight inputs.",
            constraints=["Non-manifold edges or holes often break boolean operations."],
            tags=["geometry", "worldbuilding", "engineering", "undergrad"],
            examples=["A watertight mesh has every edge shared by exactly two faces."],
            related=["shape.boolean_ops"],
        ),
        ConceptCard(
            id="wb.physics.collision_basics",
            title="Collision Basics",
            definition="Collision detection uses simplified shapes (AABB/OBB, spheres, capsules, convex hulls) for speed.",
            constraints=["Use coarse-to-fine: broadphase (AABB) then narrowphase (convex/mesh)."],
            tags=["geometry", "worldbuilding", "physics", "undergrad", "engineering"],
            examples=["Character controllers often use a capsule collider."],
        ),
        ConceptCard(
            id="wb.materials.pbr_basics",
            title="PBR Material Basics",
            definition="Physically Based Rendering uses consistent maps: albedo/base color, roughness, metallic, normal, AO.",
            constraints=["Albedo should not include baked lighting; roughness controls microfacet scattering."],
            tags=["materials", "worldbuilding", "undergrad", "engineering"],
            examples=["Metal: metallic≈1, dielectric: metallic≈0; roughness controls glossiness."],
        ),
    ]

    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="wb.recipe.watertight_mesh_checklist",
            goal="Validate a mesh before booleans/export (watertight checklist).",
            steps=[
                "Check for holes: ensure the surface is closed.",
                "Check for non-manifold edges (edges shared by 1 or >2 faces).",
                "Remove self-intersections and duplicate vertices.",
                "Recompute normals consistently (outward for solids).",
                "Run an export test and re-import to confirm integrity.",
            ],
            quality_checks=["no non-manifold edges", "consistent normals", "boolean ops succeed"],
            failure_modes=["booleans fail due to open boundaries", "shading artifacts due to flipped normals"],
            tags=["geometry", "worldbuilding", "undergrad", "engineering", "recipe"],
        ),
        SkillRecipe(
            id="wb.recipe.author_pbr_material",
            goal="Author a basic PBR material set for a game asset.",
            steps=[
                "Decide material type (metal vs dielectric) and reference real materials.",
                "Create albedo (no lighting), roughness, metallic, and normal maps.",
                "Keep values physically plausible (avoid pure white albedo except near snow).",
                "Test under neutral HDRI lighting and multiple angles.",
                "Adjust roughness first for realism, then albedo/normal details.",
            ],
            quality_checks=["looks consistent under different lighting", "no baked shadows in albedo"],
            failure_modes=["overly bright albedo causing unrealistic glow", "inverted normal map (Y channel)"],
            tags=["materials", "worldbuilding", "undergrad", "engineering", "recipe"],
        ),
        SkillRecipe(
            id="wb.recipe.build_modular_prop",
            goal="Build a modular world prop that fits a consistent grid/scale.",
            steps=[
                "Choose a unit scale and grid size (e.g., 0.5m increments).",
                "Model using primitives and transforms; keep pivots consistent.",
                "Apply bevels/chamfers for believable edges.",
                "Create simple colliders (box/capsule/convex) aligned to the prop.",
                "Export with consistent naming and verify in-engine placement and snapping.",
            ],
            quality_checks=["snaps to grid", "colliders stable", "scale consistent with other assets"],
            failure_modes=["off-grid pivots break modular placement", "too-detailed colliders cause performance issues"],
            tags=["geometry", "worldbuilding", "engineering", "undergrad", "recipe"],
        ),
    ]

    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_cs_foundations(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="cs.ds.data_structures",
            title="Data Structures (Overview)",
            definition="Ways to organize data to support efficient operations (lookup, insert, delete, traversal).",
            tags=["undergrad", "computer_science", "cs", "data_structures"],
            examples=["Hash maps for fast key lookup; trees for ordered data."],
        ),
        ConceptCard(
            id="cs.algorithms",
            title="Algorithms (Overview)",
            definition="Step-by-step procedures to solve problems; correctness and efficiency are core concerns.",
            tags=["undergrad", "computer_science", "cs"],
            examples=["Binary search finds items in sorted arrays in O(log n)."],
        ),
        ConceptCard(
            id="cs.complexity.big_o",
            title="Big-O Complexity",
            definition="Big-O describes how runtime/memory grows with input size; used to reason about scalability.",
            tags=["undergrad", "computer_science", "cs"],
            examples=["O(n) linear scan, O(n log n) sorting, O(1) hash lookup (average case)."],
        ),
        ConceptCard(
            id="cs.debugging",
            title="Debugging Strategies",
            definition="A systematic process: reproduce, minimize, hypothesize, instrument, test, and fix.",
            tags=["undergrad", "computer_science", "cs", "engineering"],
            examples=["Reduce a failing case to the smallest input that still fails."],
        ),
        ConceptCard(
            id="cs.version_control.mental_model",
            title="Version Control (Git Mental Model)",
            definition="Commits form a directed acyclic graph; branches are pointers; merging reconciles histories.",
            tags=["undergrad", "computer_science", "cs", "engineering"],
            examples=["A branch is a movable label pointing at a commit."],
        ),
    ]

    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="cs.recipe.choose_data_structure",
            goal="Choose an appropriate data structure for a task.",
            steps=[
                "List required operations (lookup/insert/delete/iterate) and their frequency.",
                "Decide if ordering matters (sorted iteration, min/max).",
                "Estimate size and constraints (memory, latency).",
                "Pick candidates (array/list, hash map, tree, heap, graph) and compare big-O and constants.",
                "Prototype and measure if performance is critical.",
            ],
            quality_checks=["operations match structure strengths", "ordering needs satisfied"],
            failure_modes=["choosing a structure that makes a frequent operation expensive"],
            tags=["undergrad", "computer_science", "cs", "data_structures", "recipe"],
        ),
        SkillRecipe(
            id="cs.recipe.big_o_estimation",
            goal="Estimate Big-O for a code path.",
            steps=[
                "Identify the input size variables (n, m, k).",
                "Count loops and nested loops (n, n², etc.).",
                "Account for expensive operations inside loops (sorting, hashing, recursion).",
                "Use worst-case unless average-case is justified and safe.",
                "Validate with a quick benchmark if unsure.",
            ],
            quality_checks=["dominant term identified", "assumptions stated"],
            failure_modes=["missing hidden loops (e.g., list 'in' checks)", "confusing average vs worst case"],
            tags=["undergrad", "computer_science", "cs", "recipe"],
        ),
        SkillRecipe(
            id="cs.recipe.debugging_loop",
            goal="Debug a bug efficiently.",
            steps=[
                "Make the bug reproducible (write a minimal repro or test).",
                "Reduce the repro to the smallest failing case.",
                "Add instrumentation (logs/assertions) at key boundaries.",
                "Form one hypothesis and test it; iterate.",
                "Fix and add a regression test.",
            ],
            quality_checks=["regression test added", "root cause understood"],
            failure_modes=["changing many things at once", "fixing symptom not cause"],
            tags=["undergrad", "computer_science", "engineering", "recipe"],
        ),
        SkillRecipe(
            id="cs.recipe.git_safe_workflow",
            goal="Use Git safely for changes and experiments.",
            steps=[
                "Create a branch for the change.",
                "Commit small, coherent steps with clear messages.",
                "Use `git diff` to review before committing.",
                "Use pull/merge to integrate, resolve conflicts intentionally.",
                "If stuck: make a backup branch or stash, then reset carefully.",
            ],
            quality_checks=["history is understandable", "changes reviewed before merge"],
            failure_modes=["large commits that mix concerns", "force pushing without backups"],
            tags=["undergrad", "computer_science", "engineering", "recipe"],
        ),
    ]

    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_daemon_operating_norms(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="daemon.arch.event_driven",
            title="Event-Driven Architecture",
            definition="A system that reacts to events (messages) from sources; handlers process events and emit new events.",
            constraints=["Handlers should be fast; push slow work to background workers/queues."],
            tags=["graduate", "engineering", "systems", "computer_science"],
        ),
        ConceptCard(
            id="daemon.reliability.failure_modes",
            title="Failure Modes",
            definition="Common failures: timeouts, partial outages, invalid inputs, race conditions, resource exhaustion.",
            tags=["graduate", "engineering", "systems"],
            examples=["Mic adapter missing dependency should emit a system_event, not crash the daemon."],
        ),
        ConceptCard(
            id="daemon.reliability.retry_backoff",
            title="Retry and Backoff",
            definition="Retries should be bounded and spaced (exponential backoff + jitter) to avoid thundering herds.",
            constraints=["Only retry idempotent operations or ensure deduplication."],
            tags=["graduate", "engineering", "systems", "computer_science"],
        ),
        ConceptCard(
            id="daemon.observability.logging_telemetry",
            title="Logging and Telemetry",
            definition="Logs record events; metrics measure rates/latency; traces follow a request across components.",
            constraints=["Do not log secrets; sample high-volume logs."],
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="daemon.safety.enforceable_policies",
            title="Safety/Ethics as Enforceable Policy",
            definition="Policies should be machine-checkable rules that gate actions (approve/reject/review).",
            tags=["graduate", "engineering", "systems", "ethics"],
            examples=["Reject plans containing 'harm' or 'manipulate' unless explicitly safe-reviewed."],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="daemon.recipe.design_handler",
            goal="Design a robust event handler for the daemon.",
            steps=[
                "Validate the event schema (type/payload/source).",
                "Keep the handler fast; push slow work to a queue/worker.",
                "Handle missing dependencies/device errors as soft failures (emit system_event).",
                "Make actions idempotent or add deduplication keys.",
                "Log outcomes and measure latency/error rates.",
            ],
            quality_checks=["handler never crashes daemon loop", "errors become events", "latency bounded"],
            failure_modes=["doing heavy work inline", "logging secrets", "unbounded retries"],
            tags=["graduate", "engineering", "systems", "recipe"],
        ),
        SkillRecipe(
            id="daemon.recipe.retry_policy",
            goal="Implement a safe retry policy for a flaky dependency.",
            steps=[
                "Classify errors: retryable vs non-retryable.",
                "Use exponential backoff with jitter and a max attempt count.",
                "Add timeouts and circuit breakers for repeated failures.",
                "Ensure idempotency (or attach request IDs for deduplication).",
                "Emit metrics: retry_count, success_rate, latency.",
            ],
            quality_checks=["bounded retries", "no retry storms", "idempotency ensured"],
            failure_modes=["retrying non-idempotent calls", "no timeout leading to thread exhaustion"],
            tags=["graduate", "engineering", "systems", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_research_methods(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="research.reading_papers",
            title="Reading Research Papers",
            definition="Skim abstract/figures first, then methods; extract contributions, assumptions, and limitations.",
            tags=["graduate", "research_methods", "computer_science"],
        ),
        ConceptCard(
            id="research.baselines",
            title="Baselines and Evaluation",
            definition="Compare against strong baselines; report metrics and ablations; avoid cherry-picking results.",
            tags=["graduate", "research_methods"],
        ),
        ConceptCard(
            id="research.replication",
            title="Replication and Reproducibility",
            definition="Replication repeats results with the same method; reproducibility includes code/data/config to rerun.",
            constraints=["Track seeds, versions, and environment details."],
            tags=["doctorate", "research_methods"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="research.recipe.paper_summary",
            goal="Summarize a paper into a compact note usable by the daemon.",
            steps=[
                "Write 1–2 sentence problem statement.",
                "List the key contributions (bullets).",
                "Describe the method at a high level (what is new vs standard).",
                "Record datasets/benchmarks and evaluation metrics.",
                "Note assumptions, limitations, and failure cases.",
                "Write 1 idea for follow-up or application.",
            ],
            quality_checks=["captures contributions and limitations", "metrics/datasets included"],
            failure_modes=["rewriting the abstract without extracting method/assumptions"],
            tags=["graduate", "research_methods", "recipe"],
        ),
        SkillRecipe(
            id="research.recipe.experiment_design",
            goal="Design an experiment that tests a hypothesis.",
            steps=[
                "State a falsifiable hypothesis and measurable outcomes.",
                "Define variables/controls and a baseline method.",
                "Choose evaluation metrics and success criteria.",
                "Plan for ablations to isolate the effect of each component.",
                "Record protocol so it can be replicated (config, seeds, data splits).",
            ],
            quality_checks=["clear baseline", "metrics defined", "replication info recorded"],
            failure_modes=["no baseline", "changing multiple factors at once"],
            tags=["doctorate", "research_methods", "recipe"],
        ),
        SkillRecipe(
            id="research.recipe.replication_checklist",
            goal="Replicate a result reliably.",
            steps=[
                "Pin versions (code commit, dependencies, data snapshot).",
                "Record random seeds and hardware details when relevant.",
                "Run the authors’ default settings first (no modifications).",
                "Compare metrics and confirm differences are explained.",
                "Document deviations and create a minimal runnable script.",
            ],
            quality_checks=["versions pinned", "runs reproducibly", "differences explained"],
            failure_modes=["silent data preprocessing differences", "unstated hyperparameters"],
            tags=["doctorate", "research_methods", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_math_beyond_k12(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="math.calculus.derivative",
            title="Derivative (Calculus)",
            definition="The derivative measures instantaneous rate of change; geometrically, slope of the tangent line.",
            tags=["undergrad", "math", "calculus"],
            examples=["d/dx(x²)=2x."],
        ),
        ConceptCard(
            id="math.linear_algebra.matrix",
            title="Matrices (Linear Algebra)",
            definition="Matrices represent linear transformations; multiplication composes transformations.",
            tags=["undergrad", "math", "linear_algebra"],
            examples=["A rotation matrix rotates vectors in a plane."],
        ),
        ConceptCard(
            id="math.probability.bayes",
            title="Bayes’ Rule (Probability)",
            definition="P(A|B) = P(B|A)P(A)/P(B). Useful for updating beliefs given evidence.",
            tags=["undergrad", "math", "probability"],
        ),
        ConceptCard(
            id="math.statistics.confidence_interval",
            title="Confidence Interval (Statistics)",
            definition="A range estimate for a parameter; a 95% interval means the procedure covers the true value 95% of the time.",
            tags=["undergrad", "math", "statistics"],
        ),
        ConceptCard(
            id="math.optimization.gradient_descent",
            title="Gradient Descent (Optimization)",
            definition="Iteratively update parameters in the direction of negative gradient to minimize a loss function.",
            constraints=["Step size (learning rate) must be tuned; too large can diverge."],
            tags=["graduate", "math", "optimization", "computer_science"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="math.recipe.take_derivative",
            goal="Compute a basic derivative.",
            steps=[
                "Rewrite the function in a simple form (expand/simplify).",
                "Apply rules: power rule, sum rule, product/quotient as needed.",
                "Use chain rule for nested functions.",
                "Simplify the result and (optionally) verify numerically at a point.",
            ],
            quality_checks=["rules applied correctly", "result simplified"],
            failure_modes=["missing chain rule", "algebra mistakes"],
            tags=["undergrad", "math", "calculus", "recipe"],
        ),
        SkillRecipe(
            id="math.recipe.matrix_multiply",
            goal="Multiply two matrices A (m×n) and B (n×p).",
            steps=[
                "Confirm inner dimensions match (n).",
                "For each output entry (i,j), compute dot(row i of A, column j of B).",
                "Assemble the m×p result.",
                "Check special cases (identity, zeros) for sanity.",
            ],
            quality_checks=["dimensions correct", "spot-check entries"],
            failure_modes=["mixing row/column order", "dimension mismatch"],
            tags=["undergrad", "math", "linear_algebra", "recipe"],
        ),
        SkillRecipe(
            id="math.recipe.apply_bayes",
            goal="Apply Bayes’ rule to update a probability.",
            steps=[
                "Define events A (hypothesis) and B (evidence).",
                "Write down P(A) (prior), P(B|A) (likelihood), and P(B) (evidence).",
                "Compute P(B) via total probability if needed.",
                "Compute P(A|B) = P(B|A)P(A)/P(B).",
                "Sanity check: result between 0 and 1; compare to prior.",
            ],
            quality_checks=["events defined", "probabilities coherent"],
            failure_modes=["confusing P(A|B) with P(B|A)", "forgetting to compute P(B)"],
            tags=["undergrad", "math", "probability", "recipe"],
        ),
        SkillRecipe(
            id="math.recipe.gradient_descent",
            goal="Run gradient descent on a differentiable loss.",
            steps=[
                "Define the loss L(θ) and compute/approximate ∇L(θ).",
                "Choose a learning rate α and initialize θ.",
                "Iterate θ ← θ − α∇L(θ).",
                "Monitor loss; reduce α or add scheduling if unstable.",
                "Stop when convergence criteria are met (small gradient or no improvement).",
            ],
            quality_checks=["loss decreases", "learning rate stable"],
            failure_modes=["divergence due to large α", "stuck due to poor initialization"],
            tags=["graduate", "math", "optimization", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_physics_simulation(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="phys.vectors",
            title="Vectors",
            definition="Vectors represent magnitude and direction; used for position, velocity, force, etc.",
            tags=["undergrad", "science", "physics", "engineering"],
        ),
        ConceptCard(
            id="phys.kinematics",
            title="Kinematics",
            definition="Describes motion (position, velocity, acceleration) without focusing on forces.",
            tags=["undergrad", "science", "physics"],
            examples=["v = v0 + at; x = x0 + v0 t + 0.5 a t² (constant acceleration)."],
        ),
        ConceptCard(
            id="phys.newton_second",
            title="Newton’s Second Law",
            definition="Force relates to acceleration: F = m a (in an inertial frame).",
            tags=["undergrad", "science", "physics"],
        ),
        ConceptCard(
            id="phys.rigid_body",
            title="Rigid Body Concepts",
            definition="Rigid bodies resist deformation; rotation involves angular velocity, torque, and inertia tensor.",
            tags=["graduate", "science", "physics", "engineering"],
        ),
        ConceptCard(
            id="phys.constraints",
            title="Constraints",
            definition="Constraints restrict motion (joints, contacts). Solvers enforce them approximately each time step.",
            constraints=["Poorly tuned constraints can cause jitter or instability."],
            tags=["graduate", "science", "physics", "engineering"],
        ),
        ConceptCard(
            id="phys.numerical_stability",
            title="Numerical Stability (Simulation)",
            definition="Discrete integration can accumulate error; step size and solver choices determine stability.",
            tags=["graduate", "science", "physics", "math", "engineering"],
            examples=["Explicit Euler is simple but can be unstable for stiff systems."],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="phys.recipe.integrate_motion",
            goal="Integrate motion for a particle with forces.",
            steps=[
                "Compute net force F at the current state.",
                "Compute acceleration a = F/m.",
                "Update velocity v and position x using a time step Δt (semi-implicit Euler is often stable).",
                "Clamp or adapt Δt if the system becomes unstable.",
                "Validate energy behavior for your system (does it explode?).",
            ],
            quality_checks=["stable over time", "units consistent", "Δt appropriate"],
            failure_modes=["too-large Δt causing explosion", "unit mismatch (meters vs centimeters)"],
            tags=["undergrad", "science", "physics", "recipe"],
        ),
        SkillRecipe(
            id="phys.recipe.stable_constraints",
            goal="Tune constraints to reduce jitter in a physics simulation.",
            steps=[
                "Start with simple colliders and correct mass/inertia values.",
                "Use a stable integrator and reasonable time step.",
                "Increase solver iterations gradually (don’t overspend).",
                "Reduce constraint stiffness or add damping when oscillating.",
                "Test edge cases (stacking, sliding contacts, resting contacts).",
            ],
            quality_checks=["minimal jitter", "stacking stable", "performance acceptable"],
            failure_modes=["overly stiff constraints", "insufficient solver iterations"],
            tags=["graduate", "science", "physics", "engineering", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_writing_communication(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="writing.argument_structure",
            title="Argument Structure",
            definition="A good argument states a claim, supports it with reasons/evidence, addresses counterarguments, and concludes.",
            tags=["undergrad", "english", "writing", "humanities"],
        ),
        ConceptCard(
            id="writing.outlining",
            title="Outlining",
            definition="An outline is a hierarchical plan for ideas; it prevents wandering and ensures logical flow.",
            tags=["undergrad", "english", "writing"],
        ),
        ConceptCard(
            id="writing.clarity",
            title="Clarity",
            definition="Clarity comes from precise terms, short sentences, explicit structure, and removing ambiguity.",
            tags=["undergrad", "english", "writing"],
        ),
        ConceptCard(
            id="writing.audience_adaptation",
            title="Audience Adaptation",
            definition="Adjust depth, vocabulary, and examples to match what the audience knows and needs.",
            tags=["undergrad", "english", "writing", "humanities"],
        ),
        ConceptCard(
            id="writing.tech_docs_patterns",
            title="Technical Documentation Patterns",
            definition="Common patterns: quickstart, API reference, tutorials, troubleshooting, and architecture overview.",
            tags=["undergrad", "english", "writing", "computer_science"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="writing.recipe.write_clear_explanation",
            goal="Write a clear explanation of a concept or procedure.",
            steps=[
                "Define the goal and audience.",
                "Give a one-paragraph overview and why it matters.",
                "Explain key terms before using them heavily.",
                "Provide an example and a non-example.",
                "End with a short summary and next steps.",
            ],
            quality_checks=["audience assumptions explicit", "includes example"],
            failure_modes=["using jargon without definitions", "no motivating context"],
            tags=["undergrad", "english", "writing", "recipe"],
        ),
        SkillRecipe(
            id="writing.recipe.tech_doc_page",
            goal="Draft a high-quality technical documentation page.",
            steps=[
                "Write a quickstart that gets the reader to success quickly.",
                "Add conceptual overview and constraints.",
                "Provide API/commands with examples.",
                "Add troubleshooting with common errors and fixes.",
                "Link to deeper references and related topics.",
            ],
            quality_checks=["reader can succeed end-to-end", "errors documented"],
            failure_modes=["missing examples", "only reference docs with no narrative"],
            tags=["undergrad", "english", "writing", "computer_science", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_project_management_agents(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="pm.decomposition",
            title="Task Decomposition",
            definition="Break goals into smaller tasks with clear inputs/outputs; reduce coupling and unknowns.",
            tags=["graduate", "engineering", "systems", "research_methods"],
        ),
        ConceptCard(
            id="pm.dependencies",
            title="Dependency Tracking",
            definition="Track which tasks block others; unblock the critical path first.",
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="pm.estimation",
            title="Estimation",
            definition="Estimate effort by analogy and uncertainty ranges; revise estimates as you learn.",
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="pm.definition_of_done",
            title="Definition of Done",
            definition="A checklist that states when work is complete (tests, docs, review, safety).",
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="pm.postmortems",
            title="Postmortems",
            definition="A structured analysis after failure: what happened, why, and how to prevent recurrence.",
            tags=["graduate", "engineering", "systems", "research_methods"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="pm.recipe.agent_execution_plan",
            goal="Create an execution plan suitable for an agent-based system.",
            steps=[
                "Define the objective and success criteria (Definition of Done).",
                "List tasks and dependencies; identify the critical path.",
                "Assign owners (modules/agents) and interfaces between them.",
                "Choose checkpoints (tests/logs) to validate progress.",
                "Run, measure, and revise plan as new info arrives.",
            ],
            quality_checks=["DoD defined", "dependencies explicit", "checkpoints exist"],
            failure_modes=["ambiguous DoD", "hidden dependencies causing churn"],
            tags=["graduate", "engineering", "systems", "recipe"],
        ),
        SkillRecipe(
            id="pm.recipe.postmortem_template",
            goal="Write a postmortem after an incident.",
            steps=[
                "Describe impact and timeline (what users saw and when).",
                "Identify root causes and contributing factors.",
                "List what went well and what went poorly.",
                "Create action items with owners and deadlines.",
                "Add prevention: tests, monitoring, and policy changes.",
            ],
            quality_checks=["root cause identified", "action items assigned"],
            failure_modes=["blame-focused analysis", "no follow-up owners"],
            tags=["graduate", "engineering", "systems", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_security_basics(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="sec.least_privilege",
            title="Least Privilege",
            definition="Grant only the minimal permissions necessary for a task; reduces blast radius of compromise.",
            tags=["undergrad", "computer_science", "security", "engineering"],
        ),
        ConceptCard(
            id="sec.input_validation",
            title="Input Validation",
            definition="Treat inputs as untrusted; validate type/format/range and reject or sanitize invalid data.",
            constraints=["Prefer allow-lists over block-lists."],
            tags=["undergrad", "computer_science", "security", "engineering"],
        ),
        ConceptCard(
            id="sec.secrets_handling",
            title="Secrets Handling",
            definition="Secrets (API keys, tokens) must not be logged or hardcoded; store in env/secret managers.",
            constraints=["Rotate compromised secrets; scope tokens narrowly."],
            tags=["undergrad", "computer_science", "security", "engineering"],
        ),
        ConceptCard(
            id="sec.threat_modeling",
            title="Threat Modeling",
            definition="Identify assets, attackers, entry points, and mitigations; focus on realistic threats.",
            tags=["graduate", "computer_science", "security", "engineering"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="sec.recipe.threat_model",
            goal="Create a simple threat model for a daemon subsystem.",
            steps=[
                "List assets (secrets, user data, system access).",
                "List entry points (web textbox, mic/camera adapters, file IO).",
                "Enumerate threats (spoofing, tampering, info disclosure, DoS).",
                "Add mitigations (auth, validation, rate limits, least privilege).",
                "Decide what to log and what must never be logged (secrets).",
            ],
            quality_checks=["entry points identified", "mitigations assigned"],
            failure_modes=["missing a major entry point", "logging sensitive data"],
            tags=["graduate", "computer_science", "security", "recipe"],
        ),
        SkillRecipe(
            id="sec.recipe.validate_untrusted_input",
            goal="Validate untrusted input safely.",
            steps=[
                "Define the schema (expected types, required fields).",
                "Apply allow-list validation and length/range limits.",
                "Reject early with clear errors (don’t attempt to 'guess').",
                "Normalize safely (trim whitespace, canonicalize encodings).",
                "Log only non-sensitive metadata; never log raw secrets.",
            ],
            quality_checks=["schema enforced", "limits applied", "no sensitive logs"],
            failure_modes=["overly permissive parsing", "secret leakage in logs"],
            tags=["undergrad", "computer_science", "security", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_logic_reasoning(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="logic.propositional",
            title="Propositional Logic",
            definition="Logic of statements (propositions) combined with connectives: AND, OR, NOT, IMPLIES.",
            constraints=["Validity depends on form, not on the content of propositions."],
            tags=["logic", "reasoning", "undergrad", "proof"],
            examples=["If (P→Q) and P, then Q (modus ponens)."],
        ),
        ConceptCard(
            id="logic.predicate",
            title="Predicate Logic (First-Order Logic)",
            definition="Extends propositional logic with quantifiers (∀, ∃) and predicates over objects.",
            constraints=["Quantifier scope matters; be explicit about domains."],
            tags=["logic", "reasoning", "graduate", "proof"],
            examples=["∀x Human(x) → Mortal(x)."],
        ),
        ConceptCard(
            id="logic.proof_techniques",
            title="Proof Techniques",
            definition="Common proof methods: direct proof, contrapositive, contradiction, induction, construction.",
            tags=["logic", "reasoning", "undergrad", "proof"],
            examples=["Induction proves statements over integers by base case + inductive step."],
        ),
        ConceptCard(
            id="logic.fallacies",
            title="Common Logical Fallacies",
            definition="Patterns of bad reasoning that can sound persuasive (ad hominem, strawman, false dilemma, circular reasoning).",
            tags=["logic", "reasoning", "fallacies", "undergrad"],
            examples=["False dilemma: presenting only two options when more exist."],
        ),
        ConceptCard(
            id="reasoning.cognitive_biases",
            title="Cognitive Biases (Overview)",
            definition="Systematic patterns of deviation from rational judgment (confirmation bias, availability, anchoring).",
            tags=["logic", "reasoning", "graduate", "humanities"],
            examples=["Confirmation bias: noticing evidence that supports your belief and ignoring contrary evidence."],
        ),
        ConceptCard(
            id="reasoning.decision_theory",
            title="Decision Theory (Basics)",
            definition="Choose actions by comparing expected utilities under uncertainty; requires a utility model and probabilities.",
            constraints=["Utility functions encode preferences; mismatched utilities lead to wrong choices."],
            tags=["logic", "reasoning", "decision_theory", "graduate"],
        ),
        ConceptCard(
            id="reasoning.godel",
            title="Gödel’s Incompleteness (High-Level)",
            definition="Any sufficiently expressive consistent formal system cannot prove all true statements about arithmetic within itself.",
            tags=["logic", "reasoning", "doctorate", "proof"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="logic.recipe.check_argument_validity",
            goal="Check whether an argument is logically valid.",
            steps=[
                "Identify premises and conclusion clearly.",
                "Translate into logical form (symbols) if helpful.",
                "Test validity using known rules (modus ponens/tollens) or truth-table/counterexample.",
                "If invalid, produce a counterexample where premises are true but conclusion is false.",
                "If valid, note the rule/structure that justifies it.",
            ],
            quality_checks=["premises separated from conclusion", "counterexample found if invalid"],
            failure_modes=["arguing about truth of premises instead of form", "missing hidden premises"],
            tags=["logic", "reasoning", "undergrad", "recipe"],
        ),
        SkillRecipe(
            id="logic.recipe.proof_by_induction",
            goal="Prove a statement by mathematical induction.",
            steps=[
                "State the proposition P(n) and the domain (typically integers ≥ 0 or ≥ 1).",
                "Prove the base case P(n0).",
                "Assume inductive hypothesis P(k) for arbitrary k ≥ n0.",
                "Prove P(k+1) using the hypothesis.",
                "Conclude P(n) holds for all n ≥ n0.",
            ],
            quality_checks=["base case correct", "inductive step uses hypothesis properly"],
            failure_modes=["assuming P(k+1) (circularity)", "wrong base index"],
            tags=["logic", "reasoning", "proof", "undergrad", "recipe"],
        ),
        SkillRecipe(
            id="reasoning.recipe.expected_utility",
            goal="Choose between options using expected utility.",
            steps=[
                "List options and possible outcomes for each.",
                "Assign probabilities to outcomes (explicitly state uncertainty).",
                "Assign utilities to outcomes (what you value).",
                "Compute expected utility for each option (sum p×u).",
                "Pick the highest expected utility; sanity-check sensitivity to assumptions.",
            ],
            quality_checks=["probabilities sum to 1 per option", "utilities consistent"],
            failure_modes=["confusing probability with utility", "ignoring rare high-impact risks"],
            tags=["logic", "reasoning", "decision_theory", "graduate", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_philosophy(store: KnowledgeStore, palace: MindPalace) -> None:
    cards: List[ConceptCard] = [
        ConceptCard(
            id="phil.epistemology.knowledge",
            title="Epistemology: Knowledge",
            definition="Epistemology studies knowledge—what it is, how we justify beliefs, and limits of certainty.",
            constraints=["Justification matters: true belief alone is not typically considered knowledge."],
            tags=["philosophy", "epistemology", "undergrad", "humanities"],
            examples=["A common framing: knowledge as 'justified true belief' (with known challenges like Gettier cases)."],
        ),
        ConceptCard(
            id="phil.epistemology.gettier",
            title="Gettier Problems (High-Level)",
            definition="Thought experiments suggesting 'justified true belief' can still fail to be knowledge due to luck.",
            tags=["philosophy", "epistemology", "graduate", "humanities"],
        ),
        ConceptCard(
            id="phil.ethics.utilitarianism",
            title="Utilitarianism",
            definition="An ethical view that evaluates actions by consequences—often maximizing overall well-being.",
            constraints=["Requires specifying what counts as well-being and how to aggregate across people."],
            tags=["philosophy", "ethics", "undergrad", "humanities"],
            examples=["Choose the action that produces the greatest net benefit (with caveats about measurement)."],
        ),
        ConceptCard(
            id="phil.ethics.deontology",
            title="Deontology",
            definition="An ethical view that emphasizes duties/rules; some actions are right/wrong regardless of outcomes.",
            tags=["philosophy", "ethics", "undergrad", "humanities"],
            examples=["A rule against lying might hold even if lying could produce better outcomes."],
        ),
        ConceptCard(
            id="phil.ethics.virtue",
            title="Virtue Ethics",
            definition="Ethics focused on character and virtues (e.g., courage, temperance); asks what a good person would do.",
            tags=["philosophy", "ethics", "undergrad", "humanities"],
        ),
        ConceptCard(
            id="phil.metaphysics.identity",
            title="Metaphysics: Identity Over Time",
            definition="Explores what makes an entity the same across time despite change (Ship of Theseus-style problems).",
            tags=["philosophy", "metaphysics", "undergrad", "humanities"],
        ),
        ConceptCard(
            id="phil.mind.consciousness",
            title="Philosophy of Mind: Consciousness",
            definition="Studies subjective experience and mental states; debates include physicalism vs dualism and the 'hard problem'.",
            tags=["philosophy", "mind", "graduate", "humanities"],
        ),
        ConceptCard(
            id="phil.science.demarcation",
            title="Philosophy of Science: Demarcation",
            definition="Questions what distinguishes science from non-science; focuses on testability, falsifiability, and methodology.",
            tags=["philosophy", "science", "graduate", "humanities", "research_methods"],
        ),
        ConceptCard(
            id="phil.political.social_contract",
            title="Political Philosophy: Social Contract",
            definition="Views political legitimacy as arising from an implicit/explicit agreement among individuals to form society and government.",
            tags=["philosophy", "political", "undergrad", "humanities"],
        ),
        ConceptCard(
            id="phil.meta.metaethics",
            title="Metaethics (High-Level)",
            definition="Investigates what moral statements mean (objective facts vs attitudes) and whether moral truths exist.",
            tags=["philosophy", "ethics", "doctorate", "humanities"],
        ),
    ]
    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="phil.recipe.analyze_argument",
            goal="Analyze a philosophical argument carefully.",
            steps=[
                "State the conclusion in one sentence.",
                "List the premises explicitly (number them).",
                "Check validity: does the conclusion follow if premises are true?",
                "Evaluate soundness: are premises plausible/true? what assumptions are hidden?",
                "Consider counterexamples and alternative interpretations.",
            ],
            quality_checks=["premises explicit", "validity vs soundness separated"],
            failure_modes=["attacking conclusions without addressing premises", "equivocation on key terms"],
            tags=["philosophy", "epistemology", "undergrad", "recipe"],
        ),
        SkillRecipe(
            id="phil.recipe.compare_ethics",
            goal="Compare ethical frameworks on a decision.",
            steps=[
                "Describe the decision context and stakeholders.",
                "Apply utilitarian lens (outcomes, harms/benefits).",
                "Apply deontological lens (duties/rights/rules).",
                "Apply virtue lens (character, virtues, long-term habits).",
                "Note where frameworks disagree and why; choose with an explicit rationale.",
            ],
            quality_checks=["each framework applied explicitly", "tradeoffs documented"],
            failure_modes=["mixing frameworks without noticing", "ignoring affected stakeholders"],
            tags=["philosophy", "ethics", "undergrad", "recipe"],
        ),
        SkillRecipe(
            id="phil.recipe.define_terms",
            goal="Define key terms to prevent confusion in discussion.",
            steps=[
                "List ambiguous words central to the debate (e.g., 'knowledge', 'good', 'freedom').",
                "Provide working definitions and note alternatives.",
                "Check whether conclusions depend on one definition vs another.",
                "Replace ambiguous terms with clearer phrasing when possible.",
                "Re-run the argument with clarified terms.",
            ],
            quality_checks=["definitions stated", "ambiguities flagged"],
            failure_modes=["talking past others due to different definitions"],
            tags=["philosophy", "epistemology", "graduate", "recipe"],
        ),
    ]
    _upsert_all(store, palace, cards=cards, recipes=recipes)


def seed_all_advanced(store: KnowledgeStore, palace: MindPalace) -> None:
    """
    Seed all 9 requested categories beyond K-12.
    """
    seed_geometry_worldbuilding(store, palace)
    seed_cs_foundations(store, palace)
    seed_daemon_operating_norms(store, palace)
    seed_research_methods(store, palace)
    seed_math_beyond_k12(store, palace)
    seed_physics_simulation(store, palace)
    seed_writing_communication(store, palace)
    seed_project_management_agents(store, palace)
    seed_security_basics(store, palace)
    seed_logic_reasoning(store, palace)
    seed_philosophy(store, palace)


def seed_deeper_tiers(store: KnowledgeStore, palace: MindPalace) -> None:
    """
    Add deeper (graduate/doctorate) expansions for all existing categories.
    These are intentionally compact but non-placeholder: each card has a real definition
    and each recipe has actionable steps.
    """
    cards: List[ConceptCard] = [
        # ---- Geometry / worldbuilding (grad/phd) ----
        ConceptCard(
            id="wb.geometry.computational_geometry",
            title="Computational Geometry (Overview)",
            definition="Algorithms for geometric problems (intersections, convex hulls, Voronoi/Delaunay, spatial queries).",
            constraints=["Robustness matters: floating-point error can break predicates; use epsilon/robust predicates."],
            tags=["geometry", "worldbuilding", "graduate", "engineering", "computer_science"],
            examples=["Spatial partitioning (BVH) speeds up ray queries and collisions."],
        ),
        ConceptCard(
            id="wb.geometry.sdf",
            title="Signed Distance Fields (SDFs)",
            definition="A scalar field where value is distance to the nearest surface (negative inside, positive outside).",
            constraints=["SDF composition uses min/max and smooth blends; sampling resolution affects detail."],
            tags=["geometry", "worldbuilding", "graduate", "computer_science", "engineering"],
            examples=["Use SDF booleans to model smooth unions procedurally."],
        ),
        ConceptCard(
            id="wb.procgen.grammar",
            title="Procedural Generation via Grammars",
            definition="Rule-based systems (L-systems, shape grammars) generate complex structures from compact rules.",
            constraints=["Rules must avoid infinite expansion; enforce depth/size budgets."],
            tags=["worldbuilding", "doctorate", "computer_science", "research_methods"],
            examples=["A building grammar generates floors/windows based on constraints."],
        ),

        # ---- CS foundations (grad/phd) ----
        ConceptCard(
            id="cs.systems.concurrency",
            title="Concurrency (Threads, Async, Races)",
            definition="Concurrency runs tasks overlapping in time; correctness requires controlling shared-state access (locks, message passing).",
            constraints=["Data races cause non-deterministic bugs; prefer immutable data or queues where possible."],
            tags=["graduate", "computer_science", "systems", "engineering"],
        ),
        ConceptCard(
            id="cs.systems.distributed_systems",
            title="Distributed Systems (Core Ideas)",
            definition="Systems across multiple nodes must handle partial failure, latency, and consistency tradeoffs.",
            constraints=["You cannot assume reliable ordering; design for retries, idempotency, and partitions."],
            tags=["doctorate", "computer_science", "systems", "engineering"],
            examples=["Consensus (Raft/Paxos) replicates state safely under failures."],
        ),
        ConceptCard(
            id="cs.formal.verification",
            title="Formal Verification (Overview)",
            definition="Mathematically proving program properties (safety/liveness) using logic, types, and model checking.",
            tags=["doctorate", "computer_science", "research_methods"],
            examples=["Model checking can prove a protocol never reaches an unsafe state."],
        ),

        # ---- Daemon operating norms (grad/phd) ----
        ConceptCard(
            id="daemon.reliability.chaos_engineering",
            title="Chaos Engineering",
            definition="Deliberately inject failures to validate resilience and reveal weak assumptions before real incidents.",
            constraints=["Use guardrails: limit blast radius; monitor outcomes; revert quickly."],
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="daemon.observability.distributed_tracing",
            title="Distributed Tracing (Spans/Traces)",
            definition="Tracing correlates work across components using trace/span IDs; reveals latency breakdowns and bottlenecks.",
            tags=["graduate", "engineering", "systems"],
            examples=["A trace shows time spent in NLU vs Unimind vs router."],
        ),
        ConceptCard(
            id="daemon.specs.formal_interfaces",
            title="Formal Interfaces and Contracts",
            definition="Precise interface contracts (schemas, invariants) reduce ambiguity and enable verification/testing.",
            tags=["doctorate", "engineering", "systems", "computer_science"],
        ),

        # ---- Research methods (deeper) ----
        ConceptCard(
            id="research.causal_inference",
            title="Causal Inference (High-Level)",
            definition="Distinguishes correlation from causation using assumptions, interventions, and causal graphs.",
            constraints=["Causal claims require strong assumptions or experimental design."],
            tags=["doctorate", "research_methods", "math", "science"],
        ),

        # ---- Math beyond K-12 (grad/phd) ----
        ConceptCard(
            id="math.analysis.real_analysis",
            title="Real Analysis (Graduate Overview)",
            definition="Rigorous foundations of calculus: limits, continuity, differentiation/integration, convergence.",
            tags=["graduate", "math"],
        ),
        ConceptCard(
            id="math.optimization.convex",
            title="Convex Optimization",
            definition="Optimization where the objective and constraints are convex; any local minimum is global.",
            constraints=["Convexity enables strong guarantees and efficient solvers."],
            tags=["graduate", "math", "optimization"],
        ),
        ConceptCard(
            id="math.measure_theory",
            title="Measure Theory (Doctorate Overview)",
            definition="Generalizes length/area/volume; foundation for probability and integration on complex spaces.",
            tags=["doctorate", "math"],
        ),

        # ---- Physics simulation (grad/phd) ----
        ConceptCard(
            id="phys.lagrangian",
            title="Lagrangian Mechanics (Overview)",
            definition="Formulates dynamics using energy: L = T − V; equations of motion from the Euler–Lagrange equation.",
            tags=["graduate", "science", "physics"],
        ),
        ConceptCard(
            id="phys.integrators.symplectic",
            title="Symplectic Integrators",
            definition="Integrators designed to preserve geometric properties (like energy behavior) in Hamiltonian systems.",
            constraints=["Often preferred for long-term stability in conservative systems."],
            tags=["doctorate", "science", "physics", "math"],
        ),

        # ---- Writing/communication (grad/phd) ----
        ConceptCard(
            id="writing.rhetoric",
            title="Rhetoric (Persuasion Tools)",
            definition="Rhetoric studies effective persuasion: ethos (credibility), pathos (emotion), logos (logic).",
            tags=["graduate", "english", "writing", "humanities"],
        ),
        ConceptCard(
            id="writing.scholarly_style",
            title="Scholarly Writing Style",
            definition="A style emphasizing clear claims, evidence, precise definitions, and careful limitation of scope.",
            tags=["doctorate", "english", "writing", "research_methods"],
        ),

        # ---- Project management (grad/phd) ----
        ConceptCard(
            id="pm.risk_management",
            title="Risk Management",
            definition="Identify, assess, and mitigate risks; track probability/impact and trigger conditions.",
            tags=["graduate", "engineering", "systems"],
        ),
        ConceptCard(
            id="pm.sociotechnical",
            title="Sociotechnical Systems",
            definition="Systems where humans and technology co-evolve; incidents often arise from interactions, not single faults.",
            tags=["doctorate", "engineering", "systems", "humanities"],
        ),

        # ---- Security (grad/phd) ----
        ConceptCard(
            id="sec.authn_authz",
            title="Authentication vs Authorization",
            definition="Authentication verifies identity; authorization decides what an identity may do (permissions/policy).",
            tags=["graduate", "computer_science", "security", "engineering"],
        ),
        ConceptCard(
            id="sec.crypto.hashing",
            title="Cryptographic Hashing",
            definition="A one-way function mapping input to fixed-size output; used for integrity and password hashing (with salts).",
            constraints=["Use modern password hashing (bcrypt/argon2) instead of raw SHA for passwords."],
            tags=["undergrad", "computer_science", "security"],
        ),
        ConceptCard(
            id="sec.privacy.differential_privacy",
            title="Differential Privacy (High-Level)",
            definition="A framework that limits what can be learned about any individual from aggregate outputs by adding calibrated noise.",
            tags=["doctorate", "computer_science", "security", "research_methods"],
        ),
    ]

    recipes: List[SkillRecipe] = [
        SkillRecipe(
            id="wb.recipe.sdf_modeling_loop",
            goal="Model a shape procedurally using SDF primitives and operations.",
            steps=[
                "Choose SDF primitives (sphere, box, capsule) and define their parameters.",
                "Combine primitives using min/max (union/intersection/difference).",
                "Add smooth blends where appropriate for natural transitions.",
                "Sample the SDF to a mesh (marching cubes) at a chosen resolution.",
                "Validate watertightness and scale; export and test in-engine.",
            ],
            quality_checks=["mesh stable at target resolution", "watertight surface"],
            failure_modes=["aliasing due to low resolution", "over-smoothing removes key features"],
            tags=["geometry", "worldbuilding", "graduate", "computer_science", "recipe"],
        ),
        SkillRecipe(
            id="cs.recipe.avoid_data_races",
            goal="Avoid data races in a concurrent system.",
            steps=[
                "Identify shared mutable state and who accesses it.",
                "Prefer message passing (queues) over shared memory when possible.",
                "When sharing is necessary, use locks or atomic primitives with clear ownership rules.",
                "Add tests or stress runs that increase concurrency (repeat, randomize timing).",
                "Instrument and log concurrency failures with correlation IDs.",
            ],
            quality_checks=["no unsynchronized shared writes", "stress test passes repeatedly"],
            failure_modes=["lock order deadlocks", "race conditions only appearing under load"],
            tags=["graduate", "computer_science", "systems", "recipe"],
        ),
        SkillRecipe(
            id="daemon.recipe.chaos_test_plan",
            goal="Design a safe chaos engineering experiment.",
            steps=[
                "Pick a hypothesis (e.g., 'daemon remains responsive if mic fails').",
                "Define blast radius and rollback plan (feature flags, time limits).",
                "Inject one failure mode (dependency missing, timeout, queue overload).",
                "Observe metrics/logs; confirm the hypothesis or record deviations.",
                "Convert learnings into fixes and regression tests.",
            ],
            quality_checks=["safe rollback exists", "metrics observed", "action items created"],
            failure_modes=["too-large blast radius", "no monitoring so outcomes are unclear"],
            tags=["graduate", "engineering", "systems", "recipe"],
        ),
        SkillRecipe(
            id="math.recipe.check_convexity",
            goal="Check whether a function is convex (basic cases).",
            steps=[
                "Use known convex functions and closure properties (sums, affine composition).",
                "For twice-differentiable functions in 1D, check second derivative ≥ 0.",
                "In multiple dimensions, check Hessian is positive semidefinite (where applicable).",
                "State the domain clearly; convexity depends on domain.",
                "If unsure, consult references or test numerically (not a proof).",
            ],
            quality_checks=["domain stated", "criterion applied correctly"],
            failure_modes=["ignoring domain restrictions", "confusing local curvature with global convexity"],
            tags=["graduate", "math", "optimization", "recipe"],
        ),
        SkillRecipe(
            id="sec.recipe.authz_policy",
            goal="Design an authorization policy for a daemon feature.",
            steps=[
                "Define roles/identities (user, daemon, subsystem) and assets (files, sensors, network).",
                "Define allowed actions per role (least privilege).",
                "Implement checks at the boundary (router/adapter) not deep inside internals.",
                "Log decisions with non-sensitive metadata for auditing.",
                "Test denial cases and escalation attempts.",
            ],
            quality_checks=["least privilege enforced", "denials tested", "logs safe"],
            failure_modes=["implicit trust between modules", "policy bypass via alternate path"],
            tags=["graduate", "computer_science", "security", "recipe"],
        ),
        SkillRecipe(
            id="research.recipe.ablation_study",
            goal="Run an ablation study to understand which components matter.",
            steps=[
                "Define a full system and a baseline system.",
                "Remove or alter one component at a time (keep everything else fixed).",
                "Measure the same metrics and report variance (multiple runs).",
                "Interpret results cautiously; interactions can hide effects.",
                "Document configs so others can replicate.",
            ],
            quality_checks=["one factor changed at a time", "variance reported"],
            failure_modes=["multiple confounds", "over-interpreting noisy results"],
            tags=["doctorate", "research_methods", "recipe"],
        ),
    ]

    _upsert_all(store, palace, cards=cards, recipes=recipes)

