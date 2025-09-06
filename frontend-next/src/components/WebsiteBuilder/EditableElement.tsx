import React, { useState, useEffect, useRef, useCallback } from 'react';
import './EditableElement.css';

const EditableElement = ({ 
  type, 
  value, 
  onSave, 
  editMode, 
  placeholder = "Click to edit...",
  className = "",
  tag = "div",
  dataPath = "" // For mapping to backend data structure
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value || '');
  const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, saved, error
  const [originalValue, setOriginalValue] = useState(value || '');
  const inputRef = useRef(null);
  const saveTimeoutRef = useRef(null);

  // Update local state when prop value changes
  useEffect(() => {
    setEditValue(value || '');
    setOriginalValue(value || '');
  }, [value]);

  // Auto-save with debouncing
  const debouncedSave = useCallback(
    (newValue) => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      saveTimeoutRef.current = setTimeout(async () => {
        if (newValue !== originalValue && newValue.trim() !== '') {
          setSaveStatus('saving');
          try {
            await onSave(type, newValue, dataPath);
            setSaveStatus('saved');
            setOriginalValue(newValue);
            
            // Clear saved status after 2 seconds
            setTimeout(() => {
              setSaveStatus('idle');
            }, 2000);
          } catch (error) {
            console.error('Save failed:', error);
            setSaveStatus('error');
            // Rollback on error
            setEditValue(originalValue);
            
            // Clear error status after 3 seconds
            setTimeout(() => {
              setSaveStatus('idle');
            }, 3000);
          }
        }
      }, 2000);
    },
    [type, originalValue, onSave, dataPath]
  );

  // Handle click to edit
  const handleClick = (e) => {
    if (editMode && !isEditing) {
      e.preventDefault();
      e.stopPropagation();
      setIsEditing(true);
    }
  };

  // Handle input change
  const handleChange = (e) => {
    const newValue = e.target.value;
    setEditValue(newValue);
    debouncedSave(newValue);
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  // Handle save
  const handleSave = async () => {
    if (editValue !== originalValue) {
      setSaveStatus('saving');
      try {
        await onSave(type, editValue, dataPath);
        setSaveStatus('saved');
        setOriginalValue(editValue);
        setTimeout(() => setSaveStatus('idle'), 2000);
      } catch (error) {
        console.error('Save failed:', error);
        setSaveStatus('error');
        setEditValue(originalValue);
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    }
    setIsEditing(false);
  };

  // Handle cancel
  const handleCancel = () => {
    setEditValue(originalValue);
    setIsEditing(false);
    setSaveStatus('idle');
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
  };

  // Handle blur (save on focus loss)
  const handleBlur = () => {
    if (isEditing) {
      handleSave();
    }
  };

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Determine the HTML tag to use
  const Tag = tag;

  // Render save status indicator
  const renderSaveStatus = () => {
    if (saveStatus === 'idle') return null;

    return (
      <div className={`save-status save-status-${saveStatus}`}>
        {saveStatus === 'saving' && (
          <>
            <div className="save-spinner"></div>
            <span>Saving...</span>
          </>
        )}
        {saveStatus === 'saved' && (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20,6 9,17 4,12"/>
            </svg>
            <span>Saved</span>
          </>
        )}
        {saveStatus === 'error' && (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span>Error - Reverted</span>
          </>
        )}
      </div>
    );
  };

  // Build CSS classes
  const cssClasses = [
    'editable-element',
    className,
    editMode ? 'edit-mode' : '',
    isEditing ? 'editing' : '',
    saveStatus !== 'idle' ? `save-${saveStatus}` : ''
  ].filter(Boolean).join(' ');

  if (isEditing) {
    return (
      <div className="editable-wrapper editing">
        <input
          ref={inputRef}
          type="text"
          value={editValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          className="editable-input"
          placeholder={placeholder}
        />
        <div className="edit-controls">
          <button 
            className="edit-btn save-btn"
            onClick={handleSave}
            title="Save (Enter)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20,6 9,17 4,12"/>
            </svg>
          </button>
          <button 
            className="edit-btn cancel-btn"
            onClick={handleCancel}
            title="Cancel (Esc)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        {renderSaveStatus()}
      </div>
    );
  }

  return (
    <div className="editable-wrapper">
      <Tag
        className={cssClasses}
        onClick={handleClick}
        title={editMode ? 'Click to edit' : ''}
        data-editable-type={type}
        data-editable-path={dataPath}
      >
        {editValue || placeholder}
      </Tag>
      {renderSaveStatus()}
    </div>
  );
};

export default EditableElement;