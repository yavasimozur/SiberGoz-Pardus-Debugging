import cv2
import numpy as np
import urllib.request
import os

class VisionEngine:
    def __init__(self):
        # Hedef adresi otomatik bul
        self.camera_url = "http://10.215.235.123/capture"
        # BMP dosyası büyük olduğu için ağ gecikmelerine karşı sabrı (timeout) 5 saniyeye çıkardık
        self.timeout = 5.0  
        
        # Watchdog Zırhı (Bağlantı koptuğunda sistemi çökmekten kurtaran siyah ekran)
        self.black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(self.black_frame, "SISTEM UYARISI: GORUNTU KOPTU", (80, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(self.black_frame, "WATCHDOG AKTIF - YENIDEN BAGLANILIYOR", (40, 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def _load_url_from_env(self):
        """ .env dosyasını bularak ESP32 IP adresini gizlice okur """
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("ESP32_CAMERA_URL="):
                        return line.strip().split("=")[1]
        return None

    def get_frame(self):
        if not self.camera_url:
            print("[HATA] Hedef IP bulunamadi. Lütfen config/.env dosyasini kontrol edin.")
            return self.black_frame

        try:
            # İstihbarat Logu: Terminal ekranına nereye bağlandığını yazacak
            print(f"[HEDEF KONTROL] Siber Goz su adrese baglaniliyor: {self.camera_url}")
            
            # Kameradan (ESP32) gelen BMP/JPEG verisini çek
            req = urllib.request.urlopen(self.camera_url, timeout=self.timeout)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            
            # Ham byte verisini OpenCV'nin anlayacağı bir resme çevir
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                return frame
            else:
                return self.black_frame
                
        except Exception as e:
            # Görüntü gelmezse siyah zırhı (Watchdog) ekrana bas
            print(f"[WATCHDOG TETIKLENDI] Hata detayi: {e}")
            return self.black_frame