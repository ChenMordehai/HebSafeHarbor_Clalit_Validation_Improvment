from typing import Dict
from datetime import datetime, timedelta
from presidio_anonymizer.operators import OperatorType, Operator

from hebsafeharbor.anonymizer.setting import DAY_MASK
from hebsafeharbor.common.date_utils import extract_date_components, find_pattern
from hebsafeharbor.common.date_regex import TIME_REGEX

DAYS_TO_SHIFT = 13
def shift_day(day_str):
    day = int(day_str)
    shifted_day = day - DAYS_TO_SHIFT
    if shifted_day <= 0:
        shifted_day += 31
    return str(shifted_day).zfill(2)

class MedicalDateAnonymizerOperator(Operator):
    """
    An instance of the DateAnonymizerOperator which extends the Operator abstract class (@Presidio). For each recognized
    entity of type MEDICAL_DATE, this custom operator anonymizes the only the day.
    """

    def operate(self, text: str, params: Dict = None) -> str:
        """
        This method applies the anonymization policy of the BirthDateAnonymizerOperator on the given recognized entity text

        :param text: recognized entity text for anonymization
        :param params: optional parameters
        :return: the anonymized text of the entity
        """
        
        date_container = extract_date_components(text)
        # in case that the components extraction failed, all values will be none - returning the original text
        if date_container.day is None and date_container.month is None and date_container.year is None:
            time_pattern = find_pattern(text, [TIME_REGEX])
            if time_pattern:
                original_hours, original_minutes, original_seconds = map(int, time_pattern.group().split(':'))
                time_duration = timedelta(hours=3, minutes=32, seconds=41)
                updated_time = datetime(1, 1, 1, original_hours, original_minutes, original_seconds) + time_duration
                updated_time_str = updated_time.strftime("%H:%M:%S")
                return  updated_time_str
            return text

        # masking
        if date_container.day and date_container.day.text:
            # date_container.day.text = DAY_MASK
            date_container.day.text = shift_day(date_container.day.text) # TODO: check if 10 days is ok
        return date_container.reconstruct_date_string()

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

        return "replace_only_day"

    def operator_type(self) -> OperatorType:
        """
        Returns the operator type

        :return: the operator type
        """

        return OperatorType.Anonymize
