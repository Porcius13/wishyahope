# Firebase Console'da Index Oluşturma - Adım Adım

## 📝 Index Oluşturma Formu

### Collection ID
**Yazılacak:** `products`

### Fields (Alanlar)

1. **Field 1:**
   - Field path: `user_id`
   - Order: `Ascending` (Artan)

2. **Field 2:**
   - Field path: `created_at`
   - Order: `Descending` (Azalan)

### Query scope
- `Collection` seçin (varsayılan)

## 🎯 Tam Adımlar

1. **Firebase Console'a git:**
   - https://console.firebase.google.com/
   - Proje: **miayis**

2. **Firestore Database → Indexes** sekmesine git

3. **"Create Index"** butonuna tıkla

4. **Formu doldur:**
   ```
   Collection ID: products
   
   Field 1:
   - Field path: user_id
   - Order: Ascending
   
   Field 2:
   - Field path: created_at
   - Order: Descending
   ```

5. **"Create"** butonuna tıkla

6. **Bekle:** Index oluşturulması 1-2 dakika sürebilir

## ✅ Index Durumu

- **Building** (Oluşturuluyor): Henüz hazır değil, bekleyin
- **Enabled** (Etkin): Hazır, kullanılabilir

## 🔄 Diğer Gerekli Index'ler

Aynı şekilde şu collection'lar için de index oluşturun:

### 2. Collections
- Collection ID: `collections`
- Fields:
  - `user_id` (Ascending)
  - `created_at` (Descending)

### 3. Price Tracking
- Collection ID: `price_tracking`
- Fields:
  - `user_id` (Ascending)
  - `is_active` (Ascending)
  - `created_at` (Descending)

### 4. Notifications
- Collection ID: `notifications`
- Fields:
  - `user_id` (Ascending)
  - `created_at` (Descending)

### 5. Price History
- Collection ID: `price_history`
- Fields:
  - `product_id` (Ascending)
  - `recorded_at` (Ascending)

## ⚡ Hızlı Yol (Önerilen)

Hata mesajındaki linke tıklayın - otomatik olarak doğru index'i oluşturur!

