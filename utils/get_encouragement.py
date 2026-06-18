import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUOTE_FILE = BASE_DIR / "config" / "curated_quotes.json"

with open(QUOTE_FILE, "r", encoding="utf-8") as f:
    QUOTES = json.load(f)

def get_random_quote():
    item = random.choice(QUOTES)
    return [item["quote"], item["author"]]