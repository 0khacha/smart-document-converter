import re
from collections import defaultdict

class StructureDetector:
    """Detect document structure - FIXED VERSION"""
    
    def __init__(self):
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]+$',
            r'^\d+\.?\s+[A-Z]',
            r'^Chapter\s+\d+',
            r'^Section\s+\d+',
        ]
    
    def analyze_text_structure(self, text):
        """Analyze text structure - SAFE VERSION"""
        try:
            if not text or not isinstance(text, str):
                return {
                    'headings': [],
                    'paragraphs': [],
                    'lists': [],
                    'structure': []
                }
            
            lines = text.split('\n')
            
            result = {
                'headings': [],
                'paragraphs': [],
                'lists': [],
                'structure': []
            }
            
            current_paragraph = []
            current_list = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                if not line:
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        result['paragraphs'].append(para_text)
                        result['structure'].append({
                            'type': 'paragraph',
                            'content': para_text,
                            'line': i
                        })
                        current_paragraph = []
                    
                    if current_list:
                        # Determine list type from first item
                        list_type = 'bullet'
                        if current_list:
                            first_type = self.get_list_type(current_list[0])
                            if first_type:
                                list_type = first_type
                                
                        result['lists'].append(current_list.copy())
                        result['structure'].append({
                            'type': 'list',
                            'list_type': list_type,
                            'items': current_list.copy(),
                            'line': i
                        })
                        current_list = []
                    
                    continue
                
                if self.is_heading(line):
                    result['headings'].append(line)
                    result['structure'].append({
                        'type': 'heading',
                        'content': line,
                        'level': self.get_heading_level(line),
                        'line': i
                    })
                
                elif self.is_list_item(line):
                    current_list.append(line)
                
                else:
                    current_paragraph.append(line)
            
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                result['paragraphs'].append(para_text)
                result['structure'].append({
                    'type': 'paragraph',
                    'content': para_text,
                    'line': len(lines)
                })
            
            if current_list:
                # Determine list type
                list_type = 'bullet'
                if current_list:
                    first_type = self.get_list_type(current_list[0])
                    if first_type:
                        list_type = first_type

                result['lists'].append(current_list)
                result['structure'].append({
                    'type': 'list',
                    'list_type': list_type,
                    'items': current_list,
                    'line': len(lines)
                })
            
            return result
        
        except Exception as e:
            print(f"Structure analysis error: {str(e)}")
            return {
                'headings': [],
                'paragraphs': [text] if text else [],
                'lists': [],
                'structure': [{'type': 'paragraph', 'content': text, 'line': 0}] if text else []
            }
    
    def is_heading(self, line):
        """Check if line is heading"""
        try:
            if not line or len(line) > 100:
                return False
            
            for pattern in self.heading_patterns:
                if re.match(pattern, line):
                    return True
            
            if len(line) < 60 and not line.endswith(('.', ',', ';', ':')):
                words = line.split()
                if len(words) <= 8 and line[0].isupper():
                    return True
            
            return False
        except:
            return False
    
    def get_heading_level(self, line):
        """Get heading level"""
        try:
            match = re.match(r'^(\d+\.)+', line)
            if match:
                return min(len(match.group(0).split('.')), 6)
            
            if line.isupper():
                return 1
            
            return 2
        except:
            return 2
    
    def is_list_item(self, line):
        """Check if line is list item"""
        return self.get_list_type(line) is not None

    def get_list_type(self, line):
        """Get type of list item: 'bullet' or 'numbered'"""
        try:
            # Numbered patterns (1., 1), a., A.)
            numbered_patterns = [
                r'^\s*\d+\.\s+',
                r'^\s*\d+\)\s+',
                r'^\s*[a-z]\.\s+',
                r'^\s*[A-Z]\.\s+',
            ]
            
            # Bullet patterns (-, *, •)
            bullet_patterns = [
                r'^\s*[-•*]\s+',
            ]
            
            for pattern in numbered_patterns:
                if re.match(pattern, line):
                    return 'numbered'
            
            for pattern in bullet_patterns:
                if re.match(pattern, line):
                    return 'bullet'
            
            return None
        except:
            return None
    
    def merge_close_words(self, row, avg_char_width):
        """Merge words that are close together into a single text block"""
        if not row:
            return []
            
        merged_row = []
        current_block = row[0].copy()
        
        # Threshold for merging: 3.5x average character width
        # Use a reasonable default if width calc is weird
        gap_threshold = avg_char_width * 3.5 if avg_char_width > 0 else 35
        
        for i in range(1, len(row)):
            box = row[i]
            prev_right = current_block['left'] + current_block['width']
            gap = box['left'] - prev_right
            
            if gap < gap_threshold:
                # Merge
                current_block['text'] += " " + box['text']
                current_block['width'] = (box['left'] + box['width']) - current_block['left']
                current_block['height'] = max(current_block['height'], box['height'])
            else:
                # Gap is large enough to be a new column
                merged_row.append(current_block)
                current_block = box.copy()
        
        merged_row.append(current_block)
        return merged_row

    def detect_table_structure(self, text_boxes):
        """
        Detect table structure from OCR text boxes
        
        Args:
            text_boxes: List of dicts with text and position info
            
        Returns:
            list: Detected tables as structured data
        """
        # ULTRA-STRICT MODE: NO TABLES ALLOWED
        return []
        
        avg_height = sum(heights) / len(heights)
        # Approximate char width (very rough)
        avg_char_width = avg_height * 0.5 
        
        row_tolerance = avg_height * 0.6  # Tolerance for being in the same row
        
        # Sort boxes by top position
        sorted_boxes = sorted(text_boxes, key=lambda x: x['top'])
        
        # Group into rows
        rows = []
        current_row = []
        current_row_y = 0
        
        for box in sorted_boxes:
            if not current_row:
                current_row.append(box)
                current_row_y = box['top']
            else:
                # Check if box belongs to current row (vertical overlap)
                if abs(box['top'] - current_row_y) < row_tolerance:
                    current_row.append(box)
                else:
                    # Start new row
                    rows.append(current_row)
                    current_row = [box]
                    current_row_y = box['top']
        
        if current_row:
            rows.append(current_row)
        
        # Sort each row horizontally
        for row in rows:
            row.sort(key=lambda x: x['left'])
        
        # Filter for table-like structure (aligned columns)
        # Simple heuristic: consecutive rows with similar number of items
        tables = []
        current_table = []
        
        for i, row in enumerate(rows):
            # MERGE STEP: Merge close words into blocks
            # This turns "Hello World" (2 items) into "Hello World" (1 item)
            # But "Column1   Column2" (2 items) stays (2 items) due to gap
            merged_row = self.merge_close_words(row, avg_char_width)
            
            # If row has multiple items after merge, it might be table row
            if len(merged_row) >= 2:
                # Keep BOX objects for validation, extract text later
                current_table.append(merged_row)
            else:
                if len(current_table) >= 2:
                    tables.append(current_table)
                    current_table = []
                elif current_table: 
                     current_table = []
        
        if len(current_table) >= 2:
            tables.append(current_table)
            
        # Strict validation with Alignment Check
        valid_tables_text = []
        
        for table_boxes in tables:
            # Rule 1: Must have at least 2 rows
            if len(table_boxes) < 2:
                continue
            
            # Rule 2: Calculate average columns
            avg_cols = sum(len(row) for row in table_boxes) / len(table_boxes)
            if avg_cols < 2:
                continue
            
            # Rule 3: Visual Alignment Check
            # Check if columns (items at index j) overlap horizontally across rows
            aligned = True
            if len(table_boxes) > 1:
                # Compare first row with middle row to check alignment
                mid = len(table_boxes) // 2
                row_a = table_boxes[0]
                row_b = table_boxes[mid]
                
                # Crude overlap check: at least one column must overlap significantly
                overlap_found = False
                for box_a in row_a:
                    for box_b in row_b:
                        # Check horizontal overlap
                        x_overlap = min(box_a['left'] + box_a['width'], box_b['left'] + box_b['width']) - max(box_a['left'], box_b['left'])
                        if x_overlap > 0:
                            overlap_found = True
                            break
                    if overlap_found:
                        break
                
                if not overlap_found:
                    aligned = False

            if not aligned:
                continue

            # Valid table found - Convert to text
            table_text = []
            for row in table_boxes:
                table_text.append([box['text'] for box in row])
            valid_tables_text.append(table_text)
            
        return valid_tables_text

    def clean_text(self, text):
        """Clean text"""
        try:
            if not text:
                return ""
            
            text = re.sub(r'\s+', ' ', text)
            # Removed number filtering to preserve data
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
        except:
            return text if text else ""