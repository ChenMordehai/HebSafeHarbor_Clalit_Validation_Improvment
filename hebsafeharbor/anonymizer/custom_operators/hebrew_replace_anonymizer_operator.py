from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType


def has_no_whitespace(s: str) -> bool:
    for ch in s:
        if ch.isspace():
            return False
    return True

def has_no_plus_sign(s: str) -> bool:
    for ch in s:
        if ch == '+':
            return False
    return True


class ReplaceInHebrew(Operator):
    """
    An instance of the Operator abstract class (@Presidio). For each recognized entity ,this custom
    replace it by custom string depending on its entity type.
    """

    def operate(self, text: str = None, params: Dict = None) -> str:
        """:return: new_value."""
        entity_type = params.get("entity_type")
        if entity_type in ["PERS", "PER", "PER_fixed", "PERS_fixed"] and has_no_plus_sign(text):
            return "<שם_>"
        elif entity_type in ["LOC", "GPE"]:
            return "<מיקום_>"
        elif entity_type in ["ORG", "FAC", "HOSPITALS"]:
            return "<ארגון_>"
        elif entity_type in ["CREDIT_CARD", "ISRAELI_ID_NUMBER", "ID"]:
            return "<מזהה_>"
        elif entity_type in ["EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "URL"] and has_no_whitespace(text):
            return "<קשר_>"
        elif entity_type in ["DATE"]:
            return "<תאריך_>"
        return text


    def validate(self, params: Dict = None) -> None:
        """Validate the new value is string."""
        pass

    def operator_name(self) -> str:
        """Return operator name."""
        return "replace_in_hebrew"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
