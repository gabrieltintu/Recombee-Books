import os

import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import SetItemValues, Batch
from recombee_api_client.exceptions import APIException

DB_NAME = os.getenv('RECOMBEE_DB', 'numele_bazei_tale_de_date')
PRIVATE_TOKEN = os.getenv('RECOMBEE_TOKEN', 'tokenul_tau_privat')
REGION = os.getenv('RECOMBEE_REGION', 'eu-west')

client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=Region[REGION.upper().replace('-', '_')])

PATH_DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'books.csv')
BATCH_SIZE = 100


def send_batch(requests):
    responses = client.send(Batch(requests))
    return sum(1 for r in responses if r['code'] not in (200, 201))


def send_items():
    """Functie care citeste dataset-ul si trimite item-urile in Recombee"""
    df = pd.read_csv(PATH_DATASET)
    print(f"Se trimit {len(df)} item-uri in Recombee...")

    requests = []
    erori = 0
    trimise = 0

    for index, row in df.iterrows():
        item_id = str(row['book_id'])

        properties = {
            "title": str(row['title']),
            "authors": str(row['authors']),
            "publication_year": int(row['publication_year']),
            "language_code": str(row['language_code']),
            "average_rating": float(row['average_rating']),
            "ratings_count": int(row['ratings_count']),
            "image_url": str(row['image_url']),
        }

        # Adaugam request-ul de setare a valorilor pentru item
        # (SetItemValues creează automat item-ul dacă acesta nu există)
        requests.append(SetItemValues(item_id, properties, cascade_create=True))

        # Trimitem in loturi (batch) de cate 100 pentru eficienta
        if len(requests) == BATCH_SIZE:
            erori += send_batch(requests)
            trimise += len(requests)
            requests = []
            print(f"S-a trimis un lot de {BATCH_SIZE} item-uri... ({trimise}/{len(df)})")

    # Trimitem si restul ramanase (daca numarul total nu e multiplu de 100)
    if requests:
        erori += send_batch(requests)
        trimise += len(requests)
        print(f"S-a trimis ultimul lot de item-uri. ({trimise}/{len(df)})")

    if erori:
        print(f"Trimitere terminata cu {erori} erori.")
    else:
        print("Toate item-urile au fost trimise cu succes!")


if __name__ == "__main__":
    try:
        send_items()
    except APIException as e:
        print(f"Eroare API: {e}")
