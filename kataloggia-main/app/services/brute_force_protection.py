"""
Brute Force Protection Service
Tracks failed login attempts and implements account lockout
"""
import time
from datetime import datetime, timedelta
from collections import defaultdict
from app.repositories import get_repository

class BruteForceProtection:
    """Brute force protection for login attempts"""
    
    # In-memory storage (consider using Redis for production)
    _failed_attempts = defaultdict(list)  # {key: [timestamps]}
    _locked_accounts = {}  # {key: lock_until_timestamp}
    
    # Configuration
    MAX_FAILED_ATTEMPTS = 5  # Maximum failed attempts before lockout
    LOCKOUT_DURATION = 900  # 15 minutes in seconds
    IP_BLOCK_DURATION = 3600  # 1 hour in seconds for IP blocking
    MAX_FAILED_ATTEMPTS_PER_IP = 10  # Max attempts from same IP
    
    @classmethod
    def get_client_identifier(cls, username=None, ip_address=None):
        """Get identifier for tracking (username or IP)"""
        if username:
            return f"user:{username}"
        if ip_address:
            return f"ip:{ip_address}"
        return None
    
    @classmethod
    def record_failed_attempt(cls, username=None, ip_address=None):
        """Record a failed login attempt"""
        now = time.time()
        
        # Track by username if available
        if username:
            user_key = cls.get_client_identifier(username=username)
            cls._failed_attempts[user_key].append(now)
            # Clean old attempts (older than lockout duration)
            cls._failed_attempts[user_key] = [
                ts for ts in cls._failed_attempts[user_key]
                if now - ts < cls.LOCKOUT_DURATION
            ]
            
            # Check if account should be locked
            if len(cls._failed_attempts[user_key]) >= cls.MAX_FAILED_ATTEMPTS:
                lock_until = now + cls.LOCKOUT_DURATION
                cls._locked_accounts[user_key] = lock_until
                # Also store in database for persistence
                cls._store_lockout_in_db(username, lock_until)
        
        # Track by IP address
        if ip_address:
            ip_key = cls.get_client_identifier(ip_address=ip_address)
            cls._failed_attempts[ip_key].append(now)
            # Clean old attempts
            cls._failed_attempts[ip_key] = [
                ts for ts in cls._failed_attempts[ip_key]
                if now - ts < cls.IP_BLOCK_DURATION
            ]
            
            # Check if IP should be blocked
            if len(cls._failed_attempts[ip_key]) >= cls.MAX_FAILED_ATTEMPTS_PER_IP:
                lock_until = now + cls.IP_BLOCK_DURATION
                cls._locked_accounts[ip_key] = lock_until
    
    @classmethod
    def clear_failed_attempts(cls, username=None, ip_address=None):
        """Clear failed attempts after successful login"""
        if username:
            user_key = cls.get_client_identifier(username=username)
            if user_key in cls._failed_attempts:
                del cls._failed_attempts[user_key]
            if user_key in cls._locked_accounts:
                del cls._locked_accounts[user_key]
            # Clear from database
            cls._clear_lockout_from_db(username)
        
        if ip_address:
            ip_key = cls.get_client_identifier(ip_address=ip_address)
            if ip_key in cls._failed_attempts:
                del cls._failed_attempts[ip_key]
            if ip_key in cls._locked_accounts:
                del cls._locked_accounts[ip_key]
    
    @classmethod
    def is_locked(cls, username=None, ip_address=None):
        """Check if account or IP is locked"""
        now = time.time()
        
        # Check username lockout
        if username:
            user_key = cls.get_client_identifier(username=username)
            
            # Check in-memory
            if user_key in cls._locked_accounts:
                lock_until = cls._locked_accounts[user_key]
                if now < lock_until:
                    return True, int(lock_until - now)  # Return seconds remaining
                else:
                    # Lock expired, remove it
                    del cls._locked_accounts[user_key]
            
            # Check database lockout (for persistence across restarts)
            db_lockout = cls._get_lockout_from_db(username)
            if db_lockout and now < db_lockout:
                return True, int(db_lockout - now)
        
        # Check IP lockout
        if ip_address:
            ip_key = cls.get_client_identifier(ip_address=ip_address)
            if ip_key in cls._locked_accounts:
                lock_until = cls._locked_accounts[ip_key]
                if now < lock_until:
                    return True, int(lock_until - now)
                else:
                    del cls._locked_accounts[ip_key]
        
        return False, 0
    
    @classmethod
    def get_remaining_attempts(cls, username=None, ip_address=None):
        """Get remaining attempts before lockout"""
        if username:
            user_key = cls.get_client_identifier(username=username)
            attempts = len(cls._failed_attempts.get(user_key, []))
            return max(0, cls.MAX_FAILED_ATTEMPTS - attempts)
        
        if ip_address:
            ip_key = cls.get_client_identifier(ip_address=ip_address)
            attempts = len(cls._failed_attempts.get(ip_key, []))
            return max(0, cls.MAX_FAILED_ATTEMPTS_PER_IP - attempts)
        
        return cls.MAX_FAILED_ATTEMPTS
    
    @classmethod
    def _store_lockout_in_db(cls, username, lock_until):
        """Store account lockout in database"""
        try:
            repo = get_repository()
            # Find user by username first
            user_data = repo.get_user_by_username(username)
            if user_data and user_data.get('id'):
                # Store lockout timestamp in user data
                repo.update_user(user_data.get('id'), locked_until=lock_until)
        except Exception as e:
            print(f"[WARNING] Could not store lockout in DB: {e}")
    
    @classmethod
    def _get_lockout_from_db(cls, username):
        """Get account lockout from database"""
        try:
            repo = get_repository()
            user_data = repo.get_user_by_username(username)
            if user_data and user_data.get('locked_until'):
                locked_until = user_data.get('locked_until')
                # Convert to timestamp if it's a datetime
                if hasattr(locked_until, 'timestamp'):
                    return locked_until.timestamp()
                elif isinstance(locked_until, datetime):
                    import time
                    return locked_until.timestamp() if hasattr(locked_until, 'timestamp') else time.time()
                elif isinstance(locked_until, (int, float)):
                    return locked_until
        except Exception as e:
            print(f"[WARNING] Could not get lockout from DB: {e}")
        return None
    
    @classmethod
    def _clear_lockout_from_db(cls, username):
        """Clear account lockout from database"""
        try:
            repo = get_repository()
            user_data = repo.get_user_by_username(username)
            if user_data and user_data.get('id'):
                repo.update_user(user_data.get('id'), locked_until=None)
        except Exception as e:
            print(f"[WARNING] Could not clear lockout from DB: {e}")
