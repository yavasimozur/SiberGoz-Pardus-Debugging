import cv2
import time
import numpy as np
import urllib.request
import threading

# HEDEF AYARLARI
ESP32_IP = ""
CAMERA_URL = f"http://{ESP32_IP}/capture"
PENCERE_ADI = "SİBER GÖZ // CANLI İZLEME TERMINALİ (PARDUS)"

class AsenkronKameraOkuyucu:
    """ESP32 gecikmelerine toleranslı, arayüzü kilitlemeyen asenkron kare okuyucu."""
    def __init__(self, url):
        self.url = url
        self.son_kare = None
        self.kare_hazir = False
        self.calisiyor = True
        self.hata_sayaci = 0
        self.fps = 0
        self.onceki_zaman = time.time()

        # Arka plan iş parçacığını (Thread) başlat
        self.thread = threading.Thread(target=self._a_diger_kareleri_cek, daemon=True)
        self.thread.start()

    def _a_diger_kareleri_cek(self):
        while self.calisiyor:
            try:
                # ESP32'nin fotoğrafı hazırlaması için ağ zaman aşımını 3.0 saniye yaptık
                req = urllib.request.urlopen(self.url, timeout=3.0)
                img_array = np.array(bytearray(req.read()), dtype=np.uint8)
                frame = cv2.imdecode(img_array, -1)
                
                if frame is not None:
                    self.son_kare = frame
                    self.kare_hazir = True
                    self.hata_sayaci = 0
                    
                    # Ağ FPS hesaplama
                    simdiki = time.time()
                    fark = simdiki - self.onceki_zaman
                    if fark > 0:
                        self.fps = int(1 / fark)
                    self.onceki_zaman = simdiki
            except Exception:
                self.hata_sayaci += 1
                time.sleep(0.1)

            time.sleep(0.01)

    def kopyala_son_kare(self):
        return self.kare_hazir, self.son_kare, self.fps, self.hata_sayaci

    def durdur(self):
        self.calisiyor = False


def sade_hud_ciz(frame, fps, kaynak="ESP32"):
    """Görüntüyü kapatmayan, sade ve net üst/alt bilgi barları çizer."""
    h, w = frame.shape[:2]

    # Üst İnce Durum Barı
    cv2.rectangle(frame, (0, 0), (w, 30), (15, 18, 22), -1)
    cv2.putText(frame, "SİBER GÖZ  |  OTONOM SAVUNMA // KAYIT AKTİF", (15, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 136), 1)

    cv2.circle(frame, (w - 55, 15), 5, (0, 0, 255), -1)
    cv2.putText(frame, "REC", (w - 43, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)

    # Alt İnce Telemetri Barı
    cv2.rectangle(frame, (0, h - 26), (w, h), (15, 18, 22), -1)
    zaman = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, f"KAYNAK: {kaynak}   |   AĞ FPS: {fps}   |   TARIH: {zaman}", (15, h - 8), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 210, 220), 1)

    return frame


def simule_bekleme_karesi():
    """Kamera ağda yoksa veya bağlanıyorsa gösterilecek sade bekleme ekranı."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, "KAMERA BAGLANTISI BEKLENIYOR...", (170, 235), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 255), 1)
    cv2.putText(frame, "WATCHDOG AĞI KONTROL EDIYOR", (185, 265), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 150, 160), 1)
    return frame


def kamerayi_baslat():
    print("[KAMERA] Sade ve toleranslı asenkron motor başlatıldı...")
    okuyucu = AsenkronKameraOkuyucu(CAMERA_URL)
    son_log_zamani = 0

    while True:
        kare_hazir, frame, ağ_fps, hatalar = okuyucu.kopyala_son_kare()
        kaynak_adi = f"ESP32 ({ESP32_IP})"

        # Üst üste 4 kez başarısız ağ isteği olursa bekleme karesine geç
        if not kare_hazir or frame is None or hatalar >= 4:
            anlik = time.time()
            if anlik - son_log_zamani > 4.0:
                print("[WATCHDOG] ESP32 sinyali bekleniyor...")
                son_log_zamani = anlik
                
            frame = simule_bekleme_karesi()
            kaynak_adi = "BEKLEMEDE"
            ağ_fps = 0

        islenmis_frame = sade_hud_ciz(frame, fps=ağ_fps, kaynak=kaynak_adi)
        cv2.imshow(PENCERE_ADI, islenmis_frame)

        # 10ms bekleme ile UI döngüsünün akıcı olmasını sağla
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == 27:
            break

        # Sağ üstteki Çarpı (X) butonuna basılırsa döngüyü temizce kır
        try:
            if cv2.getWindowProperty(PENCERE_ADI, cv2.WND_PROP_VISIBLE) < 1:
                break
        except Exception:
            break

    okuyucu.durdur()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    kamerayi_baslat()
