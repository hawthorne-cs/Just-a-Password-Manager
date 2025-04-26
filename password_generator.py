import secrets  # More secure than random
import string

class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    
    def generate_password(self, length=16, use_lowercase=True, use_uppercase=True, 
                         use_digits=True, use_symbols=True):
        """Generate a secure random password based on specified criteria"""
        if length < 4:
            length = 4  # Minimum length for security
            
        # Determine character set based on options
        charset = ""
        if use_lowercase:
            charset += self.lowercase
        if use_uppercase:
            charset += self.uppercase
        if use_digits:
            charset += self.digits
        if use_symbols:
            charset += self.symbols
            
        # Ensure at least one character set is selected
        if not charset:
            charset = self.lowercase + self.digits
            
        # Generate password
        password = []
        
        # Ensure at least one character from each selected character set
        if use_lowercase:
            password.append(secrets.choice(self.lowercase))
        if use_uppercase:
            password.append(secrets.choice(self.uppercase))
        if use_digits:
            password.append(secrets.choice(self.digits))
        if use_symbols:
            password.append(secrets.choice(self.symbols))
            
        # Fill remaining length with random characters
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(charset))
            
        # Shuffle the password to make it more random
        # Use Fisher-Yates shuffle algorithm for better security
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]
        
        return ''.join(password)
    
    def evaluate_password_strength(self, password):
        """Evaluate the strength of a password and return a score from 0-100"""
        score = 0
        
        # Length check
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        elif len(password) >= 6:
            score += 10
            
        # Character variety checks
        has_lowercase = any(c in self.lowercase for c in password)
        has_uppercase = any(c in self.uppercase for c in password)
        has_digits = any(c in self.digits for c in password)
        has_symbols = any(c in self.symbols for c in password)
        
        variety_score = 0
        if has_lowercase:
            variety_score += 15
        if has_uppercase:
            variety_score += 15
        if has_digits:
            variety_score += 20
        if has_symbols:
            variety_score += 25
            
        score += variety_score
        
        # Repeated characters penalty
        char_count = {}
        for char in password:
            if char in char_count:
                char_count[char] += 1
            else:
                char_count[char] = 1
                
        repeated_chars = sum(1 for count in char_count.values() if count > 1)
        repeated_penalty = min(15, repeated_chars * 5)
        score = max(0, score - repeated_penalty)
        
        # Sequential characters penalty
        sequential_count = 0
        for i in range(len(password) - 2):
            # Check for sequential ASCII values
            if (ord(password[i]) + 1 == ord(password[i+1]) and 
                ord(password[i+1]) + 1 == ord(password[i+2])):
                sequential_count += 1
                
        sequential_penalty = min(10, sequential_count * 5)
        score = max(0, score - sequential_penalty)
        
        return min(100, score) 