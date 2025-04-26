# Password Manager Implementation Guide

This document provides a comprehensive explanation of how the password manager works and the security measures implemented.

## System Architecture

The password manager consists of several components:

1. **Database Module** (`database.py`): Handles secure storage of passwords
2. **Password Generator** (`password_generator.py`): Creates and evaluates secure passwords
3. **UI Layer** (`main.py`): The graphical user interface built with Tkinter
4. **Utility Functions** (`utils.py`): Icon generation and other utilities

## Security Measures

### Master Password Protection

- **PBKDF2 Key Derivation**: The master password is never stored directly. Instead, it's processed through PBKDF2 with 100,000 iterations and a unique salt to create a key.
- **Salted Hashing**: Each user gets a unique cryptographic salt to prevent rainbow table attacks.
- **Brute-Force Protection**: After 5 failed login attempts, the system locks to prevent brute-force attacks.

### Password Encryption

- **AES-256 Encryption**: All passwords are encrypted using AES-256 via the Fernet implementation, which provides authenticated encryption.
- **Whole-Database Encryption**: The entire database file is encrypted when not in use using AES-256 in CBC mode.
- **Secure Key Management**: Encryption keys are derived from the master password and never stored.

### Runtime Security

- **Auto-Timeout**: The session automatically logs out after 5 minutes of inactivity.
- **Memory Protection**: Sensitive data is cleared from memory when no longer needed.
- **Auto-Clearing Clipboard**: When a password is copied, it's automatically cleared from the clipboard after 20 seconds.
- **Secure Deletion**: Files are securely deleted by overwriting with random data before removal.

## How It Works

### User Authentication Flow

1. User enters master password
2. System derives a key from the password using PBKDF2
3. If encrypted database exists, it attempts to decrypt using this key
4. The password hash from the database is compared with the hash of the entered password
5. Upon successful authentication, the key is stored in memory for the session

### Password Storage Flow

1. When a password is saved, it's encrypted with the derived key
2. The encrypted password is stored in the SQLite database
3. When the application is closed or times out, the entire database is encrypted

### Password Retrieval Flow

1. When a password is selected, the encrypted value is retrieved from the database
2. The value is decrypted using the key derived from the master password
3. The decrypted password is displayed or copied as needed

## Cryptographic Implementation Details

### Key Derivation

```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
```

### Password Encryption

```python
fernet = Fernet(key)
encrypted = fernet.encrypt(password.encode())
```

### Database Encryption

```python
cipher = Cipher(
    algorithms.AES(key),
    modes.CBC(iv),
    backend=default_backend()
)
encryptor = cipher.encryptor()
encrypted_content = encryptor.update(db_content) + encryptor.finalize()
```

## Building the Executable

To create a standalone executable:

1. Run `build_app.bat` (Windows) or use PyInstaller directly:
   ```
   pyinstaller --name="Password Manager" --windowed --icon=key.ico --add-data="key.ico;." --add-data="lock.png;." main.py
   ```

2. To create a desktop shortcut, run `create_shortcut.bat`

## Development Notes

### Adding New Features

The codebase is modular, making it easy to extend. To add new features:

1. For database changes, modify the `Database` class in `database.py`
2. For UI changes, update the relevant methods in `PasswordManagerApp` in `main.py`
3. For new password generation features, extend the `PasswordGenerator` class

### Security Best Practices

- Never store encryption keys or passwords in plain text
- Always salt and hash passwords before storing
- Use authenticated encryption for sensitive data
- Clear sensitive data from memory when not needed
- Implement timeout mechanisms for idle sessions 