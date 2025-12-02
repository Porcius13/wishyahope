# 🚀 Farklı Lokalde Çalıştırma Rehberi

## 📋 Gereksinimler

1. **Python 3.8+** yüklü olmalı
2. **Git** (opsiyonel, kod çekmek için)
3. **Redis** (opsiyonel, caching için)
4. **Celery** (opsiyonel, background jobs için)

## 🔧 Kurulum Adımları

### 1. Projeyi İndirin/Klonlayın

```bash
# Eğer Git kullanıyorsanız:
git clone <repository-url>
cd kataloggia-main/kataloggia-main

# Veya dosyaları manuel olarak kopyalayın
```

### 2. Virtual Environment Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt

# Playwright browser'ları yükleyin
playwright install
```

### 4. Ortam Değişkenlerini Ayarlayın

Uygulama artık `app/config.Config` ve alt sınıflarını tek merkezi yapılandırma kaynağı olarak kullanır.
Bu sınıflar, hem Flask yapılandırmasını hem de ham `sqlite3` bağlantıları için kullanılacak
veritabanı yolunu okur.

`.env` dosyası oluşturabilir veya kabuk ortam değişkenleri ile değerleri ayarlayabilirsiniz.

## Environment configuration

### Yapılandırma Sınıfları ve Ortam Seçimi

- Uygulama `create_app("development")` ile başlatılır (varsayılan).
- İsterseniz uygulamayı farklı bir config ile başlatabilirsiniz (örn. `create_app("production")`),
  ancak şu anda bunu değiştiren ayrı bir ortam değişkeni tanımlamadık.
- Tüm temel ayarlar `app/config.py` içindeki `Config`, `DevelopmentConfig`, `TestingConfig`,
  `ProductionConfig` sınıflarında tutulur.

### Desteklenen Ortam Değişkenleri

- **SECRET_KEY**
  - **Amaç**: Flask oturum imzalama / güvenlik anahtarı.
  - **Varsayılan**: `favit-secret-key-2025`.
  - **Öneri**: Production ortamında mutlaka güçlü, rastgele bir değer ile override edin.
  - **Örnek**:
    ```bash
    export SECRET_KEY="super-strong-random-secret"
    ```

- **DATABASE_PATH**
  - **Amaç**: Ham `sqlite3` kullanan kodlar (ör. `models.py`, admin sorguları vb.) için
    SQLite veritabanı dosyasının dosya sistemi yolu.
  - **Varsayılan**: `favit.db` – proje kök dizininde veya `app/utils/db_path.py` tarafından
    otomatik bulunan konumda oluşturulur.
  - **Etki**:
    - `get_db_connection()` bu yolu kullanarak SQLite bağlantısı açar.
    - `Config.SQLALCHEMY_DATABASE_URI` de, `DATABASE_URL` tanımlı değilse
      `sqlite:///{DATABASE_PATH}` olarak ayarlanır. Yani `DATABASE_PATH` değiştiğinde,
      hem ham sqlite bağlantıları hem de SQLAlchemy URL’si aynı dosyayı kullanır.
  - **Örnek**:
    ```bash
    export DATABASE_PATH="/absolute/path/to/favit_dev.db"
    ```

- **DATABASE_URL**
  - **Amaç**: SQLAlchemy stilinde tam veritabanı URL’si (örn. `sqlite:///...`,
    `postgres://...` vb.).
  - **Varsayılan**: Ayarlanmazsa, `SQLALCHEMY_DATABASE_URI = sqlite:///{DATABASE_PATH}`
    olarak hesaplanır.
  - **Not**:
    - Basit lokal geliştirme için `DATABASE_URL` zorunlu değildir; yalnızca `DATABASE_PATH`
      yeterlidir.
    - Render gibi ortamlarda platform tarafından verilen bir Postgres URL’si
      `DATABASE_URL` olarak ayarlanabilir.
  - **Örnek**:
    ```bash
    # Lokal SQLite
    export DATABASE_URL="sqlite:///favit.db"

    # Örnek Postgres (deployment)
    export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
    ```

- **REDIS_URL**
  - **Amaç**: Gelecekte Celery / caching için temel Redis URL’si.
  - **Varsayılan**: `redis://localhost:6379/0`.
  - **Not**: `CELERY_BROKER_URL` ve `CELERY_RESULT_BACKEND` tanımlı değilse bu değeri kullanır.
  - **Örnek**:
    ```bash
    export REDIS_URL="redis://localhost:6379/0"
    ```

- **CELERY_BROKER_URL**
  - **Amaç**: Celery mesaj kuyruğu (broker) URL’si (genelde Redis veya RabbitMQ).
  - **Varsayılan**: `REDIS_URL` değeri.
  - **Örnek**:
    ```bash
    export CELERY_BROKER_URL="redis://localhost:6379/1"
    ```

- **CELERY_RESULT_BACKEND**
  - **Amaç**: Celery result backend URL’si.
  - **Varsayılan**: `REDIS_URL` değeri.
  - **Örnek**:
    ```bash
    export CELERY_RESULT_BACKEND="redis://localhost:6379/2"
    ```

- **JWT_SECRET_KEY**
  - **Amaç**: JWT token’ları için gizli anahtar (kullanıldığında).
  - **Varsayılan**: `SECRET_KEY` değeri kullanılır.
  - **Öneri**: JWT aktif olarak kullanılıyorsa production ortamında ayrı ve güçlü
    bir değer ile override edin.
  - **Örnek**:
    ```bash
    export JWT_SECRET_KEY="separate-jwt-secret"
    ```

### Lokal geliştirme örnekleri

Basit lokal geliştirme için genelde varsayılanlar yeterlidir:

```bash
# Sanal ortamı aktive ettikten sonra
python run.py
```

İsterseniz ortam değişkenlerini açıkça ayarlayabilirsiniz:

```bash
export SECRET_KEY="dev-secret"
export DATABASE_PATH="/absolute/path/to/favit_dev.db"
python run.py
```

### 5. Veritabanını Başlatın

```bash
python run.py
# İlk çalıştırmada veritabanı otomatik oluşturulur
```

## 🎯 Çalıştırma

### Yöntem 1: Standart Port (5000)

```bash
python run.py
```

Uygulama: `http://localhost:5000`

### Yöntem 2: Farklı Port

`run.py` dosyasını düzenleyin:

```python
if __name__ == "__main__":
    socketio = get_socketio()
    port = int(os.environ.get('PORT', 5000))  # Varsayılan 5000
    if socketio:
        socketio.run(app, host="0.0.0.0", port=port, debug=True)
    else:
        app.run(host="0.0.0.0", port=port, debug=True)
```

Veya ortam değişkeni ile:

```bash
# Windows PowerShell
$env:PORT=8080; python run.py

# Windows CMD
set PORT=8080 && python run.py

# Linux/Mac
PORT=8080 python run.py
```

### Yöntem 3: Gunicorn ile Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

## 🔍 Sorun Giderme

### Port Zaten Kullanılıyor

```bash
# Windows - Port'u kullanan process'i bulun
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

### Redis Bağlantı Hatası

Redis yüklü değilse, caching devre dışı kalır ama uygulama çalışır.

### Veritabanı Hatası

```bash
# Veritabanını sıfırlamak için
rm favit.db  # Linux/Mac
del favit.db  # Windows
python run.py  # Yeniden oluşturur
```

## 📝 Notlar

- İlk çalıştırmada veritabanı otomatik oluşturulur
- Redis ve Celery opsiyoneldir, olmadan da çalışır
- Debug modu aktif (production'da kapatın)

