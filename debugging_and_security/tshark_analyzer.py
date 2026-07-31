import os
import sys
import subprocess

# Proje kök dizininin Python yoluna eklenmesi
KOK_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KOK_DIZIN not in sys.path:
    sys.path.insert(0, KOK_DIZIN)

try:
    from database.db_manager import DatabaseManager
except ImportError:
    DatabaseManager = None

class TsharkAdliBilisimAnalizor:
    """
    PCAP Döküm Analizörü ve Adli Bilişim (Forensics) İnceleme Modülü.
    Yakalnan .pcap dosyalarını tcpdump/tshark ile çözümler ve veritabanına işler.
    """
    def __init__(self):
        self.pcap_dizini = os.path.join(KOK_DIZIN, "logs", "lcaptures")
        self.db = DatabaseManager() if DatabaseManager else None

    def pcap_analiz_et(self, pcap_dosyasi=None):
        if not pcap_dosyasi:
            pcap_dosyasi = os.path.join(self.pcap_dizini, "saldiri_kayit.pcap")

        if not os.path.exists(pcap_dosyasi):
            print(f"⚠️ [ANALİZ HATA] PCAP dosyası bulunamadı: {pcap_dosyasi}")
            return None

        print(f"🔍 [ADLİ BİLİŞİM] {pcap_dosyasi} dosyası inceleniyor...")

        try:
            cmd = ["tcpdump", "-r", pcap_dosyasi, "-n"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            satirlar = [s for s in result.stdout.strip().split("\n") if s]
            
            paket_sayisi = len(satirlar)
            ornek_paketler = "\n".join(satirlar[:3]) if satirlar else "Paket detayı ayrıştırılamadı."
            
            rapor = (
                f"=== SİBER GÖZ ADLİ BİLİŞİM PCAP ANALİZ RAPORU ===\n"
                f"📁 İncelenen Dosya: {os.path.basename(pcap_dosyasi)}\n"
                f"📊 Yakalanan Toplam Paket: {paket_sayisi}\n"
                f"📝 İlk Paket Örnekleri:\n{ornek_paketler}\n"
                f"=================================================="
            )
            print(rapor)

            # SQLite Veritabanına Adli Kaydı İşle
            if self.db:
                self.db.log_kaydet(f"[PCAP ANALİZ] {os.path.basename(pcap_dosyasi)} incelendi. Toplam paket: {paket_sayisi}")
                self.db.ai_teshis_kaydet(
                    hedef_ip="127.0.0.1", 
                    paket_sayisi=paket_sayisi, 
                    teshis_raporu=f"Adli Bilişim PCAP İncelemesi: {paket_sayisi} paketlik anomali dökümü doğrulandı."
                )
                print("💾 [DB] Adli bilişim sonuçları SQLite veritabanına kaydedildi.")

            return rapor

        except Exception as e:
            print(f"❌ [ANALİZ HATA] Adli inceleme sırasında hata oluştu: {str(e)}")
            return None

if __name__ == "__main__":
    analizor = TsharkAdliBilisimAnalizor()
    analizor.pcap_analiz_et()
