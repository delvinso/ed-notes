from medspacy.postprocess import PostprocessingRule, PostprocessingPattern
from medspacy.postprocess import postprocessing_functions

postprocess_rules = [
    PostprocessingRule(
        patterns=[
            PostprocessingPattern(
                condition=lambda ent: ent.label_ not in ["DISEASE", "PROBLEM"]
            ),
        ],
        action=postprocessing_functions.remove_ent,
        description="Remove entities that are neither a disease or problem (these are symptoms/conditions).",
    ),
    PostprocessingRule(
        patterns=[
            PostprocessingPattern(
                condition=lambda ent: ent.text == "presenting illness"
            ),
        ],
        action=postprocessing_functions.remove_ent,
        description="Remove bloat 'presenting illness' entities from NER model.",
    ),
    PostprocessingRule(
        patterns=[
            PostprocessingPattern(
                lambda ent: ent._.window(1, left=True, right=True)._.contains(
                    "?", regex=False
                )
            ),
        ],
        action=postprocessing_functions.set_uncertain,
        action_args=(True,),
        description="If an entity has a question mark directly before or after it, set to uncertain.",
    ),
]
