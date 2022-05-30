# ed-notes

This repository contains code for pre-processing and extracting clinical symptoms from SickKids crystal notes. 

### Set-Up

```
conda env create -f medsp-environment.yml
conda activate ed-notes
conda env list # sanity check
```

To use the conda environment as the kernel for a jupyter notebook:
```
conda activate ed-notes
ipython kernel install --user --name=notes
```

This will allow you to select the 'notes' kernel as the environment for your jupyter notebook in the top right corner.


To install the SpaCy models required for entity recognition and lemmatization:

```
# for entity recognition in clinical notes
pip3 install --user https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bc5cdr_md-0.4.0.tar.gz
# for lemmatization
pip3 install --user https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz
```
Model URLs can be obtained from [here](https://allenai.github.io/scispacy/) if they're outdated.


### Scripts

- `pre_process_crystal.py` - concatenates all crystal notes and restores original note by joining each patient-visit-note type together
- `filter_parse_ed_notes.py` - filters only relevant notes of interest and casts into a wide dataframe
- `remove_patient_md.py` - removes patient metadata from notes and names (where applicable) at beginning of note