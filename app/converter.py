import os
from app.ocr_processor import OCRProcessor
from app.pdf_processor import PDFProcessor
from app.structure_detector import StructureDetector
from app.exporters import WordExporter, ExcelExporter, MixedExporter
from config import Config

class DocumentConverter:
    """Main converter class that orchestrates the conversion process"""
    
    def __init__(self):
        self.ocr = OCRProcessor()
        self.pdf = PDFProcessor()
        self.structure = StructureDetector()
        self.word_exporter = WordExporter()
        self.excel_exporter = ExcelExporter()
        self.mixed_exporter = MixedExporter()
    
    def convert(self, input_path, output_format, output_dir):
        """
        Main conversion method
        
        Args:
            input_path: Path to input file (PDF or image)
            output_format: 'word', 'excel', or 'both'
            output_dir: Directory to save output files
            
        Returns:
            dict: {
                'status': 'success' or 'error',
                'files': list of created file paths,
                'message': status message
            }
        """
        try:
            file_ext = os.path.splitext(input_path)[1].lower()
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # Determine input type
            if file_ext == '.pdf':
                result = self._convert_pdf(input_path, output_format, output_dir, base_name)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                result = self._convert_image(input_path, output_format, output_dir, base_name)
            else:
                return {
                    'status': 'error',
                    'files': [],
                    'message': f'Unsupported file format: {file_ext}'
                }
            
            return result
        
        except Exception as e:
            return {
                'status': 'error',
                'files': [],
                'message': str(e)
            }
    
    def _convert_pdf(self, pdf_path, output_format, output_dir, base_name):
        """Convert PDF to specified format"""
        try:
            # Check if PDF is scanned or digital
            is_scanned = self.pdf.is_scanned_pdf(pdf_path)
            
            if is_scanned:
                # Convert to images and process with OCR
                temp_dir = os.path.join(Config.UPLOAD_FOLDER, 'temp_images')
                os.makedirs(temp_dir, exist_ok=True)
                
                image_paths = self.pdf.convert_pdf_to_images(pdf_path, temp_dir)
                
                # Process all images
                all_text = []
                all_tables = []
                
                for img_path in image_paths:
                    text = self.ocr.extract_text(img_path)
                    all_text.append(text)
                    
                    # Detect tables in image
                    text_boxes = self.ocr.extract_text_with_boxes(img_path)
                    tables = self.structure.detect_table_structure(text_boxes)
                    all_tables.extend(tables)
                
                combined_text = '\n\n'.join(all_text)
                structure_data = self.structure.analyze_text_structure(combined_text)
                
                content = {
                    'text': combined_text,
                    'structure': structure_data,
                    'tables': [{'data': t} for t in all_tables]
                }
                
                # Clean up temp images
                for img_path in image_paths:
                    os.remove(img_path)
            
            else:
                # Digital PDF - extract directly
                text_data = self.pdf.extract_text_from_pdf(pdf_path)
                tables = self.pdf.extract_tables_from_pdf(pdf_path)
                
                structure_data = self.structure.analyze_text_structure(text_data['text'])
                
                content = {
                    'text': text_data['text'],
                    'structure': structure_data,
                    'tables': tables
                }
            
            # Export based on format
            return self._export_content(content, output_format, output_dir, base_name)
        
        except Exception as e:
            raise Exception(f"PDF conversion failed: {str(e)}")
    
    def _convert_image(self, image_path, output_format, output_dir, base_name):
        """Convert image to specified format"""
        try:
            # Extract text with OCR
            text = self.ocr.extract_text(image_path)
            text_boxes = self.ocr.extract_text_with_boxes(image_path)
            
            # Detect structure
            structure_data = self.structure.analyze_text_structure(text)
            tables = self.structure.detect_table_structure(text_boxes)
            
            content = {
                'text': text,
                'structure': structure_data,
                'tables': [{'data': t} for t in tables]
            }
            
            # Export based on format
            return self._export_content(content, output_format, output_dir, base_name)
        
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")
    
    def _export_content(self, content, output_format, output_dir, base_name):
        """Export content to specified format"""
        try:
            created_files = []
            
            if output_format == 'word':
                # Export to Word only
                word_path = os.path.join(output_dir, f'{base_name}.docx')
                
                if content.get('structure'):
                    self.word_exporter.create_document_from_structure(
                        content,
                        word_path,
                        title=base_name.replace('_', ' ').title()
                    )
                else:
                    self.word_exporter.create_document_from_text(
                        content['text'],
                        word_path,
                        title=base_name.replace('_', ' ').title()
                    )
                
                created_files.append(word_path)
            
            elif output_format == 'excel':
                # Export to Excel only
                if content.get('tables') and len(content['tables']) > 0:
                    excel_path = os.path.join(output_dir, f'{base_name}.xlsx')
                    table_data = [table['data'] for table in content['tables']]
                    
                    self.excel_exporter.create_excel_from_tables(
                        table_data,
                        excel_path
                    )
                    
                    created_files.append(excel_path)
                else:
                    return {
                        'status': 'error',
                        'files': [],
                        'message': 'No tables detected in document'
                    }
            
            elif output_format == 'both':
                # Export to both Word and Excel
                results = self.mixed_exporter.create_mixed_document(
                    content,
                    output_dir,
                    base_name
                )
                
                created_files = list(results.values())
            
            return {
                'status': 'success',
                'files': created_files,
                'message': f'Successfully converted to {output_format}'
            }
        
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def get_preview(self, input_path):
        """
        Get preview information about the document
        
        Returns:
            dict: Preview data
        """
        try:
            file_ext = os.path.splitext(input_path)[1].lower()
            
            if file_ext == '.pdf':
                info = self.pdf.get_pdf_info(input_path)
                
                # Extract first page text as preview
                text_data = self.pdf.extract_text_from_pdf(input_path)
                preview_text = text_data['pages'][0][:500] if text_data['pages'] else ''
                
                return {
                    'type': 'pdf',
                    'pages': info['num_pages'],
                    'is_scanned': info['is_scanned'],
                    'preview': preview_text,
                    'has_tables': len(self.pdf.extract_tables_from_pdf(input_path)) > 0
                }
            
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                text = self.ocr.extract_text(input_path)
                preview_text = text[:500] if text else ''
                
                text_boxes = self.ocr.extract_text_with_boxes(input_path)
                tables = self.structure.detect_table_structure(text_boxes)
                
                return {
                    'type': 'image',
                    'preview': preview_text,
                    'has_tables': len(tables) > 0
                }
            
            return {
                'type': 'unknown',
                'preview': '',
                'has_tables': False
            }
        
        except Exception as e:
            return {
                'type': 'error',
                'preview': f'Error: {str(e)}',
                'has_tables': False
            }