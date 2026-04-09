import pandas as pd
import numpy as np


def transform_data(df):

    boolean_dict = {"Sim": True, "Não": False}

    # Standardizes the values in the 'media_type' column to be more descriptive
    df["media_type"] = df["media_type"].map({'F': 'Foto', 'S': 'Som'})

    location = df["location"].str.split("/", expand=True)
    df["municipality"] = location[0]
    df["state"] = location[1]

    boolean_columns = ["emitter_seen", "after_playback", "banded", "possible_release"]

    for column in boolean_columns:
        if column in df.columns:
            df[column] = df[column].map(boolean_dict)   
        else:
            df[column] = np.nan

    # If 'rec_datetime' has values in the format "DD/MM/YYYY HH:MM", it splits them into separate columns
    if df["rec_datetime"].str.contains(":").any():
        split = df["rec_datetime"].str.split(" ")
        df["rec_date"] = split.str.get(0)
        df["rec_time"] = split.str.get(1)

    # Treats values in DD/MM/YYYY HH:MM format
    full_format = pd.to_datetime(df["rec_datetime"], format="%d/%m/%Y %H:%M", errors="coerce")

    # Treats values in DD/MM/YYYY format
    date_format = pd.to_datetime(df["rec_datetime"], format="%d/%m/%Y", errors="coerce")

    # Merges both parsed formats, preventing data loss
    df["rec_datetime"] = full_format.fillna(date_format)
    
    # Converts the 'rec_date' and 'rec_time' columns to date/time format
    df["rec_date"] = pd.to_datetime(df["rec_date"], errors="coerce", dayfirst=True)
    df["rec_time"] = pd.to_datetime(df["rec_time"], format="%H:%M", errors="coerce").dt.time

    # Converts the 'photo_date' and 'publication_date' columns to date format
    df["photo_date"] = pd.to_datetime(df["photo_date"], errors="coerce", dayfirst=True).dt.date
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce", dayfirst=True).dt.date
    
    df["duration"] = df['duration'].str.removesuffix(" segundo(s)").astype("Int64")

    mask_mb = df["file_size"].str.contains("MB", na=False)
    df.loc[mask_mb, "file_size"] = (df.loc[mask_mb, "file_size"].str.removesuffix(" MB").astype("Float64") * 1024)

    mask_kb = df["file_size"].str.contains("KB", na=False)
    df.loc[mask_kb, "file_size"] = df.loc[mask_kb, "file_size"].str.removesuffix(" KB").astype("Float64")

    df["file_size"] = df["file_size"].astype("Float64")

    # Explodes the 'subject' and 'sound_type' columns into separate rows
    df['subject'] = df['subject'].str.split(r"\s*,\s*")
    df['sound_type'] = df['sound_type'].str.split(r"\s*,\s*")
    df_expanded1 = df.explode(column='subject')
    df_expanded2 = df_expanded1.explode(column='sound_type')

    # Creates a dataframe identifying different subjects
    df_subjects = pd.DataFrame({'subject_id': [1, 2, 3, 4, 5],
                                'subject': ['Ave', 'Alimento', 'Ovo', 'Ninho', 'Bando']})

    df_sounds = pd.DataFrame({'sound_id': [1, 2, 3, 4, 5, 6, 7],
                                    'sound_type': ['Canto', 'Chamado/Apelo', 'Dueto', 'Canto de madrugada/entardecer', 
                                                    'Tamborilado', 'Bater de asas', 'Estalar de bico']}) 
    
    # Creates a junction table connecting the original dataframe with df_subjects
    df_subjects = df_expanded2[['record_id', 'subject']].merge(df_subjects)

    # Creates a junction table connecting the original dataframe with df_sounds
    df_sounds = df_expanded2[['record_id', 'sound_type']].merge(df_sounds)

    # Removes the 'subject' column the original dataframe, as it will be handled in a separate table
    df_final = df_expanded2.drop(['subject', 'sound_type'], axis='columns')

    # Reorders the columns
    columns_order = ['record_id', 'media_type', 'scientific_name', 'common_name', 'sex', 'age', 'main_action', 'photo_date',
                    'publication_date', 'location', 'municipality', 'state', 'camera',  'author', 'guide', 'author_notes', 
                    'sound_emitter', 'emitter_seen', 'context', 'after_playback', 'rec_datetime', 'rec_date', 'rec_time', 
                    'recorder', 'microphone', 'file_size', 'duration', 'banded', 'possible_release']
    df_final = df_final.reindex(columns=columns_order)

with open ("wikiaves_data/tinamus_solitarius_(09-04-2026)_cards.csv", "r", encoding="utf-8") as file:
    df = pd.read_csv(file)

transform_data(df)
