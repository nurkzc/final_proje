# 📬 Destek Talep Sistemi (Flask Projesi)

Bu proje, Python ve Flask kullanılarak geliştirilmiş bir **destek talep yönetim sistemidir**. Kullanıcılar sistem üzerinden destek talepleri oluşturabilir, takip edebilir; yöneticiler (admin) ise bu talepleri görüntüleyip düzenleyebilir. Rol tabanlı kullanıcı yönetimi ile admin ve kullanıcı işlemleri ayrı ayrı yönetilmektedir.

---

## 🚀 Özellikler

- 🧑‍💻 Kullanıcı Kaydı ve Girişi
- 🗃️ Talep Oluşturma, Listeleme, Düzenleme
- 🧑‍⚖️ Admin Paneli:
  - Tüm kullanıcıları ve talepleri görüntüleyebilme
  - Talepleri düzenleyebilme ve yönetebilme
- 👤 Kullanıcı Paneli:
  - Kendi taleplerini görme ve durum takibi
- ⚙️ Profil ve Ayarlar Sayfası
- 📊 Dashboard & İstatistik Görünümü
- 🎨 Özel Tasarlanmış HTML/CSS Arayüz

---

## 🗂️ Proje Yapısı

nur/
└── final/
├── app.py # Ana Flask uygulama dosyası
├── dbtojson.py # Veritabanı verilerini JSON'a çevirici
├── herat.code-workspace # VSCode workspace dosyası
├── requirements.txt # Proje bağımlılıkları
├── veri_aktarimi.json # Örnek veri dosyası
├── instance/ # (Varsa) SQLite DB gibi özel veriler
├── static/
│ └── css/
│ └── style.css # Projenin tüm CSS stilleri
├── templates/ # HTML şablon dosyaları
│ ├── admin-login.html
│ ├── admin.html
│ ├── adminbase.html
│ ├── base.html
│ ├── create.html
│ ├── dashboard.html
│ ├── edit.html
│ ├── index.html
│ ├── kullanici-panel.html
│ ├── login.html
│ ├── profile.html
│ ├── register.html
│ ├── settings.html
└── pycache/ # Python önbellek dosyaları


---

## 🔐 Kullanıcı Rolleri

| Rol      | Yetkiler                                                                 |
|----------|--------------------------------------------------------------------------|
| **Admin**    | Tüm kullanıcıları ve talepleri görüntüleyebilir, düzenleyebilir, sistemin genel yönetimini sağlar. |
| **Kullanıcı**| Talep oluşturabilir, kendi taleplerini görebilir, profilini güncelleyebilir.                        |

Her kullanıcıya giriş yapıldıktan sonra rolüne uygun bir panel gösterilir.  
Admin için özel bir admin paneli, kullanıcı için sade ve işlevsel bir kullanıcı paneli tasarlanmıştır.

---

## 📌 Notlar

- Uygulama eğitim amaçlı geliştirilmiş olup, Flask'ın temel işleyişi üzerinden kurgulanmıştır.
- Proje içinde dinamik yönlendirme, oturum yönetimi, form verisi işleme gibi temel Flask konuları yer alır.
- Her kullanıcı için ayrı yetkilendirme uygulanmıştır. Sayfa erişim kontrolleri mevcuttur.
- Geliştirmeye açıktır. Örneğin:
  - Talep kategorileri
  - Talebe dosya ekleme
  - Bildirim sistemi
  - E-posta entegrasyonu gibi özellikler eklenebilir.

---

## 🛠️ Kurulum Talimatları

### 1. Python Sürümünü Kontrol Et

```bash
python --version
# Python 3.10+ önerilir
