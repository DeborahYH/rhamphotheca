import pandas as pd


def transform_data(df_cards):

    # Standardizes the values in the 'media_type' column to be more descriptive
    df_cards["media_type"] = df_cards["media_type"].map({'F': 'Foto', 'S': 'Som'})

    location = df_cards["location"].str.split("/", expand=True)
    df_cards["municipality"] = location[0]
    df_cards["state"] = location[1]
    print(df_cards[["media_type", "location", "municipality", "state"]])

with open ("wikiaves_data/calidris_melanotos_(30-03-2026)_cards.csv", "r", encoding="utf-8") as file:
    df_cards = pd.read_csv(file)

transform_data(df_cards)
