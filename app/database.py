import sqlite3

#g bir request boyunca verileri saklamak için kullanılan bir Flask özel nesnesidir.
#bu sayede aynı istek içinde birden fazla veritabanı bağlantısı açılmasını önleriz.
from flask import current_app, g


class DatabaseError(Exception):
    """Veritabani islemleri sirasinda olusan kontrollu hatalari temsil eder."""


def get_db():
    #Aynı istek içinde birden fazla veritabanı bağlantısı açılmasını önler.
    if "db" not in g:
        try:
            g.db = sqlite3.connect(
                current_app.config["DATABASE_URL"]
            )
        except sqlite3.Error as error:
            raise DatabaseError(
                "Veritabani baglantisi kurulamadi."
            ) from error

        #Databasedeki satırlara isim ile erişmek için row_factory ayarlanır.
        #Bu sayede satırlara dict benzeri bir şekilde erişebiliriz.
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):
    #İstek sona erdiğinde açık SQLite bağlantısını güvenli şekilde kapatır.
    db = g.pop("db", None)

    if db is not None:
        try:
            db.close()
        except sqlite3.Error:
            current_app.logger.exception(
                "Veritabani baglantisi kapatilirken hata olustu."
            )


def init_db():
    db = get_db()

    #Leads tablosu yoksa oluşturur, varsa hata vermez.
    #Bu sayede uygulama her başlatıldığında tabloyu yeniden oluşturmaz.
    try:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.commit()
    except sqlite3.Error as error:
        db.rollback()
        raise DatabaseError(
            "Veritabani tablosu hazirlanamadi."
        ) from error


def lead_ekle(isim, telefon, mesaj=None):
    db = get_db()

    #Parametreli sorgu kullanarak SQL Injection riskini önlüyoruz.
    try:
        cursor = db.execute(
            """
            INSERT INTO leads (isim, telefon, mesaj)
            VALUES (?, ?, ?)
            """,
            (isim, telefon, mesaj)
        )

        db.commit()
    except sqlite3.Error as error:
        db.rollback()
        raise DatabaseError(
            "Lead kaydi eklenemedi."
        ) from error

    #Database'e eklenen son kaydın id'sini döndürür.
    #Bu sayede eklenen lead'in id'sine erişebiliriz.
    return cursor.lastrowid


def tum_leadler():
    #Database'deki tüm lead kayıtlarını en yeniden eskiye doğru getirir.
    db = get_db()

    try:
        return db.execute(
            """
            SELECT *
            FROM leads
            ORDER BY tarih DESC, id DESC
            """
        ).fetchall()
    except sqlite3.Error as error:
        raise DatabaseError(
            "Lead kayitlari getirilemedi."
        ) from error


def init_app(app):
    #Flask uygulaması kapanırken veritabanı bağlantısını kapatmak için teardown_appcontext kullanırız.
    app.teardown_appcontext(close_db)