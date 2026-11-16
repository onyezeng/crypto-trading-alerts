
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "BNB": "binancecoin",
}

STATE_FILE = Path("last_signals.json")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# These thresholds are illustrative, not proven trading rules.
BUY_THRESHOLD = 3.0
SELL_THRESHOLD = -3.0

def load_signals():
    if not STATE_FILE.exists():
        return {}

    try:
        with STATE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Invalid signals file")
        return data
    except (OSError, ValueError) as error:
        raise RuntimeError(
            f"Unable to read previous signals: {error}"
        ) from error

def save_signals(signals):
    temporary_file = STATE_FILE.with_suffix(".json.tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(signals, file, indent=2, sort_keys=True)
        file.write("\n")

    os.replace(temporary_file, STATE_FILE)

def fetch_prices():
    coin_ids = ",".join(COINS.values())

    parameters = urllib.parse.urlencode({
        "ids": coin_ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    })

    url = (
        "https://api.coingecko.com/api/v3/simple/price?"
        + parameters
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "CryptoTradingAlerts/1.0",
        },
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)

def get_signal(change):
    if change >= BUY_THRESHOLD:
        return (
            "BUY",
            "24-hour price increase reached the BUY threshold."
        )

    if change <= SELL_THRESHOLD:
        return (
            "SELL",
            "24-hour price decrease reached the SELL threshold."
        )

    return (
        "NO TRADE",
        "Market movement does not meet the trading thresholds."
    )

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "Telegram token or chat ID is missing."
        )

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_TOKEN
        + "/sendMessage"
    )

    payload = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected the message.")

def format_alert(symbol, price, change, old_signal, signal, reason):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    return (
        "CRYPTO TRADING ALERT\n\n"
        f"Coin: {symbol}\n"
        f"Price: ${price:,.4f}\n"
        f"24-hour change: {change:+.2f}%\n\n"
        f"PREVIOUS SIGNAL: {old_signal}\n"
        f"NEW SIGNAL: {signal}\n\n"
        f"Reason: {reason}\n\n"
        f"Time: {timestamp}\n\n"
        "Signal only. Verify market conditions "
        "before making any trade."
    )

def main():
    print("=" * 45)
    print("CRYPTO TRADING ALERT BOT")
    print(
        "Time:",
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        ),
    )
    print("=" * 45)

    previous_signals = load_signals()
    prices = fetch_prices()

    updated_signals = previous_signals.copy()
    alerts_sent = 0

    for symbol, coin_id in COINS.items():
        print(f"\nANALYZING: {symbol}")

        market = prices.get(coin_id)

        if not isinstance(market, dict):
            raise RuntimeError(
                f"Missing market information for {symbol}"
            )

        price = market.get("usd")
        change = market.get("usd_24h_change")

        if price is None or change is None:
            raise RuntimeError(
                f"Incomplete market information for {symbol}"
            )

        price = float(price)
        change = float(change)

        signal, reason = get_signal(change)
        old_signal = previous_signals.get(symbol)

        print(f"Price: ${price:,.4f}")
        print(f"Change: {change:+.2f}%")
        print(f"SIGNAL: {signal}")
        print(f"Reason: {reason}")

        if old_signal is None:
            print("Initial signal recorded. No alert.")

        elif old_signal != signal:
            message = format_alert(
                symbol,
                price,
                change,
                old_signal,
                signal,
                reason,
            )

            send_telegram(message)
            alerts_sent += 1

            print(
                f"TELEGRAM ALERT SENT: "
                f"{old_signal} -> {signal}"
            )

        else:
            print("Signal unchanged. No alert.")

        updated_signals[symbol] = signal

        # Save successful progress, including sent alerts.
        save_signals(updated_signals)

        time.sleep(1)

    print("\n" + "=" * 45)
    print("MARKET CHECK COMPLETED")
    print(f"Telegram alerts sent: {alerts_sent}")
    print("Trading signals saved successfully.")
    print("=" * 45)

if __name__ == "__main__":
    main()
