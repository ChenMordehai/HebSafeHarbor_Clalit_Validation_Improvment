# coding: utf8
from hebsafeharbor import HebSafeHarbor

hsh = HebSafeHarbor()

text = '''
 10.05.2022 יום טוב
'''

doc = {"text": text}

output = hsh([doc])

print(f"'\u202B'{output[0].anonymized_text.text}'\u202C'")
print(output[0].analyzer_results)

