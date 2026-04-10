import pandas as pd
import numpy as np


BOOLEAN_DICT = {"Sim": True, "Não": False}

BOOLEAN_COLUMNS = ["emitter_seen", "after_playback", "banded", "possible_release"]

COLUMNS_ORDER = ['record_id', 'media_type', 'scientific_name', 'common_name', 'sex', 'age', 'main_action', 'photo_date',
                'publication_date', 'location', 'municipality', 'state', 'camera',  'author', 'guide', 'author_notes', 
                'sound_emitter', 'emitter_seen', 'context', 'after_playback', 'rec_datetime', 'rec_date', 'rec_time', 
                'recorder', 'microphone', 'file_size', 'duration', 'banded', 'possible_release']

MEDIA_TYPES = {'F': 'Foto',
            'S': 'Som'}

SUBJECTS = {1: 'Ave',
            2: 'Alimento',
            3: 'Ovo',
            4: 'Ninho',
            5: 'Bando'}

SOUNDS = {1: 'Canto',
        2: 'Chamado/Apelo',
        3: 'Dueto',
        4: 'Canto de madrugada/entardecer', 
        5: 'Tamborilado', 
        6: 'Bater de asas', 
        7: 'Estalar de bico'}


def transform_data(df):

    df = df.copy()

    # Standardizes the values in the 'media_type' column to be more descriptive
    df["media_type"] = df["media_type"].map(MEDIA_TYPES)

    location = df["location"].str.split("/", expand=True)
    df["municipality"] = location[0]
    df["state"] = location[1]

    # Converts the values in the selected columns to boolean values
    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].map(BOOLEAN_DICT)   
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
    
    df_subjects = pd.DataFrame(SUBJECTS.items(), columns=['subject_id', 'subject'])
    df_sounds = pd.DataFrame(SOUNDS.items(), columns=['sound_id', 'sound_type'])

    # Creates a junction table connecting the original dataframe with df_subjects
    df_subjects_bridge = df_expanded2[['record_id', 'subject']].merge(df_subjects)

    # Creates a junction table connecting the original dataframe with df_sounds
    df_sounds_bridge = df_expanded2[['record_id', 'sound_type']].merge(df_sounds)

    df_subjects_bridge.to_csv("wikiaves_data/subjects_bridge.csv", index=False)
    df_sounds_bridge.to_csv("wikiaves_data/sounds_bridge.csv", index=False)

    # Removes the 'subject' column the original dataframe, as it will be handled in a separate table
    df_final = df_expanded2.drop(['subject', 'sound_type'], axis='columns')
    
    # Reorders the columns
    df_final = df_final.reindex(columns=COLUMNS_ORDER)
    df_final.to_csv("wikiaves_data/records.csv", index=False)


with open ("wikiaves_data/tinamus_solitarius_(09-04-2026)_cards.csv", "r", encoding="utf-8") as file:
    df = pd.read_csv(file)

transform_data(df)
