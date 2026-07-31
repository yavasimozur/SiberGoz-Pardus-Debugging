import os
import sys
import traceback
from core.vision_engine import VisionEngine

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DBManager
from debugging_and_security.ufw_manager import UFWManager
from debugging_and_security.nmap_scanner import NmapScanner
from debugging_and_security.tshark_analyzer import TsharkAnalyzer


def yetki_kontrol():
    if os.geteuid() != 0:
        print("\n[KRİTİK HATA] Bu sistem Yönetici (Root) yetkisi gerektirir.")
        sys.exit(1)

# (Üstteki importlar ve yetki_kontrol fonksiyonu aynı kalsın)
from gui.main_dashboard import baslat as gui_baslat

def karargahi_baslat():
    print("[BAŞARILI] Tüm motorlar devrede. Arayüz (GUI) başlatılıyor...")
    # Siyah terminal testlerini kaldırıyoruz, doğrudan arayüzü çağırıyoruz!
    gui_baslat()

if __name__ == "__main__":
    yetki_kontrol()
    karargahi_baslat()
