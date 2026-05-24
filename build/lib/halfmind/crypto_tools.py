import os
import hashlib
import hmac
import base64
import secrets
import string
from pathlib import Path


class CryptoTools:
    """Tools for cryptographic operations, hashing, and encryption"""
    
    HASH_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'blake2s']
    
    def __init__(self):
        self.salt_length = 32
    
    def hash_text(self, text, algorithm='sha256'):
        """Computes hash of text using specified algorithm"""
        if algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        hash_func = getattr(hashlib, algorithm)
        return hash_func(text.encode()).hexdigest()
    
    def hash_file(self, file_path, algorithm='sha256', chunk_size=8192):
        """Computes hash of a file"""
        if algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def hash_multiple_files(self, file_paths, algorithm='sha256'):
        """Computes hashes for multiple files"""
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.hash_file(file_path, algorithm)
            except Exception as e:
                results[file_path] = {'error': str(e)}
        return results
    
    def generate_salt(self, length=None):
        """Generates a random salt"""
        if length is None:
            length = self.salt_length
        return secrets.token_hex(length)
    
    def hash_with_salt(self, text, salt=None, algorithm='sha256'):
        """Hashes text with a salt"""
        if salt is None:
            salt = self.generate_salt()
        salted = f"{salt}{text}".encode()
        if algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        hash_func = getattr(hashlib, algorithm)
        hashed = hash_func(salted).hexdigest()
        return {
            'hash': hashed,
            'salt': salt,
            'algorithm': algorithm
        }
    
    def verify_hash_with_salt(self, text, stored_hash, salt, algorithm='sha256'):
        """Verifies text against a hash with salt"""
        result = self.hash_with_salt(text, salt, algorithm)
        return result['hash'] == stored_hash
    
    def generate_hmac(self, message, key, algorithm='sha256'):
        """Generates HMAC for a message"""
        if isinstance(message, str):
            message = message.encode()
        if isinstance(key, str):
            key = key.encode()
        return hmac.new(key, message, getattr(hashlib, algorithm)).hexdigest()
    
    def verify_hmac(self, message, key, expected_hmac, algorithm='sha256'):
        """Verifies HMAC for a message"""
        computed_hmac = self.generate_hmac(message, key, algorithm)
        return hmac.compare_digest(computed_hmac, expected_hmac)
    
    def generate_password(self, length=16, include_uppercase=True, include_lowercase=True,
                         include_digits=True, include_special=True):
        """Generates a secure random password"""
        chars = ''
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_lowercase:
            chars += string.ascii_lowercase
        if include_digits:
            chars += string.digits
        if include_special:
            chars += string.punctuation
        if not chars:
            raise ValueError("At least one character type must be included")
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return {
            'password': password,
            'length': length,
            'entropy': length * (len(chars).bit_length())
        }
    
    def generate_token(self, length=32):
        """Generates a secure random token"""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix='sk'):
        """Generates an API key with prefix"""
        token = secrets.token_urlsafe(32)
        return f"{prefix}_{token}"
    
    def generate_uuid(self):
        """Generates a UUID4"""
        import uuid
        return str(uuid.uuid4())
    
    def generate_multiple_uuids(self, count):
        """Generates multiple UUIDs"""
        import uuid
        return [str(uuid.uuid4()) for _ in range(count)]
    
    def encode_base64(self, data):
        """Encodes data to base64"""
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()
    
    def decode_base64(self, encoded):
        """Decodes base64 data"""
        return base64.b64decode(encoded).decode()
    
    def encode_url_safe(self, data):
        """Encodes data to URL-safe base64"""
        if isinstance(data, str):
            data = data.encode()
        return base64.urlsafe_b64encode(data).decode()
    
    def decode_url_safe(self, encoded):
        """Decodes URL-safe base64"""
        return base64.urlsafe_b64decode(encoded).decode()
    
    def encrypt_aes(self, plaintext, key):
        """Encrypts plaintext using AES-256-GCM"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        if isinstance(key, str):
            key = key.encode()
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(derived_key)
        encrypted = f.encrypt(plaintext.encode())
        return {
            'encrypted': base64.b64encode(encrypted).decode(),
            'salt': base64.b64encode(salt).decode()
        }
    
    def decrypt_aes(self, encrypted_data, key, salt):
        """Decrypts AES-256-GCM encrypted data"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        if isinstance(key, str):
            key = key.encode()
        salt_bytes = base64.b64decode(salt)
        encrypted_bytes = base64.b64decode(encrypted_data)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(derived_key)
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def generate_rsa_keypair(self, key_size=2048):
        """Generates RSA public/private key pair"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return {
            'private_key': private_pem.decode(),
            'public_key': public_pem.decode(),
            'key_size': key_size
        }
    
    def rsa_encrypt(self, plaintext, public_key_pem):
        """Encrypts data using RSA public key"""
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        encrypted = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode()
    
    def rsa_decrypt(self, encrypted_data, private_key_pem):
        """Decrypts data using RSA private key"""
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        encrypted = base64.b64decode(encrypted_data)
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()
    
    def create_jwt(self, payload, secret, algorithm='HS256', expiration=None):
        """Creates a JSON Web Token"""
        import jwt
        import time
        if expiration:
            payload['exp'] = int(time.time()) + expiration
        return jwt.encode(payload, secret, algorithm=algorithm)
    
    def verify_jwt(self, token, secret, algorithms=['HS256']):
        """Verifies and decodes a JWT"""
        import jwt
        return jwt.decode(token, secret, algorithms=algorithms)
    
    def calculate_entropy(self, text):
        """Calculates Shannon entropy of text"""
        import math
        if not text:
            return 0
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        entropy = 0
        length = len(text)
        for count in frequency.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        return round(entropy, 4)
    
    def check_password_strength(self, password):
        """Checks password strength and returns score"""
        score = 0
        feedback = []
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters")
        if len(password) >= 12:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add digits")
        if any(c in string.punctuation for c in password):
            score += 1
        else:
            feedback.append("Add special characters")
        entropy = self.calculate_entropy(password)
        if entropy > 3:
            score += 1
        strength = 'weak' if score < 3 else 'medium' if score < 5 else 'strong'
        return {
            'score': score,
            'max_score': 7,
            'strength': strength,
            'entropy': entropy,
            'feedback': feedback
        }
    
    def generate_otp(self, length=6):
        """Generates a numeric OTP code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def generate_mnemonic(self, word_count=12):
        """Generates a BIP39-style mnemonic phrase"""
        import hashlib
        entropy_bits = word_count * 11 - (word_count * 11) % 32
        entropy = secrets.token_bytes(entropy_bits // 8)
        hash_bytes = hashlib.sha256(entropy).digest()
        bits = bin(int.from_bytes(entropy, 'big'))[2:].zfill(entropy_bits)
        bits += bin(int.from_bytes(hash_bytes, 'big'))[2:].zfill(256)[:entropy_bits // 32]
        words = []
        for i in range(word_count):
            start = i * 11
            end = start + 11
            index = int(bits[start:end], 2)
            words.append(f"word_{index}")
        return ' '.join(words)