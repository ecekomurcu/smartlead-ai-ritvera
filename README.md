# Ritvera SmartLead AI

Ritvera SmartLead AI, etkinlik planlama sürecindeki belirsizliği azaltmayı amaçlayan yapay zeka destekli bir EventTech MVP projesidir.

Sistem, ziyaretçilerin yapay zeka asistanıyla etkinlikleri hakkında konuşabildiği ve iletişim bilgilerini bırakabildiği bir B2C arayüz ile işletme tarafında gelen lead kayıtlarının görüntülendiği bir B2B yönetim panelinden oluşmaktadır.

## Özellikler

- Yapay zeka destekli etkinlik planlama asistanı
- Mesaj ve konuşma geçmişini destekleyen sohbet yapısı
- İsim, telefon ve isteğe bağlı mesaj bilgilerinin lead olarak kaydedilmesi
- Lead kayıtlarının yönetim panelinde listelenmesi
- Ritvera'ya özel `BUSINESS_CONTEXT` ile AI davranışlarının yönlendirilmesi
- Flask backend ile Wix Studio frontend entegrasyonu
- Eksik veya hatalı veriler için kontrollü JSON yanıtları
- Groq API anahtarı bulunmadığında demo modu

## Kullanılan Teknolojiler

- Python 3.10+
- Flask
- SQLite
- Groq API
- Wix Studio
- Wix Velo
- Wix Web Modules
- Render
- Git ve GitHub

## Sistem Mimarisi

Backend, sorumlulukların ayrılığı prensibine göre modüler olarak geliştirilmiştir. Her dosyanın belirli bir görevi bulunmaktadır.

- `config.py`: Uygulama ayarlarını ve ortam değişkenlerini yönetir.
- `app/database.py`: SQLite bağlantısını ve veritabanı işlemlerini yönetir.
- `app/services/ai_service.py`: Groq API ile iletişim kurar ve yapay zeka yanıtlarını üretir.
- `app/routes.py`: HTTP isteklerini karşılar ve ilgili servis veya veritabanı fonksiyonuna yönlendirir.
- `app/__init__.py`: Flask uygulamasını oluşturur, yapılandırmayı yükler, CORS ayarlarını yapar ve modülleri birleştirir.
- `app/templates/index.html`: Yerel sohbet test sayfasını içerir.
- `app/templates/dashboard.html`: Yerel lead yönetim panelini içerir.
- `run.py`: Flask uygulamasının giriş noktasıdır.

Veritabanı sorguları yalnızca `app/database.py` içinde, yapay zeka API çağrıları ise yalnızca `app/services/ai_service.py` içinde bulunmaktadır.

Wix tarafında frontend kodları doğrudan Flask API ile iletişim kurmak yerine `ritveraApi.web.js` isimli backend web module üzerinden API'ye bağlanır.

## Genel Sistem Akışı

```text
Wix Frontend
    ↓
Wix Backend Web Module
    ↓
Render üzerindeki Flask API
    ↓
Groq API veya SQLite
    ↓
Wix Backend
    ↓
Wix Frontend
```

### Yapay Zeka Sohbet Akışı

1. Kullanıcı Wix arayüzü üzerinden bir mesaj gönderir.
2. Mesaj ve isteğe bağlı konuşma geçmişi `sohbetEt()` fonksiyonuna iletilir.
3. Wix backend web module, Flask üzerindeki `/api/sohbet` uç noktasına POST isteği gönderir.
4. Flask rotası isteği yapay zeka servis katmanına yönlendirir.
5. `ai_service.py`, `BUSINESS_CONTEXT`, konuşma geçmişi ve kullanıcı mesajıyla Groq API'ye istek gönderir.
6. Groq tarafından oluşturulan yanıt Wix arayüzüne geri döndürülür.

`BUSINESS_CONTEXT`, yapay zekaya Ritvera'nın hizmet bölgesi, fiyat yaklaşımı ve yanıt biçimi hakkında talimat verir. Bu yapı ayrı bir teknik çıktı filtresi değil, model davranışını yönlendiren sistem talimatıdır.

### Lead Akışı

```text
Wix Formu
    ↓
leadKaydet()
    ↓
POST /api/leads
    ↓
Flask
    ↓
SQLite
```

Kullanıcının isim, telefon ve isteğe bağlı mesaj bilgileri SQLite veritabanındaki `leads` tablosuna kaydedilir.

### Yönetim Paneli Akışı

```text
Yönetim Paneli
    ↓
leadleriGetir()
    ↓
GET /api/leads
    ↓
Flask
    ↓
SQLite
    ↓
Wix Repeater
```

Kayıtlar en yeni lead önce olacak şekilde yönetim panelinde listelenir.

## API Uç Noktaları

### GET `/health`

Backend servisinin aktif olup olmadığını kontrol eder.

Örnek yanıt:

