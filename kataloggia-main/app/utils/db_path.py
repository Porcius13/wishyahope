"""
Database path utility
Veritabanı yolunu tutarlı şekilde belirlemek için yardımcı fonksiyon
"""
import os


def get_db_path():
    """Veritabanı dosya yolunu döndür.

    Öncelikle DATABASE_PATH ortam değişkenine bakar. Eğer mutlak bir yol
    verilmişse doğrudan onu kullanır. Değilse, proje kök dizinlerinde
    verilen dosya adını arar. Varsayılan dosya adı 'favit.db'dir.
    """
    # İstenen dosya adı (örn. 'favit.db' veya '/var/data/favit.db')
    filename = os.environ.get('DATABASE_PATH', 'favit.db')

    # Mutlak yol verilmişse doğrudan kullan
    if os.path.isabs(filename):
        return filename

    # Çalışma dizininde ara
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, filename)

    if not os.path.exists(db_path):
        # app/utils/db_path.py -> app/utils -> app -> project_root
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_file_dir))
        db_path = os.path.join(base_dir, filename)

        if not os.path.exists(db_path):
            # Bir üst dizinde de dene (ör. kataloggia-main/)
            parent_dir = os.path.dirname(base_dir)
            db_path = os.path.join(parent_dir, filename)

    return db_path

def get_db_connection():
    """Veritabanı bağlantısı oluştur (SQLite only, deprecated)"""
    try:
        import sqlite3
    except ImportError:
        raise ImportError(
            "SQLite is not available. "
            "This function is deprecated. Use Firestore instead by setting DB_BACKEND=firestore."
        )
    db_path = get_db_path()
    return sqlite3.connect(db_path)

