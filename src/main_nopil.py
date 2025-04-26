import tkinter as tk 
from tkinter import ttk, messagebox, simpledialog, filedialog 
import pyperclip 
import os 
import re 
from src.database import Database 
from src.password_generator import PasswordGenerator 
import threading 
import time 
from src.utils_nopil import create_icon, create_lock_icon 
 
# Constants for security 
SESSION_TIMEOUT_SECONDS = 300  # 5 minutes 
 
