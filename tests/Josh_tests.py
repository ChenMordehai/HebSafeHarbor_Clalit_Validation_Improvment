import spacy
from hebsafeharbor import HebSafeHarbor
from lingua import Language, LanguageDetectorBuilder


languages = [Language.ENGLISH, Language.HEBREW]
detector = LanguageDetectorBuilder.from_languages(*languages).build()
text = """
"""
doc = {'HEBREW': '', 'ENGLISH': ''}
index = 0
for result in detector.detect_multiple_languages_of(text):
    if index != result.start_index:
        doc['HEBREW'] += text[index:result.start_index]
    doc[result.language.name] += text[result.start_index:result.end_index]
    index = result.end_index
if index != len(text):
    doc['HEBREW'] += text[index:]
nlp = spacy.load("en_core_web_sm")
doc1 = nlp(doc['ENGLISH'])
print('english ents:')
for ent in doc1.ents:
    print(f"{ent.text} - type: {ent.label_}, start: {ent.start_char}, end: {ent.end_char}")

hsh = HebSafeHarbor()

doc2 = {"text": doc['HEBREW']}

output = hsh([doc2])
print('hebrew ents:')
print(output[0].analyzer_results)
