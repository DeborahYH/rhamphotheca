import pandas as pd
import numpy as np

# Defines the final column order of the transformed dataframe.
COLUMNS_ORDER = ['record_id', 'media_type', 'scientific_name', 'common_name', 'sex', 'age', 'main_action', 'photo_date',
                'publication_date', 'location', 'municipality', 'state', 'camera',  'author', 'guide', 'author_notes', 
                'sound_emitter', 'emitter_seen', 'context', 'after_playback', 'rec_datetime', 'rec_date', 'rec_time', 
                'recorder', 'microphone', 'file_size', 'duration', 'banded', 'possible_release']

# Maps 'Yes' or 'No' strings to Python booleans.
BOOLEAN_DICT = {"Sim": True, "Não": False}

# Columns that will have their values converted to boolean.
BOOLEAN_COLUMNS = ["emitter_seen", "after_playback", "banded", "possible_release"]

# Maps media type codes to descriptive string values.
MEDIA_TYPES = {'F': 'Foto',
            'S': 'Som'}

# # Maps each subject name to a unique ID
SUBJECTS = {1: 'Ave',
            2: 'Alimento',
            3: 'Ovo',
            4: 'Ninho',
            5: 'Bando'}

# # Maps each sound type name to a unique ID
SOUNDS = {1: 'Canto',
        2: 'Chamado/Apelo',
        3: 'Dueto',
        4: 'Canto de madrugada/entardecer', 
        5: 'Tamborilado', 
        6: 'Bater de asas', 
        7: 'Estalar de bico'}


def clean_metadata(df):
    """
    Cleans data from the 'media_type', 'duration' and 'file_size' columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the raw data to be cleaned.
    
    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the cleaned columns.
    """

    # Standardizes the values in the 'media_type' column to be more descriptive
    df["media_type"] = df["media_type"].map(MEDIA_TYPES)

    # Cleans the 'duration' column by removing the suffix " segundo(s)"
    df["duration"] = df['duration'].str.removesuffix(" segundo(s)").astype("Int64")

    # Converts values from MB to KB and removes the suffixes from the 'file_size' column
    mask_mb = df["file_size"].str.contains("MB", na=False)
    df.loc[mask_mb, "file_size"] = (df.loc[mask_mb, "file_size"].str.removesuffix(" MB").astype("Float64") * 1024)

    mask_kb = df["file_size"].str.contains("KB", na=False)
    df.loc[mask_kb, "file_size"] = df.loc[mask_kb, "file_size"].str.removesuffix(" KB").astype("Float64")

    # Ensures that all values in the 'file_size' column are float values in KB
    df["file_size"] = df["file_size"].astype("Float64")

    return df

def map_boolean(df):
    """
    Converts the values in BOOLEAN_COLUMNS to boolean values.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the columns that need to be converted.
    
    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the transformed columns.
    """

    # Converts the values in the selected columns to boolean values
    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].map(BOOLEAN_DICT)   
        else:
            df[column] = np.nan

    return df

def extract_location(df):
    """
    Creates two columns based on the 'location' column.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the 'location' column that will be split.
    
    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the new 'municipality' and 'state' columns.
    """

    # Splits the 'location' column into 'municipality' and 'state' columns
    location = df["location"].str.split("/", expand=True)
    df["municipality"] = location[0]
    df["state"] = location[1]

    return df

def parse_datetime(df):
    """
    Stantandarizes the columns contining date and time information.
    Creates separate columns from 'rec_datetime' containing the date and time.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the data that will be parsed.
    
    Returns
    -------
    df : pandas.DataFrame
        The dataframe containing the standardized values for date and time, as well as the new 'rec_date' and 'rec_time' columns.
    """

    # Converts the 'photo_date' and 'publication_date' columns to date format
    df["photo_date"] = pd.to_datetime(df["photo_date"], errors="coerce", dayfirst=True).dt.date
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce", dayfirst=True).dt.date

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

    return df

def build_junctions(df):
    """
    Creates junction tables for the 'subject' and 'sound_type' columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the columns that will be turned into individual tables.
    
    Returns
    -------
    df_clean : pandas.DataFrame
        The dataframe that had 'subject' and 'sound_type' columns removed after turning them into individual tables and creating the junction tables.
    """

    # Explodes the 'subject' and 'sound_type' columns into separate rows
    df['subject'] = df['subject'].str.split(r"\s*,\s*")
    df['sound_type'] = df['sound_type'].str.split(r"\s*,\s*")
    df_expanded1 = df.explode(column='subject')
    df_expanded2 = df_expanded1.explode(column='sound_type')
    
    # Creates dataframes that will be used as reference tables for the junction tables
    df_subjects = pd.DataFrame(SUBJECTS.items(), columns=['subject_id', 'subject'])
    df_sounds = pd.DataFrame(SOUNDS.items(), columns=['sound_id', 'sound_type'])

    # Creates a junction table connecting the original dataframe with df_subjects
    df_subjects_bridge = df_expanded2[['record_id', 'subject']].merge(df_subjects)
    df_subjects_bridge = df_subjects_bridge[['record_id', 'subject_id', 'subject']]

    # Creates a junction table connecting the original dataframe with df_sounds
    df_sounds_bridge = df_expanded2[['record_id', 'sound_type']].merge(df_sounds)
    df_sounds_bridge = df_sounds_bridge[['record_id', 'sound_id', 'sound_type']]

    # Removes the columns that will be handled in separate tables and drops duplicate rows created by explode()
    df_clean = df_expanded2.drop(['subject', 'sound_type'], axis='columns').drop_duplicates(subset=['record_id'])

    return df_clean


def transform_data(df):
    """
    Transforms data from records extracted from Wiki Aves.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the raw data to be transformed.
    """

    df = df.copy()

    df_metadata = clean_metadata(df)

    df_boolean = map_boolean(df_metadata)

    df_location = extract_location(df_boolean)
    
    df_datetime = parse_datetime(df_location)

    df_junctions = build_junctions(df_datetime)
        
    # Reorders the columns
    df_final = df_junctions.reindex(columns=COLUMNS_ORDER)
