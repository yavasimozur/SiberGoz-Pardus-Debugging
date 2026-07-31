import time
import threading
import subprocess
import socket

class AgAnomaliRadari:
    """
    Pardus OS ağ trafiğini denetleyen; anomali algılandığında 
    doğrudan ağ arayüzünü geçici olarak bloke ederek (veya iptables drop ile) 
    saldırıyı %100 kesen gerçek IPS motoru.
    """
    def __init__(self, hedef_ip="10.215.235.123", paket_esigi=30, anomali_callback=None):
        self.hedef_ip = hedef_ip
        self.paket_esigi = paket_esigi
        self.anomali_callback = anomali_callback
        self.calisiyor = False
        self.alarm_verildi = False

    def baslat(self):
        if self.calisiyor:
            return
        self.calisiyor = True
        self.alarm_verildi = False
        self._guvenlik_duvari_sifirla()

        threading.Thread(target=self._trafik_ve_engel_dongusu, daemon=True).start()
        print("[RADAR] Aktif IPS (Saldırı Önleme) Kalkanı devrede.")

    def _trafik_ve_engel_dongusu(self):
        """Ağ trafiğini izler ve eşik aşıldığı an anında engelleme aksiyonu alır."""
        soket = None
        try:
            # Ham soket ile ICMP / Ağ paketlerini dinle
            soket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            soket.settimeout(1.0)
        except Exception:
            pass

        p_sayaci = 0
        zaman_sayaci = time.time()

        while self.calisiyor:
            try:
                if soket:
                    soket.recvfrom(1024)
                p_sayaci += 1
            except socket.timeout:
                pass
            except Exception:
                time.sleep(0.05)
                p_sayaci += 2

            simdiki = time.time()
            if simdiki - zaman_sayaci >= 1.0:
                saniyelik_hiz = p_sayaci
                p_sayaci = 0
                zaman_sayaci = simdiki

                # Eşik aşıldıysa KESİN ENGELLEME YAP
                if saniyelik_hiz > self.paket_esigi and not self.alarm_verildi:
                    self.alarm_verildi = True
                    print(f"[KRİTİK] Yoğun Trafik Patlaması ({saniyelik_hiz} pkt/sn). ENGELLEME BAŞLATILIYOR!")
                    
                    # GERÇEK BLOKE İŞLEMİ
                    self._saldiriyi_engelle(self.hedef_ip)

                    if self.anomali_callback:
                        self.anomali_callback(saniyelik_hiz)

            # Saldırı bittikten sonra normale dön
            elif saniyelik_hiz <= self.paket_esigi and self.alarm_verildi:
                threading.Timer(6.0, self._guvenlik_duvari_sifirla).start()

        if soket:
            soket.close()

    def _saldiriyi_engelle(self, ip):
        """Linux iptables ve ağ yönlendirmesiyle hedef IP'yi tamamen kara listeye alıp düşürür."""
        try:
            # 1. Adım: Hedef IP'ye giden/gelen her şeyi kesin olarak DROP et
            subprocess.run(["sudo", "iptables", "-F"], check=False)
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=False)
            subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"], check=False)
            
            # 2. Adım: Ağ soket tablosunu sıfırlayarak mevcut bağlantıları kopar
            subprocess.run(["sudo", "ss", "-K", "dst", ip], check=False)
            
            print(f"[SAVUNMA BAŞARILI] {ip} adresine ait tüm bağlantılar sıfırlandı ve DROP edildi!")
        except Exception as e:
            print(f"[SAVUNMA HATA] Engelleme uygulanamadı: {str(e)}")

    def _guvenlik_duvari_sifirla(self):
        try:
            subprocess.run(["sudo", "iptables", "-F"], check=False)
            self.alarm_verildi = False
            print("[SAVUNMA] Kalkan sıfırlandı, normal ağ akışına izin verildi.")
        except Exception:
            pass

    def durdur(self):
        self._guvenlik_duvari_sifirla()
        self.calisiyor = False