```json
{
  "basari": true,
  "status": "aktif",
  "message": "Ritvera backend çalışıyor."
}
```

### POST `/api/sohbet`

Kullanıcı mesajını ve isteğe bağlı konuşma geçmişini yapay zeka servisine gönderir.

Örnek istek:

```json
{
  "mesaj": "Bahçe nişanı için tema önerir misin?",
  "gecmis": []
}
```

Başarılı yanıtta `basari` ve `cevap` alanları döndürülür.

### POST `/api/leads`

Yeni bir lead kaydı oluşturur.

Zorunlu alanlar:

- `isim`
- `telefon`

İsteğe bağlı alan:

- `mesaj`

Örnek istek:

```json
{
  "isim": "Örnek Kullanıcı",
  "telefon": "+90 555 000 00 00",
  "mesaj": "Kocaeli'de doğum günü planlıyorum."
}
```

Başarılı kayıt işleminde `201 Created` durum kodu döndürülür.

### GET `/api/leads`

Kaydedilen tüm lead kayıtlarını en yeniden eskiye doğru döndürür.

Başarılı yanıtta kayıtlar `kayitlar` alanı içinde listelenir.

## Güvenlik ve Hata Yönetimi

- Groq API anahtarı ve diğer gizli bilgiler ortam değişkenlerinde tutulur.
- `.env` dosyası `.gitignore` ile GitHub deposunun dışında bırakılır.
- SQL sorgularında kullanıcı verileri doğrudan sorguya eklenmez.
- SQL sorgularında `?` yer tutucuları kullanılır.
- SQLite hataları kontrollü `DatabaseError` hatalarına dönüştürülür.
- Yapay zeka servis hataları `AIServiceError` ile yönetilir.
- Eksik veya geçersiz kullanıcı verilerinde `400` durum kodu döndürülür.
- Yapay zeka servisine ulaşılamadığında `503` durum kodu döndürülür.
- Veritabanı işlemi başarısız olduğunda güvenli JSON hata yanıtı döndürülür.
- CORS erişimi geliştirme ve üretim ortamına göre yapılandırılabilir.
- Yönetim panelinde kullanıcı verileri `innerHTML` yerine `textContent` ile gösterilir.

## Yerelde Çalıştırma

### 1. Projeyi klonlayın

```bash
git clone PROJE_GITHUB_ADRESI
cd PROJE_KLASORU
```

### 2. Sanal ortam oluşturun

```bash
python -m venv venv
```

### 3. Sanal ortamı etkinleştirin

Windows:

```bash
venv\Scripts\activate
```

macOS veya Linux:

```bash
source venv/bin/activate
```

### 4. Bağımlılıkları yükleyin

```bash
python -m pip install -r requirements.txt
```

### 5. Ortam değişkenlerini hazırlayın

Projenin ana klasöründe `.env` dosyası oluşturun:

```env
FLASK_ENV=development
SECRET_KEY=gelistirme-icin-guvenli-bir-anahtar
DATABASE_URL=leads.db

AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key

CORS_ORIGINS=*
```

Gerçek Groq API anahtarı GitHub'a yüklenmemelidir.

### 6. Uygulamayı çalıştırın

```bash
python run.py
```

Yerel adresler:

- Karşılama sayfası: `http://127.0.0.1:5000/`
- Yönetim paneli: `http://127.0.0.1:5000/dashboard`
- Sağlık kontrolü: `http://127.0.0.1:5000/health`
- Lead API: `http://127.0.0.1:5000/api/leads`

## Render Ayarları

Render üzerinde aşağıdaki ayarlar kullanılmalıdır:

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn run:app
```

Gerekli ortam değişkenleri:

```env
FLASK_ENV=production
SECRET_KEY=uretim-icin-guvenli-bir-anahtar
DATABASE_URL=leads.db

AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key

CORS_ORIGINS=https://ecekomurcu02.wixstudio.com
```

Üretim ortamında `CORS_ORIGINS=*` yerine yalnızca yayınlanan Wix sitesinin alan adı kullanılmalıdır.

## Canlı Proje

### Wix B2C Arayüzü

[Ritvera Wix Sitesi](https://ecekomurcu02.wixstudio.com/ritvera)

### Wix Yönetim Paneli

[Ritvera Yönetim Paneli](https://ecekomurcu02.wixstudio.com/ritvera/blank)

### Render Backend

[Render Backend](https://smartlead-ai-ritvera.onrender.com)

### Health Kontrolü

[Backend Health Check](https://smartlead-ai-ritvera.onrender.com/health)

## Proje Notu

Bu proje, SmartLead AI mimarisinin Ritvera EventTech fikrine uyarlanmış bir MVP sürümüdür.

Temel backend katmanları konuya özel koddan ayrılmıştır. Ritvera'ya ait yapay zeka davranışları ağırlıklı olarak `BUSINESS_CONTEXT` üzerinden yapılandırılmıştır.
