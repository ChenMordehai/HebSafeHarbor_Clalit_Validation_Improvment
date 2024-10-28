from presidio_analyzer import PatternRecognizer, Pattern


class PathologyIdRecognizer(PatternRecognizer):
    """
    A class which extends the PatternRecognizer (@Presidio) and responsible for the recognition of IDs.
    """

    PATTERNS = [
        Pattern(
            "five or more digits optionally separated by a single dash",
            r"\d{1}[-]{1}\d{4,}|\d{2}[-]{1}\d{3,}|\d{3}[-]{1}\d{2,}|\d{4,}[-]{1}\d{1,}|\d{5,}",
            0.6)
    ]

    SUPPORTED_ENTITY = "ID"

    def __init__(self):
        """
        Initializes the PathologyIdRecognizer object
        """
        super().__init__(supported_entity=PathologyIdRecognizer.SUPPORTED_ENTITY, patterns=PathologyIdRecognizer.PATTERNS,
                         name="PathologyIdRecognizer", supported_language="he")
