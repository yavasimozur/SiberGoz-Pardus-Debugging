# 🎯 SİBER GÖZ — Pardus OS Otonom Ağ Savunma, Yapay Zekâ Teşhis ve Adli Bilişim Platformu

Bu proje, **TEKNOFEST 2026 Pardus Hata Yakalama ve Geliştirme (Geliştirme Kategorisi)** yarışması kapsamında, Pardus OS ekosistemi ve kritik otonom izleme/kamera altyapıları için geliştirilmiştir.

---

## 📌 Proje Özeti
SİBER GÖZ, Pardus işletim sistemi üzerinde çalışan sistemleri ve izleme altyapılarını ağ saldırılarına (DoS / ICMP Flood / SYN Flood) karşı koruyan, milisaniyelik zaman diliminde Linux çekirdeği seviyesinde (`iptables`) müdahale eden **IDS/IPS (Saldırı Tespit ve Önleme)**, **SQLite veritabanı kayıtlı adli bilişim** ve **otonom çoklu terminal mimarisine** sahip yeni nesil bir siber savunma platformudur.

---

## ⚡ Öne Çıkan Özellikler ve 3'lü Otonom Terminal Mimarisi

* **1. Terminal (Ana Karargâh Kontrol Paneli - `gui/control_panel.py`):**
  * Tüm sistem telemetrisini, ağ kalkanı durumunu, anomali loglarını ve AI teşhislerini canlı olarak görselleştirir.
  * Otonom Savunma ve Manuel müdahale modları arasında kesintisiz geçiş olanağı tanır.

* **2. Terminal (Otonom Delil Kayıt Ekranı - `gui/camera_terminal.py`):**
  * Ağ anomalisi veya saldırı algılandığı an ana paneli meşgul etmeden **otonom olarak 2. bağımsız terminal penceresini açar**.
  * Güvenlik kameralarından canlı yayın alarak adli bilişim (forensics) için delil toplama sürecini başlatır.

* **3. Terminal (Canlı Wi-Fi Ağ İstemci & IP Engelleme Paneli - `gui/network_scanner_terminal.py`):**
  * Arka planda çalışan alt ağ süpürücüsü (*subnet ping sweeper*) ile ağdaki **tüm Wi-Fi ve Ethernet istemcilerini (IP & MAC)** canlı olarak tespit eder.
  * Şüpheli görülen IP adreslerini **tek tıkla Linux `iptables DROP` kuralı ile bloke etme** ve engelleri kaldırma olanağı sağlar.
  * Engelleme geçmişini ve durumlarını veritabanına (`SiberGoz.db`) işler.

* **Yerel / Hibrit AI Teşhis Motoru (`core/ai_engine.py`):**
  * Sistemde Ollama (Qwen2.5) servisleri aktifse yerel LLM üzerinden, kapalıysa kural tabanlı uzman motor üzerinden anında **Kök Neden Analizi (Root Cause Analysis)** üretir, ekrana basar ve veritabanına kaydeder.

* **Kalıcı Veritabanı ve Log Mimarısı (`database/` & `logs/`):**
  * Tüm sistem olayları zaman damgalı olarak `logs/system.log` dosyasına yazılır.
  * Engellenen IP'ler, sistem logları ve yapay zekâ analizleri SQLite veritabanındaki (`database/SiberGoz.db`) ilişkisel tablolara kaydedilir.
  * Saldırı anındaki ham ağ paketleri tersine mühendislik için `logs/lcaptures/*.pcap` formatında saklanır.

---

## 📂 Güncel Proje Klasör Mimarisi

```text
SiberGoz-Pardus-Debugging/
│
├── main.py                         # Sistem Ana Giriş Noktası
├── requirements.txt                # Python Bağımlılıkları
├── README.md                       # Proje Dokümantasyonu
│
├── core/                           # Çekirdek Güvenlik ve AI Motorları
│   ├── __init__.py
│   ├── network_radar.py             # RAW Socket Ağ Radarı & iptables IPS Motoru
│   └── ai_engine.py                # Yerel / Hibrit AI Kök Neden Teşhis Motoru
│
├── gui/                            # Çoklu Terminal Arayüz Katmanı
│   ├── __init__.py
│   ├── control_panel.py             # 1. TERMINAL: Ana Karargâh Kontrol Paneli
│   ├── camera_terminal.py          # 2. TERMINAL: Otonom Canlı Kamera Ekranı
│   └── network_scanner_terminal.py # 3. TERMINAL: Canlı Wi-Fi İstemci & IP Engelleme
│
├── config/                         # Yapılandırma Modülleri
│   ├── __init__.py
│   └── settings.py
│
├── database/                       # Kalıcı Veritabanı Katmanı
│   ├── __init__.py
│   ├── db_manager.py                # SQLite Veritabanı Yöneticisi
│   ├── schema.sql                   # Veritabanı Tablo Şeması
│   └── SiberGoz.db                  # SQLite Veritabanı Dosyası
│
├── debugging_and_security/         # Adli Bilişim ve Tersine Mühendislik Araçları
│   ├── __init__.py
│   ├── nmap_scanner.py
│   ├── system_debugger.py
│   ├── ufw_manager.py
│   └── tshark_analyzer.py
│
├── logs/                           # Sistem Logları ve PCAP Dökümleri
│   ├── lcaptures/                  # Wireshark / Tshark .pcap paket kayıtları
│   └── system.log                  # Kalıcı zaman damgalı sistem logları
│
└── tests/                          # Test ve Saldırı Simülasyonları
    ├── __init__.py
    └── test_attack_sim.py
```

🛠️ Kurulum ve Çalıştırma (Pardus OS)

    Açık Kaynak Depoyu Kopyalayın:
    Bash

git clone [https://github.com/KULLANICI_ADIN/SiberGoz-Pardus-Debugging.git](https://github.com/KULLANICI_ADIN/SiberGoz-Pardus-Debugging.git)
cd SiberGoz-Pardus-Debugging

Sanal Ortamı Oluşturun ve Bağımlılıkları Yükleyin:
Bash

python3 -m venv siber_goz_env
./siber_goz_env/bin/pip install customtkinter openpyxl

Yönetici Yetkisiyle Karargâh Panelini Başlatın:
(Raw Socket dinleme ve iptables güvenlik duvarı kuralları için sudo gereklidir)
Bash

sudo ./siber_goz_env/bin/python3 main.py



Veritabanı Sorgulama ve Denetim

Sistem çalışırken veritabanı kayıtlarını doğrudan Pardus terminalinden sorgulayabilirsiniz:

    Engellenen IP Kayıtlarını Listeleme:
    Bash

sqlite3 database/SiberGoz.db "SELECT * FROM engellenen_ipler;"

Son Sistem Loglarını Görme:
Bash

sqlite3 database/SiberGoz.db "SELECT * FROM system_logs ORDER BY id DESC LIMIT 10;"

Yapay Zekâ Teşhis Kayıtlarını İnceleme:
Bash

sqlite3 database/SiberGoz.db "SELECT * FROM ai_teshisleri;"
