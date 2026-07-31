# 🎯 SİBER GÖZ — Pardus OS Otonom Ağ Savunma ve İzleme Sistemi

Bu proje, **TEKNOFEST 2026 Pardus Hata Yakalama ve Geliştirme 
(Debugging and Development)** yarışması kapsamında geliştirilmiştir.

## 📌 Proje Özeti
Siber Göz, Pardus işletim sistemi üzerinde çalışan kamera ve gözetleme sistemlerini
ağ saldırılarına (DoS / ICMP Flood / SYN Flood) karşı koruyan, gerçek zamanlı
bir **IDS/IPS (Saldırı Tespit ve Önleme)** ve **otonom hata ayıklama (debugging)**
platformudur.

## ⚡ Temel Özellikler
* **Gerçek Zamanlı Ağ Radarı (RAW Socket):** Pardus çekirdeğinde ham soketleri
* dinleyerek anomali ve trafik patlamalarını milisaniyeler içinde algılar.
* **Otonom 2. Terminal Tetiklemesi:** Tehdit algılandığında ana kontrol panelini
* meşgul etmeden, arka planda bağımsız bir Pardus terminali açarak kamera/gözetleme
* kaydını delil toplama amacıyla otomatik başlatır.
* **Linux Çekirdek Kalkanı (iptables/IPS):** Eşik değeri aşan zararlı akışları tespit
* edip güvenlik duvarı kurallarıyla hedefe yönelen paketleri engeller.
* **Wireshark & Telemetri Entegrasyonu:** Ağ paket analizi ve hata ayıklama süreçleri
* için canlı loglama ve pcap analizi altyapısı sunar.

## 🛠️ Kurulum ve Çalıştırma (Pardus OS)

1. **Depoyu Kopyalayın:**
   ```bash
   git clone [https://github.com/yavasimozur/SiberGoz-Pardus-Debugging.git](https://github.com/yavasimozur/SiberGoz-Pardus-Debugging.git)
   cd SiberGoz-Pardus-Debugging
