import os
from PIL import Image

# Remove PIL image size limit for large PDFs
Image.MAX_IMAGE_PIXELS = None

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
    
    # OCR settings
    TESSERACT_PATHS = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\tesseract\tesseract.exe',
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
    ]
    
    # Find Tesseract automatically
    TESSERACT_CMD = None
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            TESSERACT_CMD = path
            break
    
    if TESSERACT_CMD is None:
        TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # OCR configuration
    OCR_LANG = 'eng'
    OCR_CONFIG = '--oem 3 --psm 3 -c preserve_interword_spaces=1'  # Default engine + Auto seg + preserve spaces
    
    # Image processing - OPTIMIZED for QUALITY
    IMAGE_PREPROCESS = True
    DPI = 300  # Standard OCR DPI
    SCALE_FACTOR = 1.0  # Default 1.0, controlled by smart logic
    
    # Processing settings
    MIN_TABLE_CONFIDENCE = 0.7
    PRESERVE_FORMATTING = True
    
    # Flask settings
    SECRET_KEY = 'your-secret-key'
    DEBUG = True
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        
        # Check Tesseract
        if not os.path.exists(Config.TESSERACT_CMD):
            print("\n" + "="*70)
            print("WARNING: Tesseract OCR not found!")
            print(f"Expected: {Config.TESSERACT_CMD}")
            print("Download: https://github.com/UB-Mannheim/tesseract/wiki")
            print("="*70 + "\n")