# miayis - Ürün Kataloğu

Modern ve kullanıcı dostu bir ürün kataloğu uygulaması. Kullanıcılar ürün URL'lerini ekleyebilir, koleksiyonlar oluşturabilir ve ürünlerini organize edebilir.

## 🚀 Özellikler

- **Ürün Ekleme**: URL'den otomatik ürün bilgisi çekme
- **Koleksiyonlar**: Ürünleri kategorilere ayırma
- **Kullanıcı Sistemi**: Kayıt olma ve giriş yapma
- **Dark Mode**: Karanlık tema desteği
- **Responsive Design**: Mobil uyumlu tasarım
- **Arama ve Filtreleme**: Gelişmiş arama özellikleri
- **Paylaşım**: Koleksiyonları paylaşma

## 🛠️ Teknolojiler

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Web Scraping**: Playwright
- **Deployment**: Render

## 📦 Kurulum

### Yerel Geliştirme

1. Repository'yi klonlayın:
```bash
git clone <repository-url>
cd favit
```

2. Virtual environment oluşturun:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Playwright'ı kurun:
```bash
playwright install chromium
playwright install-deps chromium
```

5. Uygulamayı çalıştırın:
```bash
python app.py
```

### Production Deployment

Render üzerinde otomatik deployment için:

1. Render hesabı oluşturun
2. GitHub repository'nizi bağlayın
3. `render.yaml` dosyası otomatik olarak konfigürasyonu sağlar

## 🔧 Konfigürasyon

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `FLASK_ENV`: Production/development mode
- `FLASK_DEBUG`: Debug mode
- `PORT`: Server port

## 📱 Kullanım

1. **Kayıt Ol**: Yeni hesap oluşturun
2. **Ürün Ekle**: URL'den ürün ekleyin
3. **Koleksiyon Oluştur**: Ürünlerinizi organize edin
4. **Paylaş**: Koleksiyonlarınızı paylaşın

## 🎨 Tasarım

- Modern glassmorphism tasarım
- Gradient renkler
- Smooth animasyonlar
- Responsive layout
- Dark/Light mode

## 📄 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Commit edin
4. Push edin
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.