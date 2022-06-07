import pandas as pd
import json

if __name__ == "__main__":
    df = pd.read_csv('processed/ed-notes-tidy-patient.csv')

    master_key = df[['CSN', 'MRN']].to_dict(orient = 'records')

    with open("master_key.json", "w") as f:
        json.dump(master_key, f, indent=4)


    # remove standard pattern consisting of John doe, a X y.o. Y m.o male presented....
    df['ED Provider Notes'] = df['ED Provider Notes'].replace("^([A-Za-z].*?)presented", "[Patient Name Redacted] presented", regex = True)

    # sanity check replacements, should be 1 occurence of the replaced pattern at MOST
    cts = pd.DataFrame(df['ED Provider Notes'].str.count('\\[Patient Name Redacted\\] presented'))
    assert cts[cts['ED Provider Notes'] > 1].shape[0] == 0
    # df.iloc[cts[cts['ED Provider Notes'] > 1].index]

    df['year'] = pd.DatetimeIndex(df['Arrival Date']).year
    df = df.sort_values(['year'])
    cts['year'] = df['year'] 

    summary_cts = cts.groupby('year')['ED Provider Notes'].agg(['sum', 'count'])
    summary_cts['prop'] = summary_cts['sum']/summary_cts['count']
    df = df.drop(columns = ['year'])

    # we drop the MRN because it is not unique, the CSN is.
    df2 = df.drop(columns = ['MRN', 'Patient Name', 'Sex', 'Date of Birth', 'Age (Years)', 'Address', 'Postal Code', 'City', 'Province', 'Country', 'Provider to Dispo', 'EMS Offload Time'])

    df2.to_csv('processed/ed-notes-tidy-patient-no-metadata.csv', index = False)