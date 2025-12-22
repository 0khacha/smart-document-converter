import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import io
import os

class PDFProcessor:
    """Enhanced PDF processing with better text extraction"""
    
    def __init__(self):
        pass
    
    def is_scanned_pdf(self, pdf_path):
        """
        Accurately determine if PDF is scanned or digital
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check first 3 pages for better accuracy
                total_text = ""
                pages_to_check = min(3, len(pdf.pages))
                
                for i in range(pages_to_check):
                    text = pdf.pages[i].extract_text()
                    if text:
                        total_text += text
                
                # If less than 100 chars in 3 pages, likely scanned
                return len(total_text.strip()) < 100
        
        except Exception as e:
            print(f"Error checking PDF type: {str(e)}")
            return True
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Enhanced text extraction preserving formatting
        """
        try:
            result = {
                'text': '',
                'pages': [],
                'metadata': {}
            }
            
            with pdfplumber.open(pdf_path) as pdf:
                result['metadata'] = pdf.metadata
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text with layout preserved
                    text = page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3,
                        layout=True,
                        x_density=7.25,
                        y_density=13
                    )
                    
                    if text:
                        # Clean up the text
                        text = self.clean_extracted_text(text)
                        result['pages'].append(text)
                        result['text'] += text + '\n\n'
                    else:
                        result['pages'].append('')
            
            return result
        
        except Exception as e:
            print(f"Text extraction error: {str(e)}")
            # Fallback to basic extraction
            try:
                return self._basic_text_extraction(pdf_path)
            except:
                raise Exception(f"Failed to extract text: {str(e)}")
    
    def _basic_text_extraction(self, pdf_path):
        """Fallback basic extraction"""
        result = {'text': '', 'pages': [], 'metadata': {}}
        
        with pdfplumber.open(pdf_path) as pdf:
            result['metadata'] = pdf.metadata
            for page in pdf.pages:
                text = page.extract_text() or ''
                result['pages'].append(text)
                result['text'] += text + '\n\n'
        
        return result
    
    def clean_extracted_text(self, text):
        """
        Clean extracted text while preserving structure
        """
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            # Remove excessive spaces but preserve indentation
            line = ' '.join(line.split())
            cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def extract_tables_from_pdf(self, pdf_path):
        """
        Enhanced table extraction with better accuracy
        """
        try:
            tables = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables with better settings
                    page_tables = page.extract_tables({
                        "vertical_strategy": "lines_strict",
                        "horizontal_strategy": "lines_strict",
                        "intersection_tolerance": 15,
                        "min_words_vertical": 3,
                        "min_words_horizontal": 1,
                    })
                    
                    for table in page_tables:
                        if table and len(table) > 0:
                            # Clean table data
                            cleaned_table = self.clean_table(table)
                            if cleaned_table:
                                tables.append({
                                    'page': page_num + 1,
                                    'data': cleaned_table
                                })
            
            return tables
        
        except Exception as e:
            print(f"Table extraction error: {str(e)}")
            # Fallback to basic extraction
            try:
                return self._basic_table_extraction(pdf_path)
            except:
                return []
    
    def _basic_table_extraction(self, pdf_path):
        """Fallback basic table extraction"""
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        tables.append({
                            'page': page_num + 1,
                            'data': table
                        })
        return tables
    
    def clean_table(self, table):
        """
        Clean table data - remove empty rows/cols
        """
        if not table:
            return None
        
        # Remove completely empty rows
        cleaned = []
        for row in table:
            if any(cell and str(cell).strip() for cell in row):
                # Clean each cell
                cleaned_row = []
                for cell in row:
                    if cell:
                        # Clean cell content
                        cell_str = str(cell).strip()
                        cell_str = ' '.join(cell_str.split())
                        cleaned_row.append(cell_str)
                    else:
                        cleaned_row.append('')
                cleaned.append(cleaned_row)
        
        # Remove completely empty columns
        if not cleaned:
            return None
        
        num_cols = len(cleaned[0])
        non_empty_cols = []
        
        for col_idx in range(num_cols):
            has_content = any(
                row[col_idx] if col_idx < len(row) else '' 
                for row in cleaned
            )
            if has_content:
                non_empty_cols.append(col_idx)
        
        # Rebuild table with non-empty columns
        if not non_empty_cols:
            return None
        
        final_table = []
        for row in cleaned:
            final_row = [row[idx] if idx < len(row) else '' for idx in non_empty_cols]
            final_table.append(final_row)
        
        return final_table if final_table else None
    
    def convert_pdf_to_images(self, pdf_path, output_dir):
        """
        Convert PDF to high-quality images for OCR
        """
        try:
            image_paths = []
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Use higher DPI for better quality
                zoom = 300 / 72  # 300 DPI
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Save as high-quality PNG
                img_path = os.path.join(output_dir, f'page_{page_num + 1}.png')
                pix.save(img_path)
                image_paths.append(img_path)
            
            doc.close()
            return image_paths
        
        except Exception as e:
            raise Exception(f"PDF to image conversion failed: {str(e)}")
    
    def extract_images_from_pdf(self, pdf_path, output_dir):
        """Extract embedded images"""
        try:
            image_paths = []
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    img_path = os.path.join(
                        output_dir,
                        f'page_{page_num + 1}_img_{img_index + 1}.png'
                    )
                    
                    with open(img_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    
                    image_paths.append(img_path)
            
            doc.close()
            return image_paths
        
        except Exception as e:
            print(f"Image extraction error: {str(e)}")
            return []
    
    def get_pdf_info(self, pdf_path):
        """Get detailed PDF information"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                is_scanned = self.is_scanned_pdf(pdf_path)
                
                return {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata,
                    'is_scanned': is_scanned,
                    'has_text': not is_scanned
                }
        
        except Exception as e:
            raise Exception(f"Failed to get PDF info: {str(e)}")