# unimind/models/native/advanced_data.py
# Advanced Training Data - Problem Solving, Creativity, and Expert Skills

"""
Advanced training data for higher-order cognitive skills.
Includes problem-solving, creativity, systems thinking, and expert methodologies.
"""

from typing import List, Tuple, Dict

# =============================================================================
# PROBLEM SOLVING FRAMEWORKS
# =============================================================================

PROBLEM_SOLVING = [
    ("how do i approach complex problems",
     "For complex problems: 1) Define precisely what you're trying to solve, 2) Break into smaller sub-problems, 3) Identify constraints and resources, 4) Research similar solved problems, 5) Generate multiple solution approaches, 6) Evaluate trade-offs of each approach, 7) Start with simplest viable solution, 8) Iterate and improve based on feedback, 9) Document your solution."),
    
    ("how do i break down problems",
     "Breaking down problems: 1) State the main problem clearly, 2) Identify components or aspects, 3) Find dependencies between parts, 4) Prioritize by impact or sequence, 5) Define success criteria for each part, 6) Solve smaller problems first, 7) Integrate solutions, 8) Test the complete solution. Use techniques like mind mapping or work breakdown structures."),
    
    ("what is first principles thinking",
     "First principles thinking: Strip a problem to its fundamental truths and build up from there. Steps: 1) Identify assumptions, 2) Break down to basic elements, 3) Question each element, 4) Rebuild from verified foundations. Example: Elon Musk on batteries - instead of accepting high costs, he analyzed raw materials and found they were cheap, so he built his own."),
    
    ("how do i think systematically",
     "Systematic thinking: 1) See the whole system, not just parts, 2) Identify components and their relationships, 3) Look for feedback loops, 4) Consider second-order effects, 5) Find leverage points, 6) Model the system, 7) Test interventions, 8) Monitor unintended consequences. Systems thinking reveals why quick fixes often fail."),
    
    ("how do i debug problems",
     "Debugging approach: 1) Reproduce the problem reliably, 2) Gather information (logs, errors, context), 3) Form hypotheses about cause, 4) Test hypotheses one at a time, 5) Isolate the problem (binary search), 6) Trace the flow of execution/logic, 7) Check recent changes, 8) Ask 'What changed?', 9) Fix and verify, 10) Prevent recurrence."),
    
    ("how do i find root causes",
     "Root cause analysis: 1) Define the problem clearly, 2) Ask 'Why?' five times (5 Whys technique), 3) Create a cause-effect diagram (fishbone), 4) Distinguish symptoms from causes, 5) Look for systemic issues, 6) Verify the root cause, 7) Address the root, not just symptoms, 8) Implement preventive measures."),
    
    ("how do i prioritize problems",
     "Prioritization frameworks: 1) Eisenhower Matrix (urgent vs important), 2) Impact/Effort matrix, 3) MoSCoW (Must/Should/Could/Won't), 4) Pareto principle (80/20 rule), 5) Consider dependencies, 6) Evaluate cost of delay, 7) Align with goals, 8) Consult stakeholders, 9) Time-box decisions."),
    
    ("how do i handle uncertainty",
     "Handling uncertainty: 1) Gather more information if possible, 2) Identify what you can and can't control, 3) Make reversible decisions quickly, 4) Use probabilistic thinking, 5) Prepare multiple scenarios, 6) Build in flexibility, 7) Start small and iterate, 8) Accept that perfect information rarely exists, 9) Learn from outcomes."),
]

# =============================================================================
# CREATIVITY AND INNOVATION
# =============================================================================

