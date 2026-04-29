from telethon import TelegramClient, events
import re

api_id = 35433634
api_hash = "a9468f9a7654ae557f8eb8ce74b2c79f"

source_channel = -1001729775431
target_channel = -1003864471994

client = TelegramClient("session", api_id, api_hash)


def parse_signal(text):
    # Remove emojis (important)
    text = text.upper()

    # Signal
    signal = re.search(r"(BUY|SELL)", text)

    # Ticker
    ticker = re.search(r"(GOLD|XAUUSD)", text)

    # Entry (handles space issue)
    entry = re.search(r"ENTER IN\s*=\s*([\d\-\s]+)", text)

    # SL (ignore brackets like (80 pips))
    sl = re.search(r"SL\s*=\s*(\d+)", text)

    # TP (supports TP1, TP2, etc.)
    tps = re.findall(r"TP\d*\s*=\s*(\d+)", text)

    entry_value = entry.group(1).strip() if entry else ""
    entry_value = entry_value.replace(" ", "").replace("-", " - ")

    return {
        "signal": signal.group(1) if signal else "",
        "ticker": "XAUUSD",
        "entry": entry_value,
        "sl": sl.group(1) if sl else "",
        "tp1": tps[0] if len(tps) > 0 else "",
        "tp2": tps[1] if len(tps) > 1 else "",
        "tp3": tps[2] if len(tps) > 2 else "",
        "tp4": tps[3] if len(tps) > 3 else "",
    }


def format_message(d):
    # Only include TP if exists
    tp_lines = "\n".join(
        [f"🎯 TP{i+1}: {tp}" for i, tp in enumerate([d['tp1'], d['tp2'], d['tp3'], d['tp4']]) if tp]
    )

    return f"""📢 SIGNAL ALERT

🔔 Signal: {d['signal']}
📊 Ticker: {d['ticker']}

🎯 Entry: {d['entry']}

{tp_lines}

🛑 SL: {d['sl']}"""


@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    text = event.message.message

    if not text:
        return

    data = parse_signal(text)

    if data["signal"] and data["entry"] and data["sl"]:
        msg = format_message(data)
        await client.send_message(target_channel, msg)


client.start()
print("Bot running...")
client.run_until_disconnected()
