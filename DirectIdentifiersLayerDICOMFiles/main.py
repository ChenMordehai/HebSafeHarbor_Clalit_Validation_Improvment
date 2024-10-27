# coding: utf8

import sys

from os import path

from datetime import datetime

from multiprocessing import Pool

import pandas as pd

import pydicom

from bs4 import BeautifulSoup

from pydicom.tag import Tag

from itertools import permutations

from relevant_tests_paths_with_text import relevant_tests_full_dcm_paths

from colors import bcolors

EXCEL_SHEET_PATH = "text_from_dicom.xlsx"

HebSafeHarborLocalPath = r"..\HebSafeHarborAdjust"

PRIVATE_INFO_DICT = {}

sys.path.append(path.abspath(HebSafeHarborLocalPath))

from hebsafeharbor import HebSafeHarbor


def extract_private_info_to_dict(ds, elem, f_path):
    """

    Extracts names, dates and IDs from Dicom tags into private dictionary.

    :param ds: Dicom file

    :param elem: Dicom tag

    :param f_path: Dicom file path (string)

    :return:

    """

    elem_value = str(elem.value)

    # All tags with name property

    if elem.VR == "PN":

        temp_str = elem_value.replace('^', ' ')

        names_arr = temp_str.split('=')

        for n in names_arr:

            if n != 'NA' and len(n) > 1:
                PRIVATE_INFO_DICT[f_path]['names'].add(n)

    # Specific tag for executing doctor name

    elif elem.tag == Tag(0x07a31023):

        if len(elem_value) > 1 and elem_value != 'NA':
            PRIVATE_INFO_DICT[f_path]['names'].add(elem_value)

    # All tags with date property

    elif elem.VR == 'DA' and elem_value != 'NA':

        if len(elem_value) > 2:
            temp_str = datetime.strptime(elem_value, '%Y%m%d').strftime('%d/%m/%Y')

            PRIVATE_INFO_DICT[f_path]['dates'].add(temp_str)

    # All tags with ID property

    elif elem.VR == 'SH' and elem_value != 'NA':

        if all(s.isdigit() for s in elem_value) and len(elem_value) > 2:
            PRIVATE_INFO_DICT[f_path]['ids'].add(elem_value)

    elif elem.VR == 'LO':

        if all(s.isdigit() for s in elem_value) and len(elem_value) > 2:
            PRIVATE_INFO_DICT[f_path]['ids'].add(elem_value)


def extract_span_values_from_html(data_element):
    """

    Extract text from HTML.

    :param data_element: pydicom data_element where data_element.VR == "UT"

    :return: array of strings

    """

    raw_data = data_element.value

    chunk_size = 1024

    data_generator = (raw_data[i:i + chunk_size] for i in range(0, len(raw_data), chunk_size))

    html_data = ""

    for chunk in data_generator:
        html_data += chunk

    html_parser = BeautifulSoup(html_data, "html.parser")

    span_values = [span.text.replace('\xa0', '') for span in html_parser.find_all("span")]

    span_values = [s for s in span_values if s.strip()]

    return span_values


def GetText(data_element):
    """

    :param data_element: pydicom data_element where data_element.VR == "UT"

    :return: free text in data_element.value (string)

    """

    if data_element.VR == "UT":
        txt = '  '.join(extract_span_values_from_html(data_element))

        return txt


def GetEncryptedText(original_text):
    """

    calls HebSafeHarbor and encrypts given text

    :param original_text: text to encrypt (string)

    :return: encrypted text (string)

    """

    if original_text:
        hsh = HebSafeHarbor(context='imaging')

        doc = {"text": original_text}

        output = hsh([doc])

        return f"'\u202B'{output[0].anonymized_text.text}'\u202C'"


def get_total_enc(text):
    """

    :param text: encrypted text (string)

    :return: number of encrypted terms in text (int)

    """

    count = 0

    stack = []

    if text is None:
        return count

    for char in text:

        if char == '<':

            stack.append(char)

        elif char == '>':

            if stack:
                stack.pop()

                count += 1

    return count


