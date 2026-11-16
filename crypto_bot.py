import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ==========================================
# CRYPTOCURRENCIES TO MONITOR
# ==========================================

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "BNB": "binancecoin"
}

STATE_FILE = "last_signals.json"


# ==========================================
# LOAD PREVIOUS SIGNALS
# ==========================================

def load_signals():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

    except (OSError, ValueError) as error:
        print("Unable to load previous signals:", error)

    return {}


# ==========================================
# SAVE CURRENT SIGNALS
# ==========================================

def save_signals(signals):
    temporary_file = STATE_FILE + ".tmp"

    try:
        with open(temporary_file, "w") as file:
            json.dump(signals, file, indent=4)

        os.replace(temporary_file, STATE_FILE)

        print("Trading signals saved successfully.")

    except OSError as error:
        print("Unable to save signals:", error)


# ==========================================
# SEND TELEGRAM NOTIFICATIONS
# ==========================================

def send_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials are missing.")
        return False

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/sendMessage"
    )

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            if response.status == 200:
                print("Telegram notification delivered.")
                return True

    except Exception as error:
        print("Telegram delivery failed:", error)

    return False


# ==========================================
# GET LIVE CRYPTO MARKET DATA
# ==========================================

def get_market_data(coin_id):
    url = (
        "https://api.coingecko.com/api/v3/"
        "coins/"
        + coin_id
        + "/market_chart?vs_currency=usd&days=1"
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CryptoTradingAlerts/1.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return json.load(response)


# ==========================================
# ANALYZE EACH CRYPTOCURRENCY
# ==========================================

def analyze_coin(symbol, coin_id, previous_signals):

    print()
    print("==============================")
    print("ANALYZING:", symbol)
    print("==============================")

    try:
        data = get_market_data(coin_id)

        prices = [
            float(item[1])
            for item in data["prices"]
        ]

        if len(prices) < 15:
            print("SIGNAL: NO TRADE")
            print("Reason: Insufficient market data")
            return

        current_price = prices[-1]
        previous_price = prices[-13]

        if previous_price <= 0:
            print("SIGNAL: NO TRADE")
            print("Reason: Invalid market data")
            return

        price_change = (
            (current_price - previous_price)
            / previous_price
        ) * 100

        moving_average = (
            sum(prices[-14:]) / 14
        )

        # ==================================
        # TRADING DECISION
        # ==================================

        if (
            price_change > 1.0
            and current_price > moving_average
        ):

            signal = "BUY"

            reason = (
                "Positive short-term momentum. "
                "Price is above its recent average."
            )

        elif (
            price_change < -1.0
            and current_price < moving_average
        ):

            signal = "SELL"

            reason = (
                "Negative short-term momentum. "
                "Price is below its recent average."
            )

        else:

            signal = "NO TRADE"

            reason = (
                "Market conditions do not meet "
                "the trading requirements."
            )

        # ==================================
        # DISPLAY RESULTS
        # ==================================

        print("Coin:", symbol)

        print(
            "Price: $"
            + format(current_price, ",.4f")
        )

        print(
            "Change: "
            + format(price_change, "+.2f")
            + "%"
        )

        print("SIGNAL:", signal)
        print("Reason:", reason)

        # ==================================
        # PREPARE TELEGRAM MESSAGE
        # ==================================

        message = (
            "CRYPTO TRADING ALERT\n\n"
            f"Coin: {symbol}\n"
            f"Signal: {signal}\n"
            f"Price: ${current_price:,.4f}\n"
            f"Change: {price_change:+.2f}%\n\n"
            f"Reason: {reason}\n\n"
            "This is a market signal, "
            "not a guaranteed profitable trade."
        )

        # ==================================
        # CHECK FOR SIGNAL CHANGES
        # ==================================

             send_telegram(message)
        previous_signals[symbol] = signal  
    except Exception as error:

        print("SIGNAL: DATA UNAVAILABLE")
        print("Reason:", str(error))


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    print()
    print("================================")
    print("CRYPTO TRADING ALERT BOT")
    print("================================")

    current_time = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    print("Time:", current_time)

    previous_signals = load_signals()

    for symbol, coin_id in COINS.items():

        analyze_coin(
            symbol,
            coin_id,
            previous_signals
        )

    save_signals(previous_signals)

    print()
    print("================================")
    print("MARKET CHECK COMPLETED")
    print("================================")


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
