import sqlite3
import uuid
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.utils.db_path import get_db_path, get_db_connection

def init_db():
    """Veritabanını başlat"""
    import os
    from app.repositories import get_repository
    from app.config import Config
    
    # Check if using Firestore
    try:
        db_backend = Config.DB_BACKEND
    except:
        db_backend = os.environ.get('DB_BACKEND', 'sqlite')
    
    if db_backend == 'firestore':
        # Firestore doesn't need schema initialization
        repo = get_repository()
        repo.init_db()
        print("[INFO] Firestore database initialized")
        return
    
    # SQLite initialization
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profile_url TEXT UNIQUE,
            last_read_notifications_at TIMESTAMP,
            avatar_url TEXT
        )
    ''')
    
    # Ürünler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT,
            brand TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            old_price TEXT,
            current_price TEXT,
            discount_percentage TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Eksik kolonları ekle (eğer yoksa)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN old_price TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN current_price TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN discount_percentage TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN images TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN discount_info TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez

    # Users tablosuna last_read_notifications_at ekle (backward compatibility)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_read_notifications_at TIMESTAMP')
    except:
        pass

    # Users tablosuna avatar_url ekle (backward compatibility)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_url TEXT')
    except:
        pass

    # Collections tablosuna cover_image ekle (backward compatibility)
    try:
        cursor.execute('ALTER TABLE collections ADD COLUMN cover_image TEXT')
    except:
        pass

    # Koleksiyonlar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            is_public BOOLEAN DEFAULT 1,
            share_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Koleksiyon ürünleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_products (
            id TEXT PRIMARY KEY,
            collection_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (collection_id) REFERENCES collections (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Fiyat takip tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_tracking (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            current_price TEXT NOT NULL,
            original_price TEXT NOT NULL,
            price_change TEXT DEFAULT '0',
            is_active BOOLEAN DEFAULT 1,
            alert_price TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Fiyat geçmişi tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            price TEXT NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Beğeni ve yorum tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            collection_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (collection_id) REFERENCES collections (id)
        )
    ''')
    
    # Takip tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            id TEXT PRIMARY KEY,
            follower_id TEXT NOT NULL,
            following_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users (id),
            FOREIGN KEY (following_id) REFERENCES users (id)
        )
    ''')

    # Favoriler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE(user_id, product_id)
        )
    ''')

    # Bildirimler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Ürün import sorunları tablosu (başarısız veya eksik bilgiyle yüklenenler)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_import_issues (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            url TEXT NOT NULL,
            status TEXT NOT NULL, -- failed | partial
            reason TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at, profile_url, last_read_notifications_at=None, avatar_url=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.profile_url = profile_url
        self.last_read_notifications_at = last_read_notifications_at
        self.avatar_url = avatar_url
    
    @staticmethod
    def get_by_id(user_id):
        """Kullanıcı ID'sine göre kullanıcı getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            user_data = repo.get_user_by_id(user_id)
            
            if user_data:
                # Handle timestamp conversion
                created_at = user_data.get('created_at')
                if hasattr(created_at, 'timestamp'):  # Firestore Timestamp
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                last_read = user_data.get('last_read_notifications_at')
                if last_read and hasattr(last_read, 'timestamp'):  # Firestore Timestamp
                    last_read = last_read
                elif isinstance(last_read, str):
                    try:
                        last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                        except:
                            last_read = None
                
                return User(
                    user_data.get('id'),
                    user_data.get('username'),
                    user_data.get('email'),
                    user_data.get('password_hash'),
                    created_at,
                    user_data.get('profile_url'),
                    last_read,
                    user_data.get('avatar_url')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get user by id error: {e}")
            return None
    
    @staticmethod
    def get_by_username(username):
        """Kullanıcı adına göre kullanıcı getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            user_data = repo.get_user_by_username(username)
            
            if user_data:
                # Handle timestamp conversion (same as get_by_id)
                created_at = user_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                last_read = user_data.get('last_read_notifications_at')
                if last_read and hasattr(last_read, 'timestamp'):
                    last_read = last_read
                elif isinstance(last_read, str):
                    try:
                        last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                        except:
                            last_read = None
                
                return User(
                    user_data.get('id'),
                    user_data.get('username'),
                    user_data.get('email'),
                    user_data.get('password_hash'),
                    created_at,
                    user_data.get('profile_url'),
                    last_read,
                    user_data.get('avatar_url')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get user by username error: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Email'e göre kullanıcı getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            user_data = repo.get_user_by_email(email)
            
            if user_data:
                # Handle timestamp conversion (same as get_by_id)
                created_at = user_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                last_read = user_data.get('last_read_notifications_at')
                if last_read and hasattr(last_read, 'timestamp'):
                    last_read = last_read
                elif isinstance(last_read, str):
                    try:
                        last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                        except:
                            last_read = None
                
                return User(
                    user_data.get('id'),
                    user_data.get('username'),
                    user_data.get('email'),
                    user_data.get('password_hash'),
                    created_at,
                    user_data.get('profile_url'),
                    last_read,
                    user_data.get('avatar_url')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get user by email error: {e}")
            return None
    
    @staticmethod
    def get_by_profile_url(profile_url):
        """Profile URL'e göre kullanıcı getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            user_data = repo.get_user_by_profile_url(profile_url)
            
            if user_data:
                # Handle timestamp conversion (same as get_by_id)
                created_at = user_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                last_read = user_data.get('last_read_notifications_at')
                if last_read and hasattr(last_read, 'timestamp'):
                    last_read = last_read
                elif isinstance(last_read, str):
                    try:
                        last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                        except:
                            last_read = None
                
                return User(
                    user_data.get('id'),
                    user_data.get('username'),
                    user_data.get('email'),
                    user_data.get('password_hash'),
                    created_at,
                    user_data.get('profile_url'),
                    last_read,
                    user_data.get('avatar_url')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get user by profile url error: {e}")
            return None
    
    @staticmethod
    def create(username, email, password):
        """Yeni kullanıcı oluştur"""
        try:
            from app.repositories import get_repository
            from app.config import Config
            
            repo = get_repository()
            password_hash = generate_password_hash(password)
            profile_url = f"user_{str(uuid.uuid4())[:8]}"
            created_at = datetime.now()
            
            # Check if user already exists
            if repo.get_user_by_username(username):
                raise Exception("Bu kullanıcı adı zaten kullanılıyor")
            if repo.get_user_by_email(email):
                raise Exception("Bu email zaten kullanılıyor")
            
            # Create user via repository
            user_id = repo.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                profile_url=profile_url,
                created_at=created_at,
                last_read_notifications_at=None,
                avatar_url=None
            )
            
            # Return User object (fetch from repository to ensure consistency)
            user_data = repo.get_user_by_id(user_id)
            if not user_data:
                raise Exception("Kullanıcı oluşturuldu ama veritabanından okunamadı")
            
            # Convert dict to User object
            # Handle timestamp conversion for Firestore
            created_at = user_data.get('created_at')
            if created_at and hasattr(created_at, 'timestamp'):  # Firestore Timestamp
                # Firestore Timestamp object, convert to datetime
                created_at = created_at
            elif isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = datetime.now()
            elif created_at is None:
                created_at = datetime.now()
            
            last_read = user_data.get('last_read_notifications_at')
            if last_read and hasattr(last_read, 'timestamp'):  # Firestore Timestamp
                last_read = last_read
            elif isinstance(last_read, str):
                try:
                    last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                    except:
                        last_read = None
            
            return User(
                user_data.get('id'),
                user_data.get('username'),
                user_data.get('email'),
                user_data.get('password_hash'),
                created_at,
                user_data.get('profile_url'),
                last_read,
                user_data.get('avatar_url')
            )
        except Exception as e:
            print(f"[HATA] Kullanıcı oluşturma hatası: {e}")
            raise Exception(f"Kullanıcı oluşturulamadı: {str(e)}")
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def get_products(self):
        """Kullanıcının ürünlerini getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            from app.models.product import Product
            
            repo = get_repository()
            products_data = repo.get_products_by_user_id(self.id)
            
            products = []
            for p_data in products_data:
                # Handle images
                images_data = p_data.get('images')
                if isinstance(images_data, str):
                    import json
                    try:
                        images_data = json.loads(images_data)
                    except:
                        images_data = [p_data.get('image')] if p_data.get('image') else []
                elif not images_data:
                    images_data = [p_data.get('image')] if p_data.get('image') else []
                
                # Handle timestamp
                created_at_data = p_data.get('created_at')
                if hasattr(created_at_data, 'timestamp'):
                    created_at_data = created_at_data
                elif isinstance(created_at_data, str):
                    try:
                        created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at_data = datetime.now()
                elif created_at_data is None:
                    created_at_data = datetime.now()
                
                products.append(Product(
                    p_data.get('id'),
                    p_data.get('user_id'),
                    p_data.get('name'),
                    p_data.get('price'),
                    p_data.get('image'),
                    p_data.get('brand'),
                    p_data.get('url'),
                    created_at_data,
                    p_data.get('old_price'),
                    p_data.get('current_price'),
                    p_data.get('discount_percentage'),
                    images_data,
                    p_data.get('discount_info')
                ))
            
            return products
        except Exception as e:
            print(f"[ERROR] Get user products error: {e}")
            return []
    
    def get_collections(self):
        """Kullanıcının koleksiyonlarını getir"""
        return Collection.get_user_collections(self.id)

    def set_password(self, new_password):
        """Kullanıcının şifresini güncelle ve veritabanına kaydet (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            new_hash = generate_password_hash(new_password)
            repo = get_repository()
            result = repo.update_user(self.id, password_hash=new_hash)
            
            if result:
                self.password_hash = new_hash
                return True
            return False
        except Exception as e:
            print(f"[HATA] Şifre güncelleme hatası: {e}")
            return False

    def save(self):
        """Kullanıcı bilgilerini güncellemek için save metodu (Repository üzerinden)"""
        try:
            from app.repositories import get_repository

            repo = get_repository()
            success = repo.update_user(
                self.id,
                username=self.username,
                email=self.email,
                avatar_url=self.avatar_url
            )

            if not success:
                raise Exception("User update failed in repository")

        except Exception as e:
            print(f"[HATA] Kullanıcı kaydetme hatası: {e}")
            raise


class ProductImportIssue:
    """Ürün eklenirken yaşanan sorunları (başarısız/eksik) saklar"""

    def __init__(self, id, user_id, url, status, reason, raw_data, created_at):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.status = status  # failed | partial
        self.reason = reason
        self.raw_data = raw_data
        self.created_at = created_at

    @staticmethod
    def create(user_id, url, status, reason=None, raw_data=None):
        """Yeni import sorunu kaydı oluştur (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            
            # raw_data'yı JSON string'e çevir
            import json
            raw_str = None
            if raw_data is not None:
                try:
                    raw_str = json.dumps(raw_data, ensure_ascii=False) if not isinstance(raw_data, str) else raw_data
                except Exception:
                    raw_str = str(raw_data)
            
            issue_id = repo.create_import_issue(
                user_id=user_id,
                url=url,
                status=status,
                reason=reason,
                raw_data=raw_str,
                created_at=datetime.now()
            )

            # Basit dosya logu: ürün linki + hata mesajı
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(base_dir)
                logs_dir = os.path.join(project_root, "logs")
                os.makedirs(logs_dir, exist_ok=True)
                log_path = os.path.join(logs_dir, "import_issues.log")

                with open(log_path, "a", encoding="utf-8") as f:
                    ts = datetime.now().isoformat(timespec="seconds")
                    safe_reason = (reason or "").replace("\n", " ").strip()
                    f.write(f"[{ts}] status={status} user_id={user_id} url={url} reason={safe_reason}\n")
            except Exception as file_err:
                # Dosyaya yazma hatası uygulamayı bozmasın, sadece logla
                print(f"[WARN] Could not write import issue to file log: {file_err}")

            return ProductImportIssue(issue_id, user_id, url, status, reason, raw_str, datetime.now())
        except Exception as e:
            print(f"[ERROR] Create import issue error: {e}")
            raise

    @staticmethod
    def get_by_user_id(user_id, limit=50):
        """Kullanıcının son import sorunlarını getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            issues_data = repo.get_import_issues_by_user_id(user_id, limit)
            
            issues = []
            for issue_data in issues_data:
                # Handle timestamp conversion
                created_at = issue_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                issues.append(ProductImportIssue(
                    issue_data.get('id'),
                    issue_data.get('user_id'),
                    issue_data.get('url'),
                    issue_data.get('status'),
                    issue_data.get('reason'),
                    issue_data.get('raw_data'),
                    created_at
                ))
            
            return issues
        except Exception as e:
            print(f"[ERROR] Get import issues by user id error: {e}")
            return []

class Product:
    def __init__(self, id, user_id, name, price, image, brand, url, created_at, old_price=None, current_price=None, discount_percentage=None, images=None, discount_info=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.price = price
        self.image = image
        self.brand = brand
        self.url = url
        self.created_at = created_at
        self.old_price = old_price
        self.current_price = current_price
        self.discount_percentage = discount_percentage
        self.discount_info = discount_info
        # images JSON array olarak saklanır, parse et
        if images:
            try:
                import json
                self.images = json.loads(images) if isinstance(images, str) else images
            except:
                self.images = [image] if image else []
        else:
            # Eğer images yoksa, mevcut image'i kullan (backward compatibility)
            self.images = [image] if image else []
    
    @staticmethod
    def create(user_id, name, price, image, brand, url, old_price=None, current_price=None, discount_percentage=None, images=None, discount_info=None):
        """Yeni ürün oluştur"""
        try:
            from app.repositories import get_repository
            from app.config import Config
            
            # Debug: Check which backend is being used
            db_backend = Config.DB_BACKEND
            print(f"[DEBUG Product.create] DB_BACKEND: {db_backend}")
            
            repo = get_repository()
            repo_type = type(repo).__name__
            print(f"[DEBUG Product.create] Repository type: {repo_type}")
            
            created_at = datetime.now()
            
            # Create product via repository
            print(f"[DEBUG Product.create] Creating product: name={name}, user_id={user_id}")
            product_id = repo.create_product(
                user_id=user_id,
                name=name,
                price=price,
                image=image,
                brand=brand,
                url=url,
                created_at=created_at,
                old_price=old_price,
                current_price=current_price,
                discount_percentage=discount_percentage,
                images=images,
                discount_info=discount_info
            )
            print(f"[DEBUG Product.create] Product created with ID: {product_id}")
            
            # Return Product object (fetch from repository to ensure consistency)
            product_data = repo.get_product_by_id(product_id)
            if not product_data:
                raise Exception("Ürün oluşturuldu ama veritabanından okunamadı")
            
            # Handle images - repository returns as list for Firestore, but SQLite might be JSON string
            images_data = product_data.get('images')
            if isinstance(images_data, str):
                import json
                try:
                    images_data = json.loads(images_data)
                except:
                    images_data = [product_data.get('image')] if product_data.get('image') else []
            elif not images_data:
                images_data = [product_data.get('image')] if product_data.get('image') else []
            
            # Handle timestamp conversion
            created_at_data = product_data.get('created_at')
            if hasattr(created_at_data, 'timestamp'):  # Firestore Timestamp
                created_at_data = created_at_data
            elif isinstance(created_at_data, str):
                try:
                    created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at_data = datetime.now()
            elif created_at_data is None:
                created_at_data = datetime.now()
            
            return Product(
                product_data.get('id'),
                product_data.get('user_id'),
                product_data.get('name'),
                product_data.get('price'),
                product_data.get('image'),
                product_data.get('brand'),
                product_data.get('url'),
                created_at_data,
                product_data.get('old_price'),
                product_data.get('current_price'),
                product_data.get('discount_percentage'),
                images_data,
                product_data.get('discount_info')
            )
        except Exception as e:
            print(f"[HATA] Ürün oluşturma hatası: {e}")
            raise Exception(f"Ürün oluşturulamadı: {str(e)}")
    
    @staticmethod
    def get_by_id(product_id):
        """ID ile ürün getir (Repository pattern)"""
        from app.repositories import get_repository
        from datetime import datetime
        import json
        
        repo = get_repository()
        product_data = repo.get_product_by_id(product_id)
        
        if not product_data:
            return None
        
        # Handle images
        images_data = product_data.get('images')
        if isinstance(images_data, str):
            try:
                images_data = json.loads(images_data)
            except:
                images_data = [product_data.get('image')] if product_data.get('image') else []
        elif not images_data:
            images_data = [product_data.get('image')] if product_data.get('image') else []
        
        # Handle timestamp
        created_at = product_data.get('created_at')
        if hasattr(created_at, 'timestamp'):  # Firestore Timestamp
            created_at = created_at
        elif isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        return Product(
            product_data.get('id'),
            product_data.get('user_id'),
            product_data.get('name'),
            product_data.get('price'),
            product_data.get('image'),
            product_data.get('brand'),
            product_data.get('url'),
            created_at,
            product_data.get('old_price'),
            product_data.get('current_price'),
            product_data.get('discount_percentage'),
            images_data,
            product_data.get('discount_info')
        )
    
    @staticmethod
    def update(product_id, user_id, **kwargs):
        """Ürün güncelle (Repository pattern ile)"""
        from app.repositories import get_repository

        allowed_fields = [
            'name',
            'price',
            'image',
            'brand',
            'url',
            'old_price',
            'current_price',
            'discount_percentage',
            'images',
            'discount_info',
        ]

        update_data = {}

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                # images list ise list olarak repo'ya gönder; JSON'a çevirme işini repo halletsin
                if field == 'images' and isinstance(value, list):
                    update_data['images'] = value
                else:
                    update_data[field] = value

        # Güncellenecek bir şey yoksa
        if not update_data:
            return None

        repo = get_repository()
        success = repo.update_product(product_id, user_id, **update_data)

        if not success:
            return None

        # Güncel ürünü tekrar çekip döndür
        return Product.get_by_id(product_id)
    
    @staticmethod
    def delete(product_id, user_id):
        """Ürün sil - Repository pattern"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            
            # Delete product via repository (repository handles all related deletions)
            success = repo.delete_product(product_id, user_id)
            
            if not success:
                print(f"[HATA] Ürün silinemedi: {product_id} (kullanıcı: {user_id})")
                return False
            
            return True
        except Exception as e:
            print(f"[HATA] Ürün silme hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

class Collection:
    def __init__(self, id, user_id, name, description, type, is_public, share_url, created_at, cover_image=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.type = type
        self.is_public = is_public
        self.share_url = share_url
        self.cover_image = cover_image
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    self.created_at = datetime.now()
        else:
            self.created_at = created_at
    
    @staticmethod
    def create(user_id, name, description, type, is_public=True, cover_image=None):
        """Yeni koleksiyon oluştur (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            collection_id = str(uuid.uuid4())
            share_url = f"collection_{collection_id[:8]}"
            created_at = datetime.now()
            
            print(f"[DEBUG Collection.create] Creating collection: name={name}, user_id={user_id}")
            
            # Create collection via repository
            created_id = repo.create_collection(
                user_id=user_id,
                name=name,
                description=description,
                collection_type=type,
                is_public=is_public,
                share_url=share_url,
                created_at=created_at,
                cover_image=cover_image
            )
            
            print(f"[DEBUG Collection.create] Collection created: {created_id}")
            
            return Collection(created_id, user_id, name, description, type, is_public, share_url, created_at, cover_image)
        except Exception as e:
            print(f"[ERROR] Create collection error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    def get_by_id(collection_id):
        """ID ile koleksiyon getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            collection_data = repo.get_collection_by_id(collection_id)
            
            if collection_data:
                # Handle timestamp conversion
                created_at = collection_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                return Collection(
                    collection_data.get('id'),
                    collection_data.get('user_id'),
                    collection_data.get('name'),
                    collection_data.get('description'),
                    collection_data.get('type'),
                    collection_data.get('is_public', True),
                    collection_data.get('share_url'),
                    created_at,
                    collection_data.get('cover_image')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get collection by id error: {e}")
            return None
    
    @staticmethod
    def get_by_share_url(share_url):
        """Share URL ile koleksiyon getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            collection_data = repo.get_collection_by_share_url(share_url)
            
            if collection_data:
                # Handle timestamp conversion
                created_at = collection_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                return Collection(
                    collection_data.get('id'),
                    collection_data.get('user_id'),
                    collection_data.get('name'),
                    collection_data.get('description'),
                    collection_data.get('type'),
                    collection_data.get('is_public', True),
                    collection_data.get('share_url'),
                    created_at
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get collection by share url error: {e}")
            return None
    
    @staticmethod
    def get_user_collections(user_id):
        """Kullanıcının koleksiyonlarını getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            collections_data = repo.get_collections_by_user_id(user_id)
            
            collections = []
            for col_data in collections_data:
                # Handle timestamp conversion
                created_at = col_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                collections.append(Collection(
                    col_data.get('id'),
                    col_data.get('user_id'),
                    col_data.get('name'),
                    col_data.get('description'),
                    col_data.get('type'),
                    col_data.get('is_public', True),
                    col_data.get('share_url'),
                    created_at,
                    col_data.get('cover_image')
                ))
            
            return collections
        except Exception as e:
            print(f"[ERROR] Get user collections error: {e}")
            return []
    

    
    def get_products(self):
        """Koleksiyondaki ürünleri getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            from app.models.product import Product
            
            repo = get_repository()
            products_data = repo.get_products_by_collection_id(self.id)
            
            products = []
            for p_data in products_data:
                # Handle images
                images_data = p_data.get('images')
                if isinstance(images_data, str):
                    import json
                    try:
                        images_data = json.loads(images_data)
                    except:
                        images_data = [p_data.get('image')] if p_data.get('image') else []
                elif not images_data:
                    images_data = [p_data.get('image')] if p_data.get('image') else []
                
                # Handle timestamp
                created_at_data = p_data.get('created_at')
                if hasattr(created_at_data, 'timestamp'):
                    created_at_data = created_at_data
                elif isinstance(created_at_data, str):
                    try:
                        created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at_data = datetime.now()
                elif created_at_data is None:
                    created_at_data = datetime.now()
                
                products.append(Product(
                    p_data.get('id'),
                    p_data.get('user_id'),
                    p_data.get('name'),
                    p_data.get('price'),
                    p_data.get('image'),
                    p_data.get('brand'),
                    p_data.get('url'),
                    created_at_data,
                    p_data.get('old_price'),
                    p_data.get('current_price'),
                    p_data.get('discount_percentage'),
                    images_data,
                    p_data.get('discount_info')
                ))
            
            return products
        except Exception as e:
            print(f"[ERROR] Get collection products error: {e}")
            return []
    
    def add_product(self, product_id):
        """Koleksiyona ürün ekle (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            
            # Ürünün kullanıcıya ait olduğunu kontrol et (güvenlik)
            product = repo.get_product_by_id(product_id)
            if not product or product.get('user_id') != self.user_id:
                print(f"[WARNING] Product {product_id} not found or not owned by user {self.user_id}")
                return False
            
            print(f"[DEBUG Collection.add_product] Adding product {product_id} to collection {self.id}")
            result = repo.add_product_to_collection(self.id, product_id)
            print(f"[DEBUG Collection.add_product] Result: {result}")
            return result
        except Exception as e:
            print(f"[HATA] Koleksiyona ürün ekleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_product(self, product_id):
        """Koleksiyondan ürün çıkar (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG Collection.remove_product] Removing product {product_id} from collection {self.id}")
            result = repo.remove_product_from_collection(self.id, product_id)
            print(f"[DEBUG Collection.remove_product] Result: {result}")
            return result
        except Exception as e:
            print(f"[HATA] Koleksiyondan ürün çıkarma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete(self):
        """Koleksiyonu sil (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG Collection.delete] Deleting collection {self.id}")
            result = repo.delete_collection(self.id, self.user_id)
            print(f"[DEBUG Collection.delete] Result: {result}")
            return result
        except Exception as e:
            print(f"[HATA] Koleksiyon silme hatası: {e}")
            import traceback
            traceback.print_exc()
            return False


class PriceTracking:
    def __init__(self, id, product_id, user_id, current_price, original_price, price_change, is_active, alert_price, created_at, last_checked):
        self.id = id
        self.product_id = product_id
        self.user_id = user_id
        self.current_price = current_price
        self.original_price = original_price
        self.price_change = price_change
        self.is_active = is_active
        self.alert_price = alert_price
        self.created_at = created_at
        self.last_checked = last_checked
    
    @staticmethod
    def create(user_id, product_id, current_price, original_price=None, alert_price=None):
        """Fiyat takibi oluştur (Repository pattern)"""
        try:
            from app.repositories import get_repository
            from app.config import Config
            
            # Debug: Check which backend is being used
            db_backend = Config.DB_BACKEND
            print(f"[DEBUG PriceTracking.create] DB_BACKEND: {db_backend}")
            
            repo = get_repository()
            repo_type = type(repo).__name__
            print(f"[DEBUG PriceTracking.create] Repository type: {repo_type}")
            
            original_price = original_price or current_price
            
            print(f"[DEBUG PriceTracking.create] Creating tracking: user_id={user_id}, product_id={product_id}, price={current_price}")
            
            # Create price tracking via repository
            tracking_id = repo.create_price_tracking(
                user_id=user_id,
                product_id=product_id,
                current_price=current_price,
                original_price=original_price,
                alert_price=alert_price
            )
            
            # Add to price history
            from datetime import datetime
            repo.add_price_history(product_id, current_price, datetime.now())
            
            print(f"[DEBUG PriceTracking.create] Tracking created: {tracking_id}")
            return tracking_id
        except Exception as e:
            print(f"[ERROR] Create price tracking error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    def get_by_id(tracking_id):
        """ID ile takip getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            tracking_data = repo.get_price_tracking_by_id(tracking_id)
            
            if tracking_data:
                # Convert dict to tuple format for backward compatibility
                return (
                    tracking_data.get('id'),
                    tracking_data.get('product_id'),
                    tracking_data.get('user_id'),
                    tracking_data.get('current_price'),
                    tracking_data.get('price_change', '0'),
                    tracking_data.get('original_price'),
                    tracking_data.get('is_active', True),
                    tracking_data.get('alert_price'),
                    tracking_data.get('created_at'),
                    tracking_data.get('last_checked')
                )
            return None
        except Exception as e:
            print(f"[ERROR] Get price tracking by id error: {e}")
            return None

    @staticmethod
    def delete(tracking_id):
        """Takibi sil (soft delete)"""
        return PriceTracking.remove_tracking(tracking_id)

    @staticmethod
    def get_by_product_and_user(product_id, user_id):
        """Belirli bir ürün için kullanıcının takip kaydını getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            from app.config import Config
            
            # Debug: Check which backend is being used
            db_backend = Config.DB_BACKEND
            print(f"[DEBUG PriceTracking.get_by_product_and_user] DB_BACKEND: {db_backend}")
            
            repo = get_repository()
            repo_type = type(repo).__name__
            print(f"[DEBUG PriceTracking.get_by_product_and_user] Repository type: {repo_type}")
            print(f"[DEBUG PriceTracking.get_by_product_and_user] Checking: product_id={product_id}, user_id={user_id}")
            
            tracking_data = repo.get_price_tracking_by_product_and_user(product_id, user_id)
            
            if tracking_data:
                print(f"[DEBUG PriceTracking.get_by_product_and_user] Found existing tracking: {tracking_data.get('id')}")
                # Convert dict to tuple format for backward compatibility
                return (
                    tracking_data.get('id'),
                    tracking_data.get('product_id'),
                    tracking_data.get('user_id'),
                    tracking_data.get('current_price'),
                    tracking_data.get('price_change', '0'),
                    tracking_data.get('original_price'),
                    tracking_data.get('is_active', True),
                    tracking_data.get('alert_price'),
                    tracking_data.get('created_at'),
                    tracking_data.get('last_checked')
                )
            else:
                print(f"[DEBUG PriceTracking.get_by_product_and_user] No existing tracking found")
            return None
        except Exception as e:
            print(f"[ERROR] Get price tracking by product and user error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def remove_tracking(tracking_id):
        """Fiyat takibini kaldır (pasif hale getir) - Repository pattern"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG PriceTracking.remove_tracking] Removing tracking: {tracking_id}")
            
            # Get tracking to find user_id
            tracking_data = repo.get_price_tracking_by_id(tracking_id)
            if not tracking_data:
                print(f"[WARNING] Tracking not found: {tracking_id}")
                return False
            
            # Deactivate tracking
            result = repo.update_price_tracking(tracking_id, is_active=False)
            print(f"[DEBUG PriceTracking.remove_tracking] Result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Remove tracking error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_user_tracking(user_id):
        """Kullanıcının fiyat takiplerini getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG PriceTracking.get_user_tracking] Getting trackings for user: {user_id}")
            
            trackings_data = repo.get_price_trackings_by_user_id(user_id)
            print(f"[DEBUG PriceTracking.get_user_tracking] Found {len(trackings_data)} trackings")
            
            # Convert to tuple format for backward compatibility with template
            trackings = []
            for data in trackings_data:
                # Handle timestamp conversion
                created_at = data.get('created_at')
                if hasattr(created_at, 'timestamp'):  # Firestore Timestamp
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                last_checked = data.get('last_checked', created_at)
                if hasattr(last_checked, 'timestamp'):  # Firestore Timestamp
                    last_checked = last_checked
                elif isinstance(last_checked, str):
                    try:
                        last_checked = datetime.strptime(last_checked, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            last_checked = datetime.strptime(last_checked, '%Y-%m-%d %H:%M:%S')
                        except:
                            last_checked = created_at
                elif last_checked is None:
                    last_checked = created_at
                
                # Return tuple format: (id, product_id, user_id, current_price, price_change, original_price, is_active, alert_price, created_at, last_checked, name, brand, image)
                trackings.append((
                    data.get('id'),
                    data.get('product_id'),
                    data.get('user_id'),
                    data.get('current_price'),
                    data.get('price_change', '0'),
                    data.get('original_price'),
                    data.get('is_active', True),
                    data.get('alert_price'),
                    created_at,
                    last_checked,
                    data.get('product_name'),
                    data.get('product_brand'),
                    data.get('product_image')
                ))
            
            print(f"[DEBUG PriceTracking.get_user_tracking] Returning {len(trackings)} trackings")
            return trackings
        except Exception as e:
            print(f"[ERROR] Get user tracking error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def update_price(tracking_id, new_price):
        """Fiyat güncelle"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mevcut fiyatı ve ürün bilgisini al
        cursor.execute('SELECT product_id, current_price, original_price FROM price_tracking WHERE id = ?', (tracking_id,))
        current_data = cursor.fetchone()
        
        if current_data:
            product_id, current_price, original_price = current_data
            
            # Fiyat değişimini hesapla
            try:
                current_num = float(str(current_price).replace('₺', '').replace('TL', '').replace(',', '').strip())
                new_num = float(str(new_price).replace('₺', '').replace('TL', '').replace(',', '').strip())
                price_change = new_num - current_num
            except Exception:
                price_change = 0
            
            # Fiyat takibini güncelle
            cursor.execute('''
                UPDATE price_tracking 
                SET current_price = ?, price_change = ?, last_checked = ?
                WHERE id = ?
            ''', (new_price, str(price_change), datetime.now(), tracking_id))
            
            # Fiyat geçmişine doğru product_id ile kayıt ekle
            history_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO price_history (id, product_id, price)
                VALUES (?, ?, ?)
            ''', (history_id, product_id, new_price))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False


class Notification:
    """Persisted user notifications (e.g. price drops)"""

    def __init__(self, id, user_id, product_id, type, message, payload, created_at, read_at):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.type = type
        self.message = message
        self.payload = payload
        self.created_at = created_at
        self.read_at = read_at

    @staticmethod
    def create(user_id, product_id=None, type='PRICE_DROP', message='', payload=None):
        """Yeni bildirim oluştur (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            
            # Handle payload
            payload_str = None
            if payload is not None:
                if isinstance(payload, str):
                    payload_str = payload
                else:
                    try:
                        payload_str = json.dumps(payload, ensure_ascii=False)
                    except Exception:
                        payload_str = str(payload)
            
            print(f"[DEBUG Notification.create] Creating notification: user_id={user_id}, type={type}")
            notif_id = repo.create_notification(
                user_id=user_id,
                product_id=product_id,
                notification_type=type,
                message=message,
                payload=payload_str,
                created_at=datetime.now()
            )
            print(f"[DEBUG Notification.create] Notification created: {notif_id}")
            return notif_id
        except Exception as e:
            print(f"[ERROR] Create notification error: {e}")
            import traceback
            traceback.print_exc()
            raise

    @staticmethod
    def get_for_user(user_id, limit=50):
        """Kullanıcının bildirimlerini getir (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            notifications_data = repo.get_notifications_by_user_id(user_id, limit)
            
            notifications = []
            for notif_data in notifications_data:
                # Handle timestamp conversion
                created_at = notif_data.get('created_at')
                if hasattr(created_at, 'timestamp'):
                    created_at = created_at
                elif isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at = datetime.now()
                elif created_at is None:
                    created_at = datetime.now()
                
                read_at = notif_data.get('read_at')
                if read_at and hasattr(read_at, 'timestamp'):
                    read_at = read_at
                elif isinstance(read_at, str):
                    try:
                        read_at = datetime.strptime(read_at, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            read_at = datetime.strptime(read_at, '%Y-%m-%d %H:%M:%S')
                        except:
                            read_at = None
                
                notifications.append(Notification(
                    notif_data.get('id'),
                    notif_data.get('user_id'),
                    notif_data.get('product_id'),
                    notif_data.get('type'),
                    notif_data.get('message'),
                    notif_data.get('payload'),
                    created_at,
                    read_at
                ))
            
            return notifications
        except Exception as e:
            print(f"[ERROR] Get notifications for user error: {e}")
            return []

    @staticmethod
    def mark_all_read(user_id):
        """Kullanıcının tüm okunmamış bildirimlerini okundu işaretle (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG Notification.mark_all_read] Marking all notifications as read for user: {user_id}")
            result = repo.mark_notifications_read(user_id)
            print(f"[DEBUG Notification.mark_all_read] Result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Mark notifications read error: {e}")
            return False

class Favorite:
    def __init__(self, id, user_id, product_id, created_at):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.created_at = created_at

    @staticmethod
    def create(user_id, product_id):
        """Favori ekle (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG Favorite.create] Adding favorite: user_id={user_id}, product_id={product_id}")
            result = repo.add_favorite(user_id, product_id)
            print(f"[DEBUG Favorite.create] Result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Create favorite error: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def delete(user_id, product_id):
        """Favoriden çıkar (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            print(f"[DEBUG Favorite.delete] Removing favorite: user_id={user_id}, product_id={product_id}")
            result = repo.remove_favorite(user_id, product_id)
            print(f"[DEBUG Favorite.delete] Result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Delete favorite error: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def get_user_favorites(user_id):
        """Kullanıcının favorilerini getir (Product objeleri olarak) - Repository pattern"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            products_data = repo.get_favorites_by_user_id(user_id)
            
            products = []
            for p_data in products_data:
                # Handle images - repository returns as list for Firestore, but SQLite might be JSON string
                images_data = p_data.get('images')
                if isinstance(images_data, str):
                    import json
                    try:
                        images_data = json.loads(images_data)
                    except:
                        images_data = [p_data.get('image')] if p_data.get('image') else []
                elif not images_data:
                    images_data = [p_data.get('image')] if p_data.get('image') else []
                
                # Handle timestamp conversion
                created_at_data = p_data.get('created_at')
                if hasattr(created_at_data, 'timestamp'):  # Firestore Timestamp
                    created_at_data = created_at_data
                elif isinstance(created_at_data, str):
                    try:
                        created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            created_at_data = datetime.strptime(created_at_data, '%Y-%m-%d %H:%M:%S')
                        except:
                            created_at_data = datetime.now()
                elif created_at_data is None:
                    created_at_data = datetime.now()
                
                products.append(Product(
                    p_data.get('id'),
                    p_data.get('user_id'),
                    p_data.get('name'),
                    p_data.get('price'),
                    p_data.get('image'),
                    p_data.get('brand'),
                    p_data.get('url'),
                    created_at_data,
                    p_data.get('old_price'),
                    p_data.get('current_price'),
                    p_data.get('discount_percentage'),
                    images_data,
                    p_data.get('discount_info')
                ))
            
            return products
        except Exception as e:
            print(f"[ERROR] Get user favorites error: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def check_favorite(user_id, product_id):
        """Favori kontrolü (Repository pattern)"""
        try:
            from app.repositories import get_repository
            
            repo = get_repository()
            return repo.is_favorite(user_id, product_id)
        except Exception as e:
            print(f"[ERROR] Check favorite error: {e}")
            return False