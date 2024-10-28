from typing import List
from presidio_analyzer import EntityRecognizer, RecognizerResult, AnalysisExplanation
from presidio_analyzer.nlp_engine import NlpArtifacts
import string
from hebsafeharbor.identifier.signals.lexicon_based_recognizer import LexiconBasedRecognizer
from hebsafeharbor.common.terms_recognizer import TermsRecognizer
import pandas as pd


def split_text_to_words(text):
    words = []
    start = 0
    end = 0

    for i, char in enumerate(text):
        if char.isspace() or char in string.punctuation:
            if end > start:
                word = {
                    'term': text[start:end],
                    'start': start,
                    'end': end - 1
                }
                words.append(word)
            start = i + 1
        end = i + 1

    if end > start:
        word = {
            'term': text[start:end],
            'start': start,
            'end': end - 1
        }
        words.append(word)
    return words


class SpecialNamesRecognizer(LexiconBasedRecognizer):
    """

    """
    DEFAULT_CONFIDENCE_LEVEL = 0.8  # expected confidence level for this recognizer

    def __init__(self):
        """

        """
        super().__init__(name="special_names_recognizer", supported_entity='PERS', phrase_list=[],
                         supported_language="he")
        # self.terms_recognizer = TermsRecognizer(phrase_list)
        # self.allowed_prepositions = allowed_prepositions if allowed_prepositions else []

    def load(self) -> None:
        """No loading is required."""
        pass

    def analyze(
            self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Recognize entities based on lexicon
        :param text: text for recognition
        :param entities: supported entities
        :param nlp_artifacts: artifacts of the nlp engine
        :return list of entities recognized based on the lexicon
        """

        results = []

        terms = split_text_to_words(text)
        new_terms = []

        # Iterate over the Automaton offsets and create Recognizer result for each of them
        for t in new_terms:
            result = RecognizerResult(
                entity_type="PERS",
                start=t['start'],
                end=t['end'],
                score=self.DEFAULT_CONFIDENCE_LEVEL,
                analysis_explanation=AnalysisExplanation(self.name, self.DEFAULT_CONFIDENCE_LEVEL),
                recognition_metadata={RecognizerResult.RECOGNIZER_NAME_KEY: self.name}
            )
            results.append(result)
        return results
