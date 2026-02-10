import socketio
import requests
import os
import time

# ===== Environment Variables =====
SOCKET_TOKEN = os.environ.get("SOCKET_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not all([SOCKET_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    raise ValueError("Missing environment variables")

# ================================

# إنشاء عميل Socket.IO
sio = socketio.Client(reconnection=True, reconnection_attempts=0)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Error sending telegram: {e}")

@sio.event
def connect():
    print("✅ Connected to Streamlabs")
    print("⏳ Waiting for donations...")

@sio.event
def event(data):
    if data.get("type") == "donation":
        messages = data.get("message", [])
        if not isinstance(messages, list):
            messages = [messages]

        for donation in messages:
            name = donation.get("name", "Unknown")
            amount = donation.get("formatted_amount") or donation.get("amount")
            msg = donation.get("message") or "بدون رسالة"

            text = (
                f"<b>💰 دعم مالي جديد!</b>\n\n"
                f"👤 <b>الاسم:</b> {name}\n"
                f"💵 <b>المبلغ:</b> {amount}$\n\n"
                f"💬 <b>الرسالة:</b>\n"
                f"<blockquote>{msg}</blockquote>"
            )

            print(text)
            send_telegram(text)

@sio.event
def disconnect():
    print("⚠️ Disconnected from Streamlabs")

def connect_streamlabs():
    while True:
        try:
            url = f"https://sockets.streamlabs.com?token={SOCKET_TOKEN}"
            sio.connect(url, transports=["websocket"])
            sio.wait()
        except Exception as e:
            print(f"🔄 Connection lost, retrying in 5 seconds... ({e})")
            time.sleep(5)

if __name__ == "__main__":
    connect_streamlabs()
