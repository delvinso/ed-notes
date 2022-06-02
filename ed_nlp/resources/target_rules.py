from medspacy.ner import TargetRule


target_rules = [
    TargetRule(literal="vomit", 
        category="PROBLEM",
        pattern = [{"TEXT": {"REGEX": "vomit"}}]),

    TargetRule(literal="headache", 
        category="PROBLEM",
         pattern = [{"TEXT": {"REGEX": "headache|migraine"}}]),
]