CREATIVITY = [
    ("how do i be more creative",
     "Boosting creativity: 1) Expose yourself to diverse ideas, 2) Make unexpected connections, 3) Ask 'What if?' and 'Why not?', 4) Practice divergent thinking, 5) Take breaks to incubate ideas, 6) Keep an idea journal, 7) Embrace constraints (they spark creativity), 8) Don't judge ideas too early, 9) Collaborate with different perspectives, 10) Play and experiment."),
    
    ("how do i brainstorm",
     "Effective brainstorming: 1) Define the challenge clearly, 2) Set a time limit, 3) Quantity over quality first, 4) No criticism during generation, 5) Build on others' ideas, 6) Encourage wild ideas, 7) Use prompts like SCAMPER, 8) Take breaks, 9) Combine and improve ideas, 10) Evaluate afterward with criteria."),
    
    ("what is scamper",
     "SCAMPER is a creativity technique: Substitute (what else could we use?), Combine (what could we merge?), Adapt (what could we copy/adapt?), Modify (change size, shape, color?), Put to other uses (other applications?), Eliminate (what could we remove?), Reverse/Rearrange (flip or reorder?). Apply each to your problem for new ideas."),
    
    ("how do i generate ideas",
     "Idea generation techniques: 1) Mind mapping, 2) Brainstorming, 3) SCAMPER, 4) Random word association, 5) Analogies from other fields, 6) Reverse thinking (opposite of what you want), 7) Six Thinking Hats, 8) Worst possible idea (then invert), 9) Constraints (what if you had half the resources?), 10) Sleep on it - incubation works."),
    
    ("how do i think outside the box",
     "Thinking differently: 1) Challenge assumptions explicitly, 2) Ask 'Why is it done this way?', 3) Look at how other industries solve similar problems, 4) Invert the problem, 5) Remove all constraints temporarily, 6) Seek diverse perspectives, 7) Use random stimuli for association, 8) Travel or change environment, 9) Learn from outsiders, 10) Question the question itself."),
    
    ("how do i innovate",
     "Innovation process: 1) Deeply understand the problem and users, 2) Study existing solutions and their gaps, 3) Look to adjacent fields for inspiration, 4) Generate many ideas, 5) Prototype quickly and cheaply, 6) Get feedback early, 7) Iterate based on learning, 8) Build a minimum viable product, 9) Test with real users, 10) Scale what works."),
    
    ("how do i overcome creative blocks",
     "Overcoming blocks: 1) Change your environment, 2) Take a break - walk, shower, sleep, 3) Lower your standards temporarily - just produce, 4) Work on a different part, 5) Set constraints to focus, 6) Use prompts or random inputs, 7) Talk to someone about it, 8) Review past work for inspiration, 9) Accept that struggle is normal, 10) Just start - momentum helps."),
]

# =============================================================================
# ANALYTICAL THINKING
# =============================================================================

ANALYTICAL = [
    ("how do i analyze data",
     "Data analysis approach: 1) Understand the question you're answering, 2) Examine the data - size, types, quality, 3) Clean and prepare the data, 4) Explore with summaries and visualizations, 5) Look for patterns and anomalies, 6) Form and test hypotheses, 7) Consider confounding factors, 8) Draw conclusions cautiously, 9) Communicate findings clearly, 10) Document your process."),
    
    ("how do i interpret information",
     "Interpreting information: 1) Consider the source and its reliability, 2) Distinguish facts from opinions, 3) Look for context, 4) Identify what's missing, 5) Check for bias, 6) Compare with other sources, 7) Consider alternative interpretations, 8) Look at trends, not just snapshots, 9) Be aware of your own biases, 10) Draw tentative conclusions, not absolutes."),
    
    ("how do i compare options",
     "Comparing options: 1) Define evaluation criteria, 2) Weight criteria by importance, 3) Score each option on each criterion, 4) Calculate weighted scores, 5) Consider qualitative factors, 6) Identify deal-breakers, 7) Consider reversibility, 8) Think about implementation, 9) Consider opportunity costs, 10) Make a decision matrix for complex choices."),
    
    ("how do i evaluate ideas",
     "Evaluating ideas: 1) Define success criteria first, 2) Assess feasibility (technical, resource, time), 3) Estimate impact if successful, 4) Consider risks and how to mitigate, 5) Check alignment with goals, 6) Gather diverse perspectives, 7) Prototype or test if possible, 8) Consider long-term effects, 9) Trust intuition as one input, 10) Decide, then commit."),
    
    ("how do i find patterns",
     "Finding patterns: 1) Look at data from different angles, 2) Group similar items, 3) Look for trends over time, 4) Identify outliers and investigate, 5) Use visualization, 6) Compare to expected patterns, 7) Look for correlations, 8) Consider context, 9) Verify patterns aren't coincidental, 10) Use pattern recognition frameworks."),
    
    ("how do i make predictions",
     "Making predictions: 1) Gather historical data, 2) Identify relevant variables, 3) Look for causal relationships, 4) Consider external factors, 5) Build a mental model, 6) Make probabilistic predictions, not certainties, 7) State assumptions explicitly, 8) Track predictions and outcomes, 9) Learn from incorrect predictions, 10) Update models with new information."),
]

# =============================================================================
# COMMUNICATION SKILLS
# =============================================================================

