import requests

from config import Config


class AIServiceError(Exception):
    """Yapay zeka servisi çağrılarındaki kontrollü hatalar."""


class AIService:
    def __init__(self):
        #Groq'un OpenAI uyumlu sohbet endpoint'i ve kullanılacak model.
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-20b"

    def yanit_uret(self, mesaj, gecmis=None):
        api_key = Config.GROQ_API_KEY
        business_context = Config.BUSINESS_CONTEXT

        #API anahtarı yoksa gerçek yapay zeka isteği göndermek yerine demo mesajı döndürürüz.
        if not api_key:
            return (
                "Ritvera yapay zeka asistanı şu anda demo modunda çalışıyor. "
                "Etkinlik planlama desteği için lütfen daha sonra tekrar deneyin."
            )

        #Sistem talimatı, geçmiş konuşmalar ve son kullanıcı mesajı.
        mesajlar = [
            {
                "role": "system",
                "content": business_context
            }
        ]

        #Geçmişte yalnızca kullanıcı ve yapay zeka mesajlarına izin veririz.
        for kayit in gecmis or []:
            if not isinstance(kayit, dict):
                continue

            rol = kayit.get("role")
            icerik = kayit.get("content")

            if rol not in ["user", "assistant"]:
                continue

            if not isinstance(icerik, str) or not icerik.strip():
                continue

            mesajlar.append({
                "role": rol,
                "content": icerik.strip()
            })

        mesajlar.append({
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
                    "messages": mesajlar,
                    #Temperature düşük tutularak daha tutarlı cevaplar üretmesini sağlarız.
                    "temperature": 0.1,
                    #Yanıtların gereksiz şekilde uzamasını önlemek için token sınırı koyarız.
                    "max_completion_tokens": 600
                },
                timeout=30
            )

            #Groq başarısız isteklerde HTTP 4xx veya 5xx döndürür.
            response.raise_for_status()

            veri = response.json()

            #Groq cevabındaki asıl yapay zeka metnini çıkarırız.
            cevap = veri["choices"][0]["message"]["content"].strip()

            #İstek başarılı olsa bile model boş bir yanıt döndürürse kontrollü hata oluştururuz.
            if not cevap:
                raise AIServiceError(
                    "Yapay zeka servisi boş bir yanıt döndürdü."
                )

            return cevap

        except requests.RequestException as hata:
            raise AIServiceError(
                "Yapay zeka servisine ulaşılamadı."
            ) from hata

        except (KeyError, IndexError, TypeError, ValueError) as hata:
            #Beklenmeyen cevap yapısında kullanıcıya teknik detay göstermeden kontrollü hata oluştururuz.
            raise AIServiceError(
                "Yapay zeka servisinden geçerli bir yanıt alınamadı."
            ) from hata


#routes.py içinde tekrar nesne oluşturmadan kullanılacak servis örneği.
ai_service = AIService()