import React, { useState, useRef, useCallback } from 'react';
import './EditableImageElement.css';

const EditableImageElement = ({ 
  src, 
  alt = "Image", 
  onImageUpload, 
  editMode, 
  placeholder = "Click to upload image",
  maxSize = 5 * 1024 * 1024, // 5MB
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
  className = "",
  style = {},
  imageType = "general", // hero, about, menu_item, logo
  dataPath = "" // For mapping to backend data structure
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(src);
  const fileInputRef = useRef(null);
  const dropZoneRef = useRef(null);

  // Validate file before upload
  const validateFile = (file) => {
    if (!file) return "No file selected";
    
    if (!acceptedFormats.includes(file.type)) {
      return `Invalid file type. Accepted formats: ${acceptedFormats.join(', ')}`;
    }
    
    if (file.size > maxSize) {
      return `File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(1)}MB`;
    }
    
    return null;
  };

  // Handle file upload
  const handleFileUpload = useCallback(async (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Create preview URL immediately
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Call the upload handler
      const result = await onImageUpload(file, imageType, dataPath);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Update with final URL from server
      if (result && result.url) {
        setPreviewUrl(result.url);
      }
      
      // Clean up object URL
      URL.revokeObjectURL(objectUrl);
      
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 1000);

    } catch (error) {
      console.error('Image upload failed:', error);
      setError(error.message || 'Upload failed');
      setIsUploading(false);
      setUploadProgress(0);
      
      // Revert preview on error
      setPreviewUrl(src);
    }
  }, [onImageUpload, imageType, dataPath, maxSize, acceptedFormats, src]);

  // Handle click to upload
  const handleClick = (e) => {
    if (editMode && !isUploading) {
      e.preventDefault();
      e.stopPropagation();
      fileInputRef.current?.click();
    }
  };

  // Handle file input change
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    if (editMode && !isUploading) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (!editMode || isUploading) return;
    
    const files = Array.from(e.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));
    
    if (imageFile) {
      handleFileUpload(imageFile);
    }
  };

  // Build CSS classes
  const cssClasses = [
    'editable-image-element',
    className,
    editMode ? 'edit-mode' : '',
    isUploading ? 'uploading' : '',
    isDragOver ? 'drag-over' : '',
    error ? 'error' : '',
    !previewUrl ? 'no-image' : ''
  ].filter(Boolean).join(' ');

  // Render upload overlay
  const renderUploadOverlay = () => {
    if (!editMode) return null;

    return (
      <div className="upload-overlay">
        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-circle">
              <svg width="40" height="40" viewBox="0 0 40 40">
                <circle
                  cx="20"
                  cy="20"
                  r="18"
                  fill="none"
                  stroke="rgba(255,255,255,0.3)"
                  strokeWidth="2"
                />
                <circle
                  cx="20"
                  cy="20"
                  r="18"
                  fill="none"
                  stroke="white"
                  strokeWidth="2"
                  strokeDasharray={`${2 * Math.PI * 18}`}
                  strokeDashoffset={`${2 * Math.PI * 18 * (1 - uploadProgress / 100)}`}
                  transform="rotate(-90 20 20)"
                />
              </svg>
              <span className="progress-text">{uploadProgress}%</span>
            </div>
            <p>Uploading...</p>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7,10 12,15 17,10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </div>
            <p>Click or drag to upload</p>
            <span className="upload-hint">
              {acceptedFormats.map(format => format.split('/')[1]).join(', ')} • Max {(maxSize / (1024 * 1024)).toFixed(1)}MB
            </span>
          </div>
        )}
      </div>
    );
  };

  // Render error message
  const renderError = () => {
    if (!error) return null;

    return (
      <div className="upload-error">
        <div className="error-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <span>{error}</span>
        <button 
          className="error-dismiss"
          onClick={() => setError(null)}
          title="Dismiss error"
        >
          ×
        </button>
      </div>
    );
  };

  return (
    <div className="editable-image-wrapper">
      <div
        ref={dropZoneRef}
        className={cssClasses}
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={style}
        title={editMode ? 'Click to upload image' : ''}
        data-image-type={imageType}
        data-editable-path={dataPath}
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            alt={alt}
            className="image-preview"
            loading="lazy"
          />
        ) : (
          <div className="image-placeholder">
            <div className="placeholder-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21,15 16,10 5,21"/>
              </svg>
            </div>
            <p>{placeholder}</p>
          </div>
        )}
        
        {renderUploadOverlay()}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {renderError()}
    </div>
  );
};

export default EditableImageElement;