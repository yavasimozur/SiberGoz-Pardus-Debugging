import subprocess

class SystemDebugger:
    def get_recent_errors(self, satir_sayisi: int = 20) -> str:
        """
        Pardus (Linux) çekirdek loglarını tarar. 
        Sadece '-p 3' (Error/Kritik Hata) seviyesindeki son olayları getirir.
        """
        try:
            # journalctl komutu ile sistemi tarıyoruz
            komut = ['journalctl', '-p', '3', '-n', str(satir_sayisi), '--no-pager']
            sonuc = subprocess.run(komut, capture_output=True, text=True, check=True)
            
            if sonuc.stdout.strip():
                return sonuc.stdout
            else:
                return "Sistemde son zamanlarda donanımsal veya çekirdek bazlı kritik bir hata bulunamadı. (Temiz)"
                
        except subprocess.CalledProcessError as e:
            return f"[SİSTEM HATA AYIKLAMA BAŞARISIZ] Loglar okunamadı: {e}"