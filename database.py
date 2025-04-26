import sqlite3
import os
import shutil
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class Database:
    def __init__(self, db_file="passwords.db", encrypted_db_file="passwords.db.enc"):
        self.db_file = db_file
        self.encrypted_db_file = encrypted_db_file
        self.conn = None
        self.cursor = None
        self.salt = None
        self.key = None
        self.fernet = None
        self.db_encryption_key = None
        
        # Check if encrypted database exists and needs decryption
        if os.path.exists(self.encrypted_db_file) and not os.path.exists(self.db_file):
            # The database is currently encrypted, but will be decrypted on successful login
            pass
        else:
            # Initialize new database or use existing unencrypted one
            self.initialize_db()

    def initialize_db(self):
        """Initialize the database with required tables if they don't exist"""
        self.connect()
        
        # Create user table for master password
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            login_attempts INTEGER DEFAULT 0,
            last_attempt TIMESTAMP
        )
        ''')
        
        # Create passwords table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
        self.disconnect()

    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            
    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def generate_key(self, master_password, salt=None):
        """Generate encryption key from master password"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.key = key
        self.salt = salt
        self.fernet = Fernet(key)
        
        # Also derive a separate key for database file encryption
        db_kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=150000,  # More iterations for db encryption
            backend=default_backend()
        )
        self.db_encryption_key = db_kdf.derive(master_password.encode())
        
        return key, salt

    def create_master_password(self, master_password):
        """Create or update the master password"""
        self.connect()
        
        # Generate salt and key
        _, salt = self.generate_key(master_password)
        
        # Store the hashed password and salt
        salt_hex = salt.hex()
        password_hash = self.hash_password(master_password, salt)
        
        try:
            # Check if a record already exists
            self.cursor.execute("SELECT COUNT(*) FROM user")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                self.cursor.execute(
                    "INSERT INTO user (password_hash, salt) VALUES (?, ?)",
                    (password_hash, salt_hex)
                )
            else:
                self.cursor.execute(
                    "UPDATE user SET password_hash = ?, salt = ?, login_attempts = 0 WHERE id = 1",
                    (password_hash, salt_hex)
                )
                
            self.conn.commit()
            
            # Encrypt the database file
            self.encrypt_database()
            
            return True
        except sqlite3.Error as e:
            print(f"Error creating master password: {e}")
            return False
        finally:
            self.disconnect()

    def verify_master_password(self, master_password):
        """Verify the master password and update login attempts"""
        # If encrypted database exists, try to decrypt it
        if os.path.exists(self.encrypted_db_file):
            if not self.decrypt_database(master_password):
                return False
        
        self.connect()
        
        try:
            # Get stored salt and hash
            self.cursor.execute("SELECT password_hash, salt, login_attempts FROM user WHERE id = 1")
            result = self.cursor.fetchone()
            
            if not result:
                return False
                
            stored_hash, salt_hex, login_attempts = result
            salt = bytes.fromhex(salt_hex)
            
            # Check if too many attempts
            if login_attempts >= 5:
                self.cursor.execute("UPDATE user SET login_attempts = login_attempts + 1 WHERE id = 1")
                self.conn.commit()
                return False
                
            # Generate hash from provided password
            password_hash = self.hash_password(master_password, salt)
            
            if password_hash == stored_hash:
                # Password is correct, reset login attempts
                self.cursor.execute("UPDATE user SET login_attempts = 0 WHERE id = 1")
                self.conn.commit()
                
                # Set up encryption with master password
                self.generate_key(master_password, salt)
                return True
            else:
                # Password is incorrect, increment login attempts
                self.cursor.execute("UPDATE user SET login_attempts = login_attempts + 1 WHERE id = 1")
                self.conn.commit()
                return False
                
        except sqlite3.Error as e:
            print(f"Error verifying master password: {e}")
            return False
        finally:
            self.disconnect()

    def hash_password(self, password, salt):
        """Create a hash of the password with the given salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        hashed = kdf.derive(password.encode())
        return base64.b64encode(hashed).decode('utf-8')

    def reset_login_attempts(self):
        """Reset login attempts counter"""
        self.connect()
        self.cursor.execute("UPDATE user SET login_attempts = 0 WHERE id = 1")
        self.conn.commit()
        self.disconnect()

    def encrypt_password(self, password):
        """Encrypt a password using the encryption key"""
        if not self.fernet:
            raise ValueError("Encryption key not set. Please login first.")
        
        encrypted = self.fernet.encrypt(password.encode())
        return encrypted.decode('utf-8')

    def decrypt_password(self, encrypted_password):
        """Decrypt an encrypted password"""
        if not self.fernet:
            raise ValueError("Encryption key not set. Please login first.")
            
        decrypted = self.fernet.decrypt(encrypted_password.encode())
        return decrypted.decode('utf-8')

    def add_password(self, website, username, password, notes=""):
        """Add a new password entry"""
        self.connect()
        
        try:
            encrypted_password = self.encrypt_password(password)
            
            self.cursor.execute(
                "INSERT INTO passwords (website, username, password, notes) VALUES (?, ?, ?, ?)",
                (website, username, encrypted_password, notes)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding password: {e}")
            return False
        finally:
            self.disconnect()

    def get_all_passwords(self):
        """Retrieve all password entries"""
        self.connect()
        
        try:
            self.cursor.execute("SELECT id, website, username, password, notes FROM passwords ORDER BY website")
            entries = self.cursor.fetchall()
            
            result = []
            for entry in entries:
                id, website, username, encrypted_password, notes = entry
                decrypted_password = self.decrypt_password(encrypted_password)
                result.append({
                    'id': id,
                    'website': website,
                    'username': username,
                    'password': decrypted_password,
                    'notes': notes
                })
                
            return result
        except Exception as e:
            print(f"Error retrieving passwords: {e}")
            return []
        finally:
            self.disconnect()

    def search_passwords(self, search_term):
        """Search for password entries matching the search term"""
        self.connect()
        
        try:
            search_pattern = f"%{search_term}%"
            self.cursor.execute(
                "SELECT id, website, username, password, notes FROM passwords "
                "WHERE website LIKE ? OR username LIKE ? OR notes LIKE ?", 
                (search_pattern, search_pattern, search_pattern)
            )
            
            entries = self.cursor.fetchall()
            
            result = []
            for entry in entries:
                id, website, username, encrypted_password, notes = entry
                decrypted_password = self.decrypt_password(encrypted_password)
                result.append({
                    'id': id,
                    'website': website,
                    'username': username,
                    'password': decrypted_password,
                    'notes': notes
                })
                
            return result
        except Exception as e:
            print(f"Error searching passwords: {e}")
            return []
        finally:
            self.disconnect()

    def update_password(self, id, website, username, password, notes=""):
        """Update an existing password entry"""
        self.connect()
        
        try:
            encrypted_password = self.encrypt_password(password)
            
            self.cursor.execute(
                "UPDATE passwords SET website = ?, username = ?, password = ?, "
                "notes = ?, date_modified = CURRENT_TIMESTAMP WHERE id = ?",
                (website, username, encrypted_password, notes, id)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
        finally:
            self.disconnect()

    def delete_password(self, id):
        """Delete a password entry by ID"""
        self.connect()
        
        try:
            self.cursor.execute("DELETE FROM passwords WHERE id = ?", (id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting password: {e}")
            return False
        finally:
            self.disconnect()

    def export_database(self, export_file):
        """Export database contents to a file"""
        try:
            # Export as a new SQLite database
            source_conn = sqlite3.connect(self.db_file)
            backup_conn = sqlite3.connect(export_file)
            
            source_conn.backup(backup_conn)
            
            backup_conn.close()
            source_conn.close()
            return True
        except Exception as e:
            print(f"Error exporting database: {e}")
            return False

    def import_database(self, import_file):
        """Import database contents from a file"""
        if not os.path.exists(import_file):
            return False
            
        try:
            # Close existing connection
            self.disconnect()
            
            # Backup current database
            backup_file = f"{self.db_file}.bak"
            if os.path.exists(self.db_file):
                os.replace(self.db_file, backup_file)
                
            # Copy imported database
            import_conn = sqlite3.connect(import_file)
            target_conn = sqlite3.connect(self.db_file)
            
            import_conn.backup(target_conn)
            
            import_conn.close()
            target_conn.close()
            
            return True
        except Exception as e:
            # Restore from backup if import fails
            if os.path.exists(backup_file):
                os.replace(backup_file, self.db_file)
                
            print(f"Error importing database: {e}")
            return False 

    def encrypt_database(self):
        """Encrypt the entire database file for security"""
        # First ensure connection is closed
        self.disconnect()
        
        if not os.path.exists(self.db_file):
            return False
            
        try:
            # Read the database file
            with open(self.db_file, 'rb') as db_file:
                db_content = db_file.read()
                
            # Generate a random IV
            iv = secrets.token_bytes(16)
            
            # Create an encryptor
            cipher = Cipher(
                algorithms.AES(self.db_encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad the content to be a multiple of block size (16 bytes)
            padded_size = 16 - (len(db_content) % 16)
            db_content += bytes([padded_size]) * padded_size
            
            # Encrypt the content
            encrypted_content = encryptor.update(db_content) + encryptor.finalize()
            
            # Write the IV and encrypted content to the file
            with open(self.encrypted_db_file, 'wb') as enc_file:
                enc_file.write(iv)  # First 16 bytes are the IV
                enc_file.write(encrypted_content)
                
            # Securely delete the unencrypted file
            self.secure_delete_file(self.db_file)
                
            return True
        except Exception as e:
            print(f"Error encrypting database: {e}")
            return False
            
    def decrypt_database(self, master_password):
        """Decrypt the database file using the master password"""
        if not os.path.exists(self.encrypted_db_file):
            return False
            
        try:
            # Read the encrypted file
            with open(self.encrypted_db_file, 'rb') as enc_file:
                data = enc_file.read()
                
            # Extract IV and encrypted content
            iv = data[:16]
            encrypted_content = data[16:]
            
            # Create a temporary salt for key derivation
            temp_salt = secrets.token_bytes(16)
            
            # Generate a temporary key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=temp_salt,
                iterations=150000,
                backend=default_backend()
            )
            
            temp_key = kdf.derive(master_password.encode())
            
            # Create a decryptor
            cipher = Cipher(
                algorithms.AES(temp_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            try:
                # Try to decrypt
                decrypted_content = decryptor.update(encrypted_content) + decryptor.finalize()
                
                # Remove padding
                padding_size = decrypted_content[-1]
                decrypted_content = decrypted_content[:-padding_size]
                
                # Write decrypted content to database file
                with open(self.db_file, 'wb') as db_file:
                    db_file.write(decrypted_content)
                    
                # Test if it's a valid SQLite database
                test_conn = sqlite3.connect(self.db_file)
                test_conn.close()
                
                # Now derive the actual key using the correct salt from the DB
                # Note: this will be done after connecting to the DB in verify_master_password
                
                return True
            except Exception:
                # If decryption fails, it was probably the wrong password
                # Clean up any partially decrypted file
                if os.path.exists(self.db_file):
                    os.remove(self.db_file)
                return False
                
        except Exception as e:
            print(f"Error decrypting database: {e}")
            return False
            
    def secure_delete_file(self, filepath):
        """Securely delete a file by overwriting with random data before deleting"""
        if not os.path.exists(filepath):
            return
            
        try:
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Open file for binary write
            with open(filepath, 'wb') as f:
                # Overwrite with random data 3 times
                for _ in range(3):
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                    
            # Finally delete the file
            os.remove(filepath)
        except Exception as e:
            print(f"Error securely deleting file: {e}")
            # Attempt normal delete as fallback
            try:
                os.remove(filepath)
            except:
                pass 