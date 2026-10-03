import locale
import unittest
from unittest.mock import patch

import main


class CategoryFilteringTests(unittest.TestCase):
    @patch("main.time.sleep")
    @patch("main.requests.get")
    @patch("builtins.print")
    def test_request_reports_rate_limit_delay(self, print_, get, sleep):
        rate_limited = unittest.mock.Mock(status_code=429, headers={})
        successful = unittest.mock.Mock(status_code=200)
        successful.json.return_value = []
        get.side_effect = [rate_limited, successful]

        main.request(page=1, category="bridged-tokens")

        print_.assert_any_call(
            "CoinGecko rate limit reached; retrying in 5 seconds (retry 1/3).",
            flush=True,
        )
        sleep.assert_called_once_with(5)

    @patch("main.request")
    def test_get_category_ids_fetches_every_page_for_each_category(self, request):
        first_page = [{"id": f"stablecoin-{index}"} for index in range(main.PER_PAGE)]
        request.side_effect = [
            first_page,
            [{"id": "last-stablecoin"}],
            [{"id": "wrapped-bitcoin"}],
        ]

        excluded_ids = main.get_category_ids(("stablecoins", "wrapped-tokens"))

        self.assertEqual(len(excluded_ids), main.PER_PAGE + 2)
        self.assertIn("last-stablecoin", excluded_ids)
        self.assertIn("wrapped-bitcoin", excluded_ids)
        self.assertEqual(
            request.call_args_list,
            [
                unittest.mock.call(page=1, category="stablecoins"),
                unittest.mock.call(page=2, category="stablecoins"),
                unittest.mock.call(page=1, category="wrapped-tokens"),
            ],
        )

    def test_extract_data_excludes_category_ids(self):
        locale.setlocale(locale.LC_ALL, "")
        market_data = [
            {
                "id": "tether",
                "market_cap_rank": 3,
                "name": "Tether",
                "symbol": "usdt",
                "current_price": 1,
                "market_cap": 100,
                "total_volume": 10,
            },
            {
                "id": "bitcoin",
                "market_cap_rank": 1,
                "name": "Bitcoin",
                "symbol": "btc",
                "current_price": 100_000,
                "market_cap": 1_000,
                "total_volume": 100,
            },
        ]

        result = main.extract_data(market_data, {"tether"})

        self.assertEqual([item["id"] for item in result], ["bitcoin"])


if __name__ == "__main__":
    unittest.main()
