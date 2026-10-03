import json
import locale
import time
from pathlib import Path

import requests

COIN_GECKO_MARKET_CAP_URL = "https://api.coingecko.com/api/v3/coins/markets"
PER_PAGE = 200
MARKET_PAGES = 5
REQUEST_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
EXCLUDED_CATEGORIES = (
    "stablecoins",
    "yield-bearing-stablecoins",
    "wrapped-tokens",
    "bridged-tokens",
    "liquid-staking-tokens",
    "liquid-restaking-tokens",
    "tokenized-products",
)

BASE = Path("~/devel/Trading/data").expanduser()
FILE = "coingecko_crypto_ranks.json"


def request(page=1, category=None):
    params = {
        "vs_currency": "usd",
        "per_page": PER_PAGE,
        "page": page,
    }
    if category is not None:
        params["category"] = category

    for attempt in range(REQUEST_RETRIES + 1):
        print(
            f"Firing CoinGecko request: page={page}, "
            f"category={category or 'all'}, attempt={attempt + 1}/{REQUEST_RETRIES + 1}",
            flush=True,
        )
        response = requests.get(COIN_GECKO_MARKET_CAP_URL, params=params)

        if response.status_code != 429 or attempt == REQUEST_RETRIES:
            response.raise_for_status()
            return response.json()

        retry_after = response.headers.get("Retry-After")
        try:
            delay = float(retry_after)
        except (TypeError, ValueError):
            delay = RETRY_BACKOFF_SECONDS * 2**attempt
        print(
            f"CoinGecko rate limit reached; retrying in {delay:g} seconds "
            f"(retry {attempt + 1}/{REQUEST_RETRIES}).",
            flush=True,
        )
        time.sleep(delay)


def get_category_ids(categories):
    excluded_ids = set()

    for category in categories:
        page = 1
        while True:
            category_coins = request(page=page, category=category)
            excluded_ids.update(item["id"] for item in category_coins if "id" in item)

            if len(category_coins) < PER_PAGE:
                break

            page += 1

    return excluded_ids


def extract_data(data, excluded_ids):
    return [
        {
            "id": item["id"],
            "rank": item["market_cap_rank"],
            "name": item["name"],
            "symbol": item["symbol"],
            "price": item["current_price"],
            "market_cap": item["market_cap"],
            "market_cap_formatted": locale.currency(item["market_cap"], grouping=True),
            "market_cap_rank": item["market_cap_rank"],
            "total_volume": item["total_volume"],
        }
        for item in data
        if item["id"] not in excluded_ids and "name" in item and "symbol" in item
    ]


def main():
    locale.setlocale(locale.LC_ALL, "")
    excluded_ids = get_category_ids(EXCLUDED_CATEGORIES)
    market_data = []

    for page in range(1, MARKET_PAGES + 1):
        market_data.extend(request(page=page))

    extracted_data = extract_data(market_data, excluded_ids)

    print(json.dumps(extracted_data, indent=4))
    output_file = BASE / FILE

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(extracted_data, file, indent=4)

    print(f"{len(extracted_data)} coins/tokens written to {output_file}")


if __name__ == "__main__":
    main()
