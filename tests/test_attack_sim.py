import socket
import time
import os
import sys
import threading
import subprocess

# Proje kök dizininin Python yoluna eklenmesi
KOK_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KOK_DIZIN not in sys.path:
    sys.path.insert(0, KOK_DIZIN)

class SaldiriSimulasyonu:
    """
    SİBER GÖZ — DoS / ICMP Flood Saldırı Simülatörü ve PCAP Paket Yakalayıcı.
    Pardus OS üzerinde Ağ Radarını ve Adli Bilişim (PCAP) modülünü test eder.
    """
    def __init__(self, hedef_ip="127.0.0.1", hedef_port=80):
        self.hedef_ip = hedef_ip
        self.hedef_port = hedef_port
        self.pcap_dizini = os.path.join(KOK_DIZIN, "logs", "lcaptures")
        os.makedirs(self.pcap_dizini, exist_ok=True)
        self.pcap_dosyasi = os.path.join(self.pcap_dizini, "saldiri_kayit.pcap")

    def pcap_dinleme_baslat(self, sure=4):
        """tcpdump kullanarak saldırı anındaki paketleri .pcap olarak kaydeder."""
        try:
            print(f"📡 [PCAP] Adli bilişim paket kaydı başladı ({sure} saniye)...")
            cmd = ["sudo", "tcpdump", "-i", "any", "-c", "100", "-w", self.pcap_dosyasi]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(sure)
            proc.terminate()
            print(f"✅ [PCAP] Ham paketler kaydedildi -> {self.pcap_dosyasi}")
        except Exception as e:
            print(f"⚠️ [PCAP HATA] Paket yakalanamadı: {str(e)}")

    def icmp_flood_simule_et(self, paket_sayisi=150):
        """Hızlı soket paketleri göndererek DoS trafiği üretir."""
        print(f"⚡ [SİMÜLASYON] {self.hedef_ip} adresine {paket_sayisi} paketlik DoS akışı başlatılıyor...")
        
        # Arka planda PCAP kaydını başlat
        pcap_thread = threading.Thread(target=self.pcap_dinleme_baslat, daemon=True)
        pcap_thread.start()

        time.sleep(0.5)
        gonderilen = 0
        for _ in range(paket_sayisi):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(b"SIBER_GOZ_PARS_BUG_2026_TEST_PACKET_DATA", (self.hedef_ip, self.hedef_port))
                s.close()
                gonderilen += 1
                time.sleep(0.003)  # 3ms hızlı patlama
            except Exception:
                pass

        print(f"🎯 [SİMÜLASYON TAMAMLANDI] Toplam {gonderilen} paket başarıyla fırlatıldı!")
        pcap_thread.join(timeout=3)

if __name__ == "__main__":
    sim = SaldiriSimulasyonu(hedef_ip="127.0.0.1")
    sim.icmp_flood_simule_et(paket_sayisi=150)
