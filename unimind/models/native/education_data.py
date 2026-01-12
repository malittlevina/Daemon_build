# unimind/models/native/education_data.py
# Advanced Education and Research Training Data

"""
Comprehensive training data for education, research, and learning capabilities.
This enables the daemon to help with studying, research, and knowledge acquisition.
"""

from typing import List, Tuple, Dict

# =============================================================================
# LEARNING STRATEGIES AND STUDY TECHNIQUES
# =============================================================================

LEARNING_CONVERSATIONS = [
    # Study techniques
    ("how do i study effectively", 
     "Effective studying involves: 1) Active recall - test yourself instead of re-reading, 2) Spaced repetition - review at increasing intervals, 3) Interleaving - mix different topics, 4) Elaboration - explain concepts in your own words, 5) Take breaks using the Pomodoro technique (25 min work, 5 min break)."),
    
    ("what is the best way to learn",
     "The best learning approach combines: Active learning (doing, not just reading), teaching others (the Feynman technique), connecting new info to what you know, regular practice with feedback, and adequate sleep for memory consolidation. Everyone learns differently - experiment to find your style!"),
    
    ("how do i remember things better",
     "To improve memory: 1) Use mnemonics and memory palaces, 2) Create associations and stories, 3) Practice spaced repetition, 4) Get enough sleep (critical for memory), 5) Exercise regularly (boosts brain health), 6) Teach what you learn to others, 7) Use multiple senses when learning."),
    
    ("what is spaced repetition",
     "Spaced repetition is a learning technique where you review information at gradually increasing intervals. Instead of cramming, you might review after 1 day, then 3 days, then 1 week, then 2 weeks. This exploits how memory works - each review strengthens the neural pathways. Apps like Anki use this method."),
    
    ("what is active recall",
     "Active recall means actively trying to remember information without looking at the source. Instead of re-reading notes, you close them and try to recall key points. This strengthens memory far more than passive review. Use flashcards, practice tests, or simply try to write down everything you remember."),
    
    ("what is the feynman technique",
     "The Feynman Technique is a learning method: 1) Choose a concept to learn, 2) Explain it as if teaching a child - use simple words, 3) Identify gaps in your explanation - these are knowledge gaps, 4) Go back to the source and learn those gaps, 5) Simplify and use analogies. If you can't explain it simply, you don't understand it well enough."),
    
    ("how do i take better notes",
     "Effective note-taking strategies: 1) Cornell Method - divide page into notes, cues, and summary, 2) Mind mapping - visual connections between ideas, 3) Outline method - hierarchical structure, 4) Write in your own words, don't copy verbatim, 5) Review and summarize notes within 24 hours, 6) Use abbreviations and symbols, 7) Leave space for later additions."),
    
    ("how do i focus better",
     "To improve focus: 1) Remove distractions (phone, notifications), 2) Use the Pomodoro technique (timed work sessions), 3) Create a dedicated study environment, 4) Exercise before studying, 5) Get enough sleep, 6) Practice mindfulness/meditation, 7) Break large tasks into smaller ones, 8) Set clear goals for each session."),
    
    ("how do i stop procrastinating",
     "Combat procrastination: 1) Start with just 2 minutes - momentum builds, 2) Break tasks into tiny steps, 3) Remove friction to start, 4) Use implementation intentions ('When X happens, I will do Y'), 5) Forgive yourself for past procrastination, 6) Make the task more enjoyable, 7) Visualize completion, 8) Accountability partner."),
    
    ("how do i learn faster",
     "Learn faster by: 1) Focus on fundamentals first, 2) Use active learning, not passive reading, 3) Get immediate feedback on mistakes, 4) Practice deliberately on weak areas, 5) Teach what you learn, 6) Connect new knowledge to existing knowledge, 7) Take strategic breaks, 8) Sleep well - memory consolidates during sleep."),
    
    ("what is deliberate practice",
     "Deliberate practice is purposeful, systematic training focused on improving specific aspects of performance. Key elements: 1) Clear goals for each session, 2) Full concentration, 3) Immediate feedback, 4) Working at the edge of your abilities, 5) Repetition with reflection. It's what separates experts from amateurs."),
    
    ("how do i build good study habits",
     "Build study habits: 1) Start small - 10 minutes daily is better than 2 hours weekly, 2) Same time and place creates automatic triggers, 3) Stack habits - attach studying to existing routines, 4) Track your progress visually, 5) Reward yourself after sessions, 6) Don't break the chain - consistency matters, 7) Plan specific what/when/where."),
]

