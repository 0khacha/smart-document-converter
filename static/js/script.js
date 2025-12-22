// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const formatSelection = document.getElementById('formatSelection');
const convertBtn = document.getElementById('convertBtn');
const previewSection = document.getElementById('previewSection');
const previewContent = document.getElementById('previewContent');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const downloadLinks = document.getElementById('downloadLinks');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const convertAnotherBtn = document.getElementById('convertAnotherBtn');

// State
let uploadedFile = null;
let selectedFormat = null;

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
removeFileBtn.addEventListener('click', removeFile);
convertBtn.addEventListener('click', convertDocument);
convertAnotherBtn.addEventListener('click', resetForm);

// Format selection
document.querySelectorAll('.format-card').forEach(card => {
    card.addEventListener('click', function() {
        document.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
        this.classList.add('selected');
        selectedFormat = this.dataset.format;
        convertBtn.disabled = false;
    });
});

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// File Selection Handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// Process File
async function processFile(file) {
    // Validate file
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload PDF, PNG, or JPG files.');
        return;
    }
    
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showError('File size exceeds 16MB limit.');
        return;
    }
    
    uploadedFile = file;
    
    // Update UI
    fileName.textContent = file.name;
    fileInfo.classList.remove('d-none');
    formatSelection.classList.remove('d-none');
    convertBtn.classList.remove('d-none');
    
    // Upload file
    await uploadFile(file);
}

// Upload File
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showProgress('Uploading file...', 20);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            uploadedFile.serverFilename = data.filename;
            showProgress('File uploaded successfully', 40);
            
            // Show preview
            if (data.preview) {
                showPreview(data.preview);
            }
            
            hideProgress();
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }
}

// Show Preview
function showPreview(preview) {
    previewSection.classList.remove('d-none');
    
    let previewHTML = `
        <div class="mb-3">
            <strong>Type:</strong> ${preview.type.toUpperCase()}
        </div>
    `;
    
    if (preview.pages) {
        previewHTML += `<div class="mb-3"><strong>Pages:</strong> ${preview.pages}</div>`;
    }
    
    if (preview.is_scanned !== undefined) {
        previewHTML += `
            <div class="mb-3">
                <strong>Document Type:</strong> ${preview.is_scanned ? 'Scanned (Image-based)' : 'Digital (Text-based)'}
            </div>
        `;
    }
    
    if (preview.has_tables) {
        previewHTML += `
            <div class="alert alert-info">
                <i class="bi bi-table"></i> Tables detected in document
            </div>
        `;
    }
    
    if (preview.preview) {
        previewHTML += `
            <div class="mt-3">
                <strong>Preview:</strong>
                <div class="preview-text mt-2">${preview.preview}</div>
            </div>
        `;
    }
    
    previewContent.innerHTML = previewHTML;
}

// Convert Document
async function convertDocument() {
    if (!uploadedFile || !uploadedFile.serverFilename || !selectedFormat) {
        showError('Please upload a file and select output format');
        return;
    }
    
    try {
        hideError();
        showProgress('Converting document...', 50);
        
        const response = await fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedFile.serverFilename,
                format: selectedFormat
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showProgress('Conversion complete!', 100);
            setTimeout(() => {
                hideProgress();
                showResults(data.downloads);
            }, 500);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Conversion failed: ' + error.message);
    }
}

// Show Results
function showResults(downloads) {
    resultsSection.classList.remove('d-none');
    downloadLinks.innerHTML = '';
    
    downloads.forEach(download => {
        const fileType = download.name.endsWith('.docx') ? 'word' : 'excel';
        const icon = fileType === 'word' ? 'bi-file-word' : 'bi-file-excel';
        const color = fileType === 'word' ? 'primary' : 'success';
        
        const linkHTML = `
            <div class="download-link">
                <div>
                    <i class="bi ${icon}"></i>
                    <span>${download.name}</span>
                </div>
                <a href="${download.url}" class="btn btn-${color}" download>
                    <i class="bi bi-download"></i> Download
                </a>
            </div>
        `;
        
        downloadLinks.innerHTML += linkHTML;
    });
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Progress Management
function showProgress(text, percent) {
    progressSection.classList.remove('d-none');
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    progressSection.classList.add('d-none');
}

// Error Management
function showError(message) {
    errorSection.classList.remove('d-none');
    errorMessage.textContent = message;
    hideProgress();
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    errorSection.classList.add('d-none');
}

// Remove File
function removeFile() {
    uploadedFile = null;
    selectedFormat = null;
    
    fileInfo.classList.add('d-none');
    formatSelection.classList.add('d-none');
    convertBtn.classList.add('d-none');
    previewSection.classList.add('d-none');
    
    fileInput.value = '';
    
    document.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
}

// Reset Form
function resetForm() {
    removeFile();
    resultsSection.classList.add('d-none');
    hideError();
    hideProgress();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}