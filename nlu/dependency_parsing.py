# nlu/dependency_parsing.py
# Dependency Parsing Module

"""
Dependency Parsing Module

Provides syntactic tree analysis:
- Dependency relation detection
- Head-dependent relationships
- Syntactic tree construction
- Clause boundary detection
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import re


class DependencyRelation(Enum):
    """Universal Dependency Relations (simplified)."""
    # Core arguments
    NSUBJ = "nsubj"      # Nominal subject
    NSUBJ_PASS = "nsubj:pass"  # Passive subject
    OBJ = "obj"          # Direct object
    IOBJ = "iobj"        # Indirect object
    CSUBJ = "csubj"      # Clausal subject
    CCOMP = "ccomp"      # Clausal complement
    XCOMP = "xcomp"      # Open clausal complement
    
    # Non-core dependents
    OBL = "obl"          # Oblique nominal
    VOCATIVE = "vocative"
    EXPL = "expl"        # Expletive
    DISLOCATED = "dislocated"
    
    # Nominal dependents
    NMOD = "nmod"        # Nominal modifier
    APPOS = "appos"      # Appositional modifier
    NUMMOD = "nummod"    # Numeric modifier
    
    # Clausal dependents
    ACL = "acl"          # Adjectival clause
    ADVCL = "advcl"      # Adverbial clause
    
    # Modifier words
    ADVMOD = "advmod"    # Adverbial modifier
    DISCOURSE = "discourse"
    AMOD = "amod"        # Adjectival modifier
    
    # Function words
    AUX = "aux"          # Auxiliary
    AUX_PASS = "aux:pass"  # Passive auxiliary
    COP = "cop"          # Copula
    MARK = "mark"        # Marker
    DET = "det"          # Determiner
    CLF = "clf"          # Classifier
    CASE = "case"        # Case marking
    
    # Coordination
    CC = "cc"            # Coordinating conjunction
    CONJ = "conj"        # Conjunct
    
    # Multi-word expressions
    FIXED = "fixed"
    FLAT = "flat"
    COMPOUND = "compound"
    
    # Loose relations
    LIST = "list"
    PARATAXIS = "parataxis"
    
    # Special
    ORPHAN = "orphan"
    GOESWITH = "goeswith"
    REPARANDUM = "reparandum"
    PUNCT = "punct"      # Punctuation
    ROOT = "root"        # Root of tree
    DEP = "dep"          # Unspecified dependency


@dataclass
class DependencyNode:
    """Node in dependency tree."""
    id: int
    word: str
    lemma: str
    pos: str
    head_id: int
    relation: DependencyRelation
    children: List['DependencyNode'] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.word}({self.relation.value})"


@dataclass
class DependencyTree:
    """Complete dependency tree for a sentence."""
    text: str
    nodes: List[DependencyNode]
    root: Optional[DependencyNode] = None
    
    def get_subtree(self, node: DependencyNode) -> List[DependencyNode]:
        """Get all nodes in subtree rooted at node."""
        result = [node]
        for child in node.children:
            result.extend(self.get_subtree(child))
        return result
        
    def get_subject(self) -> Optional[DependencyNode]:
        """Get the subject of the sentence."""
        for node in self.nodes:
            if node.relation in (DependencyRelation.NSUBJ, DependencyRelation.NSUBJ_PASS, DependencyRelation.CSUBJ):
                return node
        return None
        
    def get_object(self) -> Optional[DependencyNode]:
        """Get the direct object of the sentence."""
        for node in self.nodes:
            if node.relation == DependencyRelation.OBJ:
                return node
        return None
        
    def get_verb(self) -> Optional[DependencyNode]:
        """Get the main verb."""
        if self.root and self.root.pos.startswith('V'):
            return self.root
        for node in self.nodes:
            if node.pos.startswith('V') and node.relation == DependencyRelation.ROOT:
                return node
        return None


class DependencyParser:
    """
    Rule-based dependency parser.
    
    Uses heuristics and patterns to build dependency trees.
    """
    
    def __init__(self):
        # Part-of-speech patterns
        self.pos_patterns = self._load_pos_patterns()
        
        # Function words
        self.determiners = {"the", "a", "an", "this", "that", "these", "those", 
                           "my", "your", "his", "her", "its", "our", "their",
                           "some", "any", "no", "every", "each", "all", "both"}
        self.prepositions = {"in", "on", "at", "by", "for", "with", "about", 
                            "from", "to", "of", "into", "through", "during",
                            "before", "after", "above", "below", "between"}
        self.auxiliaries = {"be", "am", "is", "are", "was", "were", "been", "being",
                           "have", "has", "had", "having", "do", "does", "did",
                           "will", "would", "shall", "should", "can", "could",
                           "may", "might", "must"}
        self.conjunctions = {"and", "but", "or", "nor", "for", "yet", "so",
                            "because", "although", "while", "if", "unless",
                            "when", "where", "that", "which", "who"}
                            
    def _load_pos_patterns(self) -> Dict[str, str]:
        """Load part-of-speech detection patterns."""
        return {
            # Determiners
            "the": "DT", "a": "DT", "an": "DT", "this": "DT", "that": "DT",
            "these": "DT", "those": "DT", "my": "PRP$", "your": "PRP$",
            
            # Pronouns
            "i": "PRP", "you": "PRP", "he": "PRP", "she": "PRP", "it": "PRP",
            "we": "PRP", "they": "PRP", "me": "PRP", "him": "PRP", "her": "PRP",
            "us": "PRP", "them": "PRP",
            
            # Auxiliaries
            "is": "VBZ", "are": "VBP", "was": "VBD", "were": "VBD",
            "am": "VBP", "be": "VB", "been": "VBN", "being": "VBG",
            "have": "VBP", "has": "VBZ", "had": "VBD", "having": "VBG",
            "do": "VBP", "does": "VBZ", "did": "VBD", "doing": "VBG",
            "will": "MD", "would": "MD", "can": "MD", "could": "MD",
            "may": "MD", "might": "MD", "must": "MD", "shall": "MD", "should": "MD",
            
            # Prepositions
            "in": "IN", "on": "IN", "at": "IN", "by": "IN", "for": "IN",
            "with": "IN", "from": "IN", "to": "TO", "of": "IN", "about": "IN",
            
            # Conjunctions
            "and": "CC", "but": "CC", "or": "CC", "nor": "CC",
            "if": "IN", "because": "IN", "although": "IN", "while": "IN",
            
            # Question words
            "what": "WP", "who": "WP", "whom": "WP", "which": "WDT",
            "when": "WRB", "where": "WRB", "why": "WRB", "how": "WRB",
        }
        
    def _get_pos(self, word: str) -> str:
        """Get POS tag for a word."""
        word_lower = word.lower()
        
        # Check patterns
        if word_lower in self.pos_patterns:
            return self.pos_patterns[word_lower]
            
        # Heuristics
        if word.endswith('ly'):
            return "RB"  # Adverb
        if word.endswith('ing'):
            return "VBG"  # Gerund
        if word.endswith('ed'):
            return "VBD"  # Past tense
        if word.endswith('s') and not word.endswith('ss'):
            if word[0].isupper():
                return "NNP"
            return "NNS"  # Plural noun or verb
        if word.endswith(('tion', 'ment', 'ness', 'ity')):
            return "NN"  # Noun
        if word.endswith(('ful', 'less', 'ous', 'ive', 'able')):
            return "JJ"  # Adjective
        if word[0].isupper():
            return "NNP"  # Proper noun
            
        return "NN"  # Default to noun
        
    def _get_lemma(self, word: str, pos: str) -> str:
        """Get lemma for word."""
        word_lower = word.lower()
        
        # Common irregular forms
        irregulars = {
            "is": "be", "are": "be", "was": "be", "were": "be", "am": "be",
            "has": "have", "had": "have", "does": "do", "did": "do",
            "goes": "go", "went": "go", "gone": "go",
        }
        
        if word_lower in irregulars:
            return irregulars[word_lower]
            
        # Remove common suffixes
        if word_lower.endswith('ed') and len(word_lower) > 3:
            return word_lower[:-2]
        if word_lower.endswith('ing') and len(word_lower) > 4:
            return word_lower[:-3]
        if word_lower.endswith('s') and not word_lower.endswith('ss') and len(word_lower) > 2:
            return word_lower[:-1]
            
        return word_lower
        
    def parse(self, text: str) -> DependencyTree:
        """
        Parse a sentence into a dependency tree.
        
        Args:
            text: Input sentence
            
        Returns:
            DependencyTree
        """
        # Tokenize
        tokens = self._tokenize(text)
        
        if not tokens:
            return DependencyTree(text=text, nodes=[], root=None)
            
        # Create nodes with POS tags
        nodes = []
        for i, token in enumerate(tokens):
            pos = self._get_pos(token)
            lemma = self._get_lemma(token, pos)
            node = DependencyNode(
                id=i,
                word=token,
                lemma=lemma,
                pos=pos,
                head_id=-1,
                relation=DependencyRelation.DEP
            )
            nodes.append(node)
            
        # Find root (main verb or first verb)
        root_idx = self._find_root(nodes)
        if root_idx >= 0:
            nodes[root_idx].head_id = -1
            nodes[root_idx].relation = DependencyRelation.ROOT
            
        # Assign dependencies
        self._assign_dependencies(nodes, root_idx)
        
        # Build tree structure
        root = None
        if root_idx >= 0:
            root = nodes[root_idx]
            
        # Link children
        for node in nodes:
            if node.head_id >= 0 and node.head_id < len(nodes):
                nodes[node.head_id].children.append(node)
                
        return DependencyTree(text=text, nodes=nodes, root=root)
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Simple tokenization
        tokens = re.findall(r"\w+(?:'\w+)?|[^\w\s]", text)
        return tokens
        
    def _find_root(self, nodes: List[DependencyNode]) -> int:
        """Find the root node (main verb)."""
        # Look for main verb
        for i, node in enumerate(nodes):
            if node.pos.startswith('VB') and node.pos not in ('VBG', 'VBN'):
                # Check if not preceded by auxiliary
                if i == 0 or nodes[i-1].pos != 'MD':
                    return i
                    
        # Look for modal + verb
        for i, node in enumerate(nodes):
            if node.pos == 'MD':
                if i + 1 < len(nodes) and nodes[i+1].pos.startswith('VB'):
                    return i + 1
                    
        # Look for any verb
        for i, node in enumerate(nodes):
            if node.pos.startswith('VB'):
                return i
                
        # Default to first word if no verb
        return 0 if nodes else -1
        
    def _assign_dependencies(self, nodes: List[DependencyNode], root_idx: int):
        """Assign dependency relations to nodes."""
        if root_idx < 0:
            return
            
        root = nodes[root_idx]
        
        for i, node in enumerate(nodes):
            if i == root_idx:
                continue
                
            word_lower = node.word.lower()
            
            # Determiners attach to following noun
            if node.pos == 'DT':
                for j in range(i + 1, len(nodes)):
                    if nodes[j].pos.startswith('NN'):
                        node.head_id = j
                        node.relation = DependencyRelation.DET
                        break
                if node.head_id < 0:
                    node.head_id = root_idx
                    node.relation = DependencyRelation.DET
                continue
                
            # Adjectives attach to following noun
            if node.pos.startswith('JJ'):
                for j in range(i + 1, len(nodes)):
                    if nodes[j].pos.startswith('NN'):
                        node.head_id = j
                        node.relation = DependencyRelation.AMOD
                        break
                if node.head_id < 0:
                    node.head_id = root_idx
                    node.relation = DependencyRelation.AMOD
                continue
                
            # Adverbs attach to verb
            if node.pos.startswith('RB'):
                node.head_id = root_idx
                node.relation = DependencyRelation.ADVMOD
                continue
                
            # Subject: noun/pronoun before verb
            if i < root_idx and node.pos in ('PRP', 'NNP', 'NN', 'NNS'):
                # Check if not already claimed
                has_subj = any(n.relation == DependencyRelation.NSUBJ for n in nodes)
                if not has_subj:
                    node.head_id = root_idx
                    node.relation = DependencyRelation.NSUBJ
                    continue
                    
            # Object: noun/pronoun after verb
            if i > root_idx and node.pos in ('PRP', 'NNP', 'NN', 'NNS'):
                # Check if previous word is not a preposition
                if i > 0 and nodes[i-1].pos != 'IN':
                    has_obj = any(n.relation == DependencyRelation.OBJ for n in nodes)
                    if not has_obj:
                        node.head_id = root_idx
                        node.relation = DependencyRelation.OBJ
                        continue
                        
            # Prepositions
            if node.pos in ('IN', 'TO'):
                node.head_id = root_idx
                node.relation = DependencyRelation.CASE
                # Following noun becomes oblique
                for j in range(i + 1, len(nodes)):
                    if nodes[j].pos.startswith('NN') or nodes[j].pos == 'PRP':
                        nodes[j].head_id = root_idx
                        nodes[j].relation = DependencyRelation.OBL
                        break
                continue
                
            # Auxiliaries
            if word_lower in self.auxiliaries:
                node.head_id = root_idx
                node.relation = DependencyRelation.AUX
                continue
                
            # Coordinating conjunctions
            if node.pos == 'CC':
                node.head_id = root_idx
                node.relation = DependencyRelation.CC
                continue
                
            # Punctuation
            if node.pos in ('PUNCT', '.', ',', '?', '!'):
                node.head_id = root_idx
                node.relation = DependencyRelation.PUNCT
                continue
                
            # Default: attach to root
            if node.head_id < 0:
                node.head_id = root_idx
                node.relation = DependencyRelation.DEP
                
    def get_tree_string(self, tree: DependencyTree, indent: int = 0) -> str:
        """Get string representation of tree."""
        if not tree.root:
            return "(empty tree)"
            
        return self._node_to_string(tree.root, indent)
        
    def _node_to_string(self, node: DependencyNode, indent: int) -> str:
        """Convert node to string with children."""
        prefix = "  " * indent
        result = f"{prefix}{node.word} ({node.relation.value})\n"
        for child in node.children:
            result += self._node_to_string(child, indent + 1)
        return result


# =============================================================================
# COREFERENCE RESOLUTION
# =============================================================================

@dataclass
class Mention:
    """A mention (noun phrase or pronoun) in text."""
    text: str
    start: int
    end: int
    sentence_id: int
    is_pronoun: bool
    gender: Optional[str] = None  # male, female, neutral
    number: Optional[str] = None  # singular, plural
    animacy: Optional[str] = None  # animate, inanimate


@dataclass
class CoreferenceChain:
    """A chain of coreferent mentions."""
    mentions: List[Mention]
    representative: Mention  # Main mention
    
    
class CoreferenceResolver:
    """
    Coreference resolution engine.
    
    Resolves pronouns and other anaphoric expressions to their antecedents.
    """
    
    def __init__(self):
        # Pronoun properties
        self.pronouns = {
            # Subject pronouns
            "i": {"gender": "neutral", "number": "singular", "person": 1},
            "you": {"gender": "neutral", "number": "singular", "person": 2},
            "he": {"gender": "male", "number": "singular", "person": 3},
            "she": {"gender": "female", "number": "singular", "person": 3},
            "it": {"gender": "neutral", "number": "singular", "person": 3},
            "we": {"gender": "neutral", "number": "plural", "person": 1},
            "they": {"gender": "neutral", "number": "plural", "person": 3},
            
            # Object pronouns
            "me": {"gender": "neutral", "number": "singular", "person": 1},
            "him": {"gender": "male", "number": "singular", "person": 3},
            "her": {"gender": "female", "number": "singular", "person": 3},
            "us": {"gender": "neutral", "number": "plural", "person": 1},
            "them": {"gender": "neutral", "number": "plural", "person": 3},
            
            # Possessive pronouns
            "my": {"gender": "neutral", "number": "singular", "person": 1},
            "your": {"gender": "neutral", "number": "singular", "person": 2},
            "his": {"gender": "male", "number": "singular", "person": 3},
            "its": {"gender": "neutral", "number": "singular", "person": 3},
            "our": {"gender": "neutral", "number": "plural", "person": 1},
            "their": {"gender": "neutral", "number": "plural", "person": 3},
        }
        
        # Common gendered names
        self.male_names = {"john", "james", "michael", "david", "robert", "william",
                          "richard", "joseph", "thomas", "charles", "daniel", "matthew",
                          "anthony", "mark", "donald", "steven", "paul", "andrew", "joshua"}
        self.female_names = {"mary", "patricia", "jennifer", "linda", "elizabeth", "barbara",
                            "susan", "jessica", "sarah", "karen", "nancy", "lisa", "betty",
                            "margaret", "sandra", "ashley", "dorothy", "kimberly", "emily"}
                            
    def extract_mentions(self, text: str) -> List[Mention]:
        """Extract all mentions from text."""
        mentions = []
        sentences = self._split_sentences(text)
        
        for sent_id, sentence in enumerate(sentences):
            # Extract noun phrases and pronouns
            words = re.findall(r'\b\w+\b', sentence)
            
            for i, word in enumerate(words):
                word_lower = word.lower()
                
                # Check if pronoun
                if word_lower in self.pronouns:
                    props = self.pronouns[word_lower]
                    start = sentence.find(word)
                    mention = Mention(
                        text=word,
                        start=start,
                        end=start + len(word),
                        sentence_id=sent_id,
                        is_pronoun=True,
                        gender=props["gender"],
                        number=props["number"]
                    )
                    mentions.append(mention)
                    
                # Check if proper noun (capitalized)
                elif word[0].isupper() and i > 0:
                    start = sentence.find(word)
                    gender = self._guess_gender(word_lower)
                    mention = Mention(
                        text=word,
                        start=start,
                        end=start + len(word),
                        sentence_id=sent_id,
                        is_pronoun=False,
                        gender=gender,
                        number="singular",
                        animacy="animate"
                    )
                    mentions.append(mention)
                    
        return mentions
        
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    def _guess_gender(self, name: str) -> str:
        """Guess gender from name."""
        name_lower = name.lower()
        if name_lower in self.male_names:
            return "male"
        if name_lower in self.female_names:
            return "female"
        return "neutral"
        
    def resolve(self, text: str) -> List[CoreferenceChain]:
        """
        Resolve coreferences in text.
        
        Args:
            text: Input text
            
        Returns:
            List of coreference chains
        """
        mentions = self.extract_mentions(text)
        
        if not mentions:
            return []
            
        # Simple algorithm: link pronouns to nearest compatible antecedent
        chains = []
        used = set()
        
        for i, mention in enumerate(mentions):
            if i in used:
                continue
                
            if mention.is_pronoun:
                # Find antecedent
                antecedent = self._find_antecedent(mention, mentions[:i])
                if antecedent:
                    # Create or extend chain
                    found_chain = None
                    for chain in chains:
                        if antecedent in chain.mentions:
                            chain.mentions.append(mention)
                            found_chain = chain
                            break
                    if not found_chain:
                        chains.append(CoreferenceChain(
                            mentions=[antecedent, mention],
                            representative=antecedent
                        ))
                    used.add(i)
            else:
                # Non-pronoun mention - could be start of chain
                if i not in used:
                    chains.append(CoreferenceChain(
                        mentions=[mention],
                        representative=mention
                    ))
                    used.add(i)
                    
        return chains
        
    def _find_antecedent(self, pronoun: Mention, candidates: List[Mention]) -> Optional[Mention]:
        """Find antecedent for a pronoun among candidates."""
        for candidate in reversed(candidates):  # Prefer recent mentions
            if candidate.is_pronoun:
                continue  # Don't link pronoun to pronoun
                
            # Check gender agreement
            if pronoun.gender != "neutral" and candidate.gender != "neutral":
                if pronoun.gender != candidate.gender:
                    continue
                    
            # Check number agreement
            if pronoun.number and candidate.number:
                if pronoun.number != candidate.number:
                    continue
                    
            return candidate
            
        return None
        
    def get_resolved_text(self, text: str) -> str:
        """
        Get text with pronouns replaced by their antecedents.
        
        Args:
            text: Input text
            
        Returns:
            Text with resolved coreferences
        """
        chains = self.resolve(text)
        
        # Build replacement map
        replacements = {}
        for chain in chains:
            rep_text = chain.representative.text
            for mention in chain.mentions:
                if mention.is_pronoun:
                    replacements[mention.text.lower()] = rep_text
                    
        # Apply replacements
        result = text
        for pronoun, replacement in replacements.items():
            # Simple replacement (case-insensitive)
            pattern = r'\b' + pronoun + r'\b'
            result = re.sub(pattern, f"[{replacement}]", result, flags=re.IGNORECASE)
            
        return result


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_parser: Optional[DependencyParser] = None
_coref: Optional[CoreferenceResolver] = None


def get_dependency_parser() -> DependencyParser:
    """Get the global dependency parser instance."""
    global _parser
    if _parser is None:
        _parser = DependencyParser()
    return _parser


def get_coreference_resolver() -> CoreferenceResolver:
    """Get the global coreference resolver instance."""
    global _coref
    if _coref is None:
        _coref = CoreferenceResolver()
    return _coref


def parse_dependencies(text: str) -> DependencyTree:
    """Parse a sentence into a dependency tree."""
    return get_dependency_parser().parse(text)


def resolve_coreferences(text: str) -> List[CoreferenceChain]:
    """Resolve coreferences in text."""
    return get_coreference_resolver().resolve(text)


def get_resolved_text(text: str) -> str:
    """Get text with resolved coreferences."""
    return get_coreference_resolver().get_resolved_text(text)
