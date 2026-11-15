import json
import os
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
STATE_FILE = "last_signals.json"

def load_signals():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_signals(signals):
    with open(STATE_FILE, "w") as f:
        json.dump(signals, f)
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


def analyze_coin(symbol, coin_id, previous_signals):
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
        if signal in ("BUY", "SELL", "NO TRADE"):
            message = (
                f"CRYPTO TRADING ALERT\n"
                f"Coin: {symbol}\n"
                f"Signal: {signal}\n"
                f"Price: ${current:,.4f}\n"
                f"Change: {change:+.2f}%\n"
                f"Reason: {reason}"
            )
            old_signal = previous_signals.get(symbol)

            if old_signal is None:
        print(symbol + ": Initial signal recorded")
            elif signal != old_signal:
        send_telegram(message)
        print(symbol + ": Signal changed from " + old_signal + " to " + signal)
            else:
        print(symbol + ": Signal unchanged. No alert.")

        previous_signals[symbol] = signal

    except Exception as e:
        print("------------------------")
        print(symbol + ": DATA UNAVAILABLE")
        print("Error: " + str(e))


def main():
    previous_signals = load_signals()



    
    print("CRYPTO TRADING ALERT BOT")
    print(
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    )

    for symbol, coin_id in COINS.items():
        analyze_coin(symbol, coin_id, previous_signals)

import os

def send_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = json.dumps({
        "chat_id": chat_id,
        "text": message
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        print("Telegram response:", response.status)

send_telegram("Crypto Trading Alerts bot is connected!")
if __name__ == "__main__":
    main()
