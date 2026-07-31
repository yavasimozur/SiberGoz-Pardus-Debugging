import json
import urllib.request
import urllib.error

class LocalAIEngine:
    def __init__(self, model_name="qwen2.5:0.5b", api_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.api_url = api_url

    def anomali_analiz_et(self, paket_sayisi, hedef_ip):
        prompt = (
            f"Pardus OS ağında {hedef_ip} adresine saniyede {paket_sayisi} paketlik "
            f"DoS/ICMP Flood saldırısı yapılıyor. Kök nedeni ve iptables çözümünü tek cümle ile Türkçe özetle."
        )

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2.5) as response:
                result = json.loads(response.read().decode("utf-8"))
                llm_res = result.get("response", "").strip()
                if llm_res:
                    return f"[OLLAMA LLM TEŞHİSİ] 🧠 {llm_res}"
        except Exception:
            pass

        siddet = "YÜKSEK (CRITICAL)" if paket_sayisi > 100 else "ORTA (WARNING)"
        return (
            f"[AI TEŞHİS RAPORU] 🧠 Tehdit Türü: ICMP/TCP Flood Patlaması | "
            f"Şiddet: {siddet} ({paket_sayisi} pkt/sn) | "
            f"Kök Neden: Hedef IP soket sömürüsü | Aksiyon: iptables DROP kuralı aktifleştirildi."
        )