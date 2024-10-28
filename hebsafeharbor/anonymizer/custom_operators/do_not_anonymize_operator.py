from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType


class DoNotAnonymize(Operator):
    """
    An instance of the Operator abstract class (@Presidio). For each recognized entity ,this custom
    returns back entity to override default operator and not anonymize the entity.
    """

    def operate(self, text: str = None, params: Dict = None) -> str:
        """:return: text."""
        return text

    def validate(self, params: Dict = None) -> None:
        """Validate the new value is string."""
        pass

    def operator_name(self) -> str:
        """Return operator name."""
        return "do_not_anonymize"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
