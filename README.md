# Ritvera SmartLead AI

Ritvera SmartLead AI, etkinlik planlama sürecindeki belirsizliği azaltmayı amaçlayan yapay zeka destekli bir EventTech MVP projesidir.

Sistem, ziyaretçilerin yapay zeka asistanı ile etkinlikleri hakkında konuşabildiği ve iletişim bilgilerini bırakabildiği bir B2C arayüz ile işletme tarafında gelen lead kayıtlarının görüntülendiği bir B2B yönetim panelinden oluşmaktadır.

## Özellikler

- Yapay zeka destekli etkinlik planlama asistanı
- Konuşma geçmişini koruyan sohbet yapısı
- İsim ve telefon bilgilerinin lead olarak kaydedilmesi
- Lead kayıtlarının yönetim panelinde listelenmesi
- Ritvera'ya özel BUSINESS_CONTEXT ile AI davranışlarının sınırlandırılması
- Yapay zekanın doğrulanmamış fiyat üretmesini engelleyen ek kontrol
- Flask backend ile Wix Studio frontend entegrasyonu

## Kullanılan Teknolojiler

- Python
- Flask
- SQLite
- Groq API
- Wix Studio
- Wix Velo
- Wix Web Modules
- Render
- Git / GitHub

## Sistem Mimarisi

Backend, sorumlulukların ayrılığı (Separation of Concerns) prensibine göre modüler olarak geliştirilmiştir.

- `config.py`: Uygulama ayarlarını ve environment variable değerlerini yönetir.
- `database.py`: SQLite veritabanı işlemlerini gerçekleştirir.
- `ai_service.py`: Groq API ile iletişim kurar ve yapay zeka cevaplarını üretir.
- `routes.py`: HTTP isteklerini karşılar ve ilgili servis veya veritabanı fonksiyonuna yönlendirir.
- `app/__init__.py`: Flask uygulamasını oluşturur, yapılandırmayı yükler, CORS ayarlarını yapar ve modülleri birleştirir.
- `run.py`: Flask uygulamasının giriş noktasıdır.

Wix tarafında frontend kodları doğrudan Flask API ile iletişim kurmak yerine `ritveraApi.web.js` isimli backend web module üzerinden API'ye bağlanır.

Genel Akış:

Wix Frontend → Wix Backend Web Module → Render / Flask → Groq veya SQLite → Wix Backend → Wix Frontend

### Yapay ZekA Sohbet Akışı

1. Kullanıcı Wix üzerinden bir mesaj gönderir.
2. Mesaj ve konuşma geçmişi `sohbetEt()` fonksiyonuna iletilir.
3. Wix backend web module, Flask üzerindeki `/api/sohbet` endpointine POST isteği gönderir.
4. Flask isteği AI servis katmanına yönlendirir.
5. `ai_service.py`, BUSINESS_CONTEXT ve konuşma geçmişi ile Groq API'ye istek gönderir.
6. Oluşturulan cevap güvenlik kontrollerinden geçirildikten sonra Wix'e geri döner.

### Lead Akışı

Wix formu → `leadKaydet()` → `POST /api/leads` → Flask → SQLite

Kullanıcının isim ve telefon bilgileri SQLite veritabanındaki `leads` tablosuna kaydedilir.

### Yönetim Paneli Akışı

Yönetim Paneli → `leadleriGetir()` → `GET /api/leads` → Flask → SQLite → Wix Repeater

Kayıtlar en yeni lead önce olacak şekilde yönetim panelinde listelenir.

## API Uç Noktaları

### GET `/health`

Backend servisinin aktif olup olmadığını kontrol eder.

### POST `/api/sohbet`

Kullanıcı mesajını ve isteğe bağlı konuşma geçmişini yapay zekA servisine gönderir.

### POST `/api/leads`

Yeni bir lead kaydı oluşturur.

Zorunlu alanlar:

- `isim`
- `telefon`

### GET `/api/leads`

Kaydedilen tüm lead kayıtlarını en yeniden eskiye doğru döndürür.

## Güvenlik ve Hata Yönetimi

- Groq API anahtarı ve diğer gizli bilgiler environment variable olarak tutulur.
- `.env` dosyası `.gitignore` ile GitHub deposunun dışında bırakılır.
- SQL sorgularında kullanıcı verileri doğrudan sorguya eklenmez ve `?` parametreleri kullanılır.
- Yapay zeka ve HTTP işlemlerinde hata yönetimi uygulanır.
- Eksik kullanıcı verilerinde uygun HTTP durum kodları döndürülür.
- Groq servisinin kullanılamadığı durumlarda güvenli hata mesajı döndürülür.
- Yapay zekanın kullanıcı tarafından verilmemiş fiyat bilgileri üretmesini önlemek için ek çıktı kontrolü uygulanır.

## Yerelde Çalıştırma

Projeyi klonladıktan sonra sanal ortam oluşturun:

```bash
python -m venv venv

Sanal ortamı aktif hale getirip bağımlılıkları yükleyin:

pip install -r requirements.txt

Proje ana klasöründe ".env" dosyası oluşturularak gerekli environment variable değerleri eklenmelidir.

GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key

Daha sonra uygulama çalıştırılabilir:

python run.py

Backend varsayılan olarak Flask sunucsunda çalışacaktır.

Canlı Proje

Wix B2C Arayüzü
https://ecekomurcu02.wixstudio.com/ritvera

Wix Yönetim Paneli
https://ecekomurcu02.wixstudio.com/ritvera/blank

Render Backend
https://smartlead-ai-ritvera.onrender.com

Health Kontrolü
Render Backend

https://smartlead-ai-ritvera.onrender.com/health


Proje Notu

Bu proje Smartlead AI mimarisinin Ritvera EventTech fikrine uyarlanmış bir MVP sürümüdür.
Temel backend katmanları konuya özel koddan ayrılmıştır. Ritvera'ya ait yapay zeka davranışları
ağırlıklı olarak "BUSINESS_CONTEXT" üzerinden yapılandırılmıştır.