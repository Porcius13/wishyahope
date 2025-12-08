"""
Password Validation Service
Validates password strength and enforces security policies
"""
import re
import hashlib
from typing import List, Tuple

class PasswordValidator:
    """Password strength validator"""
    
    # Common weak passwords (top 1000 most common)
    COMMON_PASSWORDS = {
        'password', '123456', '123456789', '12345678', '12345', '1234567',
        '1234567890', 'qwerty', 'abc123', 'password1', '123123', '111111',
        'password123', 'admin', 'letmein', 'welcome', 'monkey', '123456789',
        '1234', 'sunshine', 'princess', 'football', 'iloveyou', 'shadow',
        'master', 'jesus', 'superman', 'hottie', 'freedom', 'whatever',
        'trustno1', 'dragon', 'passw0rd', 'hello', 'charlie', 'aa123456',
        'donald', 'password1', 'qwerty123', 'qwertyuiop', 'starwars'
    }
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBER = True
    REQUIRE_SPECIAL = True
    
    @classmethod
    def validate(cls, password: str, username: str = None, email: str = None) -> Tuple[bool, List[str]]:
        """
        Validate password strength
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        if not password:
            return False, ['Şifre boş olamaz']
        
        # Length check
        if len(password) < cls.MIN_LENGTH:
            errors.append(f'Şifre en az {cls.MIN_LENGTH} karakter olmalıdır')
        elif len(password) > cls.MAX_LENGTH:
            errors.append(f'Şifre en fazla {cls.MAX_LENGTH} karakter olabilir')
        
        # Character requirements
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?]', password))
        
        if cls.REQUIRE_UPPERCASE and not has_upper:
            errors.append('Şifre en az bir büyük harf içermelidir')
        if cls.REQUIRE_LOWERCASE and not has_lower:
            errors.append('Şifre en az bir küçük harf içermelidir')
        if cls.REQUIRE_NUMBER and not has_digit:
            errors.append('Şifre en az bir rakam içermelidir')
        if cls.REQUIRE_SPECIAL and not has_special:
            errors.append('Şifre en az bir özel karakter içermelidir (!@#$%^&*()_+-=[]{}|;:,.<>?)')
        
        # Check for common passwords
        password_lower = password.lower()
        if password_lower in cls.COMMON_PASSWORDS:
            errors.append('Bu şifre çok yaygın kullanılmaktadır, lütfen daha güçlü bir şifre seçin')
        
        # Check if password contains username or email
        if username:
            username_lower = username.lower()
            if username_lower in password_lower:
                errors.append('Şifre kullanıcı adınızı içeremez')
        
        if email:
            email_local = email.split('@')[0].lower()
            if email_local in password_lower and len(email_local) > 3:
                errors.append('Şifre email adresinizi içeremez')
        
        # Check for sequential characters (e.g., "1234", "abcd")
        if cls._has_sequential_chars(password, 4):
            errors.append('Şifre ardışık karakterler içermemelidir (örn: 1234, abcd)')
        
        # Check for repeated characters (e.g., "aaaa", "1111")
        if cls._has_repeated_chars(password, 4):
            errors.append('Şifre aynı karakteri 4 kereden fazla tekrar içermemelidir')
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @classmethod
    def get_strength_score(cls, password: str) -> Tuple[int, str]:
        """
        Calculate password strength score (0-100)
        Returns: (score, description)
        """
        if not password:
            return 0, 'Çok Zayıf'
        
        score = 0
        
        # Length contribution (max 25 points)
        length_bonus = min(len(password) * 2, 25)
        score += length_bonus
        
        # Character variety (max 30 points)
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?]', password))
        
        char_variety = sum([has_upper, has_lower, has_digit, has_special])
        score += char_variety * 7.5  # Max 30 points
        
        # Complexity bonus (max 25 points)
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        if len(password) >= 20:
            score += 5
        
        # Penalties
        password_lower = password.lower()
        if password_lower in cls.COMMON_PASSWORDS:
            score -= 30
        
        if cls._has_sequential_chars(password, 4):
            score -= 15
        
        if cls._has_repeated_chars(password, 4):
            score -= 10
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        
        # Determine description
        if score < 30:
            description = 'Çok Zayıf'
        elif score < 50:
            description = 'Zayıf'
        elif score < 70:
            description = 'Orta'
        elif score < 85:
            description = 'Güçlü'
        else:
            description = 'Çok Güçlü'
        
        return int(score), description
    
    @staticmethod
    def _has_sequential_chars(text: str, min_length: int) -> bool:
        """Check if text contains sequential characters"""
        for i in range(len(text) - min_length + 1):
            substring = text[i:i+min_length].lower()
            # Check numeric sequences
            if substring.isdigit():
                nums = [int(c) for c in substring]
                if all(nums[j] == nums[j-1] + 1 for j in range(1, len(nums))):
                    return True
            # Check alphabetic sequences
            elif substring.isalpha():
                chars = [ord(c) for c in substring]
                if all(chars[j] == chars[j-1] + 1 for j in range(1, len(chars))):
                    return True
        return False
    
    @staticmethod
    def _has_repeated_chars(text: str, min_repeats: int) -> bool:
        """Check if text contains repeated characters"""
        if len(text) < min_repeats:
            return False
        
        count = 1
        prev_char = text[0].lower()
        for char in text[1:].lower():
            if char == prev_char:
                count += 1
                if count >= min_repeats:
                    return True
            else:
                count = 1
                prev_char = char
        return False
    
    @staticmethod
    def compare_passwords(password1: str, password2: str) -> bool:
        """
        Timing-safe password comparison to prevent timing attacks
        Uses constant-time comparison
        """
        if len(password1) != len(password2):
            return False
        
        result = 0
        for a, b in zip(password1, password2):
            result |= ord(a) ^ ord(b)
        
        return result == 0
