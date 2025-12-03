# Firestore Index Oluşturma Rehberi

## 🔥 Gerekli Index'ler

### 1. Products Collection - user_id + created_at

**Neden gerekli:** `get_products_by_user_id()` metodu `user_id` ile filtreleyip `created_at` ile sıralıyor.

**Index Detayları:**
- Collection: `products`
- Fields:
  - `user_id` (Ascending)
  - `created_at` (Descending)

**Oluşturma Yöntemi 1: Otomatik Link (Hızlı)**
Hata mesajındaki linke tıklayın:
```
https://console.firebase.google.com/v1/r/project/miayis/firestore/indexes?create_composite=Ckdwcm9qZWN0cy9taWF5aXMvZGF0YWJhc2VzLyhkZWZhdWx0KS9jb2xsZWN0aW9uR3JvdXBzL3Byb2R1Y3RzL2luZGV4ZXMvXxABGgsKB3VzZXJfaWQQARoOCgpjcmVhdGVkX2F0EAIaDAoIX19uYW1lX18QAg
```

**Oluşturma Yöntemi 2: Manuel**
1. Firebase Console: https://console.firebase.google.com/
2. Proje: **miayis**
3. Firestore Database → Indexes
4. "Create Index" butonuna tıkla
5. Collection ID: `products`
6. Fields ekle:
   - Field: `user_id`, Order: Ascending
   - Field: `created_at`, Order: Descending
7. "Create" butonuna tıkla

**Oluşturma Yöntemi 3: firestore.indexes.json (Önerilen)**
Proje kök dizinine `firestore.indexes.json` dosyası oluştur:

```json
{
  "indexes": [
    {
      "collectionGroup": "products",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "created_at",
          "order": "DESCENDING"
        }
      ]
    },
    {
      "collectionGroup": "collections",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "created_at",
          "order": "DESCENDING"
        }
      ]
    },
    {
      "collectionGroup": "price_tracking",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "is_active",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "created_at",
          "order": "DESCENDING"
        }
      ]
    },
    {
      "collectionGroup": "notifications",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "created_at",
          "order": "DESCENDING"
        }
      ]
    },
    {
      "collectionGroup": "price_history",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "product_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "recorded_at",
          "order": "ASCENDING"
        }
      ]
    }
  ],
  "fieldOverrides": []
}
```

Sonra Firebase CLI ile deploy et:
```bash
firebase deploy --only firestore:indexes
```

## ⏱️ Index Oluşturma Süresi

- Küçük collection'lar: 1-2 dakika
- Büyük collection'lar: 5-10 dakika
- Index oluşturulurken query'ler çalışmaya devam eder (daha yavaş olabilir)

## ✅ Index Oluşturulduktan Sonra

Index oluşturulduktan sonra hata kaybolacak ve query'ler normal hızda çalışacak.

## 🔍 Index Durumunu Kontrol Etme

Firebase Console → Firestore Database → Indexes
- **Building**: Hala oluşturuluyor
- **Enabled**: Hazır ve kullanılabilir