LEARNING_STYLES = [
    ("what is my learning style",
     "Common learning styles include: Visual (diagrams, charts), Auditory (listening, discussion), Reading/Writing (notes, lists), and Kinesthetic (hands-on practice). Most people use a mix. Experiment: try explaining with diagrams vs. writing vs. teaching aloud, and see what helps you understand and remember best."),
    
    ("how do i learn visually",
     "Visual learning techniques: 1) Create mind maps and diagrams, 2) Use color coding in notes, 3) Watch educational videos, 4) Draw concepts and processes, 5) Use charts and graphs, 6) Create visual mnemonics, 7) Sketch while listening to lectures, 8) Use flashcards with images."),
    
    ("how do i learn by doing",
     "Kinesthetic/hands-on learning: 1) Build projects while learning, 2) Do experiments and simulations, 3) Practice immediately after learning theory, 4) Use physical manipulatives, 5) Role-play scenarios, 6) Take notes by hand, 7) Walk while memorizing, 8) Teach through demonstration."),
    
    ("how do i learn from reading",
     "Reading-based learning: 1) Use SQ3R method (Survey, Question, Read, Recite, Review), 2) Annotate actively, 3) Summarize each section, 4) Create written summaries, 5) Take structured notes, 6) Write questions as you read, 7) Create your own study guides, 8) Rewrite key concepts."),
]

# =============================================================================
# RESEARCH METHODOLOGIES
# =============================================================================

RESEARCH_CONVERSATIONS = [
    ("how do i research a topic",
     "Research process: 1) Define your question clearly, 2) Do initial broad search to understand the landscape, 3) Identify key terms and concepts, 4) Find authoritative sources (academic papers, expert books), 5) Take organized notes with citations, 6) Look for multiple perspectives, 7) Evaluate source credibility, 8) Synthesize findings, 9) Identify gaps and further questions."),
    
    ("how do i find reliable sources",
     "Evaluate sources using CRAAP: Currency (when published?), Relevance (relates to your topic?), Authority (who wrote it, what credentials?), Accuracy (supported by evidence?), Purpose (why was it written?). Prefer: peer-reviewed journals, academic institutions, recognized experts, primary sources. Be skeptical of: anonymous sources, extreme claims, lack of citations."),
    
    ("how do i read academic papers",
     "Reading papers efficiently: 1) Start with abstract for overview, 2) Read intro and conclusion next, 3) Skim figures and tables, 4) Read methods if relevant, 5) Deep read sections important to you. Don't read linearly! Take notes on key findings, methods, and how it relates to your research. It's okay to not understand everything."),
    
    ("how do i take research notes",
     "Research note-taking: 1) Use a consistent system (Zettelkasten, Cornell, etc.), 2) Always record source info (author, title, page), 3) Distinguish quotes from paraphrases from your thoughts, 4) Link related notes together, 5) Write in your own words, 6) Include page numbers for quotes, 7) Organize by theme, not source, 8) Review and synthesize regularly."),
    
    ("what is the scientific method",
     "The scientific method: 1) Observation - notice something interesting, 2) Question - formulate what you want to know, 3) Hypothesis - make a testable prediction, 4) Experiment - design and conduct tests, 5) Analysis - examine results objectively, 6) Conclusion - does evidence support hypothesis?, 7) Communicate - share findings for peer review. It's iterative - new questions lead to new experiments."),
    
    ("how do i form a hypothesis",
     "Forming hypotheses: 1) Start with observation or question, 2) Research existing knowledge, 3) Identify variables (independent and dependent), 4) Make it testable and falsifiable, 5) Be specific and measurable, 6) Use 'If...then...' format, 7) Consider null hypothesis too. Good hypothesis: 'If plants receive more sunlight, then they will grow taller.' Bad: 'Plants need sun.'"),
    
    ("how do i evaluate evidence",
     "Evaluating evidence: 1) Check source credibility, 2) Look for peer review, 3) Consider sample size, 4) Distinguish correlation from causation, 5) Look for replication, 6) Check for bias, 7) Consider alternative explanations, 8) Evaluate methodology, 9) Check if conclusions match data, 10) Look for consensus among experts."),
    
    ("how do i synthesize information",
     "Synthesizing information: 1) Organize sources by theme, not chronologically, 2) Identify patterns and connections, 3) Note contradictions and debates, 4) Create a framework or model, 5) Look for gaps in the literature, 6) Draw your own conclusions from the evidence, 7) Use concept maps to visualize relationships, 8) Write summaries that integrate multiple sources."),
    
    ("how do i do a literature review",
     "Literature review process: 1) Define scope and research question, 2) Search databases systematically, 3) Screen sources for relevance, 4) Read and take notes on each source, 5) Organize by themes or chronology, 6) Identify trends and gaps, 7) Critically analyze, don't just summarize, 8) Synthesize into coherent narrative, 9) Cite properly."),
    
    ("how do i cite sources",
     "Citation basics: 1) Always cite when using others' ideas, 2) Choose a style (APA, MLA, Chicago), 3) Include: author, title, date, source, 4) Use in-text citations for quotes and paraphrases, 5) Create reference list/bibliography, 6) Use citation managers (Zotero, Mendeley), 7) When in doubt, cite it, 8) Quote directly only when exact words matter."),
]

