import subprocess

class UFWManager:
    def block_ip(self, ip_address: str) -> bool:
        """Belirtilen IP adresini UFW ile engeller."""
        try:
            # subprocess.DEVNULL ile ekrana gereksiz Linux yazıları basmasını engelliyoruz
            subprocess.run(['ufw', 'deny', 'from', ip_address], 
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def allow_ip(self, ip_address: str) -> bool:
        """Belirtilen IP adresinin UFW engelini kaldırır."""
        try:
            subprocess.run(['ufw', 'delete', 'deny', 'from', ip_address], 
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False