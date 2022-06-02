import json
from medspacy.section_detection import SectionRule

    # https://github.com/medspacy/medspacy/blob/master/notebooks/11-QuickUMLS_Extraction.ipynb
    # https://github.com/medspacy/medspacy/blob/master/notebooks/section_detection/3-Subsections.ipynb
section_rules = [
    SectionRule(category="visit_information", 
                literal="presented",
                pattern = [{"IS_SENT_START": True}, {"LOWER" : {"REGEX": ".*"}}, {"LOWER" : {"REGEX": "presented"}}]),
    SectionRule(category="history_of_presenting_illness", literal="History of Presenting Illness"),
    SectionRule(category="history_of_presenting_illness", literal="HPI"),
    SectionRule(category = "past_medical_history", literal = "Past Medical History") ,
    # seems to work better with these sections
    SectionRule(category="patient_history", literal="Patient History"),
    # SectionRule(category="social_history", literal="Social History"),
    # SectionRule(category="family_history", literal="Family History"),
    # SectionRule(category="surgical_history", literal="Surgical History"),
    SectionRule(category="medication", literal="Current Outpatient Medications"),
        SectionRule(category="medication", literal="Home Medications"),
    SectionRule(category="review_of_systems", literal="Review of Systems"),
    # sometimes found not in a word boundary eg. Physical ExamConstitutional - need to sanity check this
    SectionRule(category="physical_exam", literal="Physical",
                pattern = [{"TEXT" : {"REGEX": "Physical Exam*"}}]),
    SectionRule(category="physical_exam", literal="Physical Exam"),

    SectionRule(category = "observation_and_plan",
                literal = "Plan", 
                pattern = [{"LOWER" : {"REGEX": "impression|assessment"}},
                           {"LOWER" : {"REGEX": "and|&"}},
                            {"LOWER": {"REGEX": "plan"}} ]), 
]