# =============================================================================
# CRITICAL THINKING
# =============================================================================

CRITICAL_THINKING = [
    ("how do i think critically",
     "Critical thinking steps: 1) Question assumptions - yours and others', 2) Gather information from multiple sources, 3) Evaluate evidence quality, 4) Consider alternative viewpoints, 5) Identify logical fallacies, 6) Distinguish facts from opinions, 7) Consider context and bias, 8) Draw reasoned conclusions, 9) Remain open to changing your mind with new evidence."),
    
    ("what are logical fallacies",
     "Common logical fallacies: Ad hominem (attacking person not argument), Strawman (misrepresenting opponent's view), False dichotomy (only 2 options when more exist), Appeal to authority (experts can be wrong), Slippery slope (A leads inevitably to Z), Confirmation bias (seeking supporting evidence only), Hasty generalization (too small sample), Circular reasoning (conclusion in premise)."),
    
    ("how do i analyze arguments",
     "Analyzing arguments: 1) Identify the main claim/conclusion, 2) Find the supporting premises, 3) Check if premises are true, 4) Check if logic is valid (do premises support conclusion?), 5) Look for hidden assumptions, 6) Identify logical fallacies, 7) Consider counterarguments, 8) Evaluate overall strength of argument."),
    
    ("how do i form opinions",
     "Forming good opinions: 1) Gather information from diverse sources, 2) Distinguish facts from interpretations, 3) Consider multiple perspectives, 4) Examine your own biases, 5) Look at evidence for AND against, 6) Consider the strength of the evidence, 7) Be willing to say 'I don't know', 8) Hold opinions proportional to evidence, 9) Update views when you learn new info."),
    
    ("how do i avoid bias",
     "Avoiding bias: 1) Seek out opposing viewpoints, 2) Question your initial reactions, 3) Consider 'What would change my mind?', 4) Use structured decision-making frameworks, 5) Get diverse perspectives, 6) Be aware of common biases (confirmation, anchoring, availability), 7) Slow down important decisions, 8) Keep a decision journal to review."),
    
    ("how do i ask good questions",
     "Asking good questions: 1) Be specific, not vague, 2) Ask open-ended questions (how/why not just yes/no), 3) Question assumptions, 4) Ask 'What evidence supports this?', 5) Ask 'What are the alternatives?', 6) Use the 5 Whys to dig deeper, 7) Ask 'What would it take to change your view?', 8) Ask about implications and consequences."),
    
    ("how do i solve problems",
     "Problem-solving framework: 1) Define the problem precisely, 2) Gather relevant information, 3) Generate multiple solutions (brainstorm), 4) Evaluate each solution's pros/cons, 5) Choose the best option, 6) Implement with a plan, 7) Monitor results, 8) Adjust as needed. For complex problems, break into smaller sub-problems."),
    
    ("how do i make decisions",
     "Decision-making: 1) Clarify what you're deciding, 2) Identify your goals and values, 3) Generate options, 4) Gather information about each option, 5) Consider pros and cons, 6) Use a decision matrix for complex choices, 7) Consider reversibility, 8) Set a deadline to decide, 9) Decide and commit, 10) Review outcomes to improve future decisions."),
]

# =============================================================================
# SUBJECT-SPECIFIC LEARNING
# =============================================================================

