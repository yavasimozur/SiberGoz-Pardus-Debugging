import customtkinter as ctk
import time
import threading
import subprocess
import sys
import os

# Proje kök dizinini Python yoluna ekle (core modülünü bulabilmesi için)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.netwok_radar import AgAnomaliRadari
except ImportError:
    AgAnomaliRadari = None

# Savunma Sanayii Karanlık Tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SiberGozKarargah(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.kamera_process = None
        self.otonom_savunma_aktif = True

        # Pencere Ayarları
        self.title("SİBER GÖZ — Savunma & Kontrol Karargâhı // PARDUS OS")
        self.geometry("760x540")
        self.resizable(False, False)

        # -------------------------------------------------------------
        # 1. ÜST BAŞLIK VE RADAR BAR
        # -------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color="#12161B")
        self.header_frame.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🎯 SİBER GÖZ // OTONOM İZLEME VE SİBER SAVUNMA PANELİ", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(12, 4))

        self.radar_bar = ctk.CTkProgressBar(self.header_frame, width=480, height=6, progress_color="#00E676")
        self.radar_bar.pack(pady=(0, 10))
        self.radar_bar.set(0.15)

        # -------------------------------------------------------------
        # 2. DURUM VE TELEMETRİ KARTI (3 ROZETLİ)
        # -------------------------------------------------------------
        self.status_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#1C222A")
        self.status_card.pack(padx=20, pady=10, fill="x")

        self.ip_badge = ctk.CTkLabel(
            self.status_card, text=" HEDEF: 192.168.1.45 (ESP32) ", 
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1F4E3D", text_color="#00FF88", corner_radius=6
        )
        self.ip_badge.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.radar_badge = ctk.CTkLabel(
            self.status_card, text=" ● AĞ RADARI: KALKAN AKTİF ", 
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#10364A", text_color="#38BDF8", corner_radius=6
        )
        self.radar_badge.grid(row=0, column=1, padx=10, pady=10)

        self.watchdog_badge = ctk.CTkLabel(
            self.status_card, text=" ● WATCHDOG: NÖBETTE ", 
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1F4E3D", text_color="#00FF88", corner_radius=6
        )
        self.watchdog_badge.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        self.status_card.grid_columnconfigure(0, weight=1)
        self.status_card.grid_columnconfigure(1, weight=1)
        self.status_card.grid_columnconfigure(2, weight=1)

        # -------------------------------------------------------------
        # 3. KONTROL KARTLARI (SOL: YAYIN & MOD | SAĞ: TEHDİT & SIFIRLA)
        # -------------------------------------------------------------
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(padx=20, pady=5, fill="x")

        # --- SOL KART: KAMERA KONTROLÜ VE ÇALIŞMA MODU ---
        self.op_card = ctk.CTkFrame(self.cards_frame, width=350, height=125, corner_radius=8, fg_color="#1C222A")
        self.op_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.btn_kamera = ctk.CTkButton(
            self.op_card, 
            text="▶  CANLI KAMERAYI BAŞLAT", 
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            fg_color="#00695C", hover_color="#004D40",
            command=self.kamera_ac_kapat_toggle
        )
        self.btn_kamera.pack(padx=15, pady=(15, 8), fill="x")

        self.mod_selector = ctk.CTkSegmentedButton(
            self.op_card, 
            values=["MANUEL MOD", "OTONOM SAVUNMA"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.mod_degisti
        )
        self.mod_selector.pack(padx=15, pady=(0, 15), fill="x")
        self.mod_selector.set("OTONOM SAVUNMA")

        # --- SAĞ KART: SİBER SALDIRI & WATCHDOG TESTİ ---
        self.sim_card = ctk.CTkFrame(self.cards_frame, width=350, height=125, corner_radius=8, fg_color="#1C222A")
        self.sim_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self.btn_saldiri = ctk.CTkButton(
            self.sim_card, 
            text="⚡  SALDIRI (DoS) TETİKLE", 
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            fg_color="#C62828", hover_color="#8E0000",
            command=self.saldiri_algilandi_eventi
        )
        self.btn_saldiri.pack(padx=15, pady=(15, 8), fill="x")

        self.btn_clear = ctk.CTkButton(
            self.sim_card, 
            text="↻  SİSTEMİ VE LOGLARI SIFIRLA", 
            font=ctk.CTkFont(size=12, weight="bold"),
            height=30,
            fg_color="#374151", hover_color="#1F2937",
            command=self.sistemi_sifirla
        )
        self.btn_clear.pack(padx=15, pady=(0, 15), fill="x")

        # -------------------------------------------------------------
        # 4. SİSTEM LOG EKRANI
        # -------------------------------------------------------------
        self.log_label = ctk.CTkLabel(self, text="SİSTEM TELEMETRİ VE HATA AYIKLAMA LOGLARI:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        self.log_label.pack(padx=20, pady=(10, 4), anchor="w")

        self.log_box = ctk.CTkTextbox(self, width=720, height=180, font=ctk.CTkFont(family="Monospace", size=11), fg_color="#101418")
        self.log_box.pack(padx=20, pady=(0, 15))
        self.log_box.configure(state="disabled")

        self.log_ekle("[SİSTEM] Karargâh paneli hazır. Mod: OTONOM SAVUNMA.")

        # -------------------------------------------------------------
        # 5. GERÇEK ZAMANLI AĞ ANOMALİ RADARINI BAŞLAT
        # -------------------------------------------------------------
        if AgAnomaliRadari:
            self.radar_motoru = AgAnomaliRadari(
                hedef_ip="192.168.1.45", 
                paket_esigi=25, 
                anomali_callback=self.gercek_saldiri_algilandi
            )
            self.radar_motoru.baslat()
            self.log_ekle("[GÜVENLİK] Ağ kalkanı ve engelleyici motor devrede.")
        else:
            self.radar_motoru = None

    def log_ekle(self, mesaj):
        zaman = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{zaman}] {mesaj}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def mod_degisti(self, secilen_mod):
        self.otonom_savunma_aktif = (secilen_mod == "OTONOM SAVUNMA")
        self.log_ekle(f"[MOD] Çalışma modu güncellendi -> {secilen_mod}")

    def kamera_ac_kapat_toggle(self):
        if self.kamera_process and self.kamera_process.poll() is None:
            try:
                self.kamera_process.terminate()
                self.kamera_process = None
                self.btn_kamera.configure(text="▶  CANLI KAMERAYI BAŞLAT", fg_color="#00695C", hover_color="#004D40")
                self.log_ekle("[GÖRÜNTÜ] Kamera penceresi kullanıcı emriyle kapatıldı.")
            except Exception as e:
                self.log_ekle(f"[HATA] Kamera kapatılamadı: {str(e)}")
            return

        ana_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kamera_dosyasi = os.path.join(ana_dizin, "gui", "camera_terminal.py")

        try:
            self.kamera_process = subprocess.Popen([sys.executable, kamera_dosyasi])
            self.btn_kamera.configure(text="■  CANLI KAMERAYI DURDUR", fg_color="#D84315", hover_color="#BF360C")
            self.log_ekle("[GÖRÜNTÜ] Canlı izleme ekranı başarıyla başlatıldı.")
        except Exception as e:
            self.log_ekle(f"[HATA] Kamera açılamadı: {str(e)}")

    def saldiri_algilandi_eventi(self):
        self.watchdog_badge.configure(text=" ● SALDIRI ENGELLENDİ! ", fg_color="#5C1D24", text_color="#FF5252")
        self.radar_badge.configure(text=" ● KALKAN: AKIŞ BLOKE ", fg_color="#5C1D24", text_color="#FF5252")
        self.radar_bar.configure(progress_color="#FF5252")
        self.radar_bar.set(0.95)

        self.log_ekle("[ALARM] DoS anomalisi algılandı! Trafik engellendi (DROP).")
        if self.otonom_savunma_aktif:
            self.log_ekle("[OTONOM] Delil kaydı için kamera otomatik tetikleniyor...")
            threading.Timer(1.0, self.kamera_ac_kapat_toggle).start()
        
        threading.Timer(5.0, self.sistemi_sifirla).start()

    def gercek_saldiri_algilandi(self, paket_sayisi):
        self.watchdog_badge.configure(text=" ● SALDIRI ENGELLENDİ (DROP)! ", fg_color="#5C1D24", text_color="#FF5252")
        self.radar_badge.configure(text=" ● KALKAN AKTİF: AKIŞ BLOKE ", fg_color="#5C1D24", text_color="#FF5252")
        self.radar_bar.configure(progress_color="#FF5252")
        self.radar_bar.set(1.0)

        self.log_ekle(f"[KRİTİK ALARM] AĞDA SALDIRI TESPİT EDİLDİ -> {paket_sayisi} birim yük!")
        self.log_ekle("[GÜVENLİK DUVARI] Gelen zararlı akış Pardus çekirdeği tarafından engellendi.")
        self.log_ekle("[OTONOM] 2. Terminal canlı delil kaydı için otomatik başlatılıyor...")

        if self.otonom_savunma_aktif:
            threading.Timer(0.5, self.kamera_ac_kapat_toggle).start()
        
        threading.Timer(8.0, self.sistemi_sifirla).start()

    def sistemi_sifirla(self):
        self.watchdog_badge.configure(text=" ● WATCHDOG: NÖBETTE ", fg_color="#1F4E3D", text_color="#00FF88")
        self.radar_badge.configure(text=" ● AĞ RADARI: KALKAN AKTİF ", fg_color="#10364A", text_color="#38BDF8")
        self.radar_bar.configure(progress_color="#00E676")
        self.radar_bar.set(0.15)
        
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log_ekle("[SİSTEM] Kalkan ve loglar sıfırlandı. Watchdog nöbette.")

if __name__ == "__main__":
    app = SiberGozKarargah()
    app.mainloop()