import subprocess
import os

class TsharkAnalyzer:
    def capture_traffic(self, target_ip: str, duration: int, output_file: str) -> bool:
        """Belirli bir süre boyunca hedef IP'nin ağ paketlerini dinler ve .pcap olarak kaydeder."""
        try:
            # Klasör yoksa otomatik oluştur
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Tshark komutu (Herhangi bir ağ kartından (any) belirtilen IP'yi dinle)
            komut = ['tshark', '-i', 'any', '-f', f'host {target_ip}', '-a', f'duration:{duration}', '-w', output_file]
            
            subprocess.run(komut, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[TSHARK HATA] Paket yakalama başarısız oldu: {e}")
            return False