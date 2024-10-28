from typing import Dict, List, Callable, Optional
import spacy
from lingua import Language, LanguageDetectorBuilder
from hebsafeharbor import Doc
from hebsafeharbor.anonymizer.phi_anonymizer import PhiAnonymizer
from hebsafeharbor.identifier.phi_identifier import PhiIdentifier
from global_variables.global_variables import VARIABLES

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class HebSafeHarbor:
    """
    The manager of the application. When it called, given a Hebrew text, it executes the identification and
    anonymization process and return an anonymized text.
    """

    def __init__(self, context: str = 'general', shift_date_function: Optional[tuple] = None):
        """
        Initializes HebSafeHarbor

        :param context: optional - the medical context. supported contexts: ['imaging', 'general', 'pathology']
        :param shift_date_function: optional - tuple in the form (callable, params). where callable is the shifting
                                    function and params are additional parameters to that function(besides the date).
                                    callable signature: def f(params:any, date_string: string)--> day:string, month:string, year:string
        """

        if context in VARIABLES['supported_contexts']:
            VARIABLES['context'] = context
        else:
            raise AttributeError(f"no context named {context}")
        if shift_date_function is not None:
            shift_function, shift_params = shift_date_function
            if not callable(shift_function):
                raise TypeError("shift_date_function[0] must be callable (a function)")
        VARIABLES['shift_date_function'] = shift_date_function
        self.identifier = PhiIdentifier()
        self.anonymizer = PhiAnonymizer()

    def __call__(self, doc_list: List[Dict[str, str]]) -> List[Doc]:
        """
        The main method, executes the PHI reduction process on the given text
        :param doc_list: List of dictionary where each dict represents a document.
                        Each dictionary should consist of "id" and "text" columns
        :return: anonymized text
        """

        if VARIABLES['context'] == 'pathology':
            # create array of sub parts, based on text's language
            languages = [Language.ENGLISH, Language.HEBREW]
            detector = LanguageDetectorBuilder.from_languages(*languages).build()
            for dict_ in doc_list:
                txt = dict_.get('text', "")
                languages_in_text = detector.detect_multiple_languages_of(txt)
                txt_parts_order = {}
                for lang_part_index in range(len(languages_in_text)):
                    lang_part = languages_in_text[lang_part_index]
                    if lang_part.language.name == 'HEBREW':
                        if lang_part_index == len(languages_in_text)-1:
                            docs = [Doc({"text": txt[lang_part.start_index:]})]  # hebrew part
                        else:
                            docs = [Doc({"text": txt[lang_part.start_index:lang_part.end_index]})]
                        docs = self.identify(docs)
                        docs = self.anonymize(docs)
                        txt_parts_order[lang_part_index] = docs[0].anonymized_text.text
                    else:  # english
                        en_nlp = spacy.load('en_core_web_sm')
                        if lang_part_index == len(languages_in_text)-1:
                            en_txt = txt[lang_part.start_index:]
                        else:
                            en_txt = txt[lang_part.start_index:lang_part.end_index]
                        en_doc = en_nlp(en_txt)  # english part
                        for ent in en_doc.ents:  # mask names in english
                            if ent.label_ == 'PERSON':
                                en_txt = en_txt.replace(ent.text, "<שם_>")
                        docs = [Doc({"text": en_txt})]
                        docs = self.identify(docs)
                        docs = self.anonymize(docs, lang='en')
                        txt_parts_order[lang_part_index] = docs[0].anonymized_text.text
                all_text_parts = txt_parts_order.values()
                full_anonymized_text = " ".join(all_text_parts)
                out = AttrDict({"text": txt, "anonymized_text": AttrDict({'text': full_anonymized_text})})
                return [out]  # TODO: change structure?
        else:
            docs = [Doc(doc_dict) for doc_dict in doc_list]
            docs = self.identify(docs)
            docs = self.anonymize(docs)
            return docs

    def identify(self, docs: List[Doc]) -> List[Doc]:
        """
        This method identifies the PHI entities in the input text
        :param docs: a list of Doc objects which contains the input text for anonymization
        :return: a list of the updated Doc objects that contains the recognized PHI entities
        """
        return [self.identifier(doc) for doc in docs]

    def anonymize(self, docs: List[Doc], lang: str = 'he') -> List[Doc]:
        """
        This method anonymizes the recognized PHI entities using different techniques
        :param doc: a list of Doc objects which contains the consolidated recognized PHI entities
        lang: optional - string of language of text
        :return: a list of the updated Doc objects that contains the anonymized text
        """
        return [self.anonymizer(doc, lang) for doc in docs]

    @staticmethod
    def create_result(doc: Doc) -> Dict[str, str]:
        """
        this function will get a document and create a result map.
        """

        items = []
        for item in doc.anonymized_text.items:
            item_result = {
                "startPosition": item.start,
                "endPosition": item.end,
                "entityType": item.entity_type,
                "text": doc.text[item.start:item.end],
                "mask": item.text,
                "operator": item.operator
            }
            items.append(item_result)

        result: Dict = {
            "id": doc.id,
            "text": doc.anonymized_text.text,
            "items": items
        }
        return result

    def rec_special_names(self, docs):
        nlp_names = spacy.load(r"C:\Users\chenmor1\PycharmProjects\HebSafeHarbor_IIA\ner_rec_names")
        disabled_pipes = []
        for pipe_name in nlp_names.pipe_names:
            if pipe_name != 'ner':
                nlp_names.disable_pipes(pipe_name)
                disabled_pipes.append(pipe_name)
        new_docs = []
        for d in docs:
            temp_doc = nlp_names(d.text)
            temp_txt = temp_doc.text
            for e in temp_doc.ents:
                if len(e.text) > 3:
                    temp_txt = temp_txt.replace(e.text, "<שם_>")
            new_doc = {"text": temp_txt}
            new_docs.append(new_doc)
        for pipe_name in disabled_pipes:
            nlp_names.enable_pipe(pipe_name)
        return [Doc(doc_dict) for doc_dict in new_docs]
