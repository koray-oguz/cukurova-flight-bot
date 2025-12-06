from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import os

URL = "https://cukurovaairport.aero/yolcular-ve-ziyaretciler/ucus-bilgileri/tum-ucuslar"
AIRPORT = "Çukurova"


def send_telegram(message):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram gönderim hatası:", e)


def scrape_flights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_selector("table")

        rows = page.locator("table tr").all()

        arrivals = []
        departures = []

        for row in rows[1:]:
            cols = row.locator("td").all()
            if len(cols) < 4:
                continue

            time = cols[0].inner_text().strip()
            airline = cols[2].inner_text().strip()
            route = cols[3].inner_text().strip()

            if "-" not in route:
                continue

            left, right = [x.strip() for x in route.split("-")]

            if right == AIRPORT:
                arrivals.append(f"{airline} | {route} | {time}")
            elif left == AIRPORT:
                departures.append(f"{airline} | {route} | {time}")

        browser.close()
        return arrivals, departures


def main():
    arrivals, departures = scrape_flights()

    msg = "<b>Çukurova Havalimanı Uçuş Bilgileri</b>\n\n"

    msg += "🟢 <b>Gelen Uçuşlar</b>\n"
    if arrivals:
        for a in arrivals:
            msg += f"• {a}\n"
    else:
        msg += "• Veri yok\n"

    msg += "\n🔵 <b>Giden Uçuşlar</b>\n"
    if departures:
        for d in departures:
            msg += f"• {d}\n"
    else:
        msg += "• Veri yok\n"

    send_telegram(msg)


if __name__ == "__main__":
    main()
