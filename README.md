# Just a Password Manager

A simple, secure desktop password manager built with Python and Tkinter. This application allows you to securely store, retrieve, and manage your passwords with a user-friendly interface.

## Features

- Secure login with master password
- Encrypted password storage using AES-256 and SQLite
- Password generation with customizable options
- Convenient password retrieval and management
- Copy passwords to clipboard (auto-clears after 20 seconds)
- Backup and restore functionality
- Brute-force attack protection

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Pip package manager

### Installation

1. Clone this repository or download the zip file
2. Run the application using the provided scripts:

**Windows:**
```
run.bat
```

**Linux/Mac:**
```
chmod +x run.sh
./run.sh
```

The scripts will automatically set up a virtual environment and install the required dependencies.

### Manual Setup

If the scripts don't work for your system, you can set up manually:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## First Use

1. When you first launch the application, you'll need to create a master password
2. Enter your desired master password and click "Create Master Password"
3. Confirm your password when prompted
4. Use this master password to log in to the application in the future

## Usage

### Adding Passwords

1. Click "Add New" or use File > Add New Password
2. Enter the website, username, and password details
3. Click "Save Changes"

### Generating Passwords

1. Click "Generate Password" in the password field
2. Adjust the length and character options as needed
3. The generated password will appear in the password field

### Searching Passwords

Use the search box in the top-left to filter your passwords by website or username.

### Backup and Restore

- To backup: File > Backup Database
- To restore: File > Restore Database

## Security

This application uses industry-standard security measures:

- AES-256 encryption for all stored passwords
- PBKDF2 key derivation with 100,000 iterations
- All data stored locally, never transmitted over the internet
- Automatic clipboard clearing after password copy
- Lockout mechanism after multiple failed login attempts

## License

This project is open source and available under the MIT License. 