import spacy
from spacy.tokens import Span
from spacy.tokens import Doc

import medspacy
from medspacy.preprocess import Preprocessor
from medspacy.section_detection import Sectionizer

from .resources import preprocess_rules
from .resources import target_rules
from .resources import section_rules
from .resources import context_rules
from .resources import postprocess_rules

from typing import List, Dict, Iterator
import pandas as pd
from medspacy.io import DocConsumer


def _set_attributes():
    """
    sets custom attributes for Spans and Docs, required for pipeline.
    """
    Span.set_extension("next_sentence", getter = get_next_sentence, force = True)
    Span.set_extension("previous_sentence", getter = get_previous_sentence, force = True)
    Doc.set_extension("internal_id", default=None, force = True)
    Doc.set_extension("date", default=None, force = True)
    Doc.set_extension("csn", default=None, force = True)

def get_next_sentence(ent) -> str:
    """
    using the current token's end of sentence, get next token's sentence 
    """
    sent = ent.sent
    try:
        return str(ent.doc[sent.end + 1].sent)
    except IndexError:
        return None

def get_previous_sentence(ent) -> str:
    """
    using the current token's beginning of sentence, get previous token's sentence 
    """
    sent = ent.sent
    try:
        return str(ent.doc[sent.start - 1].sent)
    except IndexError:
        return None
    

def create_doc_consumer():
    """
    UNUSED.
    Creates a DocConsumer with custom dtypes.
    """
    nlp = medspacy.load()
    doc_cons_attrs = DocConsumer.get_default_attrs()
    ent_attrs = doc_cons_attrs['ent']
    ent_attrs.append('sent')
    ent_attrs.append('next_sentence')
    ent_attrs.append('previous_sentence')
    doc_cons_attrs['ent'] = ent_attrs

    doc_attrs = doc_cons_attrs['doc']
    doc_attrs.append('csn')
    doc_cons_attrs['doc'] = doc_attrs

    custom_doc_consumer = DocConsumer(nlp, dtypes=("ent", "context", "section", "doc"), 
                                dtype_attrs=doc_cons_attrs
    )
    return custom_doc_consumer


def query_results(
    query: str, entity_results: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    USED IN STREAMLIT DEMOS.
    searches list of entities for query and returns relevant items
    """
    return [item for item in entity_results if query in item["entity_text"]]


def get_entities(doc, use_rules: bool) -> Iterator[str]:
    """
    USED FOR EXTRACTING ENTITIES AND SENTENCES FOR LABELING - see notebook.
    iterates through entities in a doc and generates dictionaries corresponding to attributes of the entity
    """

    for ent in doc.ents:
            yield {
                "entity_text": ent.text,
                "entity_label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                # "entity_modifiers": ent._.modifiers,
                "entity_modifiers": [(x._context_rule.literal, x._context_rule.category) for x in ent._.modifiers],
                "entity_literal": ent._.target_rule.literal if use_rules else None,
                "is_negated": ent._.is_negated,
                "is_uncertain": ent._.is_uncertain,
                "is_historical": ent._.is_historical,
                "is_hypothetical": ent._.is_hypothetical,
                "is_family": ent._.is_family,
                "current_sentence_extracted": ent.sent,
                "previous_sentence_extracted": ent._.previous_sentence, #get_previous_sentence(ent),
                "next_sentence_extracted": ent._.next_sentence, #get_next_sentence(ent),
                "section_category": ent._.section_category,
                "section_title": ent._.section_title,
                # 'section_text': ent._.section_text,
            }


def get_regex_tbl(pattern:str, df:pd.DataFrame, col:str = 'Ed Provider Notes') -> pd.DataFrame:
    """
    FOR WRANGLING AND EDA
    given a string, count the number of occurences in the provider notes of a pattern and return a dataframe with the proportion of notes with said pattern across years
    """
    # str.contains counts the first occurence?
    cts = pd.DataFrame(df[col].str.contains(pattern, regex = True, case=False, na = False))
    if 'year' not in df:
        raise ValueError("Missing 'year' in dataframe")
    cts['year'] = df['year'] 
    summary_cts = cts.groupby('year')[col].agg(['sum', 'count'])
    summary_cts['prop'] = summary_cts['sum']/summary_cts['count']
    
    return summary_cts


def df_from_entity_json(results_list:List[str]) -> pd.DataFrame:
    """
    UNUSED
    creates a dataframe for labelling, downstream analytics, etc. from the output of 
    nlp pipeline
    """
    
    # create first dataframe
    first_df =  pd.json_normalize(results_list)
    # expand dataframe into 'long' format, dependent on the # of entities
    entities_df = first_df.explode('entities')
    # expand entity fields into columns
    normalized_entities_df = pd.json_normalize(entities_df['entities'])
    assert entities_df.shape[0] == normalized_entities_df.shape[0]
    # combine into final, dataframe
    final_df = pd.concat([entities_df.reset_index().drop(columns = 'index'), normalized_entities_df], axis = 1)
    # cleaning 
    for col in ['section_title', 'current_sentence_extracted', 'previous_sentence_extracted', 'next_sentence_extracted']:
        final_df[col] = final_df[col].apply(lambda x: str(x))
    final_df['final_sentences'] = final_df[['previous_sentence_extracted', 'current_sentence_extracted', 'next_sentence_extracted']].agg(''.join, axis=1)
    final_df['year'] = pd.DatetimeIndex(final_df['date']).year
    final_df = final_df.drop(columns = ['entities'])
    final_df = final_df.reset_index().rename(columns = {'index' :'unique_sentence_id'})
    return final_df

def load(
    use_rules: bool = True,
    enable={"medspacy_tokenizer", "medspacy_target_matcher", "medspacy_context"},
    disable=[],
    set_attributes = True
) -> spacy.Language:
    """ """

    if set_attributes:
        _set_attributes()

    # using target matching instead of a pre-trained model

    medspacy_pipes = {
        "medspacy_tokenizer",
        "medspacy_target_matcher",
        "medspacy_context",
    }

    if use_rules:
        nlp = medspacy.load(enable=medspacy_pipes)

        target_matcher = nlp.get_pipe("medspacy_target_matcher")

        target_matcher.add(target_rules)

        print("Target matcher added to pipeline")

    # use a pre-trained model
    else:
        nlp = medspacy.load(
            "en_ner_bc5cdr_md",
            disable=[
                "tok2vec",
                "tagger",
                "parser",  # needed for sentence parsing
                "medspacy_pyrush",
                "attribute_ruler",
                "lemmatizer",
                "medspacy_target_matcher"
            ],
        )
    # preprocessor
    preprocessor = Preprocessor(nlp.tokenizer)
    # add the rules to the preprocessor
    preprocessor.add(preprocess_rules)
    # set the attribute to the new preprocessor with the added rules
    nlp.tokenizer = preprocessor

    # load sentence boundary disambiguator
    nlp.add_pipe("medspacy_pysbd", first=True)

    # loading in sectionizer patterns
    sectionizer = nlp.add_pipe("medspacy_sectionizer")
    sectionizer.add(section_rules)

    # load context rules

    context = nlp.get_pipe('medspacy_context')
    context.add(context_rules)
 
    # load postprocess rules
    postprocessor = nlp.add_pipe("medspacy_postprocessor")
    postprocessor.add(postprocess_rules)
    return nlp