SUBJECT_LEARNING = [
    ("how do i learn math",
     "Learning math effectively: 1) Understand concepts before memorizing formulas, 2) Practice, practice, practice - math is a skill, 3) Work through examples step by step, 4) Make mistakes and learn from them, 5) Build on fundamentals - gaps cause problems later, 6) Explain solutions in words, 7) Use visualization, 8) Don't just read solutions - try problems first."),
    
    ("how do i learn programming",
     "Learning to code: 1) Start with one language (Python recommended), 2) Learn by building projects, not just tutorials, 3) Understand concepts, don't just copy code, 4) Debug your own errors - learning opportunity, 5) Read other people's code, 6) Start small, increase complexity gradually, 7) Use version control (Git), 8) Join communities and ask questions."),
    
    ("how do i learn a language",
     "Language learning: 1) Immersion is key - use it daily, 2) Focus on most common words first (80/20 rule), 3) Practice speaking from day one, 4) Use spaced repetition for vocabulary, 5) Learn phrases, not just words, 6) Consume media in the language, 7) Find conversation partners, 8) Make mistakes without fear, 9) Set specific, measurable goals."),
    
    ("how do i learn science",
     "Learning science: 1) Understand underlying principles, not just facts, 2) Do hands-on experiments when possible, 3) Connect concepts to real-world applications, 4) Draw diagrams and models, 5) Ask 'why' and 'how' not just 'what', 6) Learn the vocabulary, 7) Practice problem-solving, 8) Read primary sources when possible, 9) Discuss with others."),
    
    ("how do i learn history",
     "Learning history: 1) Focus on causation - why things happened, 2) Create timelines to see connections, 3) Understand context of the era, 4) Learn about ordinary people, not just leaders, 5) Compare different perspectives, 6) Connect to present day, 7) Use primary sources when possible, 8) Ask 'What if?' questions, 9) Tell the story in your own words."),
    
    ("how do i learn writing",
     "Improving writing: 1) Read widely and analyze good writing, 2) Write regularly - it's a skill, 3) Get feedback and revise, 4) Start with clear structure, 5) First draft is for ideas, revision is for clarity, 6) Eliminate unnecessary words, 7) Use active voice, 8) Read your work aloud, 9) Know your audience, 10) Learn grammar rules to break them intentionally."),
    
    ("how do i learn art",
     "Learning art: 1) Practice fundamentals (line, shape, value, color), 2) Draw from observation, not imagination (at first), 3) Copy masters to understand technique, 4) Get critique and feedback, 5) Focus on one skill at a time, 6) Keep a sketchbook for daily practice, 7) Study anatomy for figures, 8) Experiment with different media, 9) Embrace mistakes as learning."),
    
    ("how do i learn music",
     "Learning music: 1) Practice consistently, even 15 min daily, 2) Start slow, increase speed gradually, 3) Learn music theory basics, 4) Train your ear with interval recognition, 5) Practice with a metronome, 6) Learn songs you love for motivation, 7) Record yourself to hear mistakes, 8) Find a teacher for feedback, 9) Play with others when possible."),
]

# =============================================================================
# KNOWLEDGE MANAGEMENT
# =============================================================================

KNOWLEDGE_MANAGEMENT = [
    ("how do i organize what i learn",
     "Knowledge organization: 1) Use a personal knowledge management system, 2) Take notes in your own words, 3) Link related concepts together, 4) Review and consolidate regularly, 5) Create summaries and syntheses, 6) Use tags and categories, 7) Build a second brain (digital notes), 8) Revisit and refine your understanding."),
    
    ("what is a second brain",
     "A 'second brain' is a digital system for capturing, organizing, and retrieving information. Key components: 1) Capture - save interesting ideas, 2) Organize - group by projects/areas/resources, 3) Distill - highlight key points, 4) Express - create outputs from your notes. Tools include Notion, Obsidian, Roam. The goal is to free your mind and connect ideas."),
    
    ("what is zettelkasten",
     "Zettelkasten is a note-taking method: 1) Each note contains one idea, 2) Notes are linked to related notes, 3) Notes are atomic (self-contained), 4) Use unique identifiers, 5) Write in your own words, 6) Build a web of connected knowledge, 7) Review connections regularly, 8) Let structure emerge organically. Used by prolific writers and researchers."),
    
    ("how do i remember what i learn",
     "Retention strategies: 1) Active recall - test yourself, 2) Spaced repetition - review at intervals, 3) Teach others, 4) Connect to existing knowledge, 5) Use multiple senses, 6) Apply in practice, 7) Sleep well, 8) Review notes within 24 hours, 9) Create mental associations, 10) Use the material - don't just study for tests."),
    
    ("how do i learn something new",
     "Learning something new: 1) Define what you want to learn specifically, 2) Find quality resources (books, courses, mentors), 3) Break it into sub-skills, 4) Focus on fundamentals first, 5) Practice deliberately with feedback, 6) Set milestones to track progress, 7) Build projects to apply knowledge, 8) Teach others to solidify understanding, 9) Be patient - mastery takes time."),
    
    ("how do i become an expert",
     "Path to expertise: 1) 10,000 hours of deliberate practice (quality matters), 2) Study the best in your field, 3) Get mentorship and feedback, 4) Push beyond your comfort zone, 5) Reflect on failures and successes, 6) Build deep foundational knowledge, 7) Stay current with new developments, 8) Contribute to the field, 9) Teach others, 10) Never stop learning."),
]

