from typing import List, Tuple, Optional, Set, Dict
from collections import defaultdict
import time
import re

class SymSpell:
    """
    SymSpell algorithm for extremely fast fuzzy matching.
    How it works:
    - Pre-computes all possible deletions within max_edit_distance
    - Stores them in a hash map for O(1) lookup
    - Trade-off: More memory for much faster queries
    Time Complexity:
    - Preprocessing: O(n * w^d) where n=words, w=avg word length, d=max distance
    - Lookup: O(1) average case
    """

    def __init__(self, max_edit_distance: int = 2):
        self.max_edit_distance = max_edit_distance
        self.words: Set[str] = set()
        self.deletes: Dict[str, Set[str]] = defaultdict(set)

    def _get_deletes(self, word: str, max_distance: int) -> Set[str]:
        """Generate all delete variants within max_distance edits."""
        deletes = set()
        queue = [word]
        for d in range(max_distance):
            temp_queue = []
            for item in queue:
                if len(item) > 1:
                    for i in range(len(item)):
                        delete = item[:i] + item[i + 1:]
                        if delete not in deletes:
                            deletes.add(delete)
                            temp_queue.append(delete)
            queue = temp_queue
        return deletes

    def build_index(self, word_list: List[str]) -> None:
        """
        Build the SymSpell index from a list of words.
        Call this once with your reference list.
        """
        self.words = set(word.lower() for word in word_list)
        self.deletes.clear()
        for word in self.words:
            # Add the word itself
            self.deletes[word].add(word)
            # Add all delete variants
            for delete in self._get_deletes(word, self.max_edit_distance):
                self.deletes[delete].add(word)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def lookup(self, term: str, max_distance: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Find all words in the index within max_distance edits.
        Returns: List of (word, edit_distance) tuples, sorted by distance
        """
        if max_distance is None:
            max_distance = self.max_edit_distance
        term = term.lower()
        results = {}
        # Check exact match first
        if term in self.words:
            results[term] = 0
        # Check delete variants of the input term
        candidates = set()
        candidates.add(term)
        candidates.update(self._get_deletes(term, max_distance))
        for candidate in candidates:
            if candidate in self.deletes:
                for word in self.deletes[candidate]:
                    if word not in results:
                        distance = self._levenshtein_distance(term, word)
                        if distance <= max_distance:
                            results[word] = distance
        for part in term.split('+'):
            if part and part != term:
                # Check exact match first
                if part in self.words:
                    results[part] = 0
                # Check delete variants of the input term
                candidates = set()
                candidates.add(part)
                candidates.update(self._get_deletes(part, max_distance))
                for candidate in candidates:
                    if candidate in self.deletes:
                        for word in self.deletes[candidate]:
                            if word not in results:
                                distance = self._levenshtein_distance(part, word)
                                if distance <= max_distance:
                                    results[word] = distance
        return sorted(results.items(), key=lambda x: (x[1], x[0]))

    def is_match(self, term: str, max_distance: Optional[int] = None) -> bool:
        """Quick check if any match exists within max_distance."""
        return len(self.lookup(term, max_distance)) > 0

    def best_match(self, term: str, max_distance: Optional[int] = None) -> Optional[Tuple[str, int]]:
        """Get the best (closest) match for a term."""
        results = self.lookup(term, max_distance)
        return results[0] if results else None


class FuzzyMatcher:
    """

    Unified interface for fuzzy matching with automatic method selection.

    Usage:

        matcher = FuzzyMatcher(word_list, max_edit_distance=2)

        # Check single term

        matches = matcher.find_matches("peracatamol")

        # Check multiple terms

        results = matcher.batch_check(["peracatamol", "asprin", "ibuprofn"])

    """

    def __init__(self, word_list: List[str], max_edit_distance: int = 2,

                 method: str = "symspell"):

        """

        Initialize the fuzzy matcher.

        Args:

            word_list: Reference list of valid words

            max_edit_distance: Maximum edit distance to consider (default: 2)

            method: "symspell" (fastest)

        """

        self.max_edit_distance = max_edit_distance

        self.word_list = [w.lower() for w in word_list]

        self.method = method

        # Initialize appropriate matcher

        if method == "symspell":

            self._matcher = SymSpell(max_edit_distance)


        else:

            raise ValueError(f"Unknown method: {method}")

        self._matcher.build_index(word_list)

    def find_matches(self, term: str, max_distance: Optional[int] = None

                     ) -> List[Tuple[str, int]]:

        """

        Find all matches for a term within max_distance edits.

        Returns: List of (matched_word, edit_distance) tuples

        """

        if max_distance is None:
            max_distance = self.max_edit_distance

        return self._matcher.lookup(term, max_distance)


    def is_match(self, term: str, max_distance: Optional[int] = None) -> bool:

        """Check if term has any match within max_distance."""

        return len(self.find_matches(term, max_distance)) > 0

    def best_match(self, term: str, max_distance: Optional[int] = None

                   ) -> Optional[Tuple[str, int]]:

        """Get the closest matching word."""

        matches = self.find_matches(term, max_distance)

        return matches[0] if matches else None

    def batch_check(self, terms: List[str], max_distance: Optional[int] = None

                    ) -> Dict[str, List[Tuple[str, int]]]:

        """

        Check multiple terms efficiently.

        Returns: Dictionary mapping each term to its matches

        """

        return {term: self.find_matches(term, max_distance) for term in terms}

    def batch_is_match(self, terms: List[str], max_distance: Optional[int] = None

                       ) -> Dict[str, bool]:

        """Check multiple terms for any match."""

        return {term: self.is_match(term, max_distance) for term in terms}


