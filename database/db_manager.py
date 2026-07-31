import sqlite3
import os
import time

# Kök dizin tespiti
KOK_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIZINI = os.path.join(KOK_DIZIN, "database")
DB_PATH = os.path.join(DB_DIZINI, "SiberGoz.db")
SCHEMA_PATH = os.path.join(DB_DIZINI, "schema.sql")

class DatabaseManager:
    def __init__(self):
        os.makedirs(DB_DIZINI, exist_ok=True)
        self._tablolari_hazirla()

    def _baglanti_al(self):
        return sqlite3.connect(DB_PATH, timeout=10)

    def _tablolari_hazirla(self):
        """Veritabanı tabloları yoksa schema.sql üzerinden otomatik oluşturur."""
        try:
            with self._baglanti_al() as conn:
                cursor = conn.cursor()
                if os.path.exists(SCHEMA_PATH):
                    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                        cursor.executescript(f.read())
                else:
                    # Schema dosyası yoksa varsayılan tabloları gömülü kur
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        zaman TEXT NOT NULL,
                        mesaj TEXT NOT NULL
                    );""")
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS engellenen_ipler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_adresi TEXT UNIQUE NOT NULL,
                        engelleme_zamani TEXT NOT NULL,
                        durum TEXT DEFAULT 'BLOKE'
                    );""")
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_teshisleri (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        zaman TEXT NOT NULL,
                        hedef_ip TEXT NOT NULL,
                        paket_sayisi INTEGER,
                        teshis_raporu TEXT NOT NULL
                    );""")
                conn.commit()
        except Exception as e:
            print(f"[DB HATA] Tablo hazırlama hatası: {str(e)}")

    def log_kaydet(self, mesaj):
        """Sistem logunu veritabanına ekler."""
        zaman = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._baglanti_al() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO system_logs (zaman, mesaj) VALUES (?, ?)", (zaman, mesaj))
                conn.commit()
        except Exception as e:
            print(f"[DB HATA] Log kaydı başarısız: {str(e)}")

    def ip_engelle_kaydet(self, ip_adresi):
        """Engellenen IP adresini kaydeder veya durumunu günceller."""
        zaman = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._baglanti_al() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO engellenen_ipler (ip_adresi, engelleme_zamani, durum) 
                    VALUES (?, ?, 'BLOKE')
                    ON CONFLICT(ip_adresi) DO UPDATE SET engelleme_zamani=?, durum='BLOKE'
                """, (ip_adresi, zaman, zaman))
                conn.commit()
        except Exception as e:
            print(f"[DB HATA] IP engelleme kaydı başarısız: {str(e)}")

    def ip_engel_kaldir_kaydet(self, ip_adresi):
        """IP adresinin engellendi durumunu pasife çeker."""
        try:
            with self._baglanti_al() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE engellenen_ipler SET durum='SERBEST' WHERE ip_adresi=?", (ip_adresi,))
                conn.commit()
        except Exception as e:
            print(f"[DB HATA] IP engel kaldırma kaydı başarısız: {str(e)}")

    def ai_teshis_kaydet(self, hedef_ip, paket_sayisi, teshis_raporu):
        """Yapay zekâ analiz raporunu veritabanına kaydeder."""
        zaman = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._baglanti_al() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_teshisleri (zaman, hedef_ip, paket_sayisi, teshis_raporu)
                    VALUES (?, ?, ?, ?)
                """, (zaman, hedef_ip, paket_sayisi, teshis_raporu))
                conn.commit()
        except Exception as e:
            print(f"[DB HATA] AI teşhis kaydı başarısız: {str(e)}")
