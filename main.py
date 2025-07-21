import json
import locale
import sys

import requests

COIN_GECKO_MARKET_CAP_URL = (
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250"
)

BASE = "/Users/vatikiot/devel/Trading/data"
FILE = "coingecko_crypto_ranks.json"


def request(page=1):
    response = requests.get(f"{COIN_GECKO_MARKET_CAP_URL}&page={page}")

    locale.setlocale(locale.LC_ALL, "")
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        extracted_data = [
            {
                "rank": item["market_cap_rank"],
                "name": item["name"],
                "symbol": item["symbol"],
                "price": item["current_price"],
                "market_cap": item["market_cap"],
                "market_cap_formatted": locale.currency(
                    item["market_cap"], grouping=True
                ),
                "market_cap_rank": item["market_cap_rank"],
                "total_volume": item["total_volume"],
            }
            for item in data
            if "name" in item and "symbol" in item
        ]

        print(json.dumps(extracted_data, indent=4))
        print(f"Crypto rankings saved in {BASE}/{FILE}")

        return extracted_data

    else:
        print("Failed to retrieve data")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        sys.exit(1)


page_1 = request(page=1)
next_page = request(page=2)
page_1.extend(next_page)

with open(f"{BASE}/{FILE}", "w", encoding="utf-8") as file:
    json.dump(page_1, file, indent=4)
