import requests
import json


COIN_GECKO_MARKET_CAP_URL = (
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
)
BASE = "/Users/vatikiot/devel/Trading/data"
response = requests.get(COIN_GECKO_MARKET_CAP_URL)

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
            "total_volume": item["total_volume"],
        }
        for item in data
        if "name" in item and "symbol" in item
    ]
    with open(f"{BASE}/crypto_ranks.json", "w", encoding="utf-8") as file:
        json.dump(extracted_data, file, indent=4)

    # print(json.dumps(data, indent=4))
    print(f"Crypto rankings saved in {BASE} directory")
else:
    print("Failed to retrieve data")
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