# =============================================================================
# SELF-DIRECTED LEARNING
# =============================================================================

SELF_DIRECTED = [
    ("how do i learn on my own",
     "Self-directed learning: 1) Set clear learning goals, 2) Find quality resources (books, courses, communities), 3) Create a curriculum/roadmap, 4) Schedule regular study time, 5) Hold yourself accountable (tracking, partners), 6) Seek feedback (communities, mentors), 7) Build projects to apply knowledge, 8) Reflect on progress regularly, 9) Adjust approach based on results."),
    
    ("how do i create a study plan",
     "Creating a study plan: 1) Define your goal and deadline, 2) Break into sub-topics, 3) Estimate time for each topic, 4) Schedule specific study sessions, 5) Include review periods, 6) Build in buffer time, 7) Mix difficult and easy topics, 8) Include practice/application time, 9) Set weekly checkpoints, 10) Adjust based on progress."),
    
    ("how do i stay motivated to learn",
     "Staying motivated: 1) Connect learning to your goals, 2) Make progress visible, 3) Celebrate small wins, 4) Find a learning community, 5) Vary your methods, 6) Take breaks when needed, 7) Remember your 'why', 8) Set specific, achievable goals, 9) Make it enjoyable when possible, 10) Forgive setbacks and keep going."),
    
    ("how do i learn without a teacher",
     "Learning without a teacher: 1) Use online courses and tutorials, 2) Read books by experts, 3) Join communities and forums, 4) Find accountability partners, 5) Use feedback from practice (results tell you if you're right), 6) Seek mentors or experts to review work, 7) Compare to examples and models, 8) Teach others to get questions, 9) Build projects for real-world feedback."),
    
    ("how do i track learning progress",
     "Tracking progress: 1) Set measurable goals, 2) Keep a learning journal, 3) Take regular assessments, 4) Track time spent, 5) Document what you've completed, 6) Note difficulties and breakthroughs, 7) Review progress weekly/monthly, 8) Compare to benchmarks, 9) Celebrate milestones, 10) Adjust goals based on reality."),
    
    ("how do i learn efficiently",
     "Efficient learning: 1) Focus on highest-impact knowledge first (80/20), 2) Eliminate distractions, 3) Use active techniques, not passive, 4) Get enough sleep, 5) Exercise regularly, 6) Batch similar topics, 7) Time-box study sessions, 8) Take strategic breaks, 9) Apply immediately, 10) Don't multitask."),
]

# =============================================================================
# TEACHING AND EXPLAINING
# =============================================================================

TEACHING_SKILLS = [
    ("how do i explain something",
     "Explaining well: 1) Know your audience's level, 2) Start with what they already know, 3) Use simple language, 4) Use analogies and metaphors, 5) Build from simple to complex, 6) Use examples, 7) Check for understanding, 8) Encourage questions, 9) Summarize key points, 10) Use visuals when helpful."),
    
    ("how do i teach someone",
     "Teaching effectively: 1) Assess what they already know, 2) Set clear learning objectives, 3) Break into digestible chunks, 4) Demonstrate before asking them to do, 5) Let them practice with support, 6) Give constructive feedback, 7) Encourage questions, 8) Adapt to their pace, 9) Celebrate progress, 10) Foster independence."),
    
    ("how do i share knowledge",
     "Sharing knowledge: 1) Document what you learn, 2) Write tutorials or guides, 3) Create presentations, 4) Record explanations, 5) Answer questions in communities, 6) Mentor others, 7) Write blog posts or articles, 8) Give talks, 9) Build courses, 10) Make your resources accessible."),
    
    ("how do i simplify complex ideas",
     "Simplifying complexity: 1) Identify the core concept, 2) Remove jargon, 3) Use everyday analogies, 4) Start with 'why it matters', 5) Use concrete examples, 6) Build up step by step, 7) Focus on one idea at a time, 8) Use visuals, 9) Summarize in one sentence, 10) Test explanation on non-experts."),
]

