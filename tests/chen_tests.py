# coding: utf8
import importlib
from hebsafeharbor import HebSafeHarbor
from global_variables.global_variables import VARIABLES
from lingua import Language, LanguageDetectorBuilder

# import_string = f"hebsafeharbor.lexicons.{VARIABLES['context']}.healthcare_professional"
# m_path, att_name = import_string.rsplit('.', 1)
#
# my_m = importlib.import_module(m_path)
# m_list = getattr(my_m, att_name)
#
# print(m_list.HEALTHCARE_PROFESSIONAL)


def shift_day(params,date_):
    # day = int(day_str)
    # shifted_day = day - VARIABLES['days_to_shift']
    # if shifted_day <= 0:
    #     shifted_day += 31
    # return str(shifted_day).zfill(2)
    return "01", "01", "2000"


hsh = HebSafeHarbor(context='pathology') #context='pathology'

text = """
"""
#
doc = {"text": text}

output = hsh([doc])
# print(output[0])

# print(f"'\u202B'{output[0]['anonymized_text']['text']}'\u202C'")
print(f"'\u202B'{output[0].anonymized_text.text}'\u202C'")
# print(output[0].analyzer_results)


# languages = [Language.ENGLISH, Language.HEBREW]
# detector = LanguageDetectorBuilder.from_languages(*languages).build()
# languages_txt = detector.detect_multiple_languages_of(text)
# print(type(languages_txt))
# print(languages_txt)
# for result in detector.detect_multiple_languages_of(text):
#     print(f"{result.language.name}: '{text[result.start_index:result.end_index]}'")