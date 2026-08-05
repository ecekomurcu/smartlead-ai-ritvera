from flask import Blueprint, jsonify, render_template, request

from .database import lead_ekle, tum_leadler
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
    veri = request.get_json(silent=True) or {}

    isim = (veri.get("isim") or "").strip()
    telefon = (veri.get("telefon") or "").strip()
    mesaj = (veri.get("mesaj") or "").strip() or None

    #Zorunlu alanlar eksikse veritabanı kaydı yapmadan önce hatayı bildir.
    if not isim or not telefon:
        return jsonify({
            "basari": False,
            "hata": "İsim ve telefon alanları zorunludur."
        }), 400

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


@api_bp.get("/leads")
def leadleri_listele():
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


@api_bp.post("/sohbet")
def sohbet():
    #Kullanıcıdan gelen JSON verisini alırız. "mesaj" ve "gecmis" alanlarını bekleriz.
    veri = request.get_json(silent=True) or {}

    mesaj = (veri.get("mesaj") or "").strip()
    gecmis = veri.get("gecmis") or []

    #Boş mesajın yapay zekaya erişmesini engellemek için hatayı bildiririz.
    if not mesaj:
        return jsonify({
            "basari": False,
            "hata": "Mesaj alanı zorunludur."
        }), 400

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
        return jsonify({
            "basari": False,
            "hata": str(hata)
        }), 503