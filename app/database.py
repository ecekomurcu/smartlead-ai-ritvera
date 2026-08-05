import sqlite3

from flask import current_app, g


def get_db():
    #Aynı istek içinde birden fazla veritabanı bağlantısı açılmasını önler.
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_URL"]
        )

        #sütünlara isimle erişebilmek için row_factory ayarlanır.
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):
    #İstek sona erdiğinde açık SQLite bağlantısını güvenli şekilde kapatır.
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

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


def lead_ekle(isim, telefon, mesaj=None):
    db = get_db()

    #Parametreli sorgu kullanarak SQL Injection riskini önler.
    cursor = db.execute(
        """
        INSERT INTO leads (isim, telefon, mesaj)
        VALUES (?, ?, ?)
        """,
        (isim, telefon, mesaj)
    )

    db.commit()

    return cursor.lastrowid


def tum_leadler():
    db = get_db()

    kayitlar = db.execute(
        """
        SELECT id, isim, telefon, mesaj, tarih
        FROM leads
        ORDER BY tarih DESC
        """
    ).fetchall()

    return kayitlar


def init_app(app):
    #flask uygulaması kapanırken veritabanı bağlantısını kapatmak için teardown_appcontext kullanırız.
    app.teardown_appcontext(close_db)