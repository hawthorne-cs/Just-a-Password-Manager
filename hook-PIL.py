import PIL 
import PIL._tkinter_finder 
import PIL._imaging 
import PIL._imagingtk 
import PIL.ImageTk 
import PIL.Image 
import PIL.PngImagePlugin 
import PIL.JpegImagePlugin 
from PyInstaller.utils.hooks import collect_submodules 
hiddenimports = collect_submodules('PIL') 
