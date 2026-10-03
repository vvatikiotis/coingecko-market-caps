# Market cap APIs 

-  https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd

- Tradingview: there's no pine api for crypto *but* there is for stocks:

```pine
Outstanding = financial(syminfo.tickerid, "TOTAL_SHARES_OUTSTANDING", "FQ")
MarketCap = Outstanding*close
```

