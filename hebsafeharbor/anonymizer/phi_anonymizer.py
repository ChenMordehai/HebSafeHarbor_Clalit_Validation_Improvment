from typing import List

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer.operators import Operator
from presidio_analyzer import RecognizerResult

from hebsafeharbor import Doc
from hebsafeharbor.anonymizer.custom_operators.birth_date_anonymizer_operator import BirthDateAnonymizerOperator
from hebsafeharbor.anonymizer.custom_operators.country_anonymizer_operator import CountryAnonymizerOperator
from hebsafeharbor.anonymizer.custom_operators.hebrew_replace_anonymizer_operator import ReplaceInHebrew
from hebsafeharbor.anonymizer.custom_operators.israeli_city_anonymizer_operator import IsraeliCityAnonymizerOperator
from hebsafeharbor.anonymizer.custom_operators.medical_date_anonymizer_operator import MedicalDateAnonymizerOperator
from hebsafeharbor.anonymizer.custom_operators.do_not_anonymize_operator import DoNotAnonymize
from global_variables.global_variables import VARIABLES

def filter_low_scores(doc_granular_analyzer_results) -> List[RecognizerResult]:
    filtered = []
    MIN_FIXED_SCORE = VARIABLES['PER_MIN_SCORE']
    for item in doc_granular_analyzer_results:
        if item.entity_type in ['PERS', 'PER']:
            if item.score >= MIN_FIXED_SCORE:
                filtered.append(item)
        else:
            filtered.append(item)
    return filtered

