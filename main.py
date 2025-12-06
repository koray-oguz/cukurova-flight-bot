import requests
from bs4 import BeautifulSoup

def flightaware_verisi_cek():
    # Çukurova Havalimanı (LTDB) FlightAware Adresi
    url = "https://tr.flightaware.com/live/airport/LTDB"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            tablolar = soup.find_all("table")

            print(f"Sayfada toplam {len(tablolar)} adet tablo bulundu.\n")

            # İlk iki tabloyu al (Genellikle: 1. Kalkan, 2. İnen)
            for i, tablo in enumerate(tablolar[:2]):
                
                # --- BAŞLIK BELİRLEME ---
                tablo_icerigi = tablo.get_text()
                if "Nereye" in tablo_icerigi or "Destination" in tablo_icerigi:
                    tablo_adi = "KALKAN UÇUŞLAR (GİDEN)"
                elif "Nereden" in tablo_icerigi or "Origin" in tablo_icerigi:
                    tablo_adi = "İNEN UÇUŞLAR (GELEN)"
                else:
                    tablo_adi = "KALKAN UÇUŞLAR (GİDEN)" if i == 0 else "İNEN UÇUŞLAR (GELEN)"
                
                print(f"--- {tablo_adi} ---")

                satirlar = tablo.find_all("tr")
                veriler = []

                for satir in satirlar[1:]:
                    hucreler = satir.find_all("td")
                    
                    if len(hucreler) >= 3:
                        try:
                            # GÜNCELLEME BURADA YAPILDI:
                            # 1. Sütun -> Uçuş Kodu (Eski adıyla Havayolu)
                            ucus_kodu = hucreler[0].get_text(strip=True)
                            
                            # 2. Sütun -> Uçak Tipi (Atlıyoruz, değişkene atamaya gerek yok)
                            
                            # 3. veya 4. Sütun -> Konum
                            lokasyon = hucreler[2].get_text(strip=True)
                            
                            # Eğer 2. sütun çok kısaysa (örn: B738 gibi uçak tipiyse) ve 3. sütun varsa
                            # Konum bilgisi bazen 3. indexe kayabilir. Kontrol edelim:
                            if len(hucreler) > 3:
                                alt_lokasyon = hucreler[3].get_text(strip=True)
                                if len(lokasyon) < 5 and len(alt_lokasyon) > 3:
                                    lokasyon = alt_lokasyon

                            veriler.append({
                                "Ucus_Kodu": ucus_kodu,   # İsim düzeltildi
                                "Yon/Konum": lokasyon     # Uçak tipi çıkarıldı
                            })
                        except IndexError:
                            continue
                
                for v in veriler:
                    print(v)
                
                print("\n" + "="*50 + "\n")

        else:
            print(f"Hata Kodu: {response.status_code}")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    flightaware_verisi_cek()
