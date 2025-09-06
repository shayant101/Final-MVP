import React, { useState, useCallback } from 'react';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';

/**
 * MediaUploader - Utility component for handling file uploads
 * Provides image optimization, validation, and upload functionality
 */
const MediaUploader = {
  // Validate file before upload
  validateFile: (file, options = {}) => {
    const {
      maxSize = 5 * 1024 * 1024, // 5MB default
      acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
      minWidth = 100,
      minHeight = 100,
      maxWidth = 4000,
      maxHeight = 4000
    } = options;

    return new Promise((resolve, reject) => {
      if (!file) {
        reject(new Error('No file provided'));
        return;
      }

      // Check file type
      if (!acceptedFormats.includes(file.type)) {
        reject(new Error(`Invalid file type. Accepted formats: ${acceptedFormats.join(', ')}`));
        return;
      }

      // Check file size
      if (file.size > maxSize) {
        reject(new Error(`File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(1)}MB`));
        return;
      }

      // Check image dimensions
      if (file.type.startsWith('image/')) {
        const img = new Image();
        const objectUrl = URL.createObjectURL(file);
        
        img.onload = () => {
          URL.revokeObjectURL(objectUrl);
          
          if (img.width < minWidth || img.height < minHeight) {
            reject(new Error(`Image too small. Minimum dimensions: ${minWidth}x${minHeight}px`));
            return;
          }
          
          if (img.width > maxWidth || img.height > maxHeight) {
            reject(new Error(`Image too large. Maximum dimensions: ${maxWidth}x${maxHeight}px`));
            return;
          }
          
          resolve({
            valid: true,
            width: img.width,
            height: img.height,
            aspectRatio: img.width / img.height
          });
        };
        
        img.onerror = () => {
          URL.revokeObjectURL(objectUrl);
          reject(new Error('Invalid image file'));
        };
        
        img.src = objectUrl;
      } else {
        resolve({ valid: true });
      }
    });
  },

  // Optimize image before upload
  optimizeImage: (file, options = {}) => {
    const {
      maxWidth = 1920,
      maxHeight = 1080,
      quality = 0.85,
      format = 'image/jpeg'
    } = options;

    return new Promise((resolve, reject) => {
      if (!file.type.startsWith('image/')) {
        resolve(file); // Return original file if not an image
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      const objectUrl = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(objectUrl);

        // Calculate new dimensions
        let { width, height } = img;
        const aspectRatio = width / height;

        if (width > maxWidth) {
          width = maxWidth;
          height = width / aspectRatio;
        }

        if (height > maxHeight) {
          height = maxHeight;
          width = height * aspectRatio;
        }

        // Set canvas dimensions
        canvas.width = width;
        canvas.height = height;

        // Draw and compress image
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (blob) {
              // Create new file with optimized blob
              const optimizedFile = new File([blob], file.name, {
                type: format,
                lastModified: Date.now()
              });
              resolve(optimizedFile);
            } else {
              reject(new Error('Image optimization failed'));
            }
          },
          format,
          quality
        );
      };

      img.onerror = () => {
        URL.revokeObjectURL(objectUrl);
        reject(new Error('Failed to load image for optimization'));
      };

      img.src = objectUrl;
    });
  },

  // Upload file to server
  uploadFile: async (file, imageType = 'general', websiteId = null, onProgress = null) => {
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('image_type', imageType);
      if (websiteId) {
        formData.append('website_id', websiteId);
      }

      // Get auth headers
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      // Upload with progress tracking
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // Track upload progress
        if (onProgress) {
          xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
              const percentComplete = (e.loaded / e.total) * 100;
              onProgress(percentComplete);
            }
          });
        }

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText);
              resolve(response);
            } catch (error) {
              reject(new Error('Invalid response format'));
            }
          } else {
            reject(new Error(`Upload failed: ${xhr.statusText}`));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload failed: Network error'));
        });

        xhr.addEventListener('timeout', () => {
          reject(new Error('Upload failed: Request timeout'));
        });

        // Set timeout (30 seconds)
        xhr.timeout = 30000;

        // Open and send request - Use the same API base URL logic as websiteBuilderAPI
        const getApiBaseUrl = () => {
          if (process.env.REACT_APP_API_URL) {
            return process.env.REACT_APP_API_URL;
          }
          if (process.env.NODE_ENV === 'production') {
            return 'https://final-mvp-jc3a.onrender.com/api';
          }
          return 'http://localhost:8000/api';
        };
        const API_BASE_URL = getApiBaseUrl();
        xhr.open('POST', `${API_BASE_URL}/website-builder/upload-image`);
        
        // Set headers
        Object.keys(headers).forEach(key => {
          xhr.setRequestHeader(key, headers[key]);
        });

        xhr.send(formData);
      });
    } catch (error) {
      throw new Error(`Upload preparation failed: ${error.message}`);
    }
  },

  // Complete upload process with validation and optimization
  processAndUpload: async (file, options = {}) => {
    const {
      imageType = 'general',
      websiteId = null,
      onProgress = null,
      validateOptions = {},
      optimizeOptions = {}
    } = options;

    try {
      // Step 1: Validate file
      await MediaUploader.validateFile(file, validateOptions);

      // Step 2: Optimize image
      const optimizedFile = await MediaUploader.optimizeImage(file, optimizeOptions);

      // Step 3: Upload file
      const result = await MediaUploader.uploadFile(
        optimizedFile,
        imageType,
        websiteId,
        onProgress
      );

      return {
        success: true,
        url: result.url,
        filename: result.filename,
        size: optimizedFile.size,
        originalSize: file.size,
        compressionRatio: ((file.size - optimizedFile.size) / file.size * 100).toFixed(1)
      };
    } catch (error) {
      throw error;
    }
  },

  // Generate thumbnail URL
  getThumbnailUrl: (imageUrl, size = 'medium') => {
    if (!imageUrl) return null;
    
    const sizeMap = {
      small: '150x150',
      medium: '300x300',
      large: '600x600'
    };
    
    const dimensions = sizeMap[size] || sizeMap.medium;
    
    // If it's already a full URL, try to add thumbnail parameters
    if (imageUrl.startsWith('http')) {
      const url = new URL(imageUrl);
      url.searchParams.set('size', dimensions);
      url.searchParams.set('format', 'webp');
      return url.toString();
    }
    
    // If it's a relative path, construct thumbnail URL
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    return `${API_BASE_URL}/media/images/thumbnail/${encodeURIComponent(imageUrl)}?size=${dimensions}&format=webp`;
  },

  // Get image metadata
  getImageMetadata: (file) => {
    return new Promise((resolve, reject) => {
      if (!file.type.startsWith('image/')) {
        resolve({
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified
        });
        return;
      }

      const img = new Image();
      const objectUrl = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(objectUrl);
        resolve({
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
          width: img.width,
          height: img.height,
          aspectRatio: img.width / img.height
        });
      };

      img.onerror = () => {
        URL.revokeObjectURL(objectUrl);
        reject(new Error('Failed to load image metadata'));
      };

      img.src = objectUrl;
    });
  }
};

// React hook for using MediaUploader
export const useMediaUploader = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadImage = useCallback(async (file, options = {}) => {
    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const result = await MediaUploader.processAndUpload(file, {
        ...options,
        onProgress: (progressValue) => {
          setProgress(progressValue);
          if (options.onProgress) {
            options.onProgress(progressValue);
          }
        }
      });

      setUploading(false);
      setProgress(100);
      return result;
    } catch (err) {
      setUploading(false);
      setProgress(0);
      setError(err.message);
      throw err;
    }
  }, []);

  const resetState = useCallback(() => {
    setUploading(false);
    setProgress(0);
    setError(null);
  }, []);

  return {
    uploadImage,
    uploading,
    progress,
    error,
    resetState
  };
};

export default MediaUploader;