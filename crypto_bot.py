import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "BNB": "binancecoin"
}

def get_market_data(coin_id):
    url = (
        "https://api.coingecko.com/api/v3/"
        "coins/" + coin_id +
        "/market_chart?vs_currency=usd&days=1"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(
        req, timeout=20
    ) as response:
        return json.load(response)


def analyze_coin(symbol, coin_id):
    try:
        data = get_market_data(coin_id)
        prices = [p[1] for p in data["prices"]]

        if len(prices) < 15:
            print(symbol + ": NO TRADE")
            print("Reason: Insufficient data")
            return

        current = prices[-1]
        previous = prices[-13]

        change = (
            (current - previous) / previous
        ) * 100

        average = sum(prices[-14:]) / 14

        if change > 1 and current > average:
            signal = "BUY"
            reason = "Positive short-term momentum"

        elif change < -1 and current < average:
            signal = "SELL"
            reason = "Negative short-term momentum"

        else:
            signal = "NO TRADE"
            reason = "No strong trading opportunity"

        print("------------------------")
        print(symbol)
        print("Price: $" + format(current, ".4f"))
        print("Change: " + format(change, ".2f") + "%")
        print("SIGNAL: " + signal)
        print("Reason: " + reason)

    except Exception as e:
        print("------------------------")
        print(symbol + ": DATA UNAVAILABLE")
        print("Error: " + str(e))


def main():
    print("CRYPTO TRADING ALERT BOT")
    print(
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    )

    for symbol, coin_id in COINS.items():
        analyze_coin(symbol, coin_id)


if __name__ == "__main__":
    main()
