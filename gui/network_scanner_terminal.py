import customtkinter as ctk
import time
import threading
import subprocess
import socket
import sys
import os

# Proje kök dizininin Python yoluna eklenmesi
GUI_DIZINI = os.path.dirname(os.path.abspath(__file__))
KOK_DIZIN = os.path.dirname(GUI_DIZINI)
if KOK_DIZIN not in sys.path:
    sys.path.insert(0, KOK_DIZIN)

try:
    from database.db_manager import DatabaseManager
except ImportError:
    DatabaseManager = None

# Arayüz Tema Yapılandırması (Pardus Dark Theme)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AgTarayiciKarargah(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Yapılandırması
        self.title("SİBER GÖZ — Canlı Ağ İstemci & Engelleme Paneli // 3. TERMINAL")
        self.geometry("680x540")
        self.resizable(False, False)

        self.db = DatabaseManager() if DatabaseManager else None
        self.engellenen_ipler = set()
        self.yerel_ip = self._yerel_ip_al()
        self.ag_bloğu = ".".join(self.yerel_ip.split(".")[:-1]) + "." if self.yerel_ip else "192.168.1."

        # -------------------------------------------------------------
        # 1. ÜST BAŞLIK & TELEMETRİ
        # -------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#12161B")
        self.header_frame.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=f"📡 CANLI Wİ-Fİ İSTEMCİ İZLEME PANELİ (AĞ: {self.ag_bloğu}0/24)", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.title_label.pack(pady=12)

        # -------------------------------------------------------------
        # 2. AKTİF İSTEMCİ LİSTESİ
        # -------------------------------------------------------------
        self.list_frame = ctk.CTkScrollableFrame(self, width=640, height=230, label_text="Ağdaki Aktif Cihazlar (Wi-Fi / Ethernet)")
        self.list_frame.pack(padx=20, pady=10)

        # -------------------------------------------------------------
        # 3. İP ENGELLEME KART
        # -------------------------------------------------------------
        self.control_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#1C222A")
        self.control_card.pack(padx=20, pady=5, fill="x")

        self.ip_entry = ctk.CTkEntry(self.control_card, placeholder_text="Örn: 192.168.1.50", width=190)
        self.ip_entry.grid(row=0, column=0, padx=10, pady=10)

        self.btn_block = ctk.CTkButton(
            self.control_card, 
            text="🚫 ŞÜPHELİ IP BLOKE ET", 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#C62828", hover_color="#8E0000",
            command=self.ip_engelle
        )
        self.btn_block.grid(row=0, column=1, padx=5, pady=10)

        self.btn_unblock = ctk.CTkButton(
            self.control_card, 
            text="✅ ENGELİ KALDIR", 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#00695C", hover_color="#004D40",
            command=self.ip_engel_kaldir
        )
        self.btn_unblock.grid(row=0, column=2, padx=5, pady=10)

        self.control_card.grid_columnconfigure(0, weight=1)
        self.control_card.grid_columnconfigure(1, weight=1)
        self.control_card.grid_columnconfigure(2, weight=1)

        # -------------------------------------------------------------
        # 4. TELEMETRİ LOGLARI
        # -------------------------------------------------------------
        self.log_box = ctk.CTkTextbox(self, width=640, height=130, font=ctk.CTkFont(family="Monospace", size=10), fg_color="#101418")
        self.log_box.pack(padx=20, pady=(5, 15))
        self.log_box.configure(state="disabled")

        self.log_ekle(f"[AĞ TARAYICI] Yerel IP: {self.yerel_ip} | Wi-Fi aktif cihaz süpürme motoru ve SQLite DB aktif.")

        # Arka planda aktif cihaz keşif ve ARP tarama thread'leri
        threading.Thread(target=self._aktif_cihaz_supurucu_loop, daemon=True).start()
        threading.Thread(target=self._ag_tarama_dongusu, daemon=True).start()

    def _yerel_ip_al(self):
        """Sistemin aktif yerel IP adresini tespit eder."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "192.168.1.100"

    def log_ekle(self, mesaj):
        """Ağ tarayıcı loglarını ekrana, logs/system.log dosyasına ve SQLite veritabanına yazar."""
        zaman = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_log = f"[{zaman}] {mesaj}"

        # 1. Arayüze Ekle
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{formatted_log}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

        # 2. logs/system.log Dosyasına Yaz
        try:
            log_dizini = os.path.join(KOK_DIZIN, "logs")
            os.makedirs(log_dizini, exist_ok=True)
            log_dosyasi = os.path.join(log_dizini, "system.log")
            with open(log_dosyasi, "a", encoding="utf-8") as f:
                f.write(f"{formatted_log}\n")
        except Exception:
            pass

        # 3. SQLite Veritabanına (SiberGoz.db) Kaydet
        if self.db:
            try:
                self.db.log_kaydet(mesaj)
            except Exception:
                pass

    def _ping_ip(self, ip):
        """Milisaniyelik hızlı ping gönderimiyle IP'nin aktifliğini saptar."""
        try:
            subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _aktif_cihaz_supurucu_loop(self):
        """Ağdaki tüm 254 IP adresine arka planda hızlı ping süpürmesi yapar."""
        while True:
            threads = []
            for i in range(1, 255):
                target_ip = f"{self.ag_bloğu}{i}"
                t = threading.Thread(target=self._ping_ip, args=(target_ip,), daemon=True)
                threads.append(t)
                t.start()
                if len(threads) >= 50:
                    for th in threads:
                        th.join()
                    threads = []
            time.sleep(12)

    def _ag_tarama_dongusu(self):
        """Genişletilmiş ARP tablosunu okur ve arayüzü günceller."""
        while True:
            cihazlar = self._aktif_cihazlari_al()
            self._listeyi_guncelle(cihazlar)
            time.sleep(3)

    def _aktif_cihazlari_al(self):
        """Pardus /proc/net/arp tablosundan cihazları okur."""
        cihazlar = []
        try:
            with open("/proc/net/arp", "r") as f:
                satirlar = f.readlines()[1:]
                for satir in satirlar:
                    parcalar = satir.split()
                    if len(parcalar) >= 6 and parcalar[3] != "00:00:00:00:00:00":
                        ip = parcalar[0]
                        mac = parcalar[3]
                        cihazlar.append((ip, mac))
        except Exception:
            pass
        return cihazlar

    def _listeyi_guncelle(self, cihazlar):
        """Arayüzdeki cihaz listesini günceller."""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not cihazlar:
            lbl = ctk.CTkLabel(self.list_frame, text="Ağdaki Wi-Fi cihazları süpürülüyor...")
            lbl.pack(pady=10)
            return

        for ip, mac in cihazlar:
            is_self = " (BU PARDUS)" if ip == self.yerel_ip else ""
            durum = " [BLOKE]" if ip in self.engellenen_ipler else " [AKTİF]"
            renk = "#FF5252" if ip in self.engellenen_ipler else ("#38BDF8" if is_self else "#00FF88")
            
            row = ctk.CTkFrame(self.list_frame, fg_color="#1C222A")
            row.pack(fill="x", pady=2, padx=5)

            lbl_info = ctk.CTkLabel(
                row, 
                text=f"IP: {ip:<15} | MAC: {mac}{is_self}{durum}", 
                text_color=renk, 
                font=ctk.CTkFont(family="Monospace", size=10, weight="bold")
            )
            lbl_info.pack(side="left", padx=10, pady=5)

            if ip != self.yerel_ip:
                btn_sec = ctk.CTkButton(
                    row, text="Seç", width=45, height=22, 
                    fg_color="#374151", hover_color="#1F2937",
                    command=lambda target_ip=ip: self._ip_sec(target_ip)
                )
                btn_sec.pack(side="right", padx=5)

    def _ip_sec(self, ip):
        """Seçilen IP adresini metin kutusuna aktarır."""
        self.ip_entry.delete(0, "end")
        self.ip_entry.insert(0, ip)

    def ip_engelle(self):
        """Seçilen IP adresini Linux iptables ile engeller ve DB'ye kaydeder."""
        ip = self.ip_entry.get().strip()
        if not ip:
            return
        try:
            subprocess.run(["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"], check=False)
            subprocess.run(["sudo", "iptables", "-I", "OUTPUT", "-d", ip, "-j", "DROP"], check=False)
            self.engellenen_ipler.add(ip)
            
            # Veritabanına engelleme kaydı ekle
            if self.db:
                self.db.ip_engelle_kaydet(ip)

            self.log_ekle(f"[SAVUNMA DUVARI] {ip} adresi iptables ile tamamen BLOKE EDİLDİ!")
            self.ip_entry.delete(0, "end")
        except Exception as e:
            self.log_ekle(f"[HATA] Engelleme uygulanamadı: {str(e)}")

    def ip_engel_kaldir(self):
        """Engellenen IP üzerindeki iptables kuralını kaldırır ve DB'de günceller."""
        ip = self.ip_entry.get().strip()
        if not ip:
            return
        try:
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=False)
            subprocess.run(["sudo", "iptables", "-D", "OUTPUT", "-d", ip, "-j", "DROP"], check=False)
            if ip in self.engellenen_ipler:
                self.engellenen_ipler.remove(ip)
            
            # Veritabanında engeli kaldır olarak güncelle
            if self.db:
                self.db.ip_engel_kaldir_kaydet(ip)

            self.log_ekle(f"[SAVUNMA DUVARI] {ip} üzerindeki engelleme kaldırıldı.")
            self.ip_entry.delete(0, "end")
        except Exception as e:
            self.log_ekle(f"[HATA] Engel kaldırılamadı: {str(e)}")

if __name__ == "__main__":
    app = AgTarayiciKarargah()
    app.mainloop()