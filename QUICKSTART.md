# Quick Start Guide 🚀

Get up and running with Smart Document Converter in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed
- [ ] pip package manager available

## Step-by-Step Setup

### 1️⃣ Install Tesseract OCR

**Windows:**
```bash
# Download and run installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR\
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

### 2️⃣ Setup Project

```bash
# Clone repository (or extract zip)
cd smart-document-converter

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure Application

**Windows Users:**

Open `config.py` and verify:
```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac Users:**

Open `config.py` and verify:
```python
TESSERACT_CMD = '/usr/bin/tesseract'  # or '/usr/local/bin/tesseract'
```

### 4️⃣ Run Application

```bash
python run.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Running on http://0.0.0.0:5000
```

### 5️⃣ Open Browser

Navigate to: `http://localhost:5000`

## First Conversion

1. **Drag & drop** a PDF or image file (or click to browse)
2. **Select format**: Word, Excel, or Both
3. **Click** "Convert Document"
4. **Download** your converted files!

## Test Files

Try these test scenarios:

### Test 1: Simple PDF to Word
- Upload any PDF with text
- Select "Word Document"
- Verify text is extracted correctly

### Test 2: Table Detection
- Upload PDF with tables
- Select "Excel Spreadsheet"
- Check if tables are properly extracted

### Test 3: Image OCR
- Take a photo of a printed document
- Upload as JPG/PNG
- Select "Word Document"
- Verify OCR accuracy

## Common Issues & Quick Fixes

### Issue: "Tesseract not found"
**Fix:**
```bash
# Windows - Add to PATH or update config.py
# Linux - Reinstall: sudo apt install tesseract-ocr
# Mac - Reinstall: brew install tesseract
```

### Issue: "Module not found"
**Fix:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt --upgrade
```

### Issue: "Permission denied on uploads/"
**Fix:**
```bash
# Create directories with proper permissions
mkdir -p uploads outputs
chmod 755 uploads outputs
```

### Issue: Poor OCR quality
**Fix:**
1. Use higher resolution images (300+ DPI)
2. Enable preprocessing in `config.py`
3. Ensure good lighting/contrast in photos

## Performance Tips

### For Large Files (>5MB):
- Convert to smaller chunks if possible
- Close other applications
- Increase `MAX_FILE_SIZE` if needed

### For Better OCR:
- Use 300 DPI or higher resolution
- Ensure text is straight (not rotated)
- Good contrast between text and background
- Clean, clear images without noise

### For Table Detection:
- Tables should have clear borders
- Consistent column/row spacing
- Avoid handwritten content
- Use "Both" format for mixed documents

## Next Steps

1. **Read Full Documentation**: Check `README.md`
2. **Explore Features**: Try all conversion formats
3. **Customize Settings**: Edit `config.py` for your needs
4. **Add Languages**: Install additional Tesseract language packs

## Additional Languages

To support more languages:

**Windows:**
```bash
# Download language data files from:
# https://github.com/tesseract-ocr/tessdata
# Copy to: C:\Program Files\Tesseract-OCR\tessdata\
```

**Linux:**
```bash
sudo apt install tesseract-ocr-ara  # Arabic
sudo apt install tesseract-ocr-fra  # French
sudo apt install tesseract-ocr-deu  # German
sudo apt install tesseract-ocr-spa  # Spanish
```

Update `config.py`:
```python
OCR_LANG = 'eng+ara'  # English + Arabic
```

## Development Mode

For development with auto-reload:

```bash
# Set in config.py
DEBUG = True

# Run with Flask development server
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

## Production Deployment

### Quick Production Setup:

```bash
# Install production server
pip install gunicorn  # Linux/Mac
pip install waitress  # Windows

# Run production server
gunicorn -w 4 -b 0.0.0.0:5000 run:app  # Linux/Mac
waitress-serve --port=5000 run:app      # Windows
```

## Getting Help

- **Documentation**: See `README.md`
- **Issues**: Check GitHub Issues
- **Errors**: Check console output for details

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python run.py` | Start application |
| `pip install -r requirements.txt` | Install dependencies |
| `pip list` | Show installed packages |
| `deactivate` | Exit virtual environment |

## Success Checklist

- [x] Tesseract installed and configured
- [x] Dependencies installed
- [x] Application running on localhost:5000
- [x] Successfully converted a test file
- [x] Downloaded converted file

**You're all set! Happy converting! 🎉**