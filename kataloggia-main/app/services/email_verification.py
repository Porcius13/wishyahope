"""
Email Verification Service
Handles email verification tokens
"""
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.repositories import get_repository

class EmailVerificationService:
    """Email verification token management"""
    
    TOKEN_EXPIRY_HOURS = 24  # Tokens expire after 24 hours
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_verification_token(user_id: str, email: str) -> str:
        """Create and store verification token for user"""
        token = EmailVerificationService.generate_verification_token()
        expires_at = datetime.now() + timedelta(hours=EmailVerificationService.TOKEN_EXPIRY_HOURS)
        
        try:
            repo = get_repository()
            repo.update_user(
                user_id,
                email_verification_token=token,
                email_verification_token_expires_at=expires_at
            )
            return token
        except Exception as e:
            print(f"[ERROR] Failed to create verification token: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify token and return (is_valid, user_id)
        Returns: (True, user_id) if valid, (False, None) otherwise
        """
        try:
            repo = get_repository()
            
            # Find user by token
            # Note: This requires a method to find user by verification token
            # For now, we'll check all users (inefficient but works)
            # In production, consider adding an index or separate token collection
            
            # Get all users (with limit for safety)
            users = repo.get_all_users(limit=1000, offset=0)
            
            for user_data in users:
                stored_token = user_data.get('email_verification_token')
                if stored_token == token:
                    # Check if token is expired
                    expires_at = user_data.get('email_verification_token_expires_at')
                    
                    if expires_at:
                        # Handle different timestamp formats (Firestore, datetime, string, float)
                        if hasattr(expires_at, 'timestamp') and not isinstance(expires_at, datetime):
                            # Firestore Timestamp object
                            expires_timestamp = expires_at.timestamp()
                        elif isinstance(expires_at, datetime):
                            expires_timestamp = expires_at.timestamp()
                        elif isinstance(expires_at, str):
                            try:
                                expires_timestamp = datetime.fromisoformat(expires_at.replace('Z', '+00:00')).timestamp()
                            except:
                                expires_timestamp = time.time() + 86400  # Default to 24h from now
                        elif isinstance(expires_at, (int, float)):
                            # Already a timestamp
                            expires_timestamp = float(expires_at)
                        else:
                            expires_timestamp = time.time() + 86400  # Default to 24h from now
                        
                        if time.time() < expires_timestamp:
                            # Token is valid
                            user_id = user_data.get('id')
                            
                            # Mark email as verified and clear token
                            repo.update_user(
                                user_id,
                                email_verified=True,
                                email_verification_token=None,
                                email_verification_token_expires_at=None
                            )
                            
                            return True, user_id
                        else:
                            # Token expired
                            return False, None
            
            return False, None
            
        except Exception as e:
            print(f"[ERROR] Token verification failed: {e}")
            return False, None
    
    @staticmethod
    def is_email_verified(user_id: str) -> bool:
        """Check if user's email is verified"""
        try:
            repo = get_repository()
            user_data = repo.get_user_by_id(user_id)
            if user_data:
                return bool(user_data.get('email_verified', False))
            return False
        except Exception as e:
            print(f"[ERROR] Failed to check email verification: {e}")
            return False
    
    @staticmethod
    def resend_verification_token(user_id: str, email: str) -> Optional[str]:
        """Resend verification token (generate new one)"""
        return EmailVerificationService.create_verification_token(user_id, email)
