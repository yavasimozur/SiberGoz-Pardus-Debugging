from abc import ABC, abstractmethod

class BaseDevice(ABC):
    """
    SİBER GÖZ DONANIM ANAYASASI (Abstract Base Class)
    Sisteme eklenecek her fiziksel cihaz (ESP32, Sensör vb.) bu şablondan türetilmeli
    ve buradaki zorunlu metotları içermelidir.
    """
    
    def __init__(self, device_ip: str, device_name: str):
        self.device_ip = device_ip
        self.device_name = device_name
        self.is_connected = False

    @abstractmethod
    def baglanti_kur(self) -> bool:
        """
        Her donanım kendi bağlantı protokolünü (HTTP, TCP, Serial) 
        bu fonksiyonun içinde yazmak ZORUNDADIR.
        """
        pass

    @abstractmethod
    def durum_raporu_ver(self) -> str:
        """
        Donanımın anlık durumunu (Şarj, Ağ koptu mu, Aktif mi)
        döndürmek ZORUNDADIR.
        """
        pass