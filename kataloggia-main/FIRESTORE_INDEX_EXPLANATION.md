# Firestore Index'ler Neden Gerekli?

## 🔍 Temel Konsept

Firestore, **NoSQL** bir veritabanıdır. SQLite gibi SQL veritabanlarından farklı olarak, **composite query'ler** (birden fazla alan üzerinde filtreleme + sıralama) için **önceden index oluşturulması** gerekir.

## 📊 Örnek Senaryolar

### Senaryo 1: Basit Query (Index GEREKMEZ)
```python
# Sadece tek bir alan ile filtreleme
products = db.collection('products').where('user_id', '==', user_id).stream()
```
✅ **Index gerekmez** - Firestore otomatik olarak single-field index'leri oluşturur.

### Senaryo 2: Filtreleme + Sıralama (Index GEREKİR)
```python
# Filtreleme + Sıralama
products = db.collection('products')
    .where('user_id', '==', user_id)
    .order_by('created_at', direction=DESCENDING)
    .stream()
```
❌ **Index GEREKİR** - Çünkü hem `user_id` ile filtreliyoruz, hem de `created_at` ile sıralıyoruz.

### Senaryo 3: Çoklu Filtreleme (Index GEREKİR)
```python
# İki alan ile filtreleme
products = db.collection('price_tracking')
    .where('user_id', '==', user_id)
    .where('is_active', '==', True)
    .order_by('created_at', direction=DESCENDING)
    .stream()
```
❌ **Index GEREKİR** - Çünkü iki farklı alan ile filtreliyoruz ve sıralıyoruz.

## 🎯 Bizim Kullandığımız Query'ler

### 1. Products - Kullanıcı Ürünlerini Listeleme
```python
# Firestore Repository'de:
docs = db.collection('products')
    .where('user_id', '==', user_id)
    .order_by('created_at', direction=DESCENDING)
    .stream()
```

**Gerekli Index:**
- Collection: `products`
- Fields:
  - `user_id` (Ascending)
  - `created_at` (Descending)

### 2. Price Tracking - Aktif Takip Listesi
```python
docs = db.collection('price_tracking')
    .where('user_id', '==', user_id)
    .where('is_active', '==', True)
    .order_by('created_at', direction=DESCENDING)
    .stream()
```

**Gerekli Index:**
- Collection: `price_tracking`
- Fields:
  - `user_id` (Ascending)
  - `is_active` (Ascending)
  - `created_at` (Descending)

### 3. Notifications - Kullanıcı Bildirimleri
```python
docs = db.collection('notifications')
    .where('user_id', '==', user_id)
    .order_by('created_at', direction=DESCENDING)
    .stream()
```

**Gerekli Index:**
- Collection: `notifications`
- Fields:
  - `user_id` (Ascending)
  - `created_at` (Descending)

## ⚡ Performans Etkisi

### Index OLMADAN:
- ❌ Query çalışmaz (FailedPrecondition hatası)
- ❌ Veya çok yavaş çalışır (tüm collection'ı tarar)

### Index İLE:
- ✅ Query hızlı çalışır
- ✅ Sadece ilgili dokümanları okur
- ✅ Ölçeklenebilir (milyonlarca kayıt olsa bile hızlı)

## 🔧 Index Oluşturma

### Otomatik (Hata Mesajından)
Firestore bir index gerektiğinde otomatik olarak bir link verir:
```
https://console.firebase.google.com/v1/r/project/miayis/firestore/indexes?create_composite=...
```
Bu linke tıklayarak index'i otomatik oluşturabilirsiniz.

### Manuel (Firebase Console)
1. Firebase Console → Firestore Database → Indexes
2. "Create Index" butonuna tıklayın
3. Collection ve field'ları seçin
4. "Create" butonuna tıklayın

### firestore.indexes.json (Önerilen - Production)
Proje kök dizinine `firestore.indexes.json` dosyası oluşturup Firebase CLI ile deploy edin:
```bash
firebase deploy --only firestore:indexes
```

## 📝 Özet

**Index ne zaman gerekir?**
- ✅ Tek alan filtreleme → **GEREKMEZ** (otomatik)
- ❌ Filtreleme + Sıralama → **GEREKİR**
- ❌ Çoklu alan filtreleme → **GEREKİR**
- ❌ Filtreleme + Sıralama + Çoklu alan → **GEREKİR**

**Neden gerekir?**
- Firestore performans için index'leri kullanır
- Index olmadan tüm collection'ı taramak gerekir (yavaş ve pahalı)
- Index ile sadece ilgili dokümanları okur (hızlı ve verimli)

## 🚀 Bizim Durumumuz

Şu anda geçici çözüm uyguladık (memory'de sort ediyoruz), ama **performans için index oluşturmanız önerilir**.

Index oluşturduktan sonra query'yi tekrar `order_by` kullanacak şekilde güncelleyebiliriz.

