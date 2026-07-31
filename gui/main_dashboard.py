import customtkinter as ctk
import subprocess
import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DBManager
from debugging_and_security.nmap_scanner import NmapScanner
from debugging_and_security.ufw_manager import UFWManager
from debugging_and_security.system_debugger import SystemDebugger

# Askeri karanlık tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class AnaKarargah(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Siber Göz - Ana Karargah (Pardus)")
        self.geometry("900x600")
        
        self.db = DBManager()
        self.nmap = NmapScanner()
        self.ufw = UFWManager()
        self.debugger = SystemDebugger()
        
        # Izgara (Grid) Yapılandırması
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sol Menü Paneli
        self.menu_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.menu_frame, text="SİBER GÖZ\nKARARGAHI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Buton 1: Bağımsız Kamera Terminali
        self.btn_kamera = ctk.CTkButton(self.menu_frame, text="👁️ İkinci Terminali Aç", command=self.kamerayi_ac, fg_color="#8B0000", hover_color="#5C0000")
        self.btn_kamera.grid(row=1, column=0, padx=20, pady=10)
        
        # Buton 2: Nmap Ağ Taraması
        self.btn_nmap = ctk.CTkButton(self.menu_frame, text="📡 Sistemi Tara (Nmap)", command=self.nmap_tara_thread)
        self.btn_nmap.grid(row=2, column=0, padx=20, pady=10)

        # Buton 3: Pardus Hata Ayıklama (Journalctl)
        self.btn_debug = ctk.CTkButton(self.menu_frame, text="⚙️ Pardus Hata Ayıklama", command=self.sistem_hatalarini_getir, fg_color="#B8860B", hover_color="#8B6508")
        self.btn_debug.grid(row=3, column=0, padx=20, pady=10)

        # Sağ Alan: Akış ve Raporlama (Log) Ekranı
        self.log_ekrani = ctk.CTkTextbox(self, font=("Consolas", 14), text_color="#00FF00", fg_color="black")
        self.log_ekrani.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.log_yaz("SİSTEM BAŞLATILDI. UFW, Nmap ve Veritabanı motorları devrede. Emir bekleniyor...")
        
    def log_yaz(self, mesaj):
        """Ekrana yeşil terminal yazısı basar ve otomatik aşağı kaydırır."""
        self.log_ekrani.insert("end", f"[SİSTEM] {mesaj}\n\n")
        self.log_ekrani.see("end")
        
    def kamerayi_ac(self):
        self.log_yaz("Kamera terminali başlatılıyor... Ana ekrandan bağımsız (Multiprocess) ayrıldı.")
        kamera_script = os.path.join(os.path.dirname(__file__), "camera_terminal.py")
        # Subprocess ile Popen kullanarak programı bağımsız bir işlem olarak fırlatıyoruz (UI donmaz)
        subprocess.Popen([sys.executable, kamera_script])
        self.db.log_security_event("TERMİNAL_TETİK", "localhost", "İkinci Kamera Terminali Açıldı.")
        
    def nmap_tara_thread(self):
        """Nmap taraması 3-4 saniye sürer. Arayüzün donmaması için arka plana (Thread) alıyoruz."""
        self.log_yaz("Nmap Zafiyet Taraması Başladı (127.0.0.1)... Hedef analiz ediliyor.")
        
        def tarama_gorevi():
            sonuc = self.nmap.scan_target("127.0.0.1")
            self.log_yaz(f"Tarama Tamamlandı!\nSonuç Raporu: {sonuc}")
            self.db.log_security_event("AĞ_TARAMA", "127.0.0.1", "Sistem taraması yapıldı.")
            
        # Daemon Thread: Ana program kapanırsa bu da arkada ölür
        threading.Thread(target=tarama_gorevi, daemon=True).start()

    def sistem_hatalarini_getir(self):
        """Pardus çekirdek loglarını okuyup yeşil ekrana basar."""
        self.log_yaz("Pardus Sistem Logları (Journalctl) taranıyor... Kritik hatalar aranıyor.")
        hatalar = self.debugger.get_recent_errors(satir_sayisi=15)
        self.log_yaz(f"PARDUS ÇEKİRDEK RAPORU:\n{hatalar}")
        self.db.log_security_event("HATA_AYIKLAMA", "localhost", "Sistem logları kontrol edildi.")
        

def baslat():
    app = AnaKarargah()
    app.mainloop()