def get_accuracy_results(original_txt, enc_txt, private_dict_):
    """

    :param original_txt: text before encryption (string)

    :param enc_txt: encrypted text (string)

    :param private_dict_: dictionary of private terms (dict)

    :return: number of private terms in original text (int),

    number of encrypted private terms (int), number of false negatives (int),

    number of unique false negatives (int), set of all private terms (set)

    """

    total_private_terms = 0

    total_private_terms_enc = 0

    total_private_terms_fn = 0

    fn_terms = []

    if enc_txt is not None:

        masks = {'names': "<שם_>", 'ids': "<מזהה_>", 'dates': "<תאריך_>"}

        private_dict_private_info = {k: v for k, v in private_dict_.items() if k in masks.keys()}

        for k, v in private_dict_private_info.items():

            for term in v:

                total_private_terms += original_txt.count(term)

                if enc_txt.__contains__(term):

                    total_private_terms_fn += enc_txt.count(term)

                    fn_terms.append(term)

                elif original_txt.__contains__(term):

                    total_private_terms_enc += original_txt.count(term)

    total_unique_fn = len(set(fn_terms))

    return total_private_terms, total_private_terms_enc, total_private_terms_fn, total_unique_fn, set(fn_terms)


def check_private_info_after_enc(_txt, path):
    """

    Replace private terms with name or ID mask.

    :param _txt: text before encryption (string)

    :param path: Dicom file path (string)

    :return: True, masked text (string)

    """

    if _txt is None:
        return True, ""

    enc_text_qa = _txt

    masks = {'names': "<שם_>", 'ids': "<מזהה_>"}

    private_dict_ = PRIVATE_INFO_DICT[path]

    private_dict_ = {k: v for k, v in private_dict_.items() if k in masks.keys()}

    for key, val in private_dict_.items():

        for term in val:

            if enc_text_qa.__contains__(term):
                enc_text_qa = enc_text_qa.replace(term, masks[key])

    return True, enc_text_qa


def CallEncryption(data_element, path):
    """

    encrypts given data_element.value and saves it in a txt file

    :param data_element:

    :return:

    """

    original_txt = GetText(data_element)

    enc_txt = GetEncryptedText(original_txt)

    private_dict_ = PRIVATE_INFO_DICT[path]

    # get total anonymized data

    total_enc_in_text = get_total_enc(enc_txt)

    total_private_terms_in_txt, total_tp_in_text, total_fn_in_text, total_unique_fn_in_text, fn_terms_in_txt = get_accuracy_results(

        original_txt, enc_txt, private_dict_)

    fn_after_qa = total_unique_fn_in_text

    # qa encryption by private_info

    stat, new_org = check_private_info_after_enc(original_txt, path)

    enc_new_org = GetEncryptedText(new_org)

    qa_status, enc_txt_qa = check_private_info_after_enc(enc_new_org, path)

    if qa_status:
        total_private_terms_in_txt_after_qa, total_tp_in_text_after_qa, total_fn_in_text_after_qa, fn_after_qa, fn_terms_in_txt_after_qa = get_accuracy_results(

            original_txt, enc_txt_qa, private_dict_)

    # append to dict

    private_dict_["Total Anonymized"] = total_enc_in_text

    private_dict_["Total True Positive"] = total_tp_in_text

    private_dict_["Total False Negative Cases"] = total_fn_in_text

    private_dict_["Total False Negative Unique Cases"] = total_unique_fn_in_text

    private_dict_["Total False Negative Unique Identifiers Cases after QA"] = fn_after_qa

    private_dict_["Total Private Terms"] = total_private_terms_in_txt

    private_dict_["False Negative Terms"] = fn_terms_in_txt

    private_dict_["Original Text"] = original_txt

    private_dict_["Anonymized Text(SH)"] = enc_txt

    private_dict_["Anonymized Text(QA)"] = enc_txt_qa


def process_text(ds, elem, f_path):
    """

    Call text encryption from file path and tag of full Dicom text

    :param ds: Dicom file

    :param elem: Dicom tag

    :param f_path: Dicom file path (string)

    :return:

    """

    if elem.VR == "UT":
        CallEncryption(elem, f_path)


