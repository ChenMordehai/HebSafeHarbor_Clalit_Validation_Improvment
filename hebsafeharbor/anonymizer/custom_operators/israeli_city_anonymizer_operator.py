import ast
from typing import Dict

from presidio_anonymizer.operators import OperatorType, Operator

from global_variables.global_variables import VARIABLES
from hebsafeharbor.common.city_utils import ABOVE_THRESHOLD_CITIES_LIST, BELOW_THRESHOLD_CITIES_LIST, \
    ABBREVIATIONS_LIST, AMBIGOUS_ABOVE_THRESHOLD_CITIES_LIST, AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST


class IsraeliCityAnonymizerOperator(Operator):
    """
    An instance of the IsraeliCityAnonymizerOperator which extends the Operator abstract class (@Presidio).
    For each recognized entity of type CITY, this custom operator anonymizes the cities with population below 2000.
    """

    def operate(self, text: str, params: Dict = None) -> str:
        """
        This method applies the anonymization policy of the IsraeliCityAnonymizerOperator on the given recognized entity text

        :param text: recognized entity text for anonymization
        :param params: optional parameters
        :return: the anonymized text of the entity
        """
        # TODO: check context

        if text in ABOVE_THRESHOLD_CITIES_LIST:
            return text
        elif text in AMBIGOUS_ABOVE_THRESHOLD_CITIES_LIST:
            return text
        elif text in ABBREVIATIONS_LIST:
            return text
        elif text in AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST:
            return text
        elif text in BELOW_THRESHOLD_CITIES_LIST:
            return "<מיקום_>"
        return text
        # # check ambiguous TODO
        # # elif text in AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST:
        # amb_list = [item for item in AMBIGOUS_BELOW_THRESHOLD_CITIES_LIST if item.startswith(text)]
        # for phrase in amb_list:
        #     phrase_after_split = phrase.split(":::")
        #     if len(phrase_after_split) > 1:
        #         p_context = ast.literal_eval(phrase_after_split[1])
        #         if VARIABLES['context'] not in p_context:
        #             return text
        #         else:
        #             return "<מיקום_>"
        #     return text
        # return "<מיקום_>"

    def validate(self, params: Dict = None) -> None:
        """
        This method validates each operator parameters
        :param params: operator custom parameters
        """
        pass

    def operator_name(self) -> str:
        """
        Returns the operator name

        :return: the operator name
        """

        return "replace_cities_under_2k"

    def operator_type(self) -> OperatorType:
        """
        Returns the operator type

        :return: the operator type
        """

        return OperatorType.Anonymize
