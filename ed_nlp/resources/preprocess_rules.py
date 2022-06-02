
from medspacy.preprocess import PreprocessingRule
import re
        
preprocess_rules = [
    
        lambda x: x.lower(),

        PreprocessingRule(
            re.compile("^[a-z](.*?)presented"), repl="[Patient Name] presented",  desc="Replace patient name, age, gender"
        ),
        PreprocessingRule(
            re.compile(r'hpi.*hpi'), repl="history of presenting illness:", desc="replace hpi"
        ),
        PreprocessingRule(
            re.compile(r'\bhpi\b'), repl="history of presenting illness:", desc="replace hpi"
        ),
        PreprocessingRule(
            re.compile(r'review of systems\b'), repl="review of systems:", desc="replace review of systems"
        ),
        # PreprocessingRule(
        #     re.compile(r'         '), repl="\n", desc="replace review of systems"
        # ),

        # headers are delimited by ~9 spaces, whereas line breaks seem to be translated to 2 or more spaces (depending on the header level?)
        # this re-creates the line breaks prior to EPIC processing
        PreprocessingRule(
            re.compile(r"\s{2,}"), repl="\n", desc="replace 2 or more spaces with a new line as these are line breaks."
        ),

    ]