def process_file(file_path):
    """

    Process file from file path, through all functions to get final table results

    :param file_path: Dicom file path (string)

    :return: patient ID (string), Dicom file path (string), Dicom type (string),

    number of encrypted terms in text (int), number of true positives (int),

    number of false negatives (int), number of unique false negatives (int),

    number of false negatives after QA (int), number of private terms in text (int),

    original text (string), encrypted text (string), encrypted text after QA (string),

    set of all flase negative terms (set), dictionary of all private terms (dict)

    """

    private_info = {'names': set(), 'ids': set(), 'dates': set(), "Total False Negative Cases": 0,

                    "Total False Negative Unique Cases": 0, "Total False Negative Unique Identifiers Cases after QA": 0,

                    "Total Anonymized": 0, "Total True Positive": 0, "False Negative Terms": set(),

                    "Total Private Terms": 0, "Original Text": "", "Anonymized Text(SH)": "", "Anonymized Text(QA)": "",

                    "Private Info Dict": {}}

    PRIVATE_INFO_DICT[file_path] = private_info

    dcm = pydicom.dcmread(file_path, stop_before_pixels=True)

    pName = str(dcm.PatientName)

    pID = str(dcm.PatientID)

    if pName != 'NA' and pName != '':
        PRIVATE_INFO_DICT[file_path]['names'].add(str(dcm.PatientName))

    if pID != 'NA' and pID != '':
        PRIVATE_INFO_DICT[file_path]['ids'].add(str(dcm.PatientID))

    # extract private info to private_info dict

    dcm.walk(lambda de, el: extract_private_info_to_dict(de, el, file_path))

    # add name permutations to private_info dict

    new_names = set()

    for n in PRIVATE_INFO_DICT[file_path]['names']:
        new_name = set([" ".join(p) for p in permutations(n.split())])

        new_names = new_names.union(new_name)

    for n in new_names:
        PRIVATE_INFO_DICT[file_path]['names'].add(n)

    # encrypt free text

    dcm.walk(lambda de, el: process_text(de, el, file_path))

    total_tp = PRIVATE_INFO_DICT[file_path].get('Total True Positive', 0)

    total_fn = PRIVATE_INFO_DICT[file_path].get('Total False Negative Cases', 0)

    total_unique_fn = PRIVATE_INFO_DICT[file_path].get('Total False Negative Unique Cases', 0)

    total_anonymized = PRIVATE_INFO_DICT[file_path].get('Total Anonymized', 0)

    total_fn_qa = PRIVATE_INFO_DICT[file_path].get('Total False Negative Unique Identifiers Cases after QA', 0)

    total_private_t = PRIVATE_INFO_DICT[file_path].get("Total Private Terms", 0)

    org_txt = PRIVATE_INFO_DICT[file_path].get("Original Text", "")

    encr_txt = PRIVATE_INFO_DICT[file_path].get("Anonymized Text(SH)", "")

    qa_txt = PRIVATE_INFO_DICT[file_path].get("Anonymized Text(QA)", "")

    fn_terms_set = PRIVATE_INFO_DICT[file_path].get("False Negative Terms", set())

    try:

        dcm_type = dcm.get((0x07a1, 0x1070), "no_test_type")

    except:

        dcm_type = "no_test_type"

    return pID, file_path, dcm_type, total_anonymized, total_tp, total_fn, total_unique_fn, total_fn_qa, \
 \
        total_private_t, org_txt, encr_txt, qa_txt, fn_terms_set, PRIVATE_INFO_DICT[file_path]


def process_wrapper(file_path):
    try:

        res = process_file(file_path)

        return res

    except Exception as e:

        print(e)

        return "ERROR", file_path, str(e), None


if __name__ == '__main__':

    print(bcolors.HEADER + "--- start time:" + str(datetime.now()) + " ---" + bcolors.ENDC)

    print(bcolors.HEADER + "--- finished collecting all necessary .dcm files at:" + str(

        datetime.now()) + "| total files: " + str(len(relevant_tests_full_dcm_paths)) + " ---" + bcolors.ENDC)

    # Pool for multi-threaded code

    with Pool(1) as pool:

        results = pool.map(process_wrapper, relevant_tests_full_dcm_paths)

    # write results to excel

    df = pd.DataFrame(results, columns=["patient_original_id", "original_file_path",

                                        "test_type", "Total Anonymized", "Total True Positive",

                                        "Total False Negative Cases", "Total False Negative Unique Cases",

                                        "Total False Negative Unique Identifiers Cases after QA",

                                        "Total Private Terms", "Original Text", "Anonymized Text(SH)",

                                        "Anonymized Text(QA)", "False Negative Terms", "Private Info Dict"

                                        ])

    try:

        df.to_excel(EXCEL_SHEET_PATH, index=False)

    except:

        json_result_path = EXCEL_SHEET_PATH.replace('.xlsx', '.json')

        df.to_json(json_result_path, orient='records')

    print(bcolors.HEADER + "--- end time:" + str(datetime.now()) + " ---" + bcolors.ENDC)
