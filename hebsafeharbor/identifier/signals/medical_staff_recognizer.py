from presidio_analyzer import PatternRecognizer, Pattern
from hebsafeharbor.lexicons.healthcare_professional_staff import HEALTHCARE_PROFESSIONAL_STAFF


class GeneralMedicalStaffRecognizer(PatternRecognizer):
    """
    A class which extends the PatternRecognizer (@Presidio) and responsible for the recognition of medical staff names.
    """

    PATTERNS=[]
    #r' \s*([\u0590-\u05FF\s]+)',
    #r' \s*([\u0590-\u05FF\-]+[\s\u0590-\u05FF\-])'
    #r' \s*([\u0590-\u05FF]+-?\s[\u0590-\u05FF]+-?)
    for p in HEALTHCARE_PROFESSIONAL_STAFF:
        PATTERNS.append(Pattern(name="hebrew_staff_name_pattern",
                                regex=' ' + p + r' \s*([\u0590-\u05FF.,;\'\"]+(?:-?[\u0590-\u05FF.,;\'\"]?:-?)*)',
                                score=0.99654321))


    SUPPORTED_ENTITY = "STAFF_PER"

    def __init__(self):
        """
        Initializes the GeneralMedicalStaffRecognizer object
        """
        super().__init__(supported_entity=GeneralMedicalStaffRecognizer.SUPPORTED_ENTITY,
                         patterns=GeneralMedicalStaffRecognizer.PATTERNS,
                         name="GeneralMedicalStaffRecognizer",
                         context=HEALTHCARE_PROFESSIONAL_STAFF,
                         supported_language="he")
