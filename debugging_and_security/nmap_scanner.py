import nmap

class NmapScanner:
    def __init__(self):
        self.scanner = nmap.PortScanner()

    def scan_target(self, ip_address: str) -> dict:
        """Hedef IP'nin açık portlarını ve zafiyet durumunu tarar."""
        try:
            # -T4 (Hızlı tarama), -F (En popüler 100 port)
            self.scanner.scan(ip_address, arguments='-T4 -F')
            if ip_address in self.scanner.all_hosts():
                return self.scanner[ip_address]
            return {}
        except Exception as e:
            print(f"[NMAP KRİTİK HATA] Tarama başarısız: {e}")
            return {}