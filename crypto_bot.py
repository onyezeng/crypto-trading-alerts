import json
import urllib.request
from datetime import datetime, timezone

COINS = {
    "BTC": "XBTUSD",
    "ETH": "ETHUSD",
    "SOL": "SOLUSD",
    "XRP": "XRPUSD",
    "BNB": None
}

def get_candles(pair):
    if pair is None:
        return None

    url = (
        "https://api.kraken.com/0/public/OHLC"
        f"?pair={pair}&interval=5"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CryptoTradingAlerts/1.0"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.load(response)

    if data.get("error"):
        raise ValueError(str(data["error"]))

    result = data["result"]
    key = next(k for k in result if k != "last")

    # Exclude the candle still forming.
    return result[key][:-1]


def calculate_rsi(closes, period=14):
    if len(closes) <= period:
        return None

    changes = [
        closes[i] - closes[i - 1]
        for i in range(1, len(closes))
    ]

    gains = [max(x, 0) for x in changes]
    losses = [max(-x, 0) for x in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(changes)):
        avg_gain = (
            avg_gain * (period - 1) + gains[i]
        ) / period

        avg_loss = (
            avg_loss * (period - 1) + losses[i]
        ) / period

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def check_coin(coin, pair):
    if pair is None:
        print(f"{coin}: NO TRADE")
        print("Reason: Market data source not configured")
        return

    try:
        candles = get_candles(pair)

        closes = [float(c[4]) for c in candles]
        volumes = [float(c[6]) for c in candles]

        if len(closes) < 50:
            print(f"{coin}: NO TRADE")
            print("Reason: Insufficient market data")
            return

        price = closes[-1]
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50
        rsi = calculate_rsi(closes)

        avg_volume = sum(volumes[-21:-1]) / 20
        current_volume = volumes[-1]

        volume_strong = current_volume > avg_volume * 1.2

        if (
            price > ma20 > ma50
            and 50 <= rsi <= 65
            and volume_strong
        ):
            signal = "BUY"
            reason = "Uptrend with strong volume"

        elif (
            price < ma20 < ma50
            and rsi < 45
            and volume_strong
        ):
            signal = "SELL"
            reason = "Downtrend with strong volume"

        else:
            signal = "NO TRADE"
            reason = "Trading conditions not confirmed"

        print(f"\n{coin}: {signal}")
        print(f"Price: ${price:,.4f}")
        print(f"RSI: {rsi:.2f}")
        print(f"Reason: {reason}")

    except Exception as e:
        print(f"\n{coin}: NO TRADE")
        print(f"Reason: Market data unavailable ({e})")


print("CRYPTO TRADING ALERTS")
print("Time:", datetime.now(timezone.utc).isoformat())

for coin, pair in COINS.items():
    check_coin(coin, pair)
