import sys
import os
import subprocess

# Proje kök dizinini Python yoluna ekle
KOK_DIZIN = os.path.dirname(os.path.abspath(__file__))
if KOK_DIZIN not in sys.path:
    sys.path.insert(0, KOK_DIZIN)

def baslat():
    """SİBER GÖZ Karargâh Kontrol Panelini başlatır ve hataları görünür kılar."""
    panel_yolu = os.path.join(KOK_DIZIN, "gui", "control_panel.py")
    
    # Mevcut python yorumlayıcısını (sanal ortam dahil) kullan
    python_bin = sys.executable

    print(f"[BAŞLATICI] Siber Göz başlatılıyor... (Python: {python_bin})")
    
    try:
        # check=True kaldırıldı ki alt süreç çökerse traceback terminalde görülsün
        subprocess.run([python_bin, panel_yolu])
    except KeyboardInterrupt:
        print("\n[BİLGİ] Kullanıcı tarafından kapatıldı.")
    except Exception as e:
        print(f"[HATA] Beklenmeyen başlatma hatası: {str(e)}")

if __name__ == "__main__":
    baslat()
