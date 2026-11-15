import json
import urllib.request
from datetime import datetime, timezone

COINS = ["ETHUSDT", "BTCUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]

def get_candles(symbol):
    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval=1h&limit=100"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "CryptoAlertBot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)[:-1]

def calculate_rsi(closes, period=14):
    changes = [
        closes[i] - closes[i - 1]
        for i in range(1, len(closes))
    ]

    gains = [max(x, 0) for x in changes]
    losses = [max(-x, 0) for x in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(changes)):
        avg_gain = (avg_gain * 13 + gains[i]) / 14
        avg_loss = (avg_loss * 13 + losses[i]) / 14

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def check_coin(symbol):
    candles = get_candles(symbol)

    closes = [float(c[4]) for c in candles]
    volumes = [float(c[5]) for c in candles]

    price = closes[-1]
    ma20 = sum(closes[-20:]) / 20
    rsi = calculate_rsi(closes)

    recent_sell_volume = sum(
        volumes[-i] for i in range(1, 4)
        if closes[-i] < float(candles[-i][1])
    )

    recent_buy_volume = sum(
        volumes[-i] for i in range(1, 4)
        if closes[-i] >= float(candles[-i][1])
    )

    bearish_volume = recent_sell_volume > recent_buy_volume * 1.5

    buy = (
        price > ma20
        and 45 <= rsi <= 65
        and not bearish_volume
    )

    timestamp = datetime.fromtimestamp(
        candles[-1][6] / 1000, timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    print(f"\n{symbol} | {timestamp}")
    print(f"Price: ${price:.6f}")
    print(f"MA20: ${ma20:.6f}")
    print(f"RSI: {rsi:.2f}")

    if buy:
        print(f"POTENTIAL BUY {symbol}")
        print("Verify trend, Quidax spread and fees before trading.")
    else:
        print("NO TRADE")

for coin in COINS:
    try:
        check_coin(coin)
    except Exception as error:
        print(f"{coin}: Data unavailable ({error})")
