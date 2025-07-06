import React, { useState, useRef, useEffect, useCallback } from 'react';
import './EditableColorElement.css';

const EditableColorElement = ({ 
  color = "#015af6", 
  onColorChange, 
  editMode, 
  colorType = 'primary', // primary, secondary, accent, background, text
  presets = [
    '#015af6', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#14b8a6'
  ], 
  showPresets = true,
  className = "",
  style = {},
  dataPath = "", // For mapping to backend data structure
  label = ""
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentColor, setCurrentColor] = useState(color);
  const [tempColor, setTempColor] = useState(color);
  const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, saved, error
  const colorPickerRef = useRef(null);
  const popoverRef = useRef(null);
  const saveTimeoutRef = useRef(null);

  // Update local state when prop color changes
  useEffect(() => {
    setCurrentColor(color);
    setTempColor(color);
  }, [color]);

  // Auto-save with debouncing
  const debouncedSave = useCallback(
    (newColor) => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      saveTimeoutRef.current = setTimeout(async () => {
        if (newColor !== color && newColor) {
          setSaveStatus('saving');
          try {
            await onColorChange(colorType, newColor, dataPath);
            setSaveStatus('saved');
            
            // Clear saved status after 2 seconds
            setTimeout(() => {
              setSaveStatus('idle');
            }, 2000);
          } catch (error) {
            console.error('Color save failed:', error);
            setSaveStatus('error');
            // Rollback on error
            setCurrentColor(color);
            setTempColor(color);
            
            // Clear error status after 3 seconds
            setTimeout(() => {
              setSaveStatus('idle');
            }, 3000);
          }
        }
      }, 1000);
    },
    [colorType, color, onColorChange, dataPath]
  );

  // Handle color change
  const handleColorChange = (newColor) => {
    setTempColor(newColor);
    setCurrentColor(newColor);
    
    // Apply color immediately for live preview
    if (onColorChange) {
      debouncedSave(newColor);
    }
  };

  // Handle preset color selection
  const handlePresetSelect = (presetColor) => {
    handleColorChange(presetColor);
  };

  // Handle manual color input
  const handleColorInput = (e) => {
    const newColor = e.target.value;
    handleColorChange(newColor);
  };

  // Toggle color picker
  const toggleColorPicker = (e) => {
    if (editMode) {
      e.preventDefault();
      e.stopPropagation();
      setIsOpen(!isOpen);
    }
  };

  // Close color picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Convert hex to RGB for better color manipulation
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };

  // Get contrast color for text
  const getContrastColor = (hexColor) => {
    const rgb = hexToRgb(hexColor);
    if (!rgb) return '#000000';
    
    const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
    return brightness > 128 ? '#000000' : '#ffffff';
  };

  // Build CSS classes
  const cssClasses = [
    'editable-color-element',
    className,
    editMode ? 'edit-mode' : '',
    isOpen ? 'open' : '',
    saveStatus !== 'idle' ? `save-${saveStatus}` : ''
  ].filter(Boolean).join(' ');

  // Render save status indicator
  const renderSaveStatus = () => {
    if (saveStatus === 'idle') return null;

    return (
      <div className={`color-save-status save-status-${saveStatus}`}>
        {saveStatus === 'saving' && (
          <>
            <div className="save-spinner"></div>
            <span>Saving...</span>
          </>
        )}
        {saveStatus === 'saved' && (
          <>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20,6 9,17 4,12"/>
            </svg>
            <span>Saved</span>
          </>
        )}
        {saveStatus === 'error' && (
          <>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span>Error</span>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="editable-color-wrapper">
      <div
        className={cssClasses}
        onClick={toggleColorPicker}
        style={style}
        title={editMode ? `Click to change ${colorType} color` : ''}
        data-color-type={colorType}
        data-editable-path={dataPath}
      >
        <div 
          className="color-preview"
          style={{ 
            backgroundColor: currentColor,
            color: getContrastColor(currentColor)
          }}
        >
          <div className="color-info">
            {label && <span className="color-label">{label}</span>}
            <span className="color-value">{currentColor}</span>
          </div>
          
          {editMode && (
            <div className="color-edit-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
          )}
        </div>

        {renderSaveStatus()}
      </div>

      {isOpen && editMode && (
        <div ref={popoverRef} className="color-picker-popover">
          <div className="color-picker-header">
            <h4>Choose {colorType} color</h4>
            <button 
              className="close-picker"
              onClick={() => setIsOpen(false)}
              title="Close color picker"
            >
              ×
            </button>
          </div>

          <div className="color-picker-content">
            {/* Color Input */}
            <div className="color-input-section">
              <label htmlFor={`color-input-${colorType}`}>Custom Color</label>
              <div className="color-input-wrapper">
                <input
                  id={`color-input-${colorType}`}
                  ref={colorPickerRef}
                  type="color"
                  value={tempColor}
                  onChange={handleColorInput}
                  className="color-input"
                />
                <input
                  type="text"
                  value={tempColor}
                  onChange={(e) => handleColorChange(e.target.value)}
                  className="color-text-input"
                  placeholder="#000000"
                  pattern="^#[0-9A-Fa-f]{6}$"
                />
              </div>
            </div>

            {/* Color Presets */}
            {showPresets && presets.length > 0 && (
              <div className="color-presets-section">
                <label>Color Presets</label>
                <div className="color-presets-grid">
                  {presets.map((presetColor, index) => (
                    <button
                      key={index}
                      className={`color-preset ${currentColor === presetColor ? 'active' : ''}`}
                      style={{ backgroundColor: presetColor }}
                      onClick={() => handlePresetSelect(presetColor)}
                      title={presetColor}
                    >
                      {currentColor === presetColor && (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={getContrastColor(presetColor)} strokeWidth="2">
                          <polyline points="20,6 9,17 4,12"/>
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Color Information */}
            <div className="color-info-section">
              <div className="color-details">
                <div className="color-detail">
                  <span className="detail-label">Hex:</span>
                  <span className="detail-value">{currentColor}</span>
                </div>
                {(() => {
                  const rgb = hexToRgb(currentColor);
                  return rgb ? (
                    <div className="color-detail">
                      <span className="detail-label">RGB:</span>
                      <span className="detail-value">{rgb.r}, {rgb.g}, {rgb.b}</span>
                    </div>
                  ) : null;
                })()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditableColorElement;