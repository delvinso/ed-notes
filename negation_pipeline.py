"""
Proof of Concept SpaCy Pipeline for Negation Detection using NegEx

Delvin So
"""
import re 
import spacy
from negspacy.negation import Negex
from negspacy.termsets import termset
from pprint import pprint


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


def get_negation_entities(nlp_model: spacy.Language, text:str, print_sentences:bool = False) -> list[dict[str]]:
    """
    splits text into headers and performs entity extraction followed by negation detection on said entities.
    returns a list of tuple, each tuple is an entity and whether it is negated or asserted.
    """
    
    results = []
    
    text = text.lower()
    
    # why are these headers???? only found this through empirical testing..
    # creates sections
    text = text.split("         ")
    
    text = [segment for segment in text if segment != ""]

    # for each section, split on two spaces or more to get sentences. also found this empirically...
    for segment in text:
        
        for sentence in re.split(r'\s{2,}', segment):

            if print_sentences:
                print(sentence.strip() + '\n')

            # perform entity extraction and negation detection per sentence.
            doc = nlp_model(sentence.strip())

            for ent in doc.ents:

                # if e.label_ == "DISEASE":
                if ent._.negex == True:
                    feature = 0
                elif ent._.negex == False:
                    feature = 1 

    #                     results.append((e.text, negated, feature))

                results.append({'Text': ent.text,
                     'Start/End': (ent.start_char, ent.end_char),
                     'Label': ent.label_,
                    #  'Explanation': spacy.explain(ent._.negex),
                     'Negated' : ent._.negex,
                     'Asserted': feature,
                     'Sentence': sentence.strip(),
                    })

    return results

def query_results(query:str, entity_results:list[dict[str]]) -> list[dict[str]]:
    """
    searches list of entities for query and returns relevant items
    """
    
    return [item for item in entity_results if query in item['Text']]
    
    
    
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
    
    
    
    
    