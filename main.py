import requests
from bs4 import BeautifulSoup
import os
import sys

# --- GITHUB SECRETS'TEN ALINACAK BİLGİLER ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def telegrama_gonder(mesaj):
    """Mesajı Telegram botuna gönderir."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram token veya Chat ID bulunamadı!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # <pre> etiketi ile gönderiyoruz ki boşluklar hizalı dursun
    payload = {
        "chat_id": CHAT_ID,
        "text": f"<pre>{mesaj}</pre>", 
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print("Mesaj Telegram'a gönderildi.")
    except Exception as e:
        print(f"Telegram gönderme hatası: {e}")

def flightaware_verisi_cek():
    url = "https://tr.flightaware.com/live/airport/LTDB"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Mesajı biriktirmek için değişken
    toplam_mesaj = f"✈️ <b>Çukurova Uçuş Raporu</b>\n\n"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tablolar = soup.find_all("table")

            # İlk iki tabloyu al
            for i, tablo in enumerate(tablolar[:2]):
                tablo_icerigi = tablo.get_text()
                
                # Başlık Belirleme
                if "Nereye" in tablo_icerigi or "Destination" in tablo_icerigi:
                    tablo_adi = "🛫 KALKAN (DEPARTURES)"
                elif "Nereden" in tablo_icerigi or "Origin" in tablo_icerigi:
                    tablo_adi = "🛬 İNEN (ARRIVALS)"
                else:
                    tablo_adi = "🛫 KALKAN" if i == 0 else "🛬 İNEN"

                toplam_mesaj += f"{tablo_adi}\n{'-'*25}\n"

                satirlar = tablo.find_all("tr")
                veriler = []

                for satir in satirlar[1:]:
                    hucreler = satir.find_all("td")
                    if len(hucreler) >= 3:
                        try:
                            ucus_kodu = hucreler[0].get_text(strip=True)
                            lokasyon = hucreler[2].get_text(strip=True)

                            if len(hucreler) > 3:
                                alt_lokasyon = hucreler[3].get_text(strip=True)
                                if len(lokasyon) < 5 and len(alt_lokasyon) > 3:
                                    lokasyon = alt_lokasyon
                            
                            # Mobil görünüm için lokasyon ismini biraz kırpalım
                            if len(lokasyon) > 18:
                                lokasyon = lokasyon[:16] + ".."

                            veriler.append({
                                "Kod": ucus_kodu,
                                "Rota": lokasyon
                            })
                        except IndexError:
                            continue

                if veriler:
                    # --- PANDAS OLMADAN MANUEL TABLO OLUŞTURMA ---
                    # Başlık satırı (Kod sütunu 12 karakterlik yer kaplasın)
                    toplam_mesaj += f"{'Kod':<12} {'Rota'}\n"
                    
                    for veri in veriler:
                        # f-string padding kullanarak hizalama yapıyoruz
                        # :<12 ifadesi "sola yasla ve 12 karaktere tamamla" demektir.
                        toplam_mesaj += f"{veri['Kod']:<12} {veri['Rota']}\n"
                else:
                    toplam_mesaj += "Veri bulunamadı."

                toplam_mesaj += "\n\n" # Tablolar arası boşluk

            # Döngü bitince tek seferde gönder
            telegrama_gonder(toplam_mesaj)

        else:
            print(f"Siteye erişilemedi: {response.status_code}")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    flightaware_verisi_cek()
