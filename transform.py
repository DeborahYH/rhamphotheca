import pandas as pd


def transform_data(df_cards):

    # Standardizes the values in the 'tipo_registro' column to be more descriptive
    df_cards["tipo_registro"] = df_cards["tipo_registro"].map({'F': 'Foto', 'S': 'Som'})    

with open ("wikiaves_data/molothrus_rufoaxillaris_(30-03-2026)_cards.csv", "r", encoding="utf-8") as file:
    df_cards = pd.read_csv(file)

transform_data(df_cards)
