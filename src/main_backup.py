import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyperclip
import os
import re
from src.database import Database
from src.password_generator import PasswordGenerator
import threading
import time
from src.utils import create_icon, create_lock_icon

# Constants for security
SESSION_TIMEOUT_SECONDS = 300  # 5 minutes

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Just a Password Manager")
        self.root.geometry("950x650")
        self.root.minsize(800, 600)
        
        # Create icons if they don't exist
        if not os.path.exists("../assets/../assets/../assets/key.ico") or not os.path.exists("../assets/../assets/../assets/lock.png"):
            create_icon()
            create_lock_icon()
            
        # Set icon if available
        try:
            self.root.iconbitmap("../assets/../assets/../assets/key.ico")
        except:
            pass
            
        # Initialize database and password generator
        self.db = Database()
        self.password_generator = PasswordGenerator()
        self.logged_in = False
        self.current_password_id = None
        self.last_activity_time = time.time()
        
        # Bind activity monitoring to the root window
        self.root.bind("<Button>", self.reset_activity_timer)
        self.root.bind("<Key>", self.reset_activity_timer)
        self.root.bind("<MouseWheel>", self.reset_activity_timer)
        
        # Apply themes and styles
        self.setup_styles()
        
        # Create login frame
        self.create_login_frame()
        
        # Create main application frame (hidden initially)
        self.create_main_frame()
        
        # Display login frame initially
        self.show_login_frame()
        
    def setup_styles(self):
        """Set up styles for the application"""
        self.style = ttk.Style()
        
        # Configure colors
        bg_color = "#f5f5f5"
        accent_color = "#4a6ea9"
        
        self.root.configure(bg=bg_color)
        
        # Configure ttk styles
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10))
        
        # Configure custom styles
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 12))
        self.style.configure("Accent.TButton", background=accent_color)
        
    def create_login_frame(self):
        """Create the login frame with master password input"""
        self.login_frame = ttk.Frame(self.root, padding=20)
        
        # Header
        login_header = ttk.Label(self.login_frame, text="Just a Password Manager", 
                               style="Header.TLabel")
        login_header.pack(pady=(0, 20))
        
        # Image placeholder (if available)
        try:
            self.login_image = tk.PhotoImage(file="../assets/../assets/../assets/lock.png")
            login_img_label = ttk.Label(self.login_frame, image=self.login_image)
            login_img_label.pack(pady=(0, 20))
        except:
            pass
            
        # Login form
        login_form = ttk.Frame(self.login_frame)
        login_form.pack(pady=10, fill="x")
        
        password_label = ttk.Label(login_form, text="Master Password:")
        password_label.pack(anchor="w")
        
        self.master_password_var = tk.StringVar()
        self.master_password_entry = ttk.Entry(login_form, show="•", 
                                           textvariable=self.master_password_var,
                                           width=30)
        self.master_password_entry.pack(pady=5, fill="x")
        
        # Login buttons
        buttons_frame = ttk.Frame(login_form)
        buttons_frame.pack(pady=10, fill="x")
        
        login_button = ttk.Button(buttons_frame, text="Login", 
                               command=self.login)
        login_button.pack(side="left", padx=5)
        
        setup_button = ttk.Button(buttons_frame, text="Create Master Password", 
                               command=self.setup_master_password)
        setup_button.pack(side="left", padx=5)
        
        # Bind Enter key to login
        self.master_password_entry.bind("<Return>", lambda event: self.login())
        
    def create_main_frame(self):
        """Create the main application frame with password management features"""
        self.main_frame = ttk.Frame(self.root)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout with two panes
        main_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left pane - Password list with search
        self.left_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(self.left_frame, weight=40)
        
        # Search frame
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_passwords)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", 
                                command=self.filter_passwords)
        search_button.pack(side="right", padx=5)
        
        # Password list
        list_frame = ttk.Frame(self.left_frame)
        list_frame.pack(fill="both", expand=True)
        
        columns = ("website", "username")
        self.password_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Set column headings
        self.password_tree.heading("website", text="Website")
        self.password_tree.heading("username", text="Username")
        
        # Set column widths
        self.password_tree.column("website", width=150)
        self.password_tree.column("username", width=150)
        
        # Set scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient="vertical", 
                                   command=self.password_tree.yview)
        self.password_tree.configure(yscrollcommand=tree_scroll_y.set)
        
        # Pack components
        self.password_tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")
        
        # Bind selection event
        self.password_tree.bind("<<TreeviewSelect>>", self.on_password_select)
        
        # Button frame
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill="x", pady=10)
        
        add_button = ttk.Button(button_frame, text="Add New", command=self.add_password)
        add_button.pack(side="left", padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete", 
                                command=self.delete_password)
        delete_button.pack(side="left", padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Refresh", 
                                 command=self.refresh_password_list)
        refresh_button.pack(side="right", padx=5)
        
        # Right pane - Password details
        self.right_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(self.right_frame, weight=60)
        
        # Password details frame
        details_frame = ttk.LabelFrame(self.right_frame, text="Password Details")
        details_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Website
        website_frame = ttk.Frame(details_frame)
        website_frame.pack(fill="x", pady=5)
        
        website_label = ttk.Label(website_frame, text="Website:")
        website_label.pack(side="left", padx=5)
        
        self.website_var = tk.StringVar()
        website_entry = ttk.Entry(website_frame, textvariable=self.website_var)
        website_entry.pack(side="right", fill="x", expand=True, padx=5)
        
        # Username
        username_frame = ttk.Frame(details_frame)
        username_frame.pack(fill="x", pady=5)
        
        username_label = ttk.Label(username_frame, text="Username:")
        username_label.pack(side="left", padx=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var)
        username_entry.pack(side="right", fill="x", expand=True, padx=5)
        
        # Password
        password_frame = ttk.Frame(details_frame)
        password_frame.pack(fill="x", pady=5)
        
        password_label = ttk.Label(password_frame, text="Password:")
        password_label.pack(side="left", padx=5)
        
        password_field_frame = ttk.Frame(password_frame)
        password_field_frame.pack(side="right", fill="x", expand=True)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_field_frame, 
                                     textvariable=self.password_var, show="•")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(password_field_frame, text="Show",
                                       variable=self.show_password_var,
                                       command=self.toggle_password_visibility)
        show_password_cb.pack(side="left")
        
        # Generate password and Copy buttons
        pw_button_frame = ttk.Frame(details_frame)
        pw_button_frame.pack(fill="x", pady=5)
        
        generate_button = ttk.Button(pw_button_frame, text="Generate Password",
                                  command=self.generate_password)
        generate_button.pack(side="left", padx=5)
        
        copy_button = ttk.Button(pw_button_frame, text="Copy Password",
                              command=self.copy_password)
        copy_button.pack(side="left", padx=5)
        
        # Notes
        notes_frame = ttk.Frame(details_frame)
        notes_frame.pack(fill="both", expand=True, pady=5)
        
        notes_label = ttk.Label(notes_frame, text="Notes:")
        notes_label.pack(anchor="w", padx=5)
        
        self.notes_text = tk.Text(notes_frame, height=6, width=40)
        notes_scroll = ttk.Scrollbar(notes_frame, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        
        self.notes_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        notes_scroll.pack(side="right", fill="y", pady=5)
        
        # Save button
        save_button = ttk.Button(details_frame, text="Save Changes",
                              command=self.save_password)
        save_button.pack(pady=10)
        
        # Password generator frame
        generator_frame = ttk.LabelFrame(self.right_frame, text="Password Generator")
        generator_frame.pack(fill="x", expand=False)
        
        # Length
        length_frame = ttk.Frame(generator_frame)
        length_frame.pack(fill="x", pady=5)
        
        length_label = ttk.Label(length_frame, text="Length:")
        length_label.pack(side="left", padx=5)
        
        self.length_var = tk.IntVar(value=16)
        length_scale = ttk.Scale(length_frame, from_=8, to=32, 
                              variable=self.length_var, orient="horizontal")
        length_scale.pack(side="left", fill="x", expand=True, padx=5)
        
        length_value = ttk.Label(length_frame, textvariable=self.length_var)
        length_value.pack(side="left", padx=5)
        
        # Character options
        options_frame = ttk.Frame(generator_frame)
        options_frame.pack(fill="x", pady=5)
        
        self.lowercase_var = tk.BooleanVar(value=True)
        lowercase_cb = ttk.Checkbutton(options_frame, text="Lowercase (a-z)",
                                    variable=self.lowercase_var)
        lowercase_cb.pack(side="left", padx=5)
        
        self.uppercase_var = tk.BooleanVar(value=True)
        uppercase_cb = ttk.Checkbutton(options_frame, text="Uppercase (A-Z)",
                                    variable=self.uppercase_var)
        uppercase_cb.pack(side="left", padx=5)
        
        options_frame2 = ttk.Frame(generator_frame)
        options_frame2.pack(fill="x", pady=5)
        
        self.digits_var = tk.BooleanVar(value=True)
        digits_cb = ttk.Checkbutton(options_frame2, text="Digits (0-9)",
                                 variable=self.digits_var)
        digits_cb.pack(side="left", padx=5)
        
        self.symbols_var = tk.BooleanVar(value=True)
        symbols_cb = ttk.Checkbutton(options_frame2, text="Symbols (!@#$...)",
                                  variable=self.symbols_var)
        symbols_cb.pack(side="left", padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                                 relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add New Password", command=self.add_password)
        file_menu.add_command(label="Generate Password", command=self.generate_password)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy Username", command=self.copy_username)
        edit_menu.add_command(label="Copy Password", command=self.copy_password)
        
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Change Master Password", 
                           command=self.change_master_password)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def show_login_frame(self):
        """Display the login frame"""
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.master_password_entry.focus_set()
        
    def show_main_frame(self):
        """Display the main application frame"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.refresh_password_list()
        
    def login(self):
        """Attempt to login with the provided master password"""
        master_password = self.master_password_var.get()
        
        if not master_password:
            messagebox.showerror("Login Error", "Please enter your master password.")
            return
            
        # Verify password
        if self.db.verify_master_password(master_password):
            self.logged_in = True
            self.show_main_frame()
            self.set_status("Logged in successfully")
            
            # Start session timeout monitoring
            self.reset_activity_timer()
            self.check_activity_timeout()
        else:
            messagebox.showerror("Login Error", 
                              "Invalid master password or too many failed attempts.")
            
    def setup_master_password(self):
        """Create or change the master password"""
        password = self.master_password_var.get()
        
        if not password:
            messagebox.showerror("Setup Error", "Please enter a master password.")
            return
            
        # Confirm password
        confirm = simpledialog.askstring("Confirm Password", 
                                     "Confirm your master password:", 
                                     show="•")
        
        if confirm != password:
            messagebox.showerror("Setup Error", "Passwords do not match!")
            return
            
        # Validate password strength
        strength = self.password_generator.evaluate_password_strength(password)
        if strength < 50:
            result = messagebox.askyesno("Weak Password", 
                                     "This master password is weak. It's recommended "
                                     "to use a stronger password.\n\n"
                                     "Do you want to continue anyway?")
            if not result:
                return
                
        # Create master password
        if self.db.create_master_password(password):
            messagebox.showinfo("Setup Complete", 
                             "Master password has been set successfully.")
            
    def change_master_password(self):
        """Change the master password"""
        if not self.logged_in:
            messagebox.showerror("Error", "You must be logged in to change the master password.")
            return
            
        current_password = simpledialog.askstring("Current Password", 
                                             "Enter your current master password:", 
                                             show="•")
        
        if not current_password:
            return
            
        # Verify current password
        if not self.db.verify_master_password(current_password):
            messagebox.showerror("Error", "Current password is incorrect.")
            return
            
        # Get new password
        new_password = simpledialog.askstring("New Password", 
                                         "Enter your new master password:", 
                                         show="•")
        
        if not new_password:
            return
            
        # Confirm new password
        confirm = simpledialog.askstring("Confirm Password", 
                                     "Confirm your new master password:", 
                                     show="•")
        
        if confirm != new_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
            
        # Validate password strength
        strength = self.password_generator.evaluate_password_strength(new_password)
        if strength < 50:
            result = messagebox.askyesno("Weak Password", 
                                     "This master password is weak. It's recommended "
                                     "to use a stronger password.\n\n"
                                     "Do you want to continue anyway?")
            if not result:
                return
                
        # Change master password
        if self.db.create_master_password(new_password):
            messagebox.showinfo("Success", "Master password has been changed successfully.")
            
    def logout(self):
        """Log out from the application"""
        self.logged_in = False
        self.current_password_id = None
        self.master_password_var.set("")
        self.clear_password_details()
        self.clear_sensitive_data()
        
        # Encrypt database before logging out
        if hasattr(self, 'db') and self.db.key is not None:
            self.db.encrypt_database()
            
        self.show_login_frame()
        
    def refresh_password_list(self):
        """Refresh the password list from the database"""
        # Clear existing items
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
            
        # Get passwords from database
        passwords = self.db.get_all_passwords()
        
        # Insert into treeview
        for password in passwords:
            self.password_tree.insert("", "end", 
                                  values=(password["website"], password["username"]),
                                  tags=(str(password["id"]),))
            
        self.set_status(f"Loaded {len(passwords)} passwords")
        
    def filter_passwords(self, *args):
        """Filter passwords based on search term"""
        search_term = self.search_var.get()
        
        # Clear existing items
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
            
        if not search_term:
            # If no search term, show all passwords
            self.refresh_password_list()
            return
            
        # Search for passwords
        passwords = self.db.search_passwords(search_term)
        
        # Insert into treeview
        for password in passwords:
            self.password_tree.insert("", "end", 
                                  values=(password["website"], password["username"]),
                                  tags=(str(password["id"]),))
            
        self.set_status(f"Found {len(passwords)} matches")
        
    def on_password_select(self, event):
        """Handle password selection from the list"""
        selected_items = self.password_tree.selection()
        
        if not selected_items:
            return
            
        # Get the selected item
        item_id = selected_items[0]
        
        # Get the password ID from the tags
        password_id = int(self.password_tree.item(item_id, "tags")[0])
        
        # Get passwords from database
        passwords = self.db.get_all_passwords()
        
        # Find the selected password
        selected_password = None
        for password in passwords:
            if password["id"] == password_id:
                selected_password = password
                break
                
        if selected_password:
            # Update the password details
            self.current_password_id = password_id
            self.website_var.set(selected_password["website"])
            self.username_var.set(selected_password["username"])
            self.password_var.set(selected_password["password"])
            
            # Update notes
            self.notes_text.delete("1.0", tk.END)
            if selected_password["notes"]:
                self.notes_text.insert("1.0", selected_password["notes"])
                
    def add_password(self):
        """Add a new password entry"""
        self.current_password_id = None
        self.clear_password_details()
        
    def delete_password(self):
        """Delete the selected password"""
        if not self.current_password_id:
            messagebox.showerror("Error", "No password selected.")
            return
            
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this password?")
        
        if not result:
            return
            
        # Delete password
        if self.db.delete_password(self.current_password_id):
            messagebox.showinfo("Success", "Password has been deleted.")
            self.refresh_password_list()
            self.clear_password_details()
            self.current_password_id = None
        else:
            messagebox.showerror("Error", "Failed to delete password.")
            
    def save_password(self):
        """Save the current password details"""
        website = self.website_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not website or not username or not password:
            messagebox.showerror("Error", "Website, username and password are required.")
            return
            
        # Add or update password
        if self.current_password_id:
            # Update existing password
            if self.db.update_password(self.current_password_id, website, username, password, notes):
                messagebox.showinfo("Success", "Password has been updated.")
                self.refresh_password_list()
            else:
                messagebox.showerror("Error", "Failed to update password.")
        else:
            # Add new password
            if self.db.add_password(website, username, password, notes):
                messagebox.showinfo("Success", "Password has been added.")
                self.refresh_password_list()
            else:
                messagebox.showerror("Error", "Failed to add password.")
                
    def generate_password(self):
        """Generate a random password based on settings"""
        length = self.length_var.get()
        use_lowercase = self.lowercase_var.get()
        use_uppercase = self.uppercase_var.get()
        use_digits = self.digits_var.get()
        use_symbols = self.symbols_var.get()
        
        # Generate password
        password = self.password_generator.generate_password(
            length, use_lowercase, use_uppercase, use_digits, use_symbols
        )
        
        # Update password field
        self.password_var.set(password)
        
        # Show password
        self.show_password_var.set(True)
        self.toggle_password_visibility()
        
        self.set_status(f"Generated {length}-character password")
        
    def toggle_password_visibility(self):
        """Toggle password field between showing and hiding the password"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")
            
    def copy_username(self):
        """Copy the current username to clipboard"""
        username = self.username_var.get()
        if username:
            pyperclip.copy(username)
            self.set_status("Username copied to clipboard")
            
    def copy_password(self):
        """Copy the current password to clipboard"""
        password = self.password_var.get()
        if password:
            pyperclip.copy(password)
            self.set_status("Password copied to clipboard")
            
            # Clear clipboard after 20 seconds
            clipboard_thread = threading.Thread(
                target=self.clear_clipboard_after_delay, 
                args=(password, 20)
            )
            clipboard_thread.daemon = True
            clipboard_thread.start()
            
    def clear_clipboard_after_delay(self, original_content, delay_seconds):
        """Clear the clipboard after a delay if it still contains the original content"""
        time.sleep(delay_seconds)
        
        # Check if clipboard still contains the original content
        current_content = pyperclip.paste()
        if current_content == original_content:
            pyperclip.copy("")
            self.set_status("Clipboard cleared for security")
            
    def clear_password_details(self):
        """Clear all password detail fields"""
        self.website_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.notes_text.delete("1.0", tk.END)
        
    def backup_database(self):
        """Backup the database to a file"""
        if not self.logged_in:
            messagebox.showerror("Error", "You must be logged in to backup the database.")
            return
            
        # Ask for backup file location
        backup_file = filedialog.asksaveasfilename(
            defaultextension=".bak",
            filetypes=[("Backup Files", "*.bak"), ("All Files", "*.*")],
            title="Save Backup As"
        )
        
        if not backup_file:
            return
            
        # Backup database
        if self.db.export_database(backup_file):
            messagebox.showinfo("Success", "Database backup completed successfully.")
        else:
            messagebox.showerror("Error", "Failed to backup database.")
            
    def restore_database(self):
        """Restore the database from a file"""
        if not self.logged_in:
            messagebox.showerror("Error", "You must be logged in to restore the database.")
            return
            
        # Confirm restoration
        result = messagebox.askyesno("Confirm Restore", 
                                 "Restoring will replace your current passwords. Continue?")
        
        if not result:
            return
            
        # Ask for backup file location
        backup_file = filedialog.askopenfilename(
            filetypes=[("Backup Files", "*.bak"), ("All Files", "*.*")],
            title="Open Backup File"
        )
        
        if not backup_file:
            return
            
        # Restore database
        if self.db.import_database(backup_file):
            messagebox.showinfo("Success", "Database restored successfully.")
            self.refresh_password_list()
        else:
            messagebox.showerror("Error", "Failed to restore database.")
            
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                        "Just a Password Manager\n"
                        "Version 1.0\n\n"
                        "A simple and secure password manager\n"
                        "Built with Python and Tkinter")
        
    def set_status(self, message):
        """Set status bar message"""
        self.status_var.set(message)
        
        # Clear status after 5 seconds
        self.root.after(5000, lambda: self.status_var.set(""))
        
    def reset_activity_timer(self, event=None):
        """Reset the activity timer when user interacts with the app"""
        if self.logged_in:
            self.last_activity_time = time.time()
            
    def check_activity_timeout(self):
        """Check if user has been inactive for too long and log them out"""
        if not self.logged_in:
            return
            
        # Check if timeout reached
        if time.time() - self.last_activity_time > SESSION_TIMEOUT_SECONDS:
            # Auto logout for security
            self.set_status("Session timed out due to inactivity")
            messagebox.showinfo("Session Timeout", 
                             "Your session has timed out due to inactivity.\n"
                             "You have been logged out for security reasons.")
            self.logout()
        else:
            # Schedule next check in 10 seconds
            self.root.after(10000, self.check_activity_timeout)
            
    def clear_sensitive_data(self):
        """Clear sensitive data from memory for security"""
        if hasattr(self, 'password_var'):
            current_password = self.password_var.get()
            if current_password:
                self.password_var.set('●' * len(current_password))
                
        if hasattr(self, 'master_password_var'):
            self.master_password_var.set('')
            
        # Force garbage collection to help clear memory
        import gc
        gc.collect()
        
def main():
    """Main application entry point"""
    root = tk.Tk()
    app = PasswordManagerApp(root)
    
    # Intercept window close event to ensure database encryption
    def on_closing():
        # If logged in, encrypt database before closing
        if app.logged_in:
            app.logout()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()
    
if __name__ == "__main__":
    main() 
