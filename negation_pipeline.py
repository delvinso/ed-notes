"""
Proof of Concept SpaCy Pipeline for Negation Detection using NegEx

Delvin So
"""
import re 
import spacy
from negspacy.negation import Negex
from negspacy.termsets import termset
from pprint import pprint
from typing import List, Dict

# lemma_model_str = "en_core_sci_sm"
# lemma_model = spacy.load(lemma_model_str)
    # have this outside the function so the lemmatization model isn't instantiated every time.
    # if lemmatize: 
    #     lemma_model = spacy.load("en_core_sci_sm")
    #     text = lemmatize(text, lemma_model)

def lemmatize(note:str , nlp: spacy.Language) -> str:
    """
    Usage: lemmatized_note = lemmatize(record_notes, lemma_model)
    """
    doc = nlp(note)
    lemNote = [word.lemma_ for word in doc]
    return " ".join(lemNote)


def create_negation_model(nlp_model:str = "en_ner_bc5cdr_md") -> spacy.Language:
    """
    Loads and returns SciSpaCy model with entity recogintion and an added NegEx component.
    Patterns should be customized, likely through trial and error.
    
    "en_ner_bc5cdr_md" - NER model trained on the BC5CDR corpus

    """
    
    nlp = spacy.load(nlp_model, disable=["tok2vec", "tagger", 
                                         # "parser", needed for sentence parsing
                                         "attribute_ruler", "lemmatizer"])

    # can be one of 'en', 'en_clinical', or 'en_clinical_sensitive'
    ts = termset("en_clinical_sensitive") 

    # TODO: comment this. this will help increase specificity and sensitivity, 
    # but the problem at the moment is - what is the current sensitivity and specificity?
    ts.add_patterns(
        {
        "pseudo_negations": [],
        "termination": [],
        "preceding_negations": ['not'],
        "following_negations": ['absent'],
        }
    )

    nlp.add_pipe("negex",
                 config={ 
                     # "ent_types":["DISEASE"],
                     "neg_termset":ts.get_patterns()
                     
                 })
    
    return nlp

def custom_sentencizer(text) -> List[str]:
    """
    Splits each ED note into sections based on spaces, and each resulting 'section' into 'sentences' consisting of 2+ or 
    more  spaces. We could split on periods but empirically it seems that collective statements seem to be delimited on 2+ 
    spaces. Splitting on a period could break up the statements into less meaningful sentences.
    """
    sentences = []

    # why are these headers - only found this through empirical testing..
    text = text.split("         ")
    text = [segment for segment in text if segment != ""]

    for i, segment in enumerate(text):

        # for each section, split on two spaces or more to get sentences. also found this empirically...
        for sentence in re.split(r'\s{2,}', segment):
            sentence2 = sentence.strip()
            sentences.append(sentence2)

                # continue splitting since the pattern failed, splits on ...
                # if len(sentence2) > 500: 
                #     long_sentences.
                # more_sentences = sentence2.split('.')
    return sentences


def get_negation_entities(nlp_model: spacy.Language, text:str, print_sentences:bool = False) -> List[Dict[str, str]]:
    """
    splits text into headers and performs entity extraction followed by negation detection on said entities.
    returns a list of tuple, each tuple is an entity and whether it is negated or asserted.
    """
    
    results = []
    
    text = text.lower()
    sentences = custom_sentencizer(text)
    
    for sentence in sentences:
        doc = nlp_model(sentence)
        for ent in doc.ents:

            # if e.label_ == "DISEASE":
            if ent._.negex == True:
                feature = 0
                negated = 1
            elif ent._.negex == False:
                feature = 1 
                negated = 0

            results.append({'Entity': ent.text,
                    'Start/End': (ent.start_char, ent.end_char),
                    'Label': ent.label_,
                    'Negated' : negated,
                    'Affirmed': feature,
                    'Sentence': sentence.strip(),
                })

    return results

def query_results(query:str, entity_results:List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    searches list of entities for query and returns relevant items
    """
    
    return [item for item in entity_results if query in item['Entity']]
    
    
    
# VISUALIZATION, spacy specific...
#from https://medium.com/@MansiKukreja/clinical-text-negation-handling-using-negspacy-and-scispacy-233ce69ab2ac
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

#function to identify span objects of matched megative phrases from clinical note
def match(nlp,terms,label):
        patterns = [nlp.make_doc(text) for text in terms]
        matcher = PhraseMatcher(nlp.vocab)
        matcher.add(label, None, *patterns)
        return matcher
    
#replacing the labels for identified negative entities
def overwrite_ent_lbl(matcher, doc):
    matches = matcher(doc)
    seen_tokens = set()
    new_entities = []
    entities = doc.ents
    for match_id, start, end in matches:
        if start not in seen_tokens and end - 1 not in seen_tokens:
            new_entities.append(Span(doc, start, end, label=match_id))
            entities = [
                e for e in entities if not (e.start < end and e.end > start)
            ]
            seen_tokens.update(range(start, end))
    doc.ents = tuple(entities) + tuple(new_entities)
    return doc

if __name__ == "__main__":


    nlp = create_negation_model("en_ner_bc5cdr_md")
    
    
    
    
    