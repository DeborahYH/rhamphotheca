import pandas as pd
import numpy as np


def transform_data(df_cards):

    boolean_dict = {"Sim": True, "Não": False}

    # Standardizes the values in the 'media_type' column to be more descriptive
    df_cards["media_type"] = df_cards["media_type"].map({'F': 'Foto', 'S': 'Som'})

    location = df_cards["location"].str.split("/", expand=True)
    df_cards["municipality"] = location[0]
    df_cards["state"] = location[1]

    boolean_columns = ["emitter_seen", "after_playback", "banded", "possible_release"]

    for column in boolean_columns:
        if column in df_cards.columns:
            df_cards[column] = df_cards[column].map(boolean_dict)   
        else:
            df_cards[column] = np.nan

    # If 'rec_datetime' has values in the format "DD/MM/YYYY HH:MM", it splits them into separate columns
    if df_cards["rec_datetime"].str.contains(":").any():
        split = df_cards["rec_datetime"].str.split(" ")
        df_cards["rec_date"] = split.str.get(0)
        df_cards["rec_time"] = split.str.get(1)

    # Treats values in DD/MM/YYYY HH:MM format
    full_format = pd.to_datetime(df_cards["rec_datetime"], format="%d/%m/%Y %H:%M", errors="coerce")

    # Treats values in DD/MM/YYYY format
    date_format = pd.to_datetime(df_cards["rec_datetime"], format="%d/%m/%Y", errors="coerce")

    # Merges both parsed formats, preventing data loss
    df_cards["rec_datetime"] = full_format.fillna(date_format)
    
    # Converts the 'rec_date' and 'rec_time' columns to date/time format
    df_cards["rec_date"] = pd.to_datetime(df_cards["rec_date"], errors="coerce", dayfirst=True)
    df_cards["rec_time"] = pd.to_datetime(df_cards["rec_time"], format="%H:%M", errors="coerce").dt.time

    # Converts the 'photo_date' and 'publication_date' columns to date format
    df_cards["photo_date"] = pd.to_datetime(df_cards["photo_date"], errors="coerce", dayfirst=True).dt.date
    df_cards["publication_date"] = pd.to_datetime(df_cards["publication_date"], errors="coerce", dayfirst=True).dt.date
    
    df_cards["duration"] = df_cards['duration'].str.removesuffix(" segundo(s)").astype("Int64")

    mask_mb = df_cards["file_size"].str.contains("MB", na=False)
    df_cards.loc[mask_mb, "file_size"] = (df_cards.loc[mask_mb, "file_size"].str.removesuffix(" MB").astype("Float64") * 1024)

    mask_kb = df_cards["file_size"].str.contains("KB", na=False)
    df_cards.loc[mask_kb, "file_size"] = df_cards.loc[mask_kb, "file_size"].str.removesuffix(" KB").astype("Float64")

    df_cards["file_size"] = df_cards["file_size"].astype("Float64")

    # Explodes the 'subject' column into separate rows
    df_cards['subject'] = df_cards['subject'].str.split(r"\s*,\s*")
    df_cards_exploded = df_cards.explode(column='subject')

    # Creates a dataframe identifying different subjects
    df_subjects = pd.DataFrame({'subject_id': [1, 2, 3, 4, 5],
                                'subject': ['Ave', 'Alimento', 'Ovo', 'Ninho', 'Bando']})

    # Creates a junction table connecting the original dataframe with df_subjects
    df_cards_subjects = df_cards_exploded[['id', 'subject']].merge(df_subjects)

    # Removes the 'subject' column the original dataframe, as it will be handled in a separate table
    df_cards_exploded = df_cards_exploded.drop('subject', axis='columns')

with open ("wikiaves_data/tinamus_solitarius_(02-04-2026)_cards.csv", "r", encoding="utf-8") as file:
    df_cards = pd.read_csv(file)

transform_data(df_cards)
