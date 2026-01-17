"""
Fast Fuzzy Matching for Large Lists with Spelling Error Tolerance

This module provides highly optimized solutions for checking if words exist
in large lists while accounting for spelling errors.

Time Complexity Comparison:
- Naive approach: O(n * m * k) where n=list size, m=query terms, k=avg word length
- SymSpell: O(1) average lookup after O(n) preprocessing
- BK-Tree: O(log n) average lookup after O(n log n) preprocessing

For your use case (very long lists, multiple queries), SymSpell is recommended.
"""

from typing import List, Tuple, Optional, Set, Dict
from collections import defaultdict
import time


# =============================================================================
# METHOD 1: SYMSPELL (FASTEST - RECOMMENDED)
# =============================================================================

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
        return sorted(results.items(), key=lambda x: (x[1], x[0]))

    def is_match(self, term: str, max_distance: Optional[int] = None) -> bool:
        """Quick check if any match exists within max_distance."""
        return len(self.lookup(term, max_distance)) > 0

    def best_match(self, term: str, max_distance: Optional[int] = None) -> Optional[Tuple[str, int]]:
        """Get the best (closest) match for a term."""
        results = self.lookup(term, max_distance)
        return results[0] if results else None


# =============================================================================

# METHOD 2: BK-TREE (MEMORY EFFICIENT)

# =============================================================================

class BKTreeNode:
    """Node in a BK-Tree."""

    def __init__(self, word: str):
        self.word = word

        self.children: Dict[int, 'BKTreeNode'] = {}


class BKTree:
    """

    Burkhard-Keller Tree for efficient fuzzy matching.

    How it works:

    - Tree structure where edges are labeled with edit distances

    - Uses triangle inequality to prune search space

    - More memory efficient than SymSpell

    Time Complexity:

    - Build: O(n log n) average

    - Lookup: O(log n) average, O(n) worst case

    """

    def __init__(self):

        self.root: Optional[BKTreeNode] = None

        self.size = 0

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

    def add(self, word: str) -> None:

        """Add a word to the BK-Tree."""

        word = word.lower()

        if self.root is None:
            self.root = BKTreeNode(word)

            self.size = 1

            return

        node = self.root

        while True:

            distance = self._levenshtein_distance(word, node.word)

            if distance == 0:  # Duplicate

                return

            if distance in node.children:

                node = node.children[distance]

            else:

                node.children[distance] = BKTreeNode(word)

                self.size += 1

                return

    def build_index(self, word_list: List[str]) -> None:

        """Build the BK-Tree from a list of words."""

        self.root = None

        self.size = 0

        for word in word_list:
            self.add(word)

    def lookup(self, term: str, max_distance: int = 2) -> List[Tuple[str, int]]:

        """

        Find all words within max_distance edits.

        Returns: List of (word, edit_distance) tuples, sorted by distance

        """

        term = term.lower()

        results = []

        if self.root is None:
            return results

        # BFS with distance-based pruning

        stack = [self.root]

        while stack:

            node = stack.pop()

            distance = self._levenshtein_distance(term, node.word)

            if distance <= max_distance:
                results.append((node.word, distance))

            # Only explore children within the valid range

            # Triangle inequality: |d(term, child) - d(term, node)| <= d(node, child)

            low = max(1, distance - max_distance)

            high = distance + max_distance

            for edge_dist, child in node.children.items():

                if low <= edge_dist <= high:
                    stack.append(child)

        return sorted(results, key=lambda x: (x[1], x[0]))

    def is_match(self, term: str, max_distance: int = 2) -> bool:

        """Quick check if any match exists within max_distance."""

        return len(self.lookup(term, max_distance)) > 0

    def best_match(self, term: str, max_distance: int = 2) -> Optional[Tuple[str, int]]:

        """Get the best (closest) match for a term."""

        results = self.lookup(term, max_distance)

        return results[0] if results else None


# =============================================================================

# METHOD 3: OPTIMIZED HASH-BASED (FOR EXACT + 1 EDIT DISTANCE)

# =============================================================================

