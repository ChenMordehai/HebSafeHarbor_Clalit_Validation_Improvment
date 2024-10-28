import copy

from hebsafeharbor import Doc
from hebsafeharbor.lexicons.healthcare_professional_staff import HEALTHCARE_PROFESSIONAL_STAFF


def fix_scores(doc: Doc) -> Doc:
    entities = doc.granular_analyzer_results
    WINDOW_BEFORE = 8
    WINDOW_AFTER = 1
    MIN_FIXED_SCORE = 0.9987654321
    for i,ent in enumerate(entities):
        if ent.entity_type in ['PERS', 'PER']:
            if any(' '+name+' ' in doc.text[max(0,ent.start - WINDOW_BEFORE):min(ent.end + WINDOW_AFTER,len(doc.text))] for name in
                   HEALTHCARE_PROFESSIONAL_STAFF):
                if ent.score < MIN_FIXED_SCORE:
                    doc.granular_analyzer_results[i].entity_type = ent.entity_type + '_fixed'
                    doc.granular_analyzer_results[i].score = MIN_FIXED_SCORE
    return doc

class EntityScoreFixerRuleExecutor:
    """
    Triggers the different entity score fixer over the consolidated recognized entities after data splitter (exist in the input Doc object).
    Note that after calling the executor the entities can possibly changed
    """

    def __init__(self):
        """
        Initializing the EntityScoreFixerRuleExecutor
        """

    def __call__(self, doc: Doc) -> Doc:
        """
        Execute the different entity score fixing rules according to diffrent entity types.

        :param doc: document object
        :return an updated document after triggering the entity score fixer
        """
        
        doc = fix_scores(doc)

        return doc



