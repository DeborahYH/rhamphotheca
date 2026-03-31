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

with open ("wikiaves_data/tachyphonus_coronatus_(31-03-2026)_cards.csv", "r", encoding="utf-8") as file:
    df_cards = pd.read_csv(file)

transform_data(df_cards)
