import sqlite3
import os
import datetime
from config.settings import Config

class DBManager:
    _instance = None

    def __new__(cls):
        # Singleton Deseni: Sistemin her yerinde aynı veritabanı bağlantısı kullanılır.
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        # Eğer database klasörü yoksa fiziksel olarak oluştur
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        # check_same_thread=False ile Multiprocessing (Arayüz) çökmeleri engellenir
        self.conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def setup_database(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            self.cursor.executescript(schema_script)
            self.conn.commit()
        except Exception as e:
            print(f"[DB KRİTİK] Şema dosyası okunamadı veya çalıştırılamadı: {e}")
            raise e

    def log_security_event(self, event_type: str, source_ip: str, action_taken: str) -> bool:
        """Saldırı ve sistem olaylarını kaydeder."""
        try:
            # Zamanı sistemin kendisinden alıp SQL'e zorla basıyoruz
            anlik_zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO security_logs (timestamp, event_type, source_ip, action_taken) VALUES (?, ?, ?, ?)",
                (anlik_zaman, event_type, source_ip, action_taken)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB HATA] Güvenlik logu eklenemedi: {e}")
            return False
        
    def add_device(self, ip_address: str, device_type: str, status: str) -> bool:
        """Ağa bağlanan yeni cihazları (ESP32, iPhone) kaydeder."""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO devices (ip_address, device_type, status, last_seen) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (ip_address, device_type, status)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB HATA] Cihaz kaydedilemedi: {e}")
            return False