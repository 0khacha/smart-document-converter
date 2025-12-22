import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance
from config import Config
import os

class OCRProcessor:
    """Optimized OCR processor for large images"""
    
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
    
    def preprocess_image(self, image_path):
        """
        Optimized preprocessing for large images
        """
        try:
            # Read with PIL
            pil_img = Image.open(image_path)
            
            # Check size and resize if too large
            width, height = pil_img.size
            max_dimension = 4000  # Increased max dimension for better quality
            
            if width > max_dimension or height > max_dimension:
                # Resize to reasonable size
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))
                
                pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
                print(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            # Smart scaling logic
            if width < 2000 and height < 2000:
                # Upscale small images
                scale = 2.0
                new_size = (int(width * scale), int(height * scale))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
                print(f"Upscaled small image to {new_size}")
            elif width > 4000 or height > 4000:
                # Downscale massive images (prevent Tesseract confusion/slowdown)
                if width > height:
                    scale = 4000 / width
                else:
                    scale = 4000 / height
                new_size = (int(width * scale), int(height * scale))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
                print(f"Downscaled huge image to {new_size}")
            else:
                # Keep original high-quality size (e.g. 300 DPI scan)
                pass
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer.enhance(1.5)
            
            # Convert to grayscale
            pil_img = pil_img.convert('L')
            
            # Convert to numpy array
            img = np.array(pil_img)
            
            # ROI: Return grayscale directly for Tesseract (better for gradients/faint text)
            # _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return img
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            # Fallback
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise Exception("Cannot read image")
            return img
    
    def extract_text(self, image_path, preprocess=True):
        """
        Extract text from image with error handling
        """
        try:
            print(f"Extracting text from: {os.path.basename(image_path)}")
            
            if preprocess and Config.IMAGE_PREPROCESS:
                img = self.preprocess_image(image_path)
            else:
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    raise Exception("Cannot read image")
            
            # OCR
            custom_config = Config.OCR_CONFIG
            
            text = pytesseract.image_to_string(
                img,
                lang=Config.OCR_LANG,
                config=custom_config
            )
            
            # Clean text
            text = self.clean_ocr_text(text)
            
            print(f"Extracted {len(text)} characters")
            return text.strip()
        
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            try:
                # Simple fallback
                img = Image.open(image_path)
                # Resize if too large
                width, height = img.size
                if width > 2000 or height > 2000:
                    img.thumbnail((2000, 2000), Image.LANCZOS)
                
                text = pytesseract.image_to_string(img, lang=Config.OCR_LANG)
                return self.clean_ocr_text(text)
            except Exception as e2:
                print(f"Fallback OCR also failed: {str(e2)}")
                return f"Error extracting text: {str(e)}"

    def extract_text_with_boxes(self, image_path, lang=None):
        """Extract text with bounding box information"""
        try:
            if lang is None:
                lang = Config.OCR_LANG
                
            # Preprocess
            if Config.IMAGE_PREPROCESS:
                img_array = self.preprocess_image(image_path)
                img = Image.fromarray(img_array)
            else:
                img = Image.open(image_path)
            
            # Config
            custom_config = Config.OCR_CONFIG
            
            # Get data
            data = pytesseract.image_to_data(img, lang=lang, config=custom_config, output_type=pytesseract.Output.DICT)
            
            boxes = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                # Lower confidence threshold to capture more text
                if data['conf'][i] != '-1' and int(data['conf'][i]) > 10 and data['text'][i].strip():
                    boxes.append({
                        'text': data['text'][i].strip(),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': int(data['conf'][i])
                    })
            
            return boxes
            
        except Exception as e:
            print(f"Text box extraction error: {str(e)}")
            return []
    
    def clean_ocr_text(self, text):
        """Clean OCR output"""
        try:
            if not text:
                return ""
            
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    cleaned_lines.append(line)
                elif cleaned_lines and cleaned_lines[-1] != '':
                    cleaned_lines.append('')
            
            # Remove multiple empty lines
            result = []
            prev_empty = False
            for line in cleaned_lines:
                if line == '':
                    if not prev_empty:
                        result.append(line)
                    prev_empty = True
                else:
                    result.append(line)
                    prev_empty = False
            
            return '\n'.join(result)
        except:
            return text if text else ""
    
    def detect_tables_in_image(self, image_path):
        """
        Detect tables - optimized for large images
        """
        try:
            # Read image at lower resolution for detection
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            # Resize if too large
            height, width = img.shape[:2]
            if width > 2000 or height > 2000:
                scale = min(2000/width, 2000/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Detect lines
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel, iterations=2)
            vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel, iterations=2)
            
            # Combine
            table_mask = cv2.addWeighted(horizontal, 0.5, vertical, 0.5, 0.0)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            tables = []
            img_height, img_width = img.shape[:2]
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                img_area = img_width * img_height
                
                # Filter by size
                if w > 150 and h > 80 and area > (img_area * 0.03):
                    tables.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'area': area
                    })
            
            # Sort by area
            tables.sort(key=lambda t: t['area'], reverse=True)
            
            print(f"Detected {len(tables)} tables")
            return tables
            
        except Exception as e:
            print(f"Table detection error: {str(e)}")
            return []