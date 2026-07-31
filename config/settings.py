import os
from dotenv import load_dotenv

# .env dosyasını zorla bul ve yükle
load_dotenv()

class Config:
    """Sistem genelinde kullanılacak statik ayarlar (Sınıf Özellikleri)"""
    
    ESP32_CAMERA_URL = os.getenv("ESP32_CAMERA_URL", "http://192.168.1.Y/capture")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database/SiberGoz.db")
    PCAP_SAVE_DIR = os.getenv("PCAP_SAVE_DIR", "logs/captures/")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/system.log")
    TARGET_THREAT_IP = os.getenv("TARGET_THREAT_IP", "192.168.1.Y")
