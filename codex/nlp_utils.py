import re
from collections import Counter

class SimpleNLP:
    """
    Ground-up NLP tools to avoid heavy dependencies.
    """
    def __init__(self):
        self.stop_words = set([
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "this",
            "that", "these", "those", "it", "he", "she", "they", "i", "you", "we"
        ])

    def extract_entities(self, text, limit=10):
        """
        Extracts potential entities (concepts) based on capitalization and frequency.
        """
        # 1. Normalize
        clean_text = re.sub(r'[^\w\s]', '', text)
        words = clean_text.split()
        
        # 2. Heuristic: Capitalized words in middle of sentences often Proper Nouns
        # (Simple version: just most frequent meaningful words)
        meaningful_words = [
            w.lower() for w in words 
            if w.lower() not in self.stop_words and len(w) > 3
        ]
        
        counts = Counter(meaningful_words)
        return [word for word, count in counts.most_common(limit)]

    def extract_relations(self, text, entities):
        """
        If two entities appear in the same sentence, link them.
        """
        relations = []
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            found = [e for e in entities if e in sent.lower()]
            # Link all pairs
            for i in range(len(found)):
                for j in range(i + 1, len(found)):
                    relations.append((found[i], found[j]))
                    
        return relations
