# Smart Document Converter 📄

Convert PDF files and images to editable Word and Excel documents with intelligent structure detection.

## ✨ Features

- **PDF to Word**: Convert digital and scanned PDFs to editable Word documents
- **PDF to Excel**: Extract tables from PDFs into organized Excel spreadsheets
- **Image to Word**: OCR text extraction from images (JPG, PNG) to Word
- **Image to Excel**: Detect and extract tables from images to Excel
- **Smart Structure Detection**: Automatically identifies headings, paragraphs, lists, and tables
- **Dual Output**: Generate both Word and Excel files simultaneously
- **Modern Web Interface**: Beautiful, responsive UI with drag-and-drop support
- **Document Preview**: Preview extracted content before conversion

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask
- **OCR**: Tesseract, OpenCV
- **PDF Processing**: pdfplumber, PyMuPDF
- **Document Export**: python-docx, openpyxl, pandas
- **Frontend**: Bootstrap 5, JavaScript

## 📋 Prerequisites

### 1. Python 3.8 or higher

### 2. Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to system PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr 
sudo apt install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

### 3. System Dependencies (Linux only)

```bash
sudo apt install python3-dev
sudo apt install libgl1-mesa-glx
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart-document-converter.git
cd smart-document-converter
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Tesseract Path

Edit `config.py` and update the Tesseract path:

**Windows:**
```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac:**
```python
TESSERACT_CMD = '/usr/bin/tesseract'
```

### 5. Create Required Directories

The application will automatically create these on first run, but you can create them manually:

```bash
mkdir uploads outputs
```

## 🎯 Usage

### Starting the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

### Using the Web Interface

1. **Open Browser**: Navigate to `http://localhost:5000`
2. **Upload File**: Drag & drop or click to browse for PDF/image files
3. **Select Format**: Choose Word, Excel, or Both
4. **Convert**: Click "Convert Document" button
5. **Download**: Download your converted files

### Supported File Types

- **Input**: PDF, PNG, JPG, JPEG
- **Output**: DOCX (Word), XLSX (Excel)
- **Max File Size**: 16MB

## 📁 Project Structure

```
smart-document-converter/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── routes.py             # API endpoints
│   ├── converter.py          # Main conversion logic
│   ├── ocr_processor.py      # OCR operations
│   ├── pdf_processor.py      # PDF processing
│   ├── structure_detector.py # Document structure analysis
│   └── exporters.py          # Word/Excel export
├── static/
│   ├── css/
│   │   └── style.css         # Custom styles
│   └── js/
│       └── script.js         # Frontend logic
├── templates/
│   └── index.html            # Main UI
├── uploads/                  # Uploaded files (auto-created)
├── outputs/                  # Converted files (auto-created)
├── config.py                 # Configuration
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# File upload settings
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# OCR settings
OCR_LANG = 'eng'  # Language: eng, ara, fra, deu, etc.
OCR_CONFIG = '--oem 3 --psm 6'
IMAGE_PREPROCESS = True  # Enable image preprocessing

# Processing settings
MIN_TABLE_CONFIDENCE = 0.5
```

## 🎨 Conversion Scenarios

### 1. Image → Word
- Extracts text using OCR
- Preserves document structure
- Exports as `.docx`

### 2. Image → Excel
- Detects table structures
- Converts to DataFrame
- Exports as `.xlsx`

### 3. PDF → Word
- Digital PDFs: Direct text extraction
- Scanned PDFs: OCR processing
- Preserves formatting and structure

### 4. PDF → Excel
- Extracts all tables
- Each table becomes a sheet
- Headers are styled automatically

### 5. Mixed Content → Both
- Text content → Word document
- Tables → Excel spreadsheet
- Both files created simultaneously

## 🐛 Troubleshooting

### Tesseract Not Found Error

**Error**: `TesseractNotFoundError`

**Solution**: 
1. Verify Tesseract is installed
2. Check path in `config.py`
3. Ensure Tesseract is in system PATH

### Import Error for cv2

**Error**: `ImportError: libGL.so.1`

**Solution** (Linux):
```bash
sudo apt install libgl1-mesa-glx
```

### Poor OCR Results

**Solutions**:
1. Enable image preprocessing in `config.py`
2. Use higher quality input images
3. Adjust OCR configuration settings
4. Install additional language packs

### Table Detection Issues

**Solutions**:
1. Ensure tables have clear borders
2. Adjust `MIN_TABLE_CONFIDENCE` in config
3. Try "Both" format for better results

## 📊 API Endpoints

### Upload File
```
POST /upload
Content-Type: multipart/form-data
Body: file (PDF/Image)

Response:
{
  "status": "success",
  "filename": "abc123_document.pdf",
  "preview": {...}
}
```

### Convert Document
```
POST /convert
Content-Type: application/json
Body: {
  "filename": "abc123_document.pdf",
  "format": "word" | "excel" | "both"
}

Response:
{
  "status": "success",
  "files": [...],
  "downloads": [...]
}
```

### Download File
```
GET /download/<filename>
Response: File download
```

## 🧪 Testing

To test the application:

1. **Test PDF Conversion**:
   - Upload a PDF with text
   - Upload a scanned PDF
   - Check both Word and Excel outputs

2. **Test Image Conversion**:
   - Upload clear images with text
   - Upload images with tables
   - Verify OCR accuracy

3. **Test Error Handling**:
   - Try unsupported file types
   - Test with large files (>16MB)
   - Test with corrupted files

## 🚀 Deployment

### Production Settings

Update `config.py` for production:

```python
DEBUG = False
SECRET_KEY = 'your-secure-random-key'
```

### Using Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --port=5000 run:app
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🎯 Future Enhancements

- [ ] Batch processing multiple files
- [ ] Support for more languages
- [ ] Cloud storage integration
- [ ] PDF editing before conversion
- [ ] Custom templates for exports
- [ ] API authentication
- [ ] Progress tracking for large files
- [ ] Email notification on completion

## 🙏 Acknowledgments

- Tesseract OCR by Google
- Flask framework
- Bootstrap for UI
- All open-source libraries used

---

**Happy Converting! 📄✨**