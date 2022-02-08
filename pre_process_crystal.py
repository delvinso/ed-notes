"""
Concatenates all crystal notes, parsing out structure and saving down as i) JSON and ii) a long dataframe for downstream analyses
python3 pre-process-crystal.py

TODO: add arguments (not really necessary as ideally, this is a one-time step)
"""

import json
import os
import pandas as pd
from glob import glob 
from pprint import pprint
from tqdm import tqdm
from typing import List


def load_concat_crystal_notes(globbed_dir:list[str]) -> pd.DataFrame:
    """
    reads in and concatenates a directory of crystal excel spreadsheets
    """
    dfs_list = []
    
    for spreadsheet in tqdm(globbed_files):
        df = pd.read_excel(spreadsheet)
        if 'SK CHIRPP Notes' in df.columns:
            df.columns = df.iloc[0] # take first row as header
            df = df[1:]
        dfs_list.append(df)
        
    full_df = pd.concat(dfs_list, axis = 0)
    
    return full_df


def parse_crystal_notes(spreadsheet: pd.DataFrame)  -> List[dict]:
    """
    Parses a dataframe of crystal notes into json
    Can be used as a stand-alone function.

    A single patient-visit (CSN-MRN) can be have multiple note types, with each note type being split into several rows due to a supposed character limit in EPIC.
    """
    
    master_list = []

    # columns related to patient information, could be broken down into patient-specific and patient-visit columns 
    patient_metadata_cols = ['CSN', 'MRN', 'Patient Name', 'Sex', 'Date of Birth', 'Age (Years)', 
                             'Arrival Date', 'Arrival Time', 'CTAS', 'Address', 
                             'City', 'Province', 'Postal Code', 'Country', 'Chief Complaint', 
                             'Diagnosis', 'Provider to Dispo', 'EMS Offload Time', 'Problem List', 'Disposition'] 
    
    note_metadata_cols = ['Note Type', 'File Time', 'Author Type', "Author's Service"]
    
    multiple_val_cols = ['Note Type', 'File Time', 'Author Type', "Author's Service", 'Referral Order', 'External Referral', 'CHIRPP Icon', 'Note Text']
    
    # confident these are already sorted..
    spreadsheet['File Time'] = pd.to_datetime(spreadsheet['File Time'].astype('object'))

    grouped_df = spreadsheet.groupby(['CSN', 'MRN'])
    
    for (group_id, group) in tqdm(grouped_df):
        
        for col in ['Date of Birth', 'Arrival Date', 'Arrival Time', 'Provider to Dispo', 'File Time']:
            group[col] = group[col].astype(str)

        # create our visit-patient metadata dictionary using the known, duplicated columns. 
        # these columns are duplicated by note.
        csn_mrn_dict = group[patient_metadata_cols]\
            .drop_duplicates()\
            .to_dict(orient = 'records')[0]

        csn_mrn_dict['Notes'] = []

        # further group the remaining note types for this particular visit-patient
        for (group_id2, note_subgroup) in group[multiple_val_cols].groupby(note_metadata_cols): 

            # create a note dict corresponding to the note type and its metadata. the note text must be removed since we want a single row corresponding to the metadata.
            note_dict = note_subgroup.loc[:, note_subgroup.columns != 'Note Text'].drop_duplicates().to_dict(orient = 'records')[0]
            
            # typing
            note_subgroup = note_subgroup.fillna(value = {'Note Text': ''}).astype(str)
            
            # concatenate the note and add it to the dict which only contains the metadata
            note_dict['Note Text'] = ''.join(note_subgroup['Note Text'])

            csn_mrn_dict['Notes'].append(note_dict)

        master_list.append(csn_mrn_dict)
    
    return master_list

def crystal_json_to_df(json_list = List[dict]) -> pd.DataFrame:
    """
    Takes a json, where each element is a patient-visit along with a nested array of 'Notes' and converts it into a long dataframe. 
    """
    
    df = pd.DataFrame(json_list)
    # duplicates each row, with metadata, for each note in 'Notes' (list)
    df_notes = df.explode('Notes')

    long_df = pd.concat([df_notes.drop(columns = ['Notes']), 
                           # expand the fields in the `Notes` (now a dict) into a column
                          df_notes['Notes'].apply(pd.Series)],
                         axis = 1) 
    # comes from converting the column of dicts into a series
    if 0 in long_df.columns: long_df.drop(columns = [0], inplace = True)

    
    return long_df

if __name__ == "__main__":
    
    raw_crystal_dir = './raw/Pre-Screen/*xlsx'
    out_dir = './processed'
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    concat_df_filename = os.path.join(out_dir, 'concatenated-crystal-notes.csv')
    
    # skip if concatenated df doesn't exist, pyopenxl is slow..
    if not os.path.isfile(concat_df_filename): 
        globbed_files = glob(raw_crystal_dir)

        concat_df = load_concat_crystal_notes(globbed_files)

        concat_df.to_csv(concat_df_filename, index = False)
    else:
        concat_df = pd.read_csv(concat_df_filename)
    
    json_list = parse_crystal_notes(concat_df)

    # saves output as json and into a long dataframe
    # with open(os.path.join( out_dir, "ed-crystal-dump-v2.json"),"w") as f:
    #     f.write(json.dumps(json_list, indent = 4))

    long_df = crystal_json_to_df(json_list)
    
    long_df.to_csv(os.path.join(out_dir, 'ed-notes-long-patient.csv'), index = False)