# unimind/models/native/tokenizer.py
# Native Tokenizer System - BPE and WordPiece tokenization

import re
import json
import unicodedata
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class TokenizerConfig:
    """Configuration for the tokenizer."""
    vocab_size: int = 32000
    pad_token: str = "<pad>"
    unk_token: str = "<unk>"
    bos_token: str = "<s>"
    eos_token: str = "</s>"
    pad_id: int = 0
    unk_id: int = 1
    bos_id: int = 2
    eos_id: int = 3
    add_bos: bool = True
    add_eos: bool = True
    lowercase: bool = False
    
    
class BPETokenizer:
    """
    Byte Pair Encoding Tokenizer.
    
    A native implementation of BPE tokenization used by many LLMs.
    Can learn vocabulary from text or load pre-trained vocabularies.
    """
    
    def __init__(self, config: TokenizerConfig = None):
        self.config = config or TokenizerConfig()
        
        # Vocabulary mappings
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.merges: List[Tuple[str, str]] = []
        self.merge_ranks: Dict[Tuple[str, str], int] = {}
        
        # Special tokens
        self._init_special_tokens()
        
        # Compiled regex for tokenization
        # Using ASCII-compatible pattern (no \p{L} Unicode properties)
        self.pat = re.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?[a-zA-Z]+| ?[0-9]+| ?[^\s\w]+|\s+(?!\S)|\s+""",
            re.UNICODE
        )
        
    def _init_special_tokens(self):
        """Initialize special tokens in vocabulary."""
        special = [
            (self.config.pad_token, self.config.pad_id),
            (self.config.unk_token, self.config.unk_id),
            (self.config.bos_token, self.config.bos_id),
            (self.config.eos_token, self.config.eos_id),
        ]
        
        for token, token_id in special:
            self.vocab[token] = token_id
            self.inverse_vocab[token_id] = token
            
    def train(self, texts: List[str], vocab_size: int = None, min_frequency: int = 2):
        """
        Train BPE vocabulary from texts.
        
        Args:
            texts: List of training texts
            vocab_size: Target vocabulary size
            min_frequency: Minimum pair frequency for merge
        """
        vocab_size = vocab_size or self.config.vocab_size
        
        print(f"[BPETokenizer] Training on {len(texts)} texts, target vocab: {vocab_size}")
        
        # Get word frequencies
        word_freqs = defaultdict(int)
        for text in texts:
            if self.config.lowercase:
                text = text.lower()
            words = self._pre_tokenize(text)
            for word in words:
                word_freqs[" ".join(list(word)) + " </w>"] += 1
                
        # Build initial vocabulary from characters
        vocab = set()
        for word in word_freqs.keys():
            for char in word.split():
                vocab.add(char)
                
        # Add characters to vocabulary
        current_id = len(self.vocab)
        for char in sorted(vocab):
            if char not in self.vocab:
                self.vocab[char] = current_id
                self.inverse_vocab[current_id] = char
                current_id += 1
                
        # BPE merge loop
        num_merges = vocab_size - len(self.vocab)
        
        for i in range(num_merges):
            # Count pairs
            pairs = self._get_pair_frequencies(word_freqs)
            
            if not pairs:
                break
                
            # Find most frequent pair
            best_pair = max(pairs, key=pairs.get)
            
            if pairs[best_pair] < min_frequency:
                break
                
            # Merge pair
            self.merges.append(best_pair)
            self.merge_ranks[best_pair] = len(self.merges) - 1
            
            # Update word_freqs
            new_word_freqs = {}
            bigram = " ".join(best_pair)
            replacement = "".join(best_pair)
            
            for word, freq in word_freqs.items():
                new_word = word.replace(bigram, replacement)
                new_word_freqs[new_word] = freq
                
            word_freqs = new_word_freqs
            
            # Add merged token to vocabulary
            merged = "".join(best_pair)
            if merged not in self.vocab:
                self.vocab[merged] = current_id
                self.inverse_vocab[current_id] = merged
                current_id += 1
                
            if (i + 1) % 1000 == 0:
                print(f"  Completed {i + 1} merges")
                
        print(f"[BPETokenizer] Training complete. Vocabulary size: {len(self.vocab)}")
        
    def _pre_tokenize(self, text: str) -> List[str]:
        """Split text into words."""
        # Simple whitespace + punctuation splitting
        text = unicodedata.normalize("NFKC", text)
        words = []
        for match in re.finditer(r'\w+|[^\w\s]', text):
            words.append(match.group())
        return words
        
    def _get_pair_frequencies(self, word_freqs: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        """Count frequencies of adjacent pairs."""
        pairs = defaultdict(int)
        
        for word, freq in word_freqs.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
                
        return pairs
        
    def _bpe(self, token: str) -> List[str]:
        """Apply BPE to a single token."""
        if token in self.vocab:
            return [token]
            
        word = list(token) + ["</w>"]
        
        while len(word) > 1:
            # Find the highest priority merge
            min_pair = None
            min_rank = float('inf')
            
            for i in range(len(word) - 1):
                pair = (word[i], word[i + 1])
                rank = self.merge_ranks.get(pair, float('inf'))
                if rank < min_rank:
                    min_rank = rank
                    min_pair = pair
                    
            if min_pair is None or min_rank == float('inf'):
                break
                
            # Merge the pair
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and (word[i], word[i + 1]) == min_pair:
                    new_word.append(word[i] + word[i + 1])
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = new_word
            
        return word
        
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text
            add_special_tokens: Whether to add BOS/EOS
            
        Returns:
            List of token IDs
        """
        if self.config.lowercase:
            text = text.lower()
            
        tokens = []
        
        # Add BOS token
        if add_special_tokens and self.config.add_bos:
            tokens.append(self.config.bos_id)
            
        # Tokenize
        words = self._pre_tokenize(text)
        
        for word in words:
            subwords = self._bpe(word)
            for subword in subwords:
                if subword in self.vocab:
                    tokens.append(self.vocab[subword])
                else:
                    tokens.append(self.config.unk_id)
                    
        # Add EOS token
        if add_special_tokens and self.config.add_eos:
            tokens.append(self.config.eos_id)
            
        return tokens
        
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            Decoded text
        """
        special_ids = {
            self.config.pad_id, self.config.unk_id,
            self.config.bos_id, self.config.eos_id
        }
        
        tokens = []
        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            if token_id in self.inverse_vocab:
                tokens.append(self.inverse_vocab[token_id])
            else:
                tokens.append(self.config.unk_token)
                
        # Join and clean up
        text = "".join(tokens)
        text = text.replace("</w>", " ")
        text = text.strip()
        
        return text
        
    def save(self, path: str):
        """Save tokenizer to file."""
        data = {
            "config": {
                "vocab_size": self.config.vocab_size,
                "pad_token": self.config.pad_token,
                "unk_token": self.config.unk_token,
                "bos_token": self.config.bos_token,
                "eos_token": self.config.eos_token,
                "pad_id": self.config.pad_id,
                "unk_id": self.config.unk_id,
                "bos_id": self.config.bos_id,
                "eos_id": self.config.eos_id,
                "add_bos": self.config.add_bos,
                "add_eos": self.config.add_eos,
                "lowercase": self.config.lowercase,
            },
            "vocab": self.vocab,
            "merges": self.merges,
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"[BPETokenizer] Saved to {path}")
        
    def load(self, path: str):
        """Load tokenizer from file."""
        with open(path) as f:
            data = json.load(f)
            
        # Load config
        config_data = data["config"]
        self.config = TokenizerConfig(**config_data)
        
        # Load vocabulary
        self.vocab = data["vocab"]
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
        
        # Load merges
        self.merges = [tuple(m) for m in data["merges"]]
        self.merge_ranks = {m: i for i, m in enumerate(self.merges)}
        
        print(f"[BPETokenizer] Loaded from {path}, vocab size: {len(self.vocab)}")
        
    @property
    def vocab_size(self) -> int:
        return len(self.vocab)


class WordPieceTokenizer:
    """
    WordPiece Tokenizer (BERT-style).
    
    Uses ## prefix for subword tokens that continue a word.
    """
    
    def __init__(self, config: TokenizerConfig = None):
        self.config = config or TokenizerConfig()
        
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        
        self._init_special_tokens()
        
    def _init_special_tokens(self):
        """Initialize special tokens."""
        special = [
            ("[PAD]", self.config.pad_id),
            ("[UNK]", self.config.unk_id),
            ("[CLS]", self.config.bos_id),
            ("[SEP]", self.config.eos_id),
            ("[MASK]", 4),
        ]
        
        for token, token_id in special:
            self.vocab[token] = token_id
            self.inverse_vocab[token_id] = token
            
    def train(self, texts: List[str], vocab_size: int = None):
        """Train WordPiece vocabulary."""
        vocab_size = vocab_size or self.config.vocab_size
        
        # Count character frequencies
        char_freqs = defaultdict(int)
        word_freqs = defaultdict(int)
        
        for text in texts:
            if self.config.lowercase:
                text = text.lower()
            words = text.split()
            for word in words:
                word_freqs[word] += 1
                for char in word:
                    char_freqs[char] += 1
                    
        # Add characters to vocabulary
        current_id = len(self.vocab)
        for char in sorted(char_freqs.keys()):
            if char not in self.vocab:
                self.vocab[char] = current_id
                self.inverse_vocab[current_id] = char
                current_id += 1
                
        # Build subwords greedily
        subword_freqs = defaultdict(int)
        
        for word, freq in word_freqs.items():
            # Generate all possible subwords
            for i in range(len(word)):
                for j in range(i + 1, len(word) + 1):
                    subword = word[i:j]
                    if i > 0:
                        subword = "##" + subword
                    subword_freqs[subword] += freq
                    
        # Add most frequent subwords
        sorted_subwords = sorted(subword_freqs.items(), key=lambda x: x[1], reverse=True)
        
        for subword, freq in sorted_subwords:
            if len(self.vocab) >= vocab_size:
                break
            if subword not in self.vocab:
                self.vocab[subword] = current_id
                self.inverse_vocab[current_id] = subword
                current_id += 1
                
        print(f"[WordPieceTokenizer] Training complete. Vocabulary size: {len(self.vocab)}")
        
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text to token IDs."""
        if self.config.lowercase:
            text = text.lower()
            
        tokens = []
        
        if add_special_tokens:
            tokens.append(self.vocab.get("[CLS]", self.config.bos_id))
            
        words = text.split()
        
        for word in words:
            # Greedy longest-match tokenization
            subtokens = self._tokenize_word(word)
            for subtoken in subtokens:
                tokens.append(self.vocab.get(subtoken, self.config.unk_id))
                
        if add_special_tokens:
            tokens.append(self.vocab.get("[SEP]", self.config.eos_id))
            
        return tokens
        
    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize a single word."""
        tokens = []
        start = 0
        
        while start < len(word):
            end = len(word)
            found = False
            
            while start < end:
                substr = word[start:end]
                if start > 0:
                    substr = "##" + substr
                    
                if substr in self.vocab:
                    tokens.append(substr)
                    found = True
                    break
                    
                end -= 1
                
            if not found:
                tokens.append("[UNK]")
                start += 1
            else:
                start = end
                
        return tokens
        
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text."""
        special_tokens = {"[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"}
        
        tokens = []
        for token_id in token_ids:
            if token_id in self.inverse_vocab:
                token = self.inverse_vocab[token_id]
                if skip_special_tokens and token in special_tokens:
                    continue
                tokens.append(token)
                
        # Join tokens
        text = ""
        for token in tokens:
            if token.startswith("##"):
                text += token[2:]
            else:
                text += " " + token
                
        return text.strip()
        
    def save(self, path: str):
        """Save tokenizer."""
        data = {
            "type": "wordpiece",
            "vocab": self.vocab,
            "config": {
                "vocab_size": self.config.vocab_size,
                "lowercase": self.config.lowercase,
            }
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            
    def load(self, path: str):
        """Load tokenizer."""
        with open(path) as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
        
    @property
    def vocab_size(self) -> int:
        return len(self.vocab)


class CharacterTokenizer:
    """Simple character-level tokenizer."""
    
    def __init__(self, config: TokenizerConfig = None):
        self.config = config or TokenizerConfig()
        
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        
        # Initialize with special tokens
        self.vocab["<pad>"] = 0
        self.vocab["<unk>"] = 1
        self.vocab["<s>"] = 2
        self.vocab["</s>"] = 3
        
        self.inverse_vocab = {v: k for k, v in self.vocab.items()}
        
    def train(self, texts: List[str]):
        """Build vocabulary from texts."""
        chars = set()
        for text in texts:
            for char in text:
                chars.add(char)
                
        current_id = len(self.vocab)
        for char in sorted(chars):
            if char not in self.vocab:
                self.vocab[char] = current_id
                self.inverse_vocab[current_id] = char
                current_id += 1
                
        print(f"[CharacterTokenizer] Vocabulary size: {len(self.vocab)}")
        
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text."""
        tokens = []
        
        if add_special_tokens:
            tokens.append(2)  # <s>
            
        for char in text:
            tokens.append(self.vocab.get(char, 1))  # 1 = <unk>
            
        if add_special_tokens:
            tokens.append(3)  # </s>
            
        return tokens
        
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode tokens."""
        chars = []
        for token_id in token_ids:
            if skip_special_tokens and token_id in {0, 1, 2, 3}:
                continue
            chars.append(self.inverse_vocab.get(token_id, ""))
        return "".join(chars)
        
    @property
    def vocab_size(self) -> int:
        return len(self.vocab)


class TokenizerFactory:
    """Factory for creating tokenizers."""
    
    @staticmethod
    def create(tokenizer_type: str = "bpe", config: TokenizerConfig = None):
        """Create a tokenizer of the specified type."""
        if tokenizer_type == "bpe":
            return BPETokenizer(config)
        elif tokenizer_type == "wordpiece":
            return WordPieceTokenizer(config)
        elif tokenizer_type == "character":
            return CharacterTokenizer(config)
        else:
            raise ValueError(f"Unknown tokenizer type: {tokenizer_type}")
            
    @staticmethod
    def load(path: str):
        """Load a tokenizer from file."""
        with open(path) as f:
            data = json.load(f)
            
        tokenizer_type = data.get("type", "bpe")
        
        if tokenizer_type == "wordpiece":
            tokenizer = WordPieceTokenizer()
        else:
            tokenizer = BPETokenizer()
            
        tokenizer.load(path)
        return tokenizer


# Pre-trained basic tokenizer for quick use
def create_basic_tokenizer() -> BPETokenizer:
    """Create a basic tokenizer with common tokens."""
    tokenizer = BPETokenizer()
    
    # Add common tokens
    common_tokens = [
        # Characters
        *list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
        # Punctuation
        ".", ",", "!", "?", ":", ";", "'", '"', "-", "_", "(", ")", "[", "]",
        # Common words
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "must", "shall",
        "I", "you", "he", "she", "it", "we", "they", "this", "that", "these",
        "and", "or", "but", "if", "then", "else", "when", "where", "what",
        "who", "which", "how", "why", "not", "no", "yes",
        # Common subwords
        "ing", "ed", "er", "est", "ly", "tion", "ness", "ment", "able", "ible",
        "</w>",
    ]
    
    current_id = len(tokenizer.vocab)
    for token in common_tokens:
        if token not in tokenizer.vocab:
            tokenizer.vocab[token] = current_id
            tokenizer.inverse_vocab[current_id] = token
            current_id += 1
            
    return tokenizer