class PhiAnonymizer:
    """
    This class is responsible on the anonymization process. It anonymizes the entities using the AnonymizerEngine
    (@Presidio)
    """

    def __init__(self):
        """
        Initializes the PhiAnonymizer which is composed of Presidio anonymizer and a list of custom operators*
        """
        self.anonymizer = AnonymizerEngine()
        self.operators = self.init_custom_operators()

    def __call__(self, doc: Doc, lang) -> Doc:
        """
        This method anonymizes the entities which were previously recognized earlier by the identifier

        :param doc: Doc object which holds the input text for PHI reduction and the entities which were previously
        recognized earlier by the identifier
        lang: string of language of text
        :return: an updated Doc object that contains the anonymized text (the text itself and the anonymized entities)
        """
        # the call to the anonymizer in the long term (custom operator is part of presidio package)
        # anonymized_results = self.anonymizer.anonymize(text=doc.text, analyzer_results=doc.consolidated_results)

        # if family -> filter items with low scores else no need to filter
        if VARIABLES['context'] == 'family':
            doc.granular_analyzer_results=filter_low_scores(doc.granular_analyzer_results)

        # the call to the anonymizer in the short term (custom operator as lambda function)
        if lang == 'he':
            anonymized_results = self.anonymizer.anonymize(
                text=doc.text,
                analyzer_results=doc.granular_analyzer_results,
                operators={
                    "PERS": OperatorConfig(self.operators[0].operator_name(),
                                           {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "PER": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "LOC": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "GPE": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "ORG": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "FAC": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "CREDIT_CARD": OperatorConfig(self.operators[0].operator_name(),
                                                  {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "ISRAELI_ID_NUMBER": OperatorConfig(self.operators[0].operator_name(),
                                                        {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "ID": OperatorConfig(self.operators[0].operator_name(),
                                         {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "EMAIL_ADDRESS": OperatorConfig(self.operators[0].operator_name(),
                                                    {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "IP_ADDRESS": OperatorConfig(self.operators[0].operator_name(),
                                                 {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "URL": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "PHONE_NUMBER": OperatorConfig(self.operators[0].operator_name(),
                                                   {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "DATE": OperatorConfig(self.operators[0].operator_name(),
                                           {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "BIRTH_DATE": OperatorConfig(self.operators[1].operator_name(),
                                                 {"lambda": lambda x: self.operators[1].operate(x)}),
                    "MEDICAL_DATE": OperatorConfig(self.operators[2].operator_name(),
                                                   {"lambda": lambda x: self.operators[2].operate(x)}),
                    "COUNTRY": OperatorConfig(self.operators[3].operator_name(),
                                              {"lambda": lambda x: self.operators[3].operate(x)}),
                    "CITY": OperatorConfig(self.operators[4].operator_name(),
                                           {"lambda": lambda x: self.operators[4].operate(x)}),
                    "HOSPITALS": OperatorConfig(self.operators[0].operator_name(),
                                           {"lambda": lambda x: self.operators[4].operate(x)}),
                    "PER_fixed": OperatorConfig(self.operators[0].operator_name(),
                                                {"lambda": lambda x: self.operators[4].operate(x)}),
                    "PERS_fixed": OperatorConfig(self.operators[0].operator_name(),
                                                {"lambda": lambda x: self.operators[4].operate(x)}),
                },
            )
        # if language is english anonymize selected entity types
        elif lang == 'en':
            anonymized_results = self.anonymizer.anonymize(
                text=doc.text,
                analyzer_results=doc.granular_analyzer_results,
                operators={
                    "PERS": OperatorConfig(self.operators[5].operator_name(),
                                           {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "PER": OperatorConfig(self.operators[5].operator_name(),
                                          {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "LOC": OperatorConfig(self.operators[5].operator_name(),
                                          {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "GPE": OperatorConfig(self.operators[5].operator_name(),
                                          {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "ORG": OperatorConfig(self.operators[5].operator_name(),
                                          {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "FAC": OperatorConfig(self.operators[5].operator_name(),
                                          {"lambda": lambda x, y: self.operators[5].operate(x, y)}),
                    "CREDIT_CARD": OperatorConfig(self.operators[0].operator_name(),
                                                  {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "ISRAELI_ID_NUMBER": OperatorConfig(self.operators[0].operator_name(),
                                                        {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "ID": OperatorConfig(self.operators[0].operator_name(),
                                         {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "EMAIL_ADDRESS": OperatorConfig(self.operators[0].operator_name(),
                                                    {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "IP_ADDRESS": OperatorConfig(self.operators[0].operator_name(),
                                                 {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "URL": OperatorConfig(self.operators[0].operator_name(),
                                          {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "PHONE_NUMBER": OperatorConfig(self.operators[0].operator_name(),
                                                   {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "DATE": OperatorConfig(self.operators[0].operator_name(),
                                           {"lambda": lambda x, y: self.operators[0].operate(x, y)}),
                    "BIRTH_DATE": OperatorConfig(self.operators[1].operator_name(),
                                                 {"lambda": lambda x: self.operators[1].operate(x)}),
                    "MEDICAL_DATE": OperatorConfig(self.operators[2].operator_name(),
                                                   {"lambda": lambda x: self.operators[2].operate(x)}),
                    "COUNTRY": OperatorConfig(self.operators[5].operator_name(),
                                              {"lambda": lambda x: self.operators[5].operate(x)}),
                    "CITY": OperatorConfig(self.operators[5].operator_name(),
                                           {"lambda": lambda x: self.operators[5].operate(x)}),
                    "HOSPITALS": OperatorConfig(self.operators[5].operator_name(),
                                                {"lambda": lambda x: self.operators[5].operate(x)}),
                    "PER_fixed": OperatorConfig(self.operators[5].operator_name(),
                                                {"lambda": lambda x: self.operators[5].operate(x)}),
                    "PERS_fixed": OperatorConfig(self.operators[5].operator_name(),
                                                 {"lambda": lambda x: self.operators[5].operate(x)}),
                },
            )
        anonymized_results.items.sort(key=lambda res: res.start)
        doc.anonymized_text = anonymized_results

        return doc

    def init_custom_operators(self) -> List[Operator]:
        """
        Creates the instances of custom operators to use during the anonymization process
        :return: list of initialized custom operators
        """
        return [ReplaceInHebrew(), BirthDateAnonymizerOperator(), MedicalDateAnonymizerOperator(),
                CountryAnonymizerOperator(), IsraeliCityAnonymizerOperator(), DoNotAnonymize(),
                ]
