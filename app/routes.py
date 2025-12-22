from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
from werkzeug.utils import secure_filename
from app.converter import DocumentConverter
from config import Config
import uuid

main = Blueprint('main', __name__)
converter = DocumentConverter()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@main.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'Invalid file type. Allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get preview
        preview = converter.get_preview(filepath)
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'filename': filename,
            'preview': preview
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/convert', methods=['POST'])
def convert_file():
    """Handle file conversion"""
    try:
        data = request.json
        
        filename = data.get('filename')
        output_format = data.get('format', 'word')
        
        if not filename:
            return jsonify({
                'status': 'error',
                'message': 'No filename provided'
            }), 400
        
        # Validate format
        if output_format not in ['word', 'excel', 'both']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid output format'
            }), 400
        
        # Convert file
        input_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        if not os.path.exists(input_path):
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404
        
        result = converter.convert(input_path, output_format, Config.OUTPUT_FOLDER)
        
        if result['status'] == 'success':
            # Return download links
            download_links = []
            for file_path in result['files']:
                file_name = os.path.basename(file_path)
                download_links.append({
                    'name': file_name,
                    'url': f'/download/{file_name}'
                })
            
            result['downloads'] = download_links
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/download/<filename>')
def download_file(filename):
    """Download converted file"""
    try:
        filepath = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/preview/<filename>')
def preview_file(filename):
    """Get file preview"""
    try:
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404
        
        preview = converter.get_preview(filepath)
        
        return jsonify({
            'status': 'success',
            'preview': preview
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old files"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if filename:
            # Remove specific file
            upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            if os.path.exists(upload_path):
                os.remove(upload_path)
        
        return jsonify({
            'status': 'success',
            'message': 'Files cleaned up'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500