from flask import Blueprint, current_app, jsonify, render_template, request

from .database import DatabaseError, lead_ekle, tum_leadler
from .services.ai_service import AIServiceError, ai_service


#JSON dönen API rotalarını "/api" altına alırız. Blueprint ile modüler bir yapı kurarız.
api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

#html sayfalarını api dışındaki rotalara alırız.
pages_bp = Blueprint(
    "pages",
    __name__
)


@pages_bp.get("/")
def anasayfa():
    #Ziyaretçilerin yapay zeka ile iletişime geçeceği karşılaşma sayfası.
    return render_template("index.html")


@pages_bp.get("/dashboard")
def dashboard_sayfasi():
    #İşletme sahibinin lead kayıtlarını görebileceği yönetim paneli sayfası.
    return render_template("dashboard.html")


@api_bp.post("/leads")
def lead_kaydet():
    #İsteklerdeki JSON verisini Python dictionary'si olarak al.
    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({
            "basari": False,
            "hata": "Geçerli bir JSON nesnesi gönderilmelidir."
        }), 400

    isim = veri.get("isim")
    telefon = veri.get("telefon")
    mesaj = veri.get("mesaj")

    #Zorunlu alanlar eksikse veritabanı kaydı yapmadan önce hatayı bildir.
    if (
        not isinstance(isim, str)
        or not isinstance(telefon, str)
        or not isim.strip()
        or not telefon.strip()
    ):
        return jsonify({
            "basari": False,
            "hata": "İsim ve telefon alanları zorunludur."
        }), 400

    if mesaj is not None and not isinstance(mesaj, str):
        return jsonify({
            "basari": False,
            "hata": "Mesaj alanı metin biçiminde olmalıdır."
        }), 400

    isim = isim.strip()
    telefon = telefon.strip()
    mesaj = mesaj.strip() if mesaj and mesaj.strip() else None

    try:
        yeni_id = lead_ekle(
            isim,
            telefon,
            mesaj
        )

        return jsonify({
            "basari": True,
            "mesaj": "Lead başarıyla kaydedildi.",
            "id": yeni_id
        }), 201

    except DatabaseError:
        current_app.logger.exception(
            "Lead kaydedilirken veritabani hatasi olustu."
        )

        return jsonify({
            "basari": False,
            "hata": "Lead kaydedilirken bir sorun oluştu."
        }), 500


@api_bp.get("/leads")
def leadleri_listele():
    try:
        kayitlar = tum_leadler()

        #SQLite'den dönen kayıtları JSON uyumlu bir listeye çeviririz.
        sonuc = [
            dict(kayit)
            for kayit in kayitlar
        ]

        return jsonify({
            "basari": True,
            "kayitlar": sonuc
        }), 200

    except DatabaseError:
        current_app.logger.exception(
            "Lead kayitlari getirilirken veritabani hatasi olustu."
        )

        return jsonify({
            "basari": False,
            "hata": "Lead kayıtları getirilemedi."
        }), 500


@api_bp.post("/sohbet")
def sohbet():
    #Kullanıcıdan gelen JSON verisini alırız. "mesaj" ve "gecmis" alanlarını bekleriz.
    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({
            "basari": False,
            "hata": "Geçerli bir JSON nesnesi gönderilmelidir."
        }), 400

    mesaj = veri.get("mesaj")
    gecmis = veri.get("gecmis") or []

    #Boş mesajın yapay zekaya erişmesini engellemek için hatayı bildiririz.
    if not isinstance(mesaj, str) or not mesaj.strip():
        return jsonify({
            "basari": False,
            "hata": "Mesaj alanı zorunludur."
        }), 400

    mesaj = mesaj.strip()

    #konuşma geçmişi liste biçiminde değilse hatayı bildiririz.
    if not isinstance(gecmis, list):
        return jsonify({
            "basari": False,
            "hata": "Geçmiş alanı liste biçiminde olmalıdır."
        }), 400

    try:
        cevap = ai_service.yanit_uret(
            mesaj=mesaj,
            gecmis=gecmis
        )

        return jsonify({
            "basari": True,
            "cevap": cevap
        }), 200

    except AIServiceError as hata:
        #Yapay zeka'ya ulaşılamazsa 503 Service Unavailable hatası döndürürüz.
        current_app.logger.warning(
            "Yapay zeka servisi hatasi: %s",
            hata
        )

        return jsonify({
            "basari": False,
            "hata": str(hata)
        }), 503