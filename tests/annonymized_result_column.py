# coding: utf8
import pandas as pd
from hebsafeharbor import HebSafeHarbor
from tqdm import tqdm

tqdm.pandas()

hsh = HebSafeHarbor()

df = pd.read_excel(
    r"\\sofiler2\home$\Clinical Research Center\CRC\DataExtracts\משימות_דחופות\חן מרדכי\NLP_IHO\soroka_data\original_records_camilion_oncology.xlsx")


def get_anonymized_text(row_text):
    doc = {"text": row_text}
    output = hsh([doc])
    return output[0].anonymized_text.text


df["anonymized_text"] = df["Text"].progress_apply(get_anonymized_text)
df['row_index'] = df.index
df.to_excel(r"\\sofiler2\home$\Clinical Research Center\CRC\DataExtracts\משימות_דחופות\חן מרדכי\NLP_IHO\soroka_data\annonymized_text_general_context_fuzzy.xlsx", index=False)
df.to_json(r"\\sofiler2\home$\Clinical Research Center\CRC\DataExtracts\משימות_דחופות\חן מרדכי\NLP_IHO\soroka_data\annonymized_text_general_context_fuzzy.jsonl", orient="records", lines=True)
