"""
Filters for only ED related notes and recasts data from long to wide so each row is a patient-visit record with notes as columns.
"""
import pandas as pd
import os 


if __name__ == "__main__":

    df = pd.read_csv(os.path.join('processed', 'ed-notes-long-patient.csv'))
    
    ed_notes = df[df['Note Type'].isin(['ED Provider Notes', 'ED Triage Notes'])].reset_index()
    
    # removing note metadata, pivot so note types are the columns and the note text are the values
    ed_notes2 = ed_notes.drop(columns = ['Author Type', "Author's Service", "CHIRPP Icon", "External Referral", "File Time", "Referral Order"]).pivot_table(index = ['CSN', 'MRN'], columns ='Note Type', values = 'Note Text', aggfunc='first')

    # join the patient-visit metadata, minus the note metadata, with the notes
    merged_df = pd.merge(
        # these columns are the notes metadata and are not unique, ie. cannot be cast to 'tidy' or 'wide' data
        ed_notes.drop(columns = ['Author Type', "Author's Service", "CHIRPP Icon", "External Referral", "File Time", "Referral Order",'Note Type', 'Note Text', 'index']).drop_duplicates(),
        ed_notes2,
        how="left",
        on = ['CSN', 'MRN']
    )

    # remove duplicate - looks like they are true duplicates due to some weird parsing?
    merged_df = merged_df[~merged_df[['CSN', 'MRN']].duplicated()]
    
    merged_df.to_csv('processed/ed-notes-tidy-patient.csv', index = False)
    
    