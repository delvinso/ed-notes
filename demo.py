import streamlit as st
import pandas as pd
import numpy as np
from negation_pipeline import *
import re
from spacy_streamlit import visualize_ner


def main():
    st.title('Extracting Clinical Red Flag Symptoms from ED Notes')

    # instantiate and load our entity extraction model. the negex component is static.
    nlp = create_negation_model("en_ner_bc5cdr_md")

    queries = st.text_input("List of symptoms to query - please make sure they're comma delimited. Leave empty to show all results.")
    queries = [str(x).strip() for x in re.split(",", queries)]

    note = st.text_area("Input your note here:", height=200)

    if note:
        st.write("Queries", queries)
        # parse the text into sections and sentences and perform entity extraction and negation detection
        entities = get_negation_entities(nlp, note)

        results = []
        if queries:
            for query in queries:
                res = query_results(query, entities)
                results.extend(res)
        else:
            queries = entities

        st.write("Results", results)

        matcher0 = match(nlp, [e['Text'] for e in entities], "NEG_ENTITY")
        doc0 = overwrite_ent_lbl(matcher0, nlp(note))
        visualize_ner(title = "Negated Entities (this does NOT SHOW asserted entities)",
                      doc = doc0,
                      labels=  ["DISEASE", "NEG_ENTITY"],
                      colors = {'DISEASE': 'linear-gradient(180deg, #66ffcc, #abf763)', 
                                     "NEG_ENTITY": 'linear-gradient(90deg, #aa9cfc, #fc9ce7)'})
        
if __name__ == "__main__":
    main()