class FastFuzzySet:
    """

    Ultra-fast fuzzy matching for edit distance of 1.

    Uses hash-based approach with character deletion patterns.

    Time Complexity:

    - Build: O(n * w) where n=words, w=avg word length

    - Lookup: O(w) for edit distance 1

    Best for: When you only need to match with 1 spelling error

    """

    def __init__(self):

        self.exact_words: Set[str] = set()

        self.delete_patterns: Dict[str, Set[str]] = defaultdict(set)

    def _get_patterns(self, word: str) -> Set[str]:

        """Generate all single-character deletion patterns."""

        patterns = set()

        for i in range(len(word)):
            patterns.add(word[:i] + word[i + 1:])

        return patterns

    def build_index(self, word_list: List[str]) -> None:

        """Build the index from a list of words."""

        self.exact_words = set(word.lower() for word in word_list)

        self.delete_patterns.clear()

        for word in self.exact_words:

            for pattern in self._get_patterns(word):
                self.delete_patterns[pattern].add(word)

    def lookup(self, term: str, max_distance: int = 1) -> List[Tuple[str, int]]:

        """Find matches within edit distance 1."""

        term = term.lower()

        results = {}

        # Exact match

        if term in self.exact_words:
            results[term] = 0

        if max_distance >= 1:

            # Check deletions of term (handles insertions in dictionary)

            for pattern in self._get_patterns(term):

                if pattern in self.exact_words:
                    results[pattern] = 1

                # Also check for matches via deletion patterns

                for word in self.delete_patterns.get(pattern, []):

                    if word not in results:
                        results[word] = 1

            # Check if term matches deletion patterns (handles deletions in term)

            for word in self.delete_patterns.get(term, []):

                if word not in results:
                    results[word] = 1

        return sorted(results.items(), key=lambda x: (x[1], x[0]))


# =============================================================================

# UNIFIED INTERFACE

# =============================================================================

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

                 method: str = "auto"):

        """

        Initialize the fuzzy matcher.

        Args:

            word_list: Reference list of valid words

            max_edit_distance: Maximum edit distance to consider (default: 2)

            method: "symspell" (fastest), "bktree" (memory efficient),

                   "fast" (edit distance 1 only), or "auto"

        """

        self.max_edit_distance = max_edit_distance

        self.word_list = [w.lower() for w in word_list]

        # Auto-select method

        if method == "auto":

            if max_edit_distance == 1:

                method = "fast"

            else:

                method = "symspell"

        self.method = method

        # Initialize appropriate matcher

        if method == "symspell":

            self._matcher = SymSpell(max_edit_distance)

        elif method == "bktree":

            self._matcher = BKTree()

        elif method == "fast":

            self._matcher = FastFuzzySet()

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

        if self.method == "bktree":

            return self._matcher.lookup(term, max_distance)

        else:

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


# =============================================================================

# EXAMPLE USAGE AND BENCHMARKS

# =============================================================================

def run_demo():
    """Demonstrate usage with examples."""

    print("=" * 70)

    print("FUZZY MATCHER - DEMO")

    print("=" * 70)

    # Sample word list (pharmaceutical terms)

    word_list = [

        "Paracetamol", "Acetaminophen", "Ibuprofen", "Aspirin", "Naproxen",

        "Diclofenac", "Celecoxib", "Meloxicam", "Indomethacin", "Ketoprofen",

        "Piroxicam", "Etodolac", "Ketorolac", "Sulindac", "Mefenamic",

        "Amoxicillin", "Penicillin", "Ciprofloxacin", "Azithromycin",

        "Metformin", "Lisinopril", "Atorvastatin", "Omeprazole", "Metoprolol",

        "Amlodipine", "Hydrochlorothiazide", "Losartan", "Gabapentin",

        "Sertraline", "Fluoxetine", "Escitalopram", "Duloxetine", "Venlafaxine"

    ]

    # Terms to check (with spelling errors)

    test_terms = [

        "peracatamol",  # Paracetamol

        "asprin",  # Aspirin

        "ibuprofn",  # Ibuprofen

        "amoxicilin",  # Amoxicillin

        "metformine",  # Metformin

        "atorvasttin",  # Atorvastatin

        "lisinipril",  # Lisinopril

        "omperazole",  # Omeprazole

        "gabapentn",  # Gabapentin

        "sertrlaine",  # Sertraline

        "xyz123",  # No match

    ]

    # Initialize matcher

    print("\n1. INITIALIZING MATCHER")

    print("-" * 40)

    start = time.perf_counter()

    matcher = FuzzyMatcher(word_list, max_edit_distance=2, method="symspell")

    build_time = time.perf_counter() - start

    print(f"   Method: SymSpell")

    print(f"   Word list size: {len(word_list)}")

    print(f"   Max edit distance: 2")

    print(f"   Build time: {build_time * 1000:.3f} ms")

    # Single term lookup

    print("\n2. SINGLE TERM LOOKUPS")

    print("-" * 40)

    for term in test_terms[:5]:

        matches = matcher.find_matches(term)

        if matches:

            best = matches[0]

            print(f"   '{term}' → '{best[0]}' (distance: {best[1]})")

        else:

            print(f"   '{term}' → No match found")

    # Batch processing

    print("\n3. BATCH PROCESSING")

    print("-" * 40)

    start = time.perf_counter()

    results = matcher.batch_check(test_terms)

    batch_time = time.perf_counter() - start

    for term, matches in results.items():
        status = f"→ {matches[0][0]}" if matches else "→ NO MATCH"

        print(f"   {term:20} {status}")

    print(f"\n   Batch lookup time: {batch_time * 1000:.3f} ms")

    print(f"   Average per term: {batch_time * 1000 / len(test_terms):.3f} ms")

    return matcher


def run_benchmark(list_sizes=[1000, 10000, 100000], num_queries=1000):
    """Run performance benchmarks."""

    print("\n" + "=" * 70)

    print("PERFORMANCE BENCHMARKS")

    print("=" * 70)

    import random

    import string

    def generate_words(n, min_len=5, max_len=15):

        """Generate random words for testing."""

        words = []

        for _ in range(n):
            length = random.randint(min_len, max_len)

            word = ''.join(random.choices(string.ascii_lowercase, k=length))

            words.append(word)

        return words

    def add_typos(word, num_typos=1):

        """Add random typos to a word."""

        word = list(word)

        for _ in range(min(num_typos, len(word))):
            pos = random.randint(0, len(word) - 1)

            word[pos] = random.choice(string.ascii_lowercase)

        return ''.join(word)

    for list_size in list_sizes:

        print(f"\n{'─' * 70}")

        print(f"LIST SIZE: {list_size:,}")

        print(f"{'─' * 70}")

        # Generate word list

        word_list = generate_words(list_size)

        # Generate query terms (mix of exact matches and typos)

        sample_words = random.sample(word_list, min(num_queries, len(word_list)))

        query_terms = [add_typos(w, random.randint(0, 2)) for w in sample_words]

        methods = [

            ("SymSpell", "symspell"),

            ("BK-Tree", "bktree"),

        ]

        for name, method in methods:

            print(f"\n   {name}:")

            # Build time

            start = time.perf_counter()

            matcher = FuzzyMatcher(word_list, max_edit_distance=2, method=method)

            build_time = time.perf_counter() - start

            print(f"      Build time: {build_time * 1000:.2f} ms")

            # Query time

            start = time.perf_counter()

            for term in query_terms:
                matcher.find_matches(term)

            query_time = time.perf_counter() - start

            print(f"      {num_queries} queries: {query_time * 1000:.2f} ms")

            print(f"      Avg per query: {query_time * 1000 / num_queries:.4f} ms")

            print(f"      Queries/second: {num_queries / query_time:,.0f}")


if __name__ == "__main__":
    # Run demo

    matcher = run_demo()

    # Run benchmarks (uncomment for full benchmark)

    print("\n" + "=" * 70)

    print("Running benchmarks (this may take a moment)...")

    run_benchmark(list_sizes=[1000, 10000, 50000], num_queries=500)

    print("\n" + "=" * 70)

    print("QUICK START EXAMPLE")

    print("=" * 70)

    print("""

    # Basic usage:

    from fuzzy_matcher import FuzzyMatcher

    # Your reference list

    word_list = ["Paracetamol", "Aspirin", "Ibuprofen", ...]

    # Initialize (do once)

    matcher = FuzzyMatcher(word_list, max_edit_distance=2)

    # Find matches for a term

    matches = matcher.find_matches("peracatamol")

    # Returns: [('paracetamol', 2)]

    # Check multiple terms

    results = matcher.batch_check(["asprin", "ibuprofn"])

    # Returns: {'asprin': [('aspirin', 1)], 'ibuprofn': [('ibuprofen', 1)]}

    # Quick boolean check

    exists = matcher.is_match("peracatamol")

    # Returns: True

    """)
