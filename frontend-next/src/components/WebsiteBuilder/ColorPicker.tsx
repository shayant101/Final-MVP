import React, { useState, useRef, useEffect, useCallback } from 'react';
import './ColorPicker.css';

/**
 * Advanced ColorPicker component with color wheel, palette, and accessibility features
 */
const ColorPicker = ({ 
  color = "#015af6", 
  onChange, 
  onClose,
  colorType = 'primary',
  showPresets = true,
  showColorWheel = true,
  showPalette = true,
  presets = [
    // Brand colors
    '#015af6', '#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#84cc16',
    '#eab308', '#f59e0b', '#f97316', '#ef4444', '#ec4899', '#8b5cf6',
    // Neutral colors
    '#1f2937', '#374151', '#6b7280', '#9ca3af', '#d1d5db', '#f3f4f6',
    // Restaurant themed colors
    '#dc2626', '#ea580c', '#d97706', '#ca8a04', '#65a30d', '#16a34a'
  ]
}) => {
  const [currentColor, setCurrentColor] = useState(color);
  const [hue, setHue] = useState(0);
  const [saturation, setSaturation] = useState(100);
  const [lightness, setLightness] = useState(50);
  const [alpha, setAlpha] = useState(1);
  const [inputValue, setInputValue] = useState(color);
  const [colorFormat, setColorFormat] = useState('hex'); // hex, rgb, hsl
  
  const colorWheelRef = useRef(null);
  const saturationRef = useRef(null);
  const lightnessRef = useRef(null);
  const alphaRef = useRef(null);

  // Convert hex to HSL
  const hexToHsl = useCallback((hex) => {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
        default: h = 0;
      }
      h /= 6;
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  }, []);

  // Convert HSL to hex
  const hslToHex = useCallback((h, s, l) => {
    h /= 360;
    s /= 100;
    l /= 100;

    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };

    let r, g, b;
    if (s === 0) {
      r = g = b = l;
    } else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }

    const toHex = (c) => {
      const hex = Math.round(c * 255).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }, []);

  // Initialize HSL values from color prop
  useEffect(() => {
    if (color && color !== currentColor) {
      const hsl = hexToHsl(color);
      setHue(hsl.h);
      setSaturation(hsl.s);
      setLightness(hsl.l);
      setCurrentColor(color);
      setInputValue(color);
    }
  }, [color, currentColor, hexToHsl]);

  // Update color when HSL values change
  useEffect(() => {
    const newColor = hslToHex(hue, saturation, lightness);
    if (newColor !== currentColor) {
      setCurrentColor(newColor);
      setInputValue(newColor);
      if (onChange) {
        onChange(newColor);
      }
    }
  }, [hue, saturation, lightness, currentColor, hslToHex, onChange]);

  // Handle preset color selection
  const handlePresetSelect = (presetColor) => {
    const hsl = hexToHsl(presetColor);
    setHue(hsl.h);
    setSaturation(hsl.s);
    setLightness(hsl.l);
    setCurrentColor(presetColor);
    setInputValue(presetColor);
    if (onChange) {
      onChange(presetColor);
    }
  };

  // Handle manual input
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    
    // Validate hex color
    if (/^#[0-9A-F]{6}$/i.test(value)) {
      const hsl = hexToHsl(value);
      setHue(hsl.h);
      setSaturation(hsl.s);
      setLightness(hsl.l);
      setCurrentColor(value);
      if (onChange) {
        onChange(value);
      }
    }
  };

  // Handle slider changes
  const handleHueChange = (e) => {
    setHue(parseInt(e.target.value));
  };

  const handleSaturationChange = (e) => {
    setSaturation(parseInt(e.target.value));
  };

  const handleLightnessChange = (e) => {
    setLightness(parseInt(e.target.value));
  };

  const handleAlphaChange = (e) => {
    setAlpha(parseFloat(e.target.value));
  };

  // Get color in different formats
  const getColorInFormat = (format) => {
    switch (format) {
      case 'rgb':
        const r = parseInt(currentColor.slice(1, 3), 16);
        const g = parseInt(currentColor.slice(3, 5), 16);
        const b = parseInt(currentColor.slice(5, 7), 16);
        return alpha < 1 ? `rgba(${r}, ${g}, ${b}, ${alpha})` : `rgb(${r}, ${g}, ${b})`;
      case 'hsl':
        return alpha < 1 ? `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha})` : `hsl(${hue}, ${saturation}%, ${lightness}%)`;
      default:
        return currentColor;
    }
  };

  // Generate color harmony suggestions
  const getColorHarmony = (baseColor, type = 'complementary') => {
    const baseHsl = hexToHsl(baseColor);
    const suggestions = [];

    switch (type) {
      case 'complementary':
        suggestions.push(hslToHex((baseHsl.h + 180) % 360, baseHsl.s, baseHsl.l));
        break;
      case 'triadic':
        suggestions.push(hslToHex((baseHsl.h + 120) % 360, baseHsl.s, baseHsl.l));
        suggestions.push(hslToHex((baseHsl.h + 240) % 360, baseHsl.s, baseHsl.l));
        break;
      case 'analogous':
        suggestions.push(hslToHex((baseHsl.h + 30) % 360, baseHsl.s, baseHsl.l));
        suggestions.push(hslToHex((baseHsl.h - 30 + 360) % 360, baseHsl.s, baseHsl.l));
        break;
      case 'monochromatic':
        suggestions.push(hslToHex(baseHsl.h, baseHsl.s, Math.max(baseHsl.l - 20, 0)));
        suggestions.push(hslToHex(baseHsl.h, baseHsl.s, Math.min(baseHsl.l + 20, 100)));
        break;
      default:
        break;
    }

    return suggestions;
  };

  return (
    <div className="advanced-color-picker">
      <div className="color-picker-header">
        <h4>Color Picker - {colorType}</h4>
        <button className="close-picker" onClick={onClose}>×</button>
      </div>

      <div className="color-picker-body">
        {/* Current Color Display */}
        <div className="current-color-display">
          <div 
            className="color-preview-large"
            style={{ backgroundColor: currentColor }}
          >
            <div className="color-info-overlay">
              <span className="color-name">{colorType}</span>
              <span className="color-value">{getColorInFormat(colorFormat)}</span>
            </div>
          </div>
        </div>

        {/* Color Input */}
        <div className="color-input-section">
          <div className="input-group">
            <label>Color Value</label>
            <div className="color-input-wrapper">
              <input
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                className="color-text-input"
                placeholder="#000000"
              />
              <select 
                value={colorFormat} 
                onChange={(e) => setColorFormat(e.target.value)}
                className="format-selector"
              >
                <option value="hex">HEX</option>
                <option value="rgb">RGB</option>
                <option value="hsl">HSL</option>
              </select>
            </div>
          </div>
        </div>

        {/* Color Sliders */}
        {showColorWheel && (
          <div className="color-sliders-section">
            <div className="slider-group">
              <label>Hue: {hue}°</label>
              <input
                ref={colorWheelRef}
                type="range"
                min="0"
                max="360"
                value={hue}
                onChange={handleHueChange}
                className="color-slider hue-slider"
                style={{
                  background: `linear-gradient(to right, 
                    hsl(0, 100%, 50%), hsl(60, 100%, 50%), hsl(120, 100%, 50%), 
                    hsl(180, 100%, 50%), hsl(240, 100%, 50%), hsl(300, 100%, 50%), 
                    hsl(360, 100%, 50%))`
                }}
              />
            </div>

            <div className="slider-group">
              <label>Saturation: {saturation}%</label>
              <input
                ref={saturationRef}
                type="range"
                min="0"
                max="100"
                value={saturation}
                onChange={handleSaturationChange}
                className="color-slider saturation-slider"
                style={{
                  background: `linear-gradient(to right, 
                    hsl(${hue}, 0%, ${lightness}%), 
                    hsl(${hue}, 100%, ${lightness}%))`
                }}
              />
            </div>

            <div className="slider-group">
              <label>Lightness: {lightness}%</label>
              <input
                ref={lightnessRef}
                type="range"
                min="0"
                max="100"
                value={lightness}
                onChange={handleLightnessChange}
                className="color-slider lightness-slider"
                style={{
                  background: `linear-gradient(to right, 
                    hsl(${hue}, ${saturation}%, 0%), 
                    hsl(${hue}, ${saturation}%, 50%), 
                    hsl(${hue}, ${saturation}%, 100%))`
                }}
              />
            </div>

            <div className="slider-group">
              <label>Opacity: {Math.round(alpha * 100)}%</label>
              <input
                ref={alphaRef}
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={alpha}
                onChange={handleAlphaChange}
                className="color-slider alpha-slider"
              />
            </div>
          </div>
        )}

        {/* Color Presets */}
        {showPresets && (
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                      <polyline points="20,6 9,17 4,12"/>
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Color Harmony Suggestions */}
        {showPalette && (
          <div className="color-harmony-section">
            <label>Color Harmony</label>
            <div className="harmony-tabs">
              {['complementary', 'triadic', 'analogous', 'monochromatic'].map(type => (
                <button
                  key={type}
                  className="harmony-tab"
                  onClick={() => {
                    const suggestions = getColorHarmony(currentColor, type);
                    // You could set these as suggestions or auto-apply them
                  }}
                >
                  {type}
                </button>
              ))}
            </div>
            <div className="harmony-colors">
              {getColorHarmony(currentColor, 'complementary').map((harmonyColor, index) => (
                <button
                  key={index}
                  className="harmony-color"
                  style={{ backgroundColor: harmonyColor }}
                  onClick={() => handlePresetSelect(harmonyColor)}
                  title={`Complementary: ${harmonyColor}`}
                />
              ))}
            </div>
          </div>
        )}

        {/* Color Information */}
        <div className="color-info-section">
          <div className="color-details-grid">
            <div className="color-detail">
              <span className="detail-label">HEX</span>
              <span className="detail-value">{currentColor}</span>
            </div>
            <div className="color-detail">
              <span className="detail-label">RGB</span>
              <span className="detail-value">{getColorInFormat('rgb')}</span>
            </div>
            <div className="color-detail">
              <span className="detail-label">HSL</span>
              <span className="detail-value">{getColorInFormat('hsl')}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="color-picker-footer">
        <button className="btn-secondary" onClick={onClose}>
          Cancel
        </button>
        <button 
          className="btn-primary" 
          onClick={() => {
            if (onChange) onChange(currentColor);
            onClose();
          }}
        >
          Apply Color
        </button>
      </div>
    </div>
  );
};

export default ColorPicker;