import base64
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageDraw

def create_icon():
    """Create a simple key icon and save it as a file"""
    try:
        # Create a new image with a transparent background
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple key
        # Key circle
        draw.ellipse((8, 8, 28, 28), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=2)
        
        # Key shaft
        draw.rectangle((25, 16, 56, 22), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        
        # Key teeth
        draw.rectangle((35, 22, 40, 32), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        draw.rectangle((45, 22, 50, 32), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        
        # Save the image
        img.save('key.ico', 'ICO')
        
        # Also save as PNG for login screen
        img.save('lock.png', 'PNG')
        
        return True
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False

def get_key_icon_base64():
    """Create a key icon and return it as a base64 string for embedding"""
    try:
        # Create a new image with a transparent background
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple key
        # Key circle
        draw.ellipse((8, 8, 28, 28), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=2)
        
        # Key shaft
        draw.rectangle((25, 16, 56, 22), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        
        # Key teeth
        draw.rectangle((35, 22, 40, 32), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        draw.rectangle((45, 22, 50, 32), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=1)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_str
    except Exception as e:
        print(f"Error creating icon: {e}")
        return None

def create_lock_icon(filename='lock.png'):
    """Create a simple lock icon and save it"""
    try:
        # Create a new image with a transparent background
        img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple lock
        # Lock body
        draw.rectangle((32, 48, 96, 112), fill=(74, 110, 169, 255), outline=(41, 61, 93, 255), width=2)
        
        # Lock shackle
        draw.arc((32, 12, 96, 76), start=0, end=180, fill=(74, 110, 169, 255), width=4)
        draw.line((32, 44, 32, 56), fill=(74, 110, 169, 255), width=4)
        draw.line((96, 44, 96, 56), fill=(74, 110, 169, 255), width=4)
        
        # Lock keyhole
        draw.ellipse((58, 70, 70, 82), fill=(255, 255, 255, 255), outline=(41, 61, 93, 255), width=1)
        draw.rectangle((62, 75, 66, 95), fill=(255, 255, 255, 255), outline=(41, 61, 93, 255), width=1)
        
        # Save the image
        img.save(filename, 'PNG')
        
        return True
    except Exception as e:
        print(f"Error creating lock icon: {e}")
        return False 