COMMUNICATION = [
    ("how do i explain technical concepts",
     "Explaining technical concepts: 1) Know your audience's background, 2) Start with 'why it matters', 3) Use analogies to familiar things, 4) Avoid jargon or define it, 5) Build from simple to complex, 6) Use visuals and diagrams, 7) Give concrete examples, 8) Check understanding frequently, 9) Encourage questions, 10) Summarize key points."),
    
    ("how do i present ideas",
     "Presenting ideas: 1) Start with the key message, 2) Structure clearly (intro, body, conclusion), 3) Use the rule of three, 4) Tell stories and give examples, 5) Use visuals effectively, 6) Practice delivery, 7) Engage the audience, 8) Anticipate questions, 9) End with a call to action, 10) Keep it concise."),
    
    ("how do i write clearly",
     "Clear writing: 1) Know your purpose and audience, 2) Start with your main point, 3) Use short sentences, 4) Use simple words, 5) One idea per paragraph, 6) Use active voice, 7) Cut unnecessary words, 8) Use transitions between ideas, 9) Read aloud to check flow, 10) Revise and edit ruthlessly."),
    
    ("how do i persuade people",
     "Persuasion: 1) Understand their perspective first, 2) Build credibility, 3) Find common ground, 4) Use logic and evidence, 5) Appeal to emotions appropriately, 6) Address counterarguments, 7) Use stories and examples, 8) Make it easy to say yes, 9) Be genuine, not manipulative, 10) Follow up on commitments."),
    
    ("how do i have better conversations",
     "Better conversations: 1) Listen actively - focus on understanding, 2) Ask open-ended questions, 3) Be genuinely curious, 4) Avoid interrupting, 5) Reflect back what you hear, 6) Share relevant experiences, 7) Stay present - don't plan your response while they talk, 8) Accept different viewpoints, 9) Ask follow-up questions, 10) End gracefully."),
    
    ("how do i give feedback",
     "Giving feedback: 1) Be specific, not general, 2) Focus on behavior, not personality, 3) Give examples, 4) Be timely, 5) Balance positive and constructive, 6) Suggest improvements, 7) Make it actionable, 8) Check understanding, 9) Follow up, 10) Create psychological safety."),
]

# =============================================================================
# EXPERT SKILLS
# =============================================================================

EXPERT_SKILLS = [
    ("how do i develop expertise",
     "Developing expertise: 1) Deliberate practice on weak areas, 2) Get expert feedback, 3) Study the best in your field, 4) Build deep foundational knowledge, 5) Push beyond comfort zone, 6) Reflect on performance, 7) Create mental models, 8) Stay current with the field, 9) Teach others, 10) Put in the years - no shortcuts."),
    
    ("how do i build mental models",
     "Building mental models: 1) Study how experts think, 2) Learn frameworks across domains, 3) Extract principles from experience, 4) Connect related concepts, 5) Test your models against reality, 6) Refine based on outcomes, 7) Build a toolkit of useful models, 8) Apply models to new situations, 9) Share and discuss with others."),
    
    ("how do i think strategically",
     "Strategic thinking: 1) Define long-term vision, 2) Analyze current position honestly, 3) Identify key leverage points, 4) Consider competitors/alternatives, 5) Think about second-order effects, 6) Plan for multiple scenarios, 7) Balance short and long term, 8) Build in flexibility, 9) Align resources with strategy, 10) Review and adapt regularly."),
    
    ("how do i learn from mistakes",
     "Learning from mistakes: 1) Acknowledge the mistake, 2) Don't dwell or shame yourself, 3) Analyze what happened objectively, 4) Identify the root cause, 5) Extract the lesson, 6) Create a plan to prevent recurrence, 7) Implement the fix, 8) Track if it works, 9) Share learnings with others, 10) View mistakes as valuable data."),
    
    ("how do i build good habits",
     "Building habits: 1) Start tiny - absurdly small, 2) Anchor to existing habits, 3) Make it obvious (cues), 4) Make it attractive (rewards), 5) Make it easy (reduce friction), 6) Make it satisfying (track progress), 7) Never miss twice, 8) Be patient - habits take weeks, 9) Environment design matters, 10) Identity change: 'I am someone who...'"),
    
    ("how do i manage my time",
     "Time management: 1) Know your priorities, 2) Plan your day/week, 3) Time-block for deep work, 4) Batch similar tasks, 5) Say no to non-essentials, 6) Use deadlines (real or artificial), 7) Take breaks to stay fresh, 8) Minimize context switching, 9) Automate repetitive tasks, 10) Review what's working."),
    
    ("how do i stay current in my field",
     "Staying current: 1) Follow key publications and journals, 2) Attend conferences, 3) Join professional communities, 4) Follow thought leaders, 5) Set up alerts for new research, 6) Take continuing education, 7) Network with peers, 8) Experiment with new tools/methods, 9) Teach - it forces you to stay current, 10) Dedicate regular time for learning."),
]

# =============================================================================
# METACOGNITION
# =============================================================================

METACOGNITION = [
    ("how do i learn how to learn",
     "Learning to learn: 1) Understand how memory works, 2) Use evidence-based techniques, 3) Monitor your understanding (test yourself), 4) Identify effective strategies for you, 5) Reflect on what worked and what didn't, 6) Adjust your approach based on results, 7) Practice metacognition, 8) Be patient with yourself, 9) Seek feedback, 10) Keep experimenting."),
    
    ("how do i know what i don't know",
     "Recognizing knowledge gaps: 1) Try to explain the topic - gaps appear, 2) Ask yourself detailed questions, 3) Take practice tests, 4) Compare your knowledge to experts, 5) Seek feedback from others, 6) Notice confusion or uncertainty, 7) Be honest about limitations, 8) Embrace 'I don't know', 9) Use the Dunning-Kruger effect awareness, 10) Stay humble and curious."),
    
    ("how do i improve my thinking",
     "Improving thinking: 1) Learn about cognitive biases, 2) Practice critical thinking, 3) Seek diverse perspectives, 4) Question your assumptions, 5) Use frameworks and models, 6) Slow down important decisions, 7) Keep a thinking journal, 8) Get feedback on your reasoning, 9) Read widely, 10) Practice deliberate reasoning."),
    
    ("how do i reflect effectively",
     "Effective reflection: 1) Set aside dedicated time, 2) Ask specific questions (What worked? What didn't?), 3) Be honest with yourself, 4) Look for patterns, 5) Identify lessons and actions, 6) Write it down, 7) Review past reflections, 8) Balance analysis with forward-looking, 9) Make reflection a habit, 10) Act on insights."),
]

# =============================================================================
# RESEARCH AND STUDY COMMANDS
# =============================================================================

RESEARCH_COMMANDS = [
    {
        "patterns": ["research", "study", "investigate", "learn about", "understand"],
        "intent": "research",
        "action": "start_research",
        "response": "I can help you research that topic. Let's start by defining what specifically you want to learn, then we'll identify the best sources and create a study plan."
    },
    {
        "patterns": ["explain", "teach me", "help me understand", "what is", "how does"],
        "intent": "learn",
        "action": "explain_concept",
        "response": "I'd be happy to explain that. Let me break it down into understandable parts, starting with the fundamentals."
    },
    {
        "patterns": ["summarize", "key points", "main ideas", "tldr", "overview"],
        "intent": "summarize",
        "action": "summarize_topic",
        "response": "Let me provide a concise summary of the key points for you."
    },
    {
        "patterns": ["compare", "difference between", "versus", "vs", "contrast"],
        "intent": "compare",
        "action": "compare_concepts",
        "response": "Let me compare these for you, highlighting the similarities and differences."
    },
    {
        "patterns": ["quiz me", "test me", "check my understanding", "practice"],
        "intent": "practice",
        "action": "quiz_user",
        "response": "Great idea to test your knowledge! Let me ask you some questions about what you've learned."
    },
    {
        "patterns": ["create study plan", "learning path", "how should i learn", "curriculum"],
        "intent": "plan_learning",
        "action": "create_study_plan",
        "response": "Let's create a personalized study plan. What's your goal, how much time do you have, and what's your current level?"
    },
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_advanced_conversations() -> List[Tuple[str, str]]:
    """Get all advanced conversation pairs."""
    pairs = []
    pairs.extend(PROBLEM_SOLVING)
    pairs.extend(CREATIVITY)
    pairs.extend(ANALYTICAL)
    pairs.extend(COMMUNICATION)
    pairs.extend(EXPERT_SKILLS)
    pairs.extend(METACOGNITION)
    return pairs


def get_all_advanced_texts() -> List[str]:
    """Get all advanced texts for training."""
    texts = []
    
    # Add conversation pairs
    for q, a in get_advanced_conversations():
        texts.extend([q, a])
        
    # Add command patterns
    for cmd in RESEARCH_COMMANDS:
        texts.extend(cmd["patterns"])
        texts.append(cmd["response"])
        
    return texts


def get_research_commands() -> List[Dict]:
    """Get research-related command patterns."""
    return RESEARCH_COMMANDS


# Statistics
ADVANCED_STATS = {
    "problem_solving": len(PROBLEM_SOLVING),
    "creativity": len(CREATIVITY),
    "analytical": len(ANALYTICAL),
    "communication": len(COMMUNICATION),
    "expert_skills": len(EXPERT_SKILLS),
    "metacognition": len(METACOGNITION),
    "research_commands": len(RESEARCH_COMMANDS),
}
