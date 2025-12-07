# Scraping Hata Kayıt Sistemi İyileştirmeleri

## ✅ Yapılan İyileştirmeler

### 1. Hata Kategorileri ve Error Codes
- **Otomatik hata kategorizasyonu** eklendi
- **Error Codes:**
  - `NETWORK_ERROR`: Ağ/bağlantı hataları
  - `ACCESS_DENIED`: Bot tespiti, erişim engellendi
  - `MISSING_DATA`: Eksik veri (name, price, image)
  - `MISSING_NAME`, `MISSING_PRICE`, `MISSING_IMAGE`: Spesifik eksik alanlar
  - `PARSING_ERROR`: Parse/format hataları
  - `INVALID_URL`: Geçersiz URL
  - `UNKNOWN_ERROR`: Bilinmeyen hatalar

- **Error Categories:**
  - `network`: Ağ hataları
  - `access`: Erişim hataları
  - `data`: Veri eksikliği
  - `parsing`: Parse hataları
  - `url`: URL hataları
  - `other`: Diğer

### 2. Retry Takibi
- **Retry Count**: Aynı URL kaç kez denendi?
- **Last Retry At**: Son deneme zamanı
- Otomatik retry sayısı hesaplama (aynı URL için önceki denemeleri kontrol eder)

### 3. Domain/Site Bazlı Analiz
- **Domain Extraction**: URL'den otomatik domain çıkarma
- **Domain bazlı istatistikler**: Hangi sitelerde daha çok hata var?
- **Domain bazlı filtreleme**: Belirli bir site için hataları görüntüleme

### 4. Gelişmiş Görüntüleme
- **Filtreleme:**
  - Status: `all`, `failed`, `partial`, `resolved`
  - Domain: Belirli bir site
  - Error Category: Hata kategorisi
  
- **İstatistikler:**
  - Toplam hata sayısı
  - Failed/Partial/Resolved sayıları
  - Domain bazlı dağılım
  - Error category bazlı dağılım

### 5. Veritabanı Yapısı (Yeni Alanlar)

**Firestore:**
```javascript
{
  // Mevcut alanlar...
  error_code: "MISSING_PRICE",
  error_category: "data",
  domain: "trendyol.com",
  retry_count: 2,
  resolved: false,
  last_retry_at: Timestamp
}
```

**SQLite:** (Migration gerekli)
```sql
ALTER TABLE product_import_issues ADD COLUMN error_code TEXT;
ALTER TABLE product_import_issues ADD COLUMN error_category TEXT;
ALTER TABLE product_import_issues ADD COLUMN domain TEXT;
ALTER TABLE product_import_issues ADD COLUMN retry_count INTEGER DEFAULT 0;
ALTER TABLE product_import_issues ADD COLUMN resolved BOOLEAN DEFAULT 0;
ALTER TABLE product_import_issues ADD COLUMN last_retry_at TIMESTAMP;
```

## 📊 Yeni API Metodları

### Repository Metodları:
- `update_import_issue_retry(issue_id, retry_count)`: Retry sayısını güncelle
- `mark_import_issue_resolved(issue_id)`: Hatayı çözüldü olarak işaretle
- `get_import_issues_by_domain(domain, limit)`: Domain bazlı hataları getir
- `get_import_issue_statistics()`: Genel istatistikler

### Model Metodları:
- `_extract_domain(url)`: URL'den domain çıkar
- `_categorize_error(reason, scraped_data)`: Hatayı otomatik kategorize et

## 🎯 Kullanım Örnekleri

### Hata Kaydetme (Otomatik Kategorizasyon):
```python
ProductImportIssue.create(
    user_id=user_id,
    url=url,
    status='failed',
    reason='Ürün fiyatı bulunamadı'
    # error_code ve error_category otomatik belirlenir
    # domain otomatik çıkarılır
    # retry_count otomatik hesaplanır
)
```

### Filtreleme ve İstatistikler:
```python
# Profile route'unda otomatik olarak:
# - Status filtreleme
# - Domain filtreleme  
# - Error category filtreleme
# - İstatistikler hesaplanır
```

## 🔄 Sonraki Adımlar (TODO)

1. **SQLite Migration Scripti**: Yeni kolonları eklemek için
2. **Template Güncellemeleri**: Yeni alanları görüntülemek için
3. **Admin Dashboard**: Gelişmiş istatistikler ve grafikler
4. **Otomatik Retry Önerisi**: Çözüm önerileri ve retry butonu
5. **Email/Bildirim**: Kritik hatalar için bildirim

## 📝 Notlar

- **Geriye Dönük Uyumluluk**: Eski kayıtlar için yeni alanlar `None` olacak
- **Otomatik Kategorizasyon**: Hata mesajından otomatik olarak kategori belirlenir
- **Retry Takibi**: Aynı URL için otomatik retry sayısı hesaplanır
- **Firestore**: Tüm yeni özellikler Firestore'da çalışıyor
- **SQLite**: Migration scripti çalıştırılmalı
