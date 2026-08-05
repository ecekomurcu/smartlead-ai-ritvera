import requests

from config import Config


class AIServiceError(Exception):
    """Yapay zekâ servisi çağrılarındaki kontrollü hatalar."""


class AIService:
    def __init__(self):
        # Groq'un OpenAI uyumlu sohbet endpoint'i ve kullanılacak model.
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"

    def _sistem_talimati_getir(self):
        """Yapay zekânın davranış talimatını yapılandırma katmanından getirir."""
        return Config.BUSINESS_CONTEXT

    def yanit_uret(self, mesaj, gecmis=None):
        api_key = Config.GROQ_API_KEY
        business_context = self._sistem_talimati_getir()

        # API anahtarı yoksa uygulama çökmeden demo cevabı döndür.
        if not api_key:
            return "Demo modu aktif. Groq API anahtarı henüz eklenmedi."

        #Mesaj sırası: Sistem talimatı -> Geçmiş konuşmalar -> Kullanıcı mesajı
        mesajlar = [
            {
                "role": "system",
                "content": business_context
            }
        ]

        if gecmis:
            mesajlar.extend(gecmis)

        mesajlar.append({    #en son kullanıcı mesajını ekleriz
            "role": "user",
            "content": mesaj
        })

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": mesajlar
                },
                timeout=30
            )

            #Groq hatası durumunda HTTP 4xx veya 5xx döner. 
            response.raise_for_status()

            veri = response.json()

            #Groq cevabındaki asıl yapay zekâ metnini çıkar.
            return veri["choices"][0]["message"]["content"]

        except requests.RequestException as hata:
            raise AIServiceError(
                "Yapay zekâ servisine ulaşılamadı."
            ) from hata

        except (KeyError, IndexError, TypeError, ValueError) as hata:
            #Servis beklenmeyen bir cevap yapısı döndürürse kullanıcıya teknik ayrıntı gösterme.
            raise AIServiceError(
                "Yapay zekâ servisinden geçerli bir yanıt alınamadı."
            ) from hata


#routes.py içinde tekrar tekrar nesne oluşturmadan kullanılacak tek servis örneği.
ai_service = AIService()