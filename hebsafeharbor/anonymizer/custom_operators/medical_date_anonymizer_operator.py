from typing import Dict
from datetime import datetime, timedelta
from presidio_anonymizer.operators import OperatorType, Operator
from global_variables.global_variables import VARIABLES
from hebsafeharbor.anonymizer.setting import DAY_MASK
from hebsafeharbor.common.date_utils import extract_date_components, find_pattern
from hebsafeharbor.common.date_regex import TIME_REGEX
from dateutil import parser

# def shift_day(date_):
#     # day = int(day_str)
#     # shifted_day = day - VARIABLES['days_to_shift']
#     # if shifted_day <= 0:
#     #     shifted_day += 31
#     # return str(shifted_day).zfill(2)
#     day_str = date_.day.text
#     month_str = date_.month.text
#     year_str = date_.year.text
#     current_date = datetime.strptime(f"{year_str}-{month_str}-{day_str}", "%Y-%m-%d")
#     shift_days = VARIABLES['days_to_shift']
#     new_date = current_date + timedelta(days=shift_days)
#     date_.day.text = new_date.strftime("%d")
#     date_.month.text = new_date.strftime("%m")
#     date_.year.text = new_date.strftime("%Y")
#     return date_.day.text, date_.month.text, date_.year.text


class MedicalDateAnonymizerOperator(Operator):
    """
    An instance of the DateAnonymizerOperator which extends the Operator abstract class (@Presidio). For each recognized
    entity of type MEDICAL_DATE, this custom operator anonymizes the only the day.
    """

    def operate(self, text: str, params: Dict = None) -> str:
        """
        This method applies the anonymization on the given recognized entity text
        if shift_date_function is given when HebSafeHarbor is initialized, then anonymization process will use
        shift_date_function[0] function with shift_date_function[1] params on the recognized date

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
                return updated_time_str
            return text

        if date_container.day and date_container.day.text:
            if VARIABLES['shift_date_function'] is not None:
                shift_function, params = VARIABLES['shift_date_function']
                try:
                    # shift days
                    date_container.day.text, date_container.month.text, date_container.year.text = shift_function(params, date_container.text)
                except:
                    raise ValueError(f"shift_function {shift_function} does not support the output format.")
            else:
                # mask
                date_container.day.text = DAY_MASK
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
