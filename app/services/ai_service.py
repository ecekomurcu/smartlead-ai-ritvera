import re

import requests

from config import Config


class AIServiceError(Exception):
    """Yapay zeka servisi çağrılarındaki kontrollü hatalar."""


class AIService:
    def __init__(self):
        #Groq'un OpenAI uyumlu sohbet endpoint'i ve kullanılacak model.
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-20b"

    def _sistem_talimati_getir(self):
        """Yapay zekanın davranış talimatını yapılandırma katmanından getirir."""
        return Config.BUSINESS_CONTEXT

    #Yapay zeka modelinin fiyat üretmesinin önüne geçmek için kontrol sağlayıcı bir yöntem ekledik.
    #kullanıcının mesajında fiyat bilgisi yoksa modelin cevaplarında fiyat üretmesini engeller.

    def _fiyat_guvenlik_kontrolu(self, cevap, kullanici_mesaji):
        """Modelin kullanıcı tarafından verilmemiş fiyatlar üretmesini engeller."""
        fiyat_deseni = (
            r"\b\d[\d.,]*\s*(?:bin\s*)?"
            r"(?:TL|₺|Türk lirası|lira)\b"
        )

        cevaptaki_fiyatlar = {
            eslesme.group(0).lower().strip()
            for eslesme in re.finditer(
                fiyat_deseni,
                cevap,
                flags=re.IGNORECASE
            )
        }

        kullanici_fiyatlari = {
            eslesme.group(0).lower().strip()
            for eslesme in re.finditer(
                fiyat_deseni,
                kullanici_mesaji,
                flags=re.IGNORECASE
            )
        }

        #Kullanıcının vermediği bir fiyat üretilirse güvenli cevap döndür.
        if cevaptaki_fiyatlar - kullanici_fiyatlari:
            return (
                "Ritvera için doğrulanmış sabit bir fiyat bilgisi bulunmuyor. "
                "Fiyatlandırma; etkinlik türü, tarih, kişi sayısı, mekân ve "
                "beklentiler değerlendirildikten sonra Ritvera ekibi tarafından "
                "netleştirilir."
            )

        return cevap

    def yanit_uret(self, mesaj, gecmis=None):
        api_key = Config.GROQ_API_KEY
        business_context = self._sistem_talimati_getir()

        #API anahtarı yoksa uygulama çökmeden demo cevabı döndür.
        if not api_key:
            return "Demo modu aktif. Groq API anahtarı henüz eklenmedi."

        #sistem talimatı, geçmiş konuşmalar ve son kullanıcı mesajı.
        mesajlar = [
            {
                "role": "system",
                "content": business_context
            }
        ]

        if gecmis:
            mesajlar.extend(gecmis)

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

                #aşağıdaki değerler modelin daha tutarlı ve güvenli cevaplar üretmesini sağlamak için ayarlandı.
                json={
                    "model": self.model,
                    "messages": mesajlar,
                    #temperature daha tutarlı cevaplar için düşük kullanıyoruz. yüksek temperature modelin yaratıcı ve tahmin edilemez cevaplar üretmesine yol açar.
                    "temperature": 0.1,
                    #max tokens 600 seçildi çünkü kısa ve uygulanabilir cevaplar üretmek istiyoruz. uzun cevaplar kullanıcı deneyimi olumsuz etkileyebilir.
                    "max_tokens": 600,
                    #reasoning_effort gereksiz token kullanımını önlemek için low seçildi.
                    "reasoning_effort": "low",
                    #include_reasoning False seçildi çünkü modelin kendi mantığını döndürmesini istemiyoruz.
                    "include_reasoning": False
                },
                timeout=30
            )

            #Groq, başarısız isteklerde HTTP 4xx veya 5xx döndürür.
            response.raise_for_status()

            veri = response.json()

            #Groq cevabındaki asıl yapay zeka metnini çıkar.
            cevap = veri["choices"][0]["message"]["content"].strip()

            #istek başarılı ama model boş bir yanıt döndürdüyse güvenli cevap döndürür.
            if not cevap:
                raise AIServiceError(
                    "Yapay zekâ servisi boş bir yanıt döndürdü."
                )

            #kullanıcıya cevabı göndermeden önce fiyat güvenlik kontrolünden geçiririz.
            return self._fiyat_guvenlik_kontrolu(
                cevap=cevap,
                kullanici_mesaji=mesaj
            )

        except requests.RequestException as hata:
            raise AIServiceError(
                "Yapay zekâ servisine ulaşılamadı."
            ) from hata

        except (KeyError, IndexError, TypeError, ValueError) as hata:
            #olası bir beklenmeyen hatada kullancıya güvenli bir mesaj döndürür ve hata detaylarını loglar.
            raise AIServiceError(
                "Yapay zekâ servisinden geçerli bir yanıt alınamadı."
            ) from hata


#routes.py içinde tekrar nesne oluşturmadan kullanılacak servis örneği.
ai_service = AIService()