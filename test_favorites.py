import sqlite3
from app.utils.db_path import get_db_connection
import uuid
from datetime import datetime
from models import Favorite, User, Product, init_db

def test_favorites():
    print("Testing Favorites Feature...")
    
    # Initialize DB (creates table if not exists)
    init_db()
    
    # Create dummy user and product
    user_id = str(uuid.uuid4())
    product_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert dummy user
    cursor.execute("INSERT INTO users (id, username, email, password_hash, profile_url) VALUES (?, ?, ?, ?, ?)",
                   (user_id, f"test_user_{user_id[:8]}", f"test_{user_id[:8]}@example.com", "hash", f"user_{user_id[:8]}"))
    
    # Insert dummy product
    cursor.execute("INSERT INTO products (id, user_id, name, price, brand, url) VALUES (?, ?, ?, ?, ?, ?)",
                   (product_id, user_id, "Test Product", "100 TL", "Test Brand", "http://example.com"))
    
    conn.commit()
    conn.close()
    
    print(f"Created test user {user_id} and product {product_id}")
    
    # 1. Test Add Favorite
    print("\n1. Testing Add Favorite...")
    success = Favorite.create(user_id, product_id)
    if success:
        print("PASS: Favorite added successfully")
    else:
        print("FAIL: Failed to add favorite")
        
    # 2. Test Check Favorite
    print("\n2. Testing Check Favorite...")
    is_fav = Favorite.check_favorite(user_id, product_id)
    if is_fav:
        print("PASS: Favorite check returned True")
    else:
        print("FAIL: Favorite check returned False")
        
    # 3. Test Get User Favorites
    print("\n3. Testing Get User Favorites...")
    favorites = Favorite.get_user_favorites(user_id)
    if len(favorites) == 1 and favorites[0].id == product_id:
        print(f"PASS: Retrieved {len(favorites)} favorite(s), ID matches")
    else:
        print(f"FAIL: Retrieved {len(favorites)} favorite(s)")
        
    # 4. Test Remove Favorite
    print("\n4. Testing Remove Favorite...")
    success = Favorite.delete(user_id, product_id)
    if success:
        print("PASS: Favorite removed successfully")
    else:
        print("FAIL: Failed to remove favorite")
        
    # 5. Test Check Favorite After Removal
    print("\n5. Testing Check Favorite After Removal...")
    is_fav = Favorite.check_favorite(user_id, product_id)
    if not is_fav:
        print("PASS: Favorite check returned False")
    else:
        print("FAIL: Favorite check returned True")

    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    cursor.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    print("\nCleanup complete.")

if __name__ == "__main__":
    try:
        test_favorites()
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
