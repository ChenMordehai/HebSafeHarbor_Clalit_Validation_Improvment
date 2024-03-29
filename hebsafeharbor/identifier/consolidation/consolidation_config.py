from enum import Enum

ENTITY_TYPES_TO_IGNORE = {"MONEY", "PERCENT", "MISC__ENT", "MISC_EVENT", "WOA", "EVE", "DUC", "ANG", "MISC__AFF"}

ENTITY_TYPES_TO_POSTPROCESS = {"COUNTRY", "CITY", "DISEASE", "MEDICATION", "MEDICAL_TEST", "BODY_PARTS", "LAB_TESTS",
                               "HOSPITALS", "RCOG_MED_TERMS", "CAMONI_MED_TERMS", "GENS"}

ENTITY_TYPE_TO_CATEGORY = {
    "PERS": "NAME",
    "LOC": "LOCATION",
    "ORG": "ORG",
    "TIME": "TIME",
    "DATE": "DATE",
    "PREPOSITION_DATE": "DATE",
    "HEBREW_DATE": "DATE",
    "LATIN_DATE": "DATE",
    "NOISY_DATE": "DATE",
    "MISC__AFF": "MISC__AFF",
    "PER": "NAME",
    "GPE": "LOCATION",
    "FAC": "ORG",
    "CREDIT_CARD": "ID",
    "DATE_TIME": "DATE",
    "EMAIL_ADDRESS": "CONTACT",
    "IP_ADDRESS": "CONTACT",
    "URL": "CONTACT",
    "PHONE_NUMBER": "CONTACT",
    "ISRAELI_ID_NUMBER": "ID",
    "ID": "ID",
    "COUNTRY": "LOCATION",
    "CITY": "LOCATION",
    "DISEASE": "MEDICAL",
    "MEDICATION": "MEDICAL",
    "MEDICAL_TEST": "MEDICAL",
    "BODY_PARTS": "BODY_PARTS",
    "LAB_TESTS": "LAB_TESTS",
    "CAMONI_MED_TERMS": "MEDICAL",
    "RCOG_MED_TERMS": "MEDICAL",
    "GENS": "MEDICAL"

}

CATEGORY_TO_CONTEXT_PHRASES = {
    "ID": ["תעודה", "זהות", "מזהה", "רישיון", "מ.ר", "מ.ז", "ת.ז", "מספר אישי", "רשיון", "מנוי", "עובד", "רכב", "בנק",
           "אשראי"],
    "CONTACT": ["מיקוד", "בטלפון", "טלפון", "טלפון נייח", "טלפון נייד", "פלאפון", "פקס", "טלפון בבית", "טלפון בעבודה",
                "אימייל", "דואר אלקטרוני", "URL", "IP", "מייל"],
    "MEDICAL": ["שילוב", "לשלב", "נשלב", "אבחנת עבודה", "שדרוג", "לשדרג", "שודרג", "הוספה", "נוסיף", "להוסיף", "נוסף",
                "הוספנו", "שינוי", "לשנות", "שונה", "שינינו", "מטופל", "מטופלת", "טופל", "טופלה", "טופל בחדר אחיות",
                "טופלה בחדר אחיות", "להתחיל", "יתחיל", "תתחיל", "נשלח", "נישלח", "יישלח", "גרורות", "סיכום", "החלפה",
                "להחליף", "הוחלף", "נחליף", "נוסה", "ניסינו", "ניסיון", "מניעה", "בדיקה", "הכנסה", "הוצאה",
                "הכנסת", "הוצאת", "בשל", "בגלל", "חיסון"],
    "NAME": ["""פוענח ע"י""", "רופא מפנה", "מבצע", "נבדק"]
}


class ConflictCase(Enum):
    EXACT_MATCH = "EXACT_MATCH"
    SAME_CATEGORY = "SAME_CATEGORY"
    SAME_BOUNDARIES = "SAME_BOUNDARIES"
    MIXED = "MIXED"
