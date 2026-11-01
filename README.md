# Sistem de recomandare pentru cărți cu Recombee

Proiect pentru laboratoarele de **Sisteme de Recomandare**: un catalog de cărți încărcat în [Recombee](https://www.recombee.com/).

## Dataset

- **Domeniu:** cărți (literatură populară de pe Goodreads)
- **Sursă:** [goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k) (Zygmunt Zając), disponibil și pe [Kaggle](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)
- **Fișier:** [`books.csv`](books.csv)
- **Volum:** 2000 de cărți (cele mai populare 2000 din setul original de 10.000, după eliminarea rândurilor fără titlu, autor sau an de publicare)

Fiecare rând este o carte, identificată unic prin `book_id`. Această coloană **nu** este înregistrată ca proprietate: devine `itemId` în Recombee când se încarcă item-urile.

## Proprietăți (atribute) înregistrate în Recombee

| Proprietate | Tip Recombee | Descriere |
| --- | --- | --- |
| `title` | `string` | Titlul cărții (include seria, dacă există) |
| `authors` | `string` | Autorul / autorii, separați prin virgulă |
| `publication_year` | `int` | Anul publicării originale (poate fi negativ pentru opere antice) |
| `language_code` | `string` | Codul limbii (ex.: `eng`, `en-US`, `fre`; `unknown` dacă lipsește) |
| `average_rating` | `double` | Nota medie pe Goodreads (1–5) |
| `ratings_count` | `int` | Numărul de evaluări pe Goodreads |
| `image_url` | `image` | URL-ul copertei |

Coloana de identificare: `book_id` (`int`, 1–2000+) → `itemId`.

## Rulare

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export RECOMBEE_DB="numele-bazei-de-date"
export RECOMBEE_TOKEN="tokenul-privat"
export RECOMBEE_REGION="eu-west"

python recombee_properties.py
```

Scriptul citește `books.csv`, verifică numărul de rânduri, trimite schema către Recombee prin `AddItemProperty` și afișează proprietățile existente (`ListItemProperties`).
