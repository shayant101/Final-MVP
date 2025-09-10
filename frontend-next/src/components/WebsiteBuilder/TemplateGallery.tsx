'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import './TemplateGallery.css';

interface TemplateGalleryProps {}

const TemplateGallery: React.FC<TemplateGalleryProps> = () => {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Template data with different restaurant types
  const templates = [
    {
      id: 'fine-dining-1',
      name: 'Elegant Fine Dining',
      category: 'fine_dining',
      description: 'Sophisticated design perfect for upscale restaurants',
      preview: '🍷',
      features: ['Reservation System', 'Wine Menu', 'Chef Profile', 'Gallery'],
      colors: { primary: '#2c3e50', secondary: '#e74c3c' }
    },
    {
      id: 'casual-dining-1',
      name: 'Modern Casual',
      category: 'casual_dining',
      description: 'Clean and friendly design for family restaurants',
      preview: '🍔',
      features: ['Online Menu', 'Location Map', 'Reviews', 'Contact Form'],
      colors: { primary: '#3498db', secondary: '#f39c12' }
    },
    {
      id: 'fast-food-1',
      name: 'Quick Service',
      category: 'fast_food',
      description: 'Bold and energetic design for fast food chains',
      preview: '🍕',
      features: ['Online Ordering', 'Delivery Info', 'Promotions', 'Nutrition Facts'],
      colors: { primary: '#e74c3c', secondary: '#f1c40f' }
    },
    {
      id: 'cafe-1',
      name: 'Cozy Cafe',
      category: 'cafe',
      description: 'Warm and inviting design for cafes and bakeries',
      preview: '☕',
      features: ['Daily Specials', 'Coffee Menu', 'Events Calendar', 'WiFi Info'],
      colors: { primary: '#8b4513', secondary: '#daa520' }
    },
    {
      id: 'ethnic-1',
      name: 'Authentic Cuisine',
      category: 'ethnic',
      description: 'Cultural design celebrating traditional flavors',
      preview: '🥘',
      features: ['Cultural Story', 'Traditional Menu', 'Spice Guide', 'Catering'],
      colors: { primary: '#d35400', secondary: '#27ae60' }
    },
    {
      id: 'fine-dining-2',
      name: 'Minimalist Luxury',
      category: 'fine_dining',
      description: 'Clean, minimal design for modern fine dining',
      preview: '🥂',
      features: ['Tasting Menu', 'Wine Pairing', 'Private Dining', 'Awards'],
      colors: { primary: '#34495e', secondary: '#95a5a6' }
    }
  ];

  const categories = [
    { id: 'all', name: 'All Templates', icon: '🌐' },
    { id: 'fine_dining', name: 'Fine Dining', icon: '🍷' },
    { id: 'casual_dining', name: 'Casual Dining', icon: '🍔' },
    { id: 'fast_food', name: 'Fast Food', icon: '🍕' },
    { id: 'cafe', name: 'Cafe & Bakery', icon: '☕' },
    { id: 'ethnic', name: 'Ethnic Cuisine', icon: '🥘' }
  ];

  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(template => template.category === selectedCategory);

  const handleSelectTemplate = (templateId: string) => {
    router.push(`/website-builder/templates/${templateId}/customize`);
  };

  return (
    <div className="template-gallery">

      {/* Category Filter */}
      <div className="category-filter">
        {categories.map(category => (
          <button
            key={category.id}
            className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.id)}
          >
            <span className="category-icon">{category.icon}</span>
            <span className="category-name">{category.name}</span>
          </button>
        ))}
      </div>

      {/* Templates Grid */}
      <div className="templates-grid">
        {filteredTemplates.map(template => (
          <div key={template.id} className="template-card">
            <div className="template-preview">
              <div className="preview-icon">{template.preview}</div>
              <div className="preview-overlay">
                <button 
                  className="preview-btn"
                  onClick={() => handleSelectTemplate(template.id)}
                >
                  👁️ Preview
                </button>
              </div>
            </div>
            
            <div className="template-info">
              <h3>{template.name}</h3>
              <p className="template-description">{template.description}</p>
              
              <div className="template-features">
                <h4>Features:</h4>
                <ul>
                  {template.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>

              <div className="template-colors">
                <div className="color-preview">
                  <div 
                    className="color-dot"
                    style={{ backgroundColor: template.colors.primary }}
                    title="Primary Color"
                  ></div>
                  <div 
                    className="color-dot"
                    style={{ backgroundColor: template.colors.secondary }}
                    title="Secondary Color"
                  ></div>
                </div>
              </div>
            </div>

            <div className="template-actions">
              <button 
                className="btn-primary select-btn"
                onClick={() => handleSelectTemplate(template.id)}
              >
                🎨 Customize This Template
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No templates found</h3>
          <p>Try selecting a different category</p>
        </div>
      )}
    </div>
  );
};

export default TemplateGallery;