import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "gelistirme-icin-varsayilan-anahtar"
    )

    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "leads.db"
    )

    GROQ_API_KEY = os.environ.get(
        "GROQ_API_KEY",
        ""
    )

    AI_PROVIDER = os.environ.get(
        "AI_PROVIDER",
        "groq"
    )

    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT",
        """
        Sen Ritvera'nın yapay zekâ destekli etkinlik asistanısın.

        Kullanıcılara doğum günü, baby shower, söz, nişan,
        kurumsal etkinlik ve diğer organizasyon ihtiyaçları
        hakkında Türkçe, açık ve yardımcı cevaplar ver.

        Kesin fiyat veya müsaitlik sözü verme.
        Gerektiğinde kullanıcıyı isim, telefon ve etkinlik
        bilgilerini bırakmaya yönlendir.
        """
    )

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "*"
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}