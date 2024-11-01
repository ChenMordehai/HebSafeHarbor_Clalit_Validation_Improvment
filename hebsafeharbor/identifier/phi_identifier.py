from typing import List

from hebsafeharbor.common.city_utils import (
    BELOW_THRESHOLD_CITIES_LIST,
    ABOVE_THRESHOLD_CITIES_LIST,
    ABBREVIATIONS_LIST,
    AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST,
    AMBIGOUS_ABOVE_THRESHOLD_CITIES_LIST,
    AMBIGUOUS_CITIES_CONTEXT
)
from hebsafeharbor.common.country_utils import COUNTRY_DICT
from hebsafeharbor.common.document import Doc
from hebsafeharbor.common.prepositions import LOCATION_PREPOSITIONS, DISEASE_PREPOSITIONS, MEDICATION_PREPOSITIONS, \
    MEDICAL_TEST_PREPOSITIONS
from hebsafeharbor.identifier import HebSpacyNlpEngine
from hebsafeharbor.identifier.consolidation.consolidator import NerConsolidator
from hebsafeharbor.identifier.entity_smoother.entity_smoother_rule_executor import EntitySmootherRuleExecutor
from hebsafeharbor.identifier.entity_spliters.entity_splitter_rule_executor import EntitySplitterRuleExecutor

from hebsafeharbor.identifier.signals import *
from presidio_analyzer import AnalyzerEngine, LocalRecognizer, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer, DateRecognizer, EmailRecognizer, \
    IpRecognizer, PhoneRecognizer, UrlRecognizer
from global_variables.global_variables import VARIABLES
from hebsafeharbor.identifier.signals.noisy_date_recognizer import NoisyDateRecognizer
from hebsafeharbor.identifier.signals.special_name_recognizer import SpecialNamesRecognizer
from hebsafeharbor.lexicons.disease import DISEASES
from hebsafeharbor.lexicons.lab_tests import LAB_TESTS
from hebsafeharbor.lexicons.medical_device import MEDICAL_DEVICE
from hebsafeharbor.lexicons.medical_tests import MEDICAL_TESTS
from hebsafeharbor.lexicons.medications import MEDICATIONS
from hebsafeharbor.lexicons.body_parts import BODY_PARTS
from hebsafeharbor.lexicons.hospital_lexicon import HOSPITALS
from hebsafeharbor.lexicons.camoni_med_terms import CAMONI_MED_TERMS
from hebsafeharbor.lexicons.rcog_med_terms import RCOG_MED_TERMS
from hebsafeharbor.lexicons.gens import GENS
from hebsafeharbor.identifier.consolidation.consolidation_config import ENTITY_TYPES_TO_IGNORE
from hebsafeharbor.identifier.signals.pathology_id_recognizer import PathologyIdRecognizer
#3la2
from hebsafeharbor.identifier.signals.medical_staff_recognizer import GeneralMedicalStaffRecognizer
from hebsafeharbor.identifier.entity_score_fixer.entity_score_fixer_rule_executor import EntityScoreFixerRuleExecutor

class PhiIdentifier:
    """
    This class is responsible on the identification process, recognize entities using the AnalyzerEngine (@Presidio) and
    consolidate them using NERConsolidator.
    """

    def __init__(self):
        """
        Initializes the PhiIdentifier which is composed of Presidio analyzer and NerConsolidator
        """

        self.analyzer = self._init_presidio_analyzer()
        self.entity_smoother = EntitySmootherRuleExecutor()
        self.entity_splitter = EntitySplitterRuleExecutor()
        self.consolidator = NerConsolidator()
        #3la2
        self.entity_score_fixer = EntityScoreFixerRuleExecutor()

    def __call__(self, doc: Doc) -> Doc:
        """
        This method identifies the PHI entities

        :param doc: Doc object which holds the input text for PHI reduction
        :return: an updated Doc object that contains the the set of entities that were recognized by the different
        signals and the consolidated set of entities
        """

        # recognition
        analyzer_results = self.analyzer.analyze(text=doc.text.lower(), language="he", return_decision_process=True)
        for a in analyzer_results:
            if a.entity_type == 'DUC':
                a.entity_type = 'PERS'
            elif (a.entity_type in ["EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "URL"] and a.end-a.start<9) or (a.entity_type in ["EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "URL"] and doc.text[a.start:a.end].count('.')<2):
                a.entity_type = 'MEDICAL_TEST'

        analyzer_results = [a for a in analyzer_results if a.entity_type not in ENTITY_TYPES_TO_IGNORE]
        doc.analyzer_results = sorted(analyzer_results, key=lambda res: res.start)
        # entity smoothing
        doc = self.entity_smoother(doc)

        # consolidation
        doc = self.consolidator(doc)

        # entity splitter
        doc = self.entity_splitter(doc)

        # score fixer
        #3la2
        doc = self.entity_score_fixer(doc)

        return doc

    def _init_presidio_analyzer(self) -> AnalyzerEngine:
        """
        Creates and initializes the Presidio analyzer
        :return: Presidio analyzer
        """

        # create NLP engine based on the nlp configuration
        nlp_engine = HebSpacyNlpEngine(models={"he": "he_ner_news_trf"})

        # initialize the signals
        signals = self._init_analyzer_signals()
        # create the signals registry
        registry = RecognizerRegistry()
        # add the different signals to registry
        for signal in signals:
            registry.add_recognizer(signal)

        # create the AnalyzerEngine using the created registry, NLP engine and supported_languages
        analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine,
            supported_languages=["he"],
        )

        return analyzer

    def _init_analyzer_signals(self) -> List[LocalRecognizer]:
        """
        Creates and initializes the analyzer's NER signals

        :return: a list of NER initialized signals
        """

        ner_signals = []

        # presidio predefined recognizers
        
        #3la2
        # ner_signals.append(GeneralMedicalStaffRecognizer())

        ner_signals.append(CreditCardRecognizer(supported_language="he", context=["כרטיס", "אשראי"]))
        ner_signals.append(
            DateRecognizer(supported_language="he", context=["תאריך", "לידה", "הולדת", "נולד", "נולדה", "נולדו"]))
        ner_signals.append(
            EmailRecognizer(supported_language="he", context=["אימייל", "דואל", "email", "דואר אלקטרוני"]))
        ner_signals.append(IpRecognizer(supported_language="he", context=["IP", "כתובת IP", "כתובת איי פי"]))
        ner_signals.append(PhoneRecognizer(supported_language="he", context=["טלפון", "סלולרי", "פקס"]))
        ner_signals.append(UrlRecognizer(supported_language="he", context=["אתר אינטרנט"]))

        hebspacy_recognizer = self.init_hebspacy_recognizer()

        ner_signals.append(hebspacy_recognizer)
        # init Israeli id number recognizer
        ner_signals.append(IsraeliIdNumberRecognizer())
        # init general id recognizer
        if VARIABLES['context'] == 'pathology':
            ner_signals.append(PathologyIdRecognizer())
        else:
            ner_signals.append(GeneralIdRecognizer())
        # init dates in hebrew
        ner_signals.append(HebDateRecognizer())
        # init dates with preposition
        ner_signals.append(PrepositionDateRecognizer())
        # init latin dates
        ner_signals.append(HebLatinDateRecognizer())
        # init noisy dates
        ner_signals.append(NoisyDateRecognizer())
        # init Hebrew country recognizer
        ner_signals.append(LexiconBasedRecognizer("CountryRecognizer", "COUNTRY", COUNTRY_DICT.keys(),
                                                  allowed_prepositions=LOCATION_PREPOSITIONS))
        # init Hebrew city recognizers
        cities_set = set(BELOW_THRESHOLD_CITIES_LIST).union(
            set(ABOVE_THRESHOLD_CITIES_LIST)).union(set(ABBREVIATIONS_LIST))
        ambiguous_cities_set = set(
            AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST).union(
            set(AMBIGOUS_ABOVE_THRESHOLD_CITIES_LIST))
        disambiguated_cities_set = cities_set - ambiguous_cities_set
        ner_signals.append(LexiconBasedRecognizer("IsraeliCityRecognizer", "CITY",
                                                  disambiguated_cities_set,
                                                  allowed_prepositions=LOCATION_PREPOSITIONS))

        ner_signals.append(AmbiguousHebrewCityRecognizer("AmbiguousHebrewCityRecognizer", "CITY",
                                                         ambiguous_cities_set,
                                                         allowed_prepositions=LOCATION_PREPOSITIONS,
                                                         endorsing_entities=['LOC', 'GPE'],
                                                         context=AMBIGUOUS_CITIES_CONTEXT,
                                                         ),
                           )

        # init disease recognizer
        ner_signals.append(
            LexiconBasedRecognizer("DiseaseRecognizer", "DISEASE", DISEASES, allowed_prepositions=DISEASE_PREPOSITIONS))
        # init medication recognizer
        ner_signals.append(
            LexiconBasedRecognizer("MedicationRecognizer", "MEDICATION", MEDICATIONS,
                                   allowed_prepositions=MEDICATION_PREPOSITIONS))
        # init medical tests recognizer
        ner_signals.append(
            LexiconBasedRecognizer("MedicalTestRecognizer", "MEDICAL_TEST", MEDICAL_TESTS + MEDICAL_DEVICE + LAB_TESTS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))

        # init body parts recognizer
        ner_signals.append(
            LexiconBasedRecognizer("BodyPartsRecognizer", "BODY_PARTS", BODY_PARTS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))
        # init hospitals recognizer
        ner_signals.append(
            LexiconBasedRecognizer("HospitalsRecognizer", "HOSPITALS", HOSPITALS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))

        # init lab tests recognizer
        ner_signals.append(
            LexiconBasedRecognizer("LabTestsRecognizer", "LAB_TESTS", LAB_TESTS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))

        # init camoni terms recognizer
        ner_signals.append(
            LexiconBasedRecognizer("CamoniTermsRecognizer", "CAMONI_MED_TERMS", CAMONI_MED_TERMS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))
        # init rcog terms recognizer
        ner_signals.append(
            LexiconBasedRecognizer("RcogTermsRecognizer", "RCOG_MED_TERMS", RCOG_MED_TERMS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))
        # gens recognizer
        # init rcog terms recognizer
        ner_signals.append(
            LexiconBasedRecognizer("GensRecognizer", "GENS", GENS,
                                   allowed_prepositions=MEDICAL_TEST_PREPOSITIONS))
        # special names recognizer
        ner_signals.append(SpecialNamesRecognizer())

        return ner_signals

    def init_hebspacy_recognizer(self):
        """
        Adapt the SpacyRecognizer to fit the specific entities of HebSpacy.
        """

        hebspacy_entities = ["PERS", "LOC", "ORG", "TIME", "DATE", "MONEY", "PERCENT", "MISC__AFF", "MISC__ENT",
                             "MISC_EVENT", "PER", "GPE", "FAC", "WOA", "EVE", "DUC", "ANG"]
        hebspacy_label_groups = [
            ({ent}, {ent}) for ent in hebspacy_entities
        ]
        hebspacy_recognizer = SpacyRecognizerWithConfidence(supported_language="he",
                                              supported_entities=hebspacy_entities,
                                              ner_strength=1.0,
                                              check_label_groups=hebspacy_label_groups)
        return hebspacy_recognizer
