from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import random
import os


records = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# Extracts the data from photo/sound records
for tm in ['f', 's']:

    page = 1

    # Uses pagination to obtain all the records from the desires species
    while True:

        response = requests.get(f"https://www.wikiaves.com.br/getRegistrosJSON.php?tm={tm}&t=c&c=3550308&p=1", headers=headers)

        data = response.json()
        items = data.get("registros", {}).get("itens", {})

        # Interrupts the loop when there are no more records
        if not items:
            break 
            
        # Extracts the desired data from each record
        else:
            for item in items.values():
                records.append({
                    "ID": item["id"],
                    "Tipo de Registro": item["tipo"],
                    "Autor": item["autor"],
                    "Município": item["local"],
                    "Data do Registro": item["data"],
                    "Espécie": item["sp"]["nvt"],
                    "Nome Cientifico": item["sp"]["nome"],
                })
                
            wait = random.uniform(10, 30)
            time.sleep(wait)

            page += 1

df = pd.DataFrame(records)
df.to_csv(os.path.join("wikiaves_data", "sao_paulo_grid.csv"), index=False)