# =============================================================================
# DOMAIN KNOWLEDGE FOR RESEARCH
# =============================================================================

RESEARCH_DOMAINS = {
    "research": """Research is the systematic investigation of a topic to establish facts, 
    develop new conclusions, or solve problems. It involves: defining questions, gathering 
    evidence, analyzing data, and drawing conclusions. Good research is methodical, 
    transparent, and builds on existing knowledge.""",
    
    "hypothesis": """A hypothesis is a testable prediction about the relationship between 
    variables. Good hypotheses are: specific, measurable, falsifiable, and based on 
    observation or theory. The hypothesis guides research design and data collection.""",
    
    "methodology": """Methodology is the systematic approach to conducting research. It 
    includes: research design, data collection methods, sampling strategies, and analysis 
    techniques. Good methodology ensures reliability and validity of findings.""",
    
    "peer review": """Peer review is the evaluation of research by experts in the same field 
    before publication. It helps ensure quality, validity, and significance of research. 
    Reviewers check methodology, analysis, and conclusions for errors and improvements.""",
    
    "critical thinking": """Critical thinking is disciplined thinking that is clear, rational, 
    open-minded, and informed by evidence. It involves: questioning assumptions, evaluating 
    evidence, considering alternatives, and drawing reasoned conclusions.""",
    
    "epistemology": """Epistemology is the study of knowledge - how we know what we know. 
    It addresses: what counts as knowledge, how knowledge is acquired, and the limits of 
    knowledge. Understanding epistemology helps evaluate claims and evidence.""",
    
    "metacognition": """Metacognition is 'thinking about thinking' - awareness and 
    understanding of your own thought processes. It includes: planning how to approach 
    learning, monitoring comprehension, and evaluating learning outcomes. Key to self-improvement.""",
    
    "bloom's taxonomy": """Bloom's Taxonomy is a hierarchy of cognitive skills: Remember 
    (recall facts), Understand (explain ideas), Apply (use in new situations), Analyze 
    (draw connections), Evaluate (justify decisions), Create (produce new work). 
    Higher levels require deeper learning.""",
    
    "cognitive load": """Cognitive load is the mental effort required for learning. 
    Three types: Intrinsic (task complexity), Extraneous (poor instruction), and 
    Germane (building schemas). Good learning design minimizes extraneous load and 
    manages intrinsic load through scaffolding.""",
    
    "transfer of learning": """Transfer is applying learning from one context to another. 
    Near transfer applies to similar situations; far transfer applies to different domains. 
    Teaching for transfer requires: deep understanding, varied examples, and explicit 
    connections between contexts.""",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_education_conversations() -> List[Tuple[str, str]]:
    """Get all education-related conversation pairs."""
    pairs = []
    pairs.extend(LEARNING_CONVERSATIONS)
    pairs.extend(LEARNING_STYLES)
    pairs.extend(RESEARCH_CONVERSATIONS)
    pairs.extend(CRITICAL_THINKING)
    pairs.extend(SUBJECT_LEARNING)
    pairs.extend(KNOWLEDGE_MANAGEMENT)
    pairs.extend(SELF_DIRECTED)
    pairs.extend(TEACHING_SKILLS)
    return pairs


def get_research_knowledge() -> Dict[str, str]:
    """Get research domain knowledge."""
    return RESEARCH_DOMAINS


def get_all_education_texts() -> List[str]:
    """Get all education texts for training."""
    texts = []
    
    # Add conversation pairs
    for q, a in get_education_conversations():
        texts.extend([q, a])
        
    # Add domain knowledge
    texts.extend(RESEARCH_DOMAINS.values())
    
    return texts


# Statistics
EDUCATION_STATS = {
    "learning_conversations": len(LEARNING_CONVERSATIONS),
    "learning_styles": len(LEARNING_STYLES),
    "research_conversations": len(RESEARCH_CONVERSATIONS),
    "critical_thinking": len(CRITICAL_THINKING),
    "subject_learning": len(SUBJECT_LEARNING),
    "knowledge_management": len(KNOWLEDGE_MANAGEMENT),
    "self_directed": len(SELF_DIRECTED),
    "teaching_skills": len(TEACHING_SKILLS),
    "domain_entries": len(RESEARCH_DOMAINS),
}
