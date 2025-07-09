import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './WebsitePreview.css';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';
import EditableElement from './EditableElement';
import EditableImageElement from './EditableImageElement';
import { useMediaUploader } from './MediaUploader';

const WebsitePreview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [website, setWebsite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewMode, setPreviewMode] = useState('desktop'); // desktop, tablet, mobile
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Media uploader hook
  const { uploadImage } = useMediaUploader();

  const fetchWebsiteData = useCallback(async () => {
    try {
      console.log('🔍 DEBUG: WebsitePreview - Starting fetchWebsiteData using centralized API service');
      
      // Use the centralized API service
      const data = await websiteBuilderAPI.getWebsiteDetails(id);
      console.log('🔍 DEBUG: WebsitePreview - Response data:', data);
      console.log('🔍 DEBUG: WebsitePreview - Has generated_content?', !!data?.generated_content);
      console.log('🔍 DEBUG: WebsitePreview - Data keys:', Object.keys(data || {}));
      console.log('🔍 DEBUG: WebsitePreview - Pages:', data?.pages);
      console.log('🔍 DEBUG: WebsitePreview - Pages[0]:', data?.pages?.[0]);
      console.log('🔍 DEBUG: WebsitePreview - Pages[0].sections:', data?.pages?.[0]?.sections);
      console.log('🔍 DEBUG: WebsitePreview - Hero section:', data?.pages?.[0]?.sections?.hero);
      console.log('🔍 DEBUG: WebsitePreview - About section:', data?.pages?.[0]?.sections?.about);
      console.log('🔍 DEBUG: WebsitePreview - Contact section:', data?.pages?.[0]?.sections?.contact);
      console.log('🔍 DEBUG: WebsitePreview - Design system:', data?.design_system);
      console.log('🔍 DEBUG: WebsitePreview - Menu items:', data?.menu_items);
      console.log('🔍 DEBUG: WebsitePreview - Hero image:', data?.hero_image);
      console.log('🔍 DEBUG: WebsitePreview - Website name:', data?.website_name);
      
      // Ensure menu_items are always present with default values if missing
      if (!data.menu_items || data.menu_items.length === 0) {
        data.menu_items = [
          {
            name: "Signature Pasta",
            description: "Fresh handmade pasta with our chef's special sauce",
            price: "$18.99"
          },
          {
            name: "Grilled Salmon",
            description: "Atlantic salmon with seasonal vegetables and lemon butter",
            price: "$24.99"
          },
          {
            name: "Classic Margherita",
            description: "Wood-fired pizza with fresh mozzarella and basil",
            price: "$16.99"
          }
        ];
      }
      
      setWebsite(data);
    } catch (error) {
      console.error('🔍 DEBUG: WebsitePreview - Error fetching website:', error);
      setError('Error loading website: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchWebsiteData();
  }, [fetchWebsiteData]);

  const handleEdit = () => {
    navigate(`/website-builder/edit/${id}`);
  };

  const handlePublish = async () => {
    try {
      console.log('🔍 DEBUG: WebsitePreview - Starting publish using centralized API service');
      
      // Use the centralized API service
      await websiteBuilderAPI.publishWebsite(id);
      
      alert('Website published successfully!');
      fetchWebsiteData(); // Refresh data
      console.log('🔍 DEBUG: WebsitePreview - Publish completed successfully');
    } catch (error) {
      console.error('🔍 DEBUG: WebsitePreview - Error publishing website:', error);
      alert('Error publishing website: ' + error.message);
    }
  };

  // Content mapping for inline editing
  const contentMapping = {
    'restaurant-name': 'website_name',
    'hero-tagline': 'pages[0].sections.hero.tagline',
    'hero-description': 'pages[0].sections.hero.description',
    'about-title': 'pages[0].sections.about.title',
    'about-content': 'pages[0].sections.about.content',
    'contact-title': 'pages[0].sections.contact.title',
    'contact-description': 'pages[0].sections.contact.description',
    'contact-hours': 'pages[0].sections.contact.hours',
    'contact-phone': 'pages[0].sections.contact.phone',
    // Menu item mappings
    'menu-item-name': 'menu_items[INDEX].name',
    'menu-item-description': 'menu_items[INDEX].description',
    'menu-item-price': 'menu_items[INDEX].price',
    'menu-item-image': 'menu_items[INDEX].image',
    // Menu section mappings
    'menu-url': 'pages[0].sections.menu.menu_url',
    // FAQ mappings
    'faq-title': 'pages[0].sections.faq.title',
    'faq-question': 'pages[0].sections.faq.items[INDEX].question',
    'faq-answer': 'pages[0].sections.faq.items[INDEX].answer',
    // Gallery mappings
    'gallery-title': 'pages[0].sections.gallery.title',
    'gallery-description': 'pages[0].sections.gallery.description',
    'gallery-caption': 'pages[0].sections.gallery.images[INDEX].caption',
    // Reviews mappings
    'reviews-title': 'pages[0].sections.reviews.title',
    'review-name': 'pages[0].sections.reviews.items[INDEX].name',
    'review-text': 'pages[0].sections.reviews.items[INDEX].text',
    'review-rating': 'pages[0].sections.reviews.items[INDEX].rating'
  };

  // Handle content save for inline editing
  const handleContentSave = async (type, value, dataPath) => {
    try {
      console.log('🔍 DEBUG: Saving content:', { type, value, dataPath });
      
      // Use the content mapping to determine the backend field
      let backendPath = contentMapping[type] || dataPath;
      
      // Handle menu item updates with index replacement
      if (backendPath.includes('[INDEX]')) {
        const match = dataPath.match(/\[(\d+)\]/);
        if (match) {
          const index = match[1];
          backendPath = backendPath.replace('[INDEX]', `[${index}]`);
        }
      }
      
      const contentUpdate = {
        [backendPath]: value
      };

      await websiteBuilderAPI.updateContent(id, contentUpdate);
      
      // Mark as having unsaved changes for user feedback
      setHasUnsavedChanges(true);
      
      // Refresh data from backend to ensure consistency
      // This prevents state sync issues and ensures we have the latest data
      await fetchWebsiteData();

      console.log('🔍 DEBUG: Content saved successfully');
    } catch (error) {
      console.error('🔍 DEBUG: Error saving content:', error);
      throw error; // Re-throw to trigger error handling in EditableElement
    }
  };

  // Handle save all changes
  const handleSaveAll = async () => {
    try {
      setSaving(true);
      console.log('🔍 DEBUG: Saving all changes...');
      
      // Refresh data to ensure we have the latest version
      await fetchWebsiteData();
      
      // Clear unsaved changes flag
      setHasUnsavedChanges(false);
      
      // Show success message
      alert('All changes saved successfully!');
      
      console.log('🔍 DEBUG: All changes saved successfully');
    } catch (error) {
      console.error('🔍 DEBUG: Error saving all changes:', error);
      alert('Error saving changes: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  // Handle image upload
  const handleImageUpload = async (file, imageType, dataPath) => {
    try {
      console.log('🔍 DEBUG: Uploading image:', { imageType, dataPath });
      
      const result = await uploadImage(file, {
        imageType,
        websiteId: id,
        validateOptions: {
          maxSize: 5 * 1024 * 1024, // 5MB
          acceptedFormats: ['image/jpeg', 'image/png', 'image/webp']
        }
      });
      
      console.log('🔍 DEBUG: Image upload result:', result);
      
      // Update website with new image URL
      const contentUpdate = {
        [dataPath]: result.url
      };
      
      await websiteBuilderAPI.updateContent(id, contentUpdate);
      
      // Mark as having unsaved changes for user feedback
      setHasUnsavedChanges(true);
      
      // Refresh website data
      await fetchWebsiteData();
      
      return result;
    } catch (error) {
      console.error('🔍 DEBUG: Image upload failed:', error);
      throw error;
    }
  };

  // Handle color change
  const handleColorChange = async (colorType, color, dataPath) => {
    try {
      console.log('🔍 DEBUG: Updating color:', { colorType, color, dataPath });
      
      const colorUpdates = {
        [colorType]: color
      };
      
      await websiteBuilderAPI.updateColorTheme(id, colorUpdates);
      
      // Refresh website data to get updated colors
      await fetchWebsiteData();
      
      console.log('🔍 DEBUG: Color updated successfully');
    } catch (error) {
      console.error('🔍 DEBUG: Color update failed:', error);
      throw error;
    }
  };

  // Apply theme presets
  const applyThemePreset = async (presetName) => {
    try {
      console.log('🔍 DEBUG: Applying theme preset:', presetName);
      
      const presets = {
        elegant: {
          primary: '#2c3e50',
          secondary: '#8e44ad',
          accent: '#f39c12',
          neutral: '#ecf0f1',
          body_font: 'Georgia, serif',
          headings_font: 'Playfair Display, serif'
        },
        modern: {
          primary: '#34495e',
          secondary: '#3498db',
          accent: '#e74c3c',
          neutral: '#f8f9fa',
          body_font: 'Helvetica Neue, sans-serif',
          headings_font: 'Montserrat, sans-serif'
        },
        warm: {
          primary: '#d35400',
          secondary: '#e67e22',
          accent: '#f1c40f',
          neutral: '#fdf2e9',
          body_font: 'Georgia, serif',
          headings_font: 'Georgia, serif'
        },
        fresh: {
          primary: '#27ae60',
          secondary: '#2ecc71',
          accent: '#f39c12',
          neutral: '#e8f8f5',
          body_font: 'Arial, sans-serif',
          headings_font: 'Trebuchet MS, sans-serif'
        }
      };
      
      const preset = presets[presetName];
      if (!preset) return;
      
      // Apply all colors and typography from the preset
      const colorUpdates = {
        primary: preset.primary,
        secondary: preset.secondary,
        accent: preset.accent,
        neutral: preset.neutral,
        body_font: preset.body_font,
        headings_font: preset.headings_font
      };
      
      await websiteBuilderAPI.updateColorTheme(id, colorUpdates);
      
      // Mark as having unsaved changes
      setHasUnsavedChanges(true);
      
      // Refresh website data to get updated theme
      await fetchWebsiteData();
      
      console.log('🔍 DEBUG: Theme preset applied successfully');
    } catch (error) {
      console.error('🔍 DEBUG: Theme preset application failed:', error);
      alert('Error applying theme preset: ' + error.message);
    }
  };

  const renderWebsiteContent = () => {
    // Check if website has pages and design system (actual backend data structure)
    if (!website?.pages || !Array.isArray(website.pages) || website.pages.length === 0) {
      return (
        <div className="preview-placeholder">
          <div className="placeholder-icon">🌐</div>
          <h3>No content available</h3>
          <p>This website hasn't been generated yet or the content is missing.</p>
        </div>
      );
    }

    // If in edit mode, render React components directly
    if (editMode) {
      return renderEditableWebsite();
    }

    // Generate CSS from design system for iframe mode
    const generateCSS = () => {
      const designSystem = website.design_system || {};
      const colorPalette = designSystem.color_palette || {};
      const typography = designSystem.typography || {};
      
      return `
        :root {
          --primary-color: ${colorPalette.primary || '#2c3e50'};
          --secondary-color: ${colorPalette.secondary || '#e74c3c'};
          --accent-color: ${colorPalette.accent || '#f39c12'};
          --neutral-color: ${colorPalette.neutral || '#ecf0f1'};
          --text-primary: ${colorPalette.text_primary || '#333333'};
          --text-secondary: ${colorPalette.text_secondary || '#666666'};
        }
        
        body {
          margin: 0;
          padding: 0;
          font-family: ${typography.body_font || 'Arial, sans-serif'};
          color: var(--text-primary);
          line-height: 1.6;
        }
        
        h1, h2, h3, h4, h5, h6 {
          font-family: ${typography.headings_font || 'Georgia, serif'};
          color: var(--primary-color);
          margin: 0 0 1rem 0;
        }
        
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }
        
        .hero-section {
          background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
          color: white;
          padding: 4rem 0;
          text-align: center;
          position: relative;
          overflow: hidden;
        }
        
        .hero-background-image {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          object-fit: cover;
          opacity: 0.3;
          z-index: 0;
        }
        
        .hero-content {
          position: relative;
          z-index: 1;
        }
        
        .hero-section h1 {
          color: white;
          font-size: 3rem;
          margin-bottom: 1rem;
        }
        
        .hero-section p {
          font-size: 1.2rem;
          margin-bottom: 2rem;
        }
        
        .section {
          padding: 3rem 0;
        }
        
        .section:nth-child(even) {
          background-color: var(--neutral-color);
        }
        
        .btn {
          display: inline-block;
          padding: 12px 24px;
          background-color: var(--accent-color);
          color: white;
          text-decoration: none;
          border-radius: 5px;
          font-weight: bold;
          transition: background-color 0.3s;
        }
        
        .btn:hover {
          background-color: var(--secondary-color);
        }
        
        .menu-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin-top: 2rem;
        }
        
        .menu-item {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .menu-item h3 {
          color: var(--primary-color);
          margin-bottom: 0.5rem;
        }
        
        .price {
          color: var(--accent-color);
          font-weight: bold;
          font-size: 1.1rem;
        }
        
        /* FAQ Section Styles */
        .faq-section {
          background-color: var(--neutral-color);
        }
        
        .faq-items {
          max-width: 800px;
          margin: 0 auto;
        }
        
        .faq-item {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.2s ease;
        }
        
        .faq-item:hover {
          transform: translateY(-2px);
        }
        
        .faq-question {
          color: var(--primary-color);
          margin-bottom: 0.75rem;
          font-size: 1.1rem;
          font-weight: 600;
        }
        
        .faq-answer {
          color: var(--text-secondary);
          line-height: 1.6;
          margin: 0;
        }
        
        /* Gallery Section Styles */
        .gallery-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }
        
        .gallery-item {
          position: relative;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          transition: transform 0.3s ease;
        }
        
        .gallery-item:hover {
          transform: translateY(-5px);
        }
        
        .gallery-image {
          width: 100%;
          height: 250px;
          object-fit: cover;
        }
        
        .gallery-caption {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(transparent, rgba(0,0,0,0.7));
          color: white;
          padding: 1rem;
          margin: 0;
        }
        
        /* Reviews Section Styles */
        .reviews-section {
          background-color: var(--neutral-color);
        }
        
        .reviews-summary {
          text-align: center;
          margin: 2rem 0;
        }
        
        .overall-rating {
          display: inline-flex;
          align-items: center;
          gap: 1rem;
          background: white;
          padding: 1rem 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .rating-number {
          font-size: 2rem;
          font-weight: bold;
          color: var(--primary-color);
        }
        
        .stars {
          display: flex;
          gap: 0.25rem;
        }
        
        .star {
          font-size: 1.5rem;
        }
        
        .star.filled {
          color: #ffc107;
        }
        
        .reviews-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }
        
        .review-item {
          background: white;
          padding: 1.5rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .review-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .reviewer-name {
          color: var(--primary-color);
          margin: 0;
          font-weight: 600;
        }
        
        .review-rating {
          display: flex;
          gap: 0.25rem;
        }
        
        .review-rating .star {
          font-size: 1rem;
        }
        
        .review-text {
          color: var(--text-secondary);
          line-height: 1.6;
          font-style: italic;
          margin: 0;
        }
        
        @media (max-width: 768px) {
          .container {
            padding: 0 15px;
          }
          
          .hero-section h1 {
            font-size: 2rem;
          }
          
          .menu-grid {
            grid-template-columns: 1fr;
          }
          
          .gallery-grid {
            grid-template-columns: 1fr;
          }
          
          .reviews-grid {
            grid-template-columns: 1fr;
          }
          
          .overall-rating {
            flex-direction: column;
            gap: 0.5rem;
          }
        }
      `;
    };

    // Generate menu items HTML for iframe
    const generateMenuItemsHTML = () => {
      const menuItems = website.menu_items || [
        {
          name: "Signature Pasta",
          description: "Fresh handmade pasta with our chef's special sauce",
          price: "$18.99"
        },
        {
          name: "Grilled Salmon",
          description: "Atlantic salmon with seasonal vegetables and lemon butter",
          price: "$24.99"
        },
        {
          name: "Classic Margherita",
          description: "Wood-fired pizza with fresh mozzarella and basil",
          price: "$16.99"
        }
      ];

      return menuItems.map(item => {
        const absoluteImageUrl = item.image ? (item.image.startsWith('http') ? item.image : `${window.location.origin}${item.image}`) : null;
        
        return `
          <div class="menu-item">
            ${absoluteImageUrl ? `<img src="${absoluteImageUrl}" alt="${item.name}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 1rem;" />` : ''}
            <h3>${item.name || 'Menu Item'}</h3>
            <p>${item.description || 'Delicious dish description'}</p>
            <div class="price">${item.price || '$0.00'}</div>
          </div>
        `;
      }).join('');
    };

    // Generate FAQ items HTML for iframe
    const generateFAQItemsHTML = () => {
      const faqItems = website.pages?.[0]?.sections?.faq?.items || [
        { question: "What are your hours?", answer: "We're open Monday-Sunday, 11:00 AM - 10:00 PM" },
        { question: "Do you take reservations?", answer: "Yes, call us at (555) 123-4567 or book online" },
        { question: "Do you offer delivery?", answer: "Yes, we offer delivery through our website and third-party apps" }
      ];

      return faqItems.map(item => `
        <div class="faq-item">
          <h3 class="faq-question">${item.question || 'Question'}</h3>
          <p class="faq-answer">${item.answer || 'Answer'}</p>
        </div>
      `).join('');
    };

    // Generate gallery images HTML for iframe
    const generateGalleryImagesHTML = () => {
      const galleryImages = website.pages?.[0]?.sections?.gallery?.images || [];
      
      if (galleryImages.length === 0) {
        return '<p style="text-align: center; color: var(--text-secondary);">No gallery images yet. Add some in edit mode!</p>';
      }

      return galleryImages.map((image, index) => {
        const absoluteImageUrl = image.url ? (image.url.startsWith('http') ? image.url : `${window.location.origin}${image.url}`) : null;
        
        return `
          <div class="gallery-item">
            ${absoluteImageUrl ? `<img src="${absoluteImageUrl}" alt="${image.alt || `Gallery image ${index + 1}`}" class="gallery-image" />` : ''}
            ${image.caption ? `<p class="gallery-caption">${image.caption}</p>` : ''}
          </div>
        `;
      }).join('');
    };

    // Generate reviews HTML for iframe
    const generateReviewsHTML = () => {
      const reviewsItems = website.pages?.[0]?.sections?.reviews?.items || [
        { name: "Sarah M.", rating: 5, text: "Amazing food and atmosphere! The service was exceptional." },
        { name: "Mike R.", rating: 4, text: "Great service and delicious meals. Will definitely come back!" },
        { name: "Lisa K.", rating: 5, text: "Best restaurant in town! The pasta was incredible." }
      ];

      const overallRating = website.pages?.[0]?.sections?.reviews?.overall_rating || 4.5;

      return `
        <div class="reviews-summary">
          <div class="overall-rating">
            <span class="rating-number">${overallRating}</span>
            <div class="stars">
              ${[1,2,3,4,5].map(star => `
                <span class="star ${star <= overallRating ? 'filled' : ''}" style="color: ${star <= overallRating ? '#ffc107' : '#ddd'}">★</span>
              `).join('')}
            </div>
          </div>
        </div>
        <div class="reviews-grid">
          ${reviewsItems.map(review => `
            <div class="review-item">
              <div class="review-header">
                <h4 class="reviewer-name">${review.name || 'Anonymous'}</h4>
                <div class="review-rating">
                  ${[1,2,3,4,5].map(star => `
                    <span class="star ${star <= (review.rating || 5) ? 'filled' : ''}" style="color: ${star <= (review.rating || 5) ? '#ffc107' : '#ddd'}">★</span>
                  `).join('')}
                </div>
              </div>
              <p class="review-text">${review.text || 'Great experience!'}</p>
            </div>
          `).join('')}
        </div>
      `;
    };
    
    // Generate HTML from pages and components
    const generateHTML = () => {
      const restaurantName = website.website_name || 'Our Restaurant';
      const heroImage = website.hero_image;
      
      // Convert relative URLs to absolute URLs for iframe
      const absoluteHeroImage = heroImage ? (heroImage.startsWith('http') ? heroImage : `${window.location.origin}${heroImage}`) : null;
      
      console.log('🔍 DEBUG: generateHTML - Restaurant name:', restaurantName);
      console.log('🔍 DEBUG: generateHTML - Hero image:', heroImage);
      console.log('🔍 DEBUG: generateHTML - Absolute hero image:', absoluteHeroImage);
      console.log('🔍 DEBUG: generateHTML - Website object:', website);
      console.log('🔍 DEBUG: generateHTML - FAQ items:', website.pages?.[0]?.sections?.faq?.items);
      console.log('🔍 DEBUG: generateHTML - Gallery images:', website.pages?.[0]?.sections?.gallery?.images);
      console.log('🔍 DEBUG: generateHTML - Reviews items:', website.pages?.[0]?.sections?.reviews?.items);
      
      return `
        <div class="hero-section">
          ${absoluteHeroImage ? `<img src="${absoluteHeroImage}" alt="Hero background" class="hero-background-image" />` : ''}
          <div class="container hero-content">
            <h1>${restaurantName}</h1>
            <p>${website.pages?.[0]?.sections?.hero?.tagline || 'Experience exceptional dining with authentic flavors and warm hospitality'}</p>
            <a href="#menu" class="btn">View Our Menu</a>
          </div>
        </div>
        
        <div class="section" id="about">
          <div class="container">
            <h2>${website.pages?.[0]?.sections?.about?.title || 'About Us'}</h2>
            <p>${website.pages?.[0]?.sections?.about?.content || `Welcome to ${restaurantName}, where culinary excellence meets warm hospitality. Our passionate chefs create memorable dining experiences using the finest ingredients and time-honored techniques.`}</p>
          </div>
        </div>
        
        <div class="section" id="menu">
          <div class="container">
            <h2>Our Menu</h2>
            <p>Discover our carefully crafted dishes that celebrate flavor and tradition.</p>
            <div class="menu-grid">
              ${generateMenuItemsHTML()}
            </div>
            ${website.pages?.[0]?.sections?.menu?.menu_url ? `
              <div style="text-align: center; margin-top: 2rem;">
                <a href="${website.pages[0].sections.menu.menu_url}" target="_blank" rel="noopener noreferrer" class="btn">View Full Menu</a>
              </div>
            ` : ''}
          </div>
        </div>
        
        <div class="section faq-section" id="faq">
          <div class="container">
            <h2>${website.pages?.[0]?.sections?.faq?.title || 'Frequently Asked Questions'}</h2>
            <div class="faq-items">
              ${generateFAQItemsHTML()}
            </div>
          </div>
        </div>
        
        <div class="section" id="gallery">
          <div class="container">
            <h2>${website.pages?.[0]?.sections?.gallery?.title || 'Gallery'}</h2>
            <p>${website.pages?.[0]?.sections?.gallery?.description || 'Take a look at our restaurant and dishes'}</p>
            <div class="gallery-grid">
              ${generateGalleryImagesHTML()}
            </div>
          </div>
        </div>
        
        <div class="section reviews-section" id="reviews">
          <div class="container">
            <h2>${website.pages?.[0]?.sections?.reviews?.title || 'What Our Customers Say'}</h2>
            ${generateReviewsHTML()}
          </div>
        </div>
        
        <div class="section" id="contact">
          <div class="container">
            <h2>${website.pages?.[0]?.sections?.contact?.title || 'Visit Us'}</h2>
            <p>${website.pages?.[0]?.sections?.contact?.description || `We'd love to welcome you to ${restaurantName}. Come experience the difference that passion makes.`}</p>
            <p><strong>Hours:</strong> ${website.pages?.[0]?.sections?.contact?.hours || 'Monday - Sunday, 11:00 AM - 10:00 PM'}</p>
            <p><strong>Phone:</strong> ${website.pages?.[0]?.sections?.contact?.phone || '(555) 123-4567'}</p>
            <a href="#reservation" class="btn">Make a Reservation</a>
          </div>
        </div>
      `;
    };
    
    // Create a complete HTML document with the generated content
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${website.website_name || 'Restaurant Website'}</title>
        <style>
          ${generateCSS()}
        </style>
      </head>
      <body>
        ${generateHTML()}
        
        <script>
          // Prevent forms from submitting in preview
          document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
              form.addEventListener('submit', function(e) {
                e.preventDefault();
                alert('This is a preview - forms are disabled');
              });
            });
            
            // Prevent external links from navigating
            const links = document.querySelectorAll('a[href^="http"]');
            links.forEach(link => {
              link.addEventListener('click', function(e) {
                e.preventDefault();
                alert('External links are disabled in preview mode');
              });
            });
            
            // Smooth scrolling for anchor links
            const anchorLinks = document.querySelectorAll('a[href^="#"]');
            anchorLinks.forEach(link => {
              link.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                  target.scrollIntoView({ behavior: 'smooth' });
                }
              });
            });
          });
        </script>
      </body>
      </html>
    `;

    return (
      <iframe
        className={`website-iframe ${previewMode}`}
        srcDoc={htmlContent}
        title="Website Preview"
        sandbox="allow-scripts allow-same-origin"
      />
    );
  };

  // Render editable menu items
  const renderEditableMenuItems = () => {
    const menuItems = website.menu_items || [
      {
        name: "Signature Pasta",
        description: "Fresh handmade pasta with our chef's special sauce",
        price: "$18.99",
        image: ""
      },
      {
        name: "Grilled Salmon",
        description: "Atlantic salmon with seasonal vegetables and lemon butter",
        price: "$24.99",
        image: ""
      },
      {
        name: "Classic Margherita",
        description: "Wood-fired pizza with fresh mozzarella and basil",
        price: "$16.99",
        image: ""
      }
    ];

    return menuItems.map((item, index) => (
      <div key={index} className="menu-item" style={{
        background: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        {/* NEW: Optional menu item image */}
        {(editMode || item.image) && (
          <EditableImageElement
            src={item.image}
            alt={`${item.name} image`}
            onImageUpload={handleImageUpload}
            editMode={editMode}
            placeholder="Add menu item image"
            imageType="menu_item"
            dataPath={`menu_items[${index}].image`}
            className="menu-item-image"
            style={{
              width: '100%',
              height: '200px',
              objectFit: 'cover',
              borderRadius: '8px',
              marginBottom: '1rem'
            }}
          />
        )}
        <EditableElement
          type="menu-item-name"
          value={item.name}
          onSave={handleContentSave}
          editMode={editMode}
          tag="h3"
          className="menu-item-name"
          dataPath={`menu_items[${index}].name`}
          placeholder="Menu item name"
        />
        <EditableElement
          type="menu-item-description"
          value={item.description}
          onSave={handleContentSave}
          editMode={editMode}
          tag="p"
          className="menu-item-description"
          dataPath={`menu_items[${index}].description`}
          placeholder="Menu item description"
        />
        <EditableElement
          type="menu-item-price"
          value={item.price}
          onSave={handleContentSave}
          editMode={editMode}
          tag="div"
          className="price"
          dataPath={`menu_items[${index}].price`}
          placeholder="$0.00"
        />
      </div>
    ));
  };

  // Render editable website using React components
  const renderEditableWebsite = () => {
    const designSystem = website.design_system || {};
    const colorPalette = designSystem.color_palette || {};
    const typography = designSystem.typography || {};
    
    const restaurantName = website.website_name || 'Our Restaurant';
    const heroTagline = website.pages?.[0]?.sections?.hero?.tagline || 'Experience exceptional dining with authentic flavors and warm hospitality';
    const heroDescription = website.pages?.[0]?.sections?.hero?.description || '';
    const aboutTitle = website.pages?.[0]?.sections?.about?.title || 'About Us';
    const aboutContent = website.pages?.[0]?.sections?.about?.content || `Welcome to ${restaurantName}, where culinary excellence meets warm hospitality. Our passionate chefs create memorable dining experiences using the finest ingredients and time-honored techniques.`;

    const websiteStyles = {
      '--primary-color': colorPalette.primary || '#2c3e50',
      '--secondary-color': colorPalette.secondary || '#e74c3c',
      '--accent-color': colorPalette.accent || '#f39c12',
      '--neutral-color': colorPalette.neutral || '#ecf0f1',
      '--text-primary': colorPalette.text_primary || '#333333',
      '--text-secondary': colorPalette.text_secondary || '#666666',
      fontFamily: typography.body_font || 'Arial, sans-serif',
      color: 'var(--text-primary)',
      lineHeight: 1.6,
      margin: 0,
      padding: 0
    };

    return (
      <div className="editable-website" style={websiteStyles}>
        {/* Hero Section */}
        <div className="hero-section" style={{
          background: `linear-gradient(135deg, var(--primary-color), var(--secondary-color))`,
          color: 'white',
          padding: '4rem 0',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Hero Background Image */}
          {editMode && (
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 0 }}>
              <EditableImageElement
                src={website?.hero_image}
                alt="Hero background"
                onImageUpload={handleImageUpload}
                editMode={editMode}
                placeholder="Click to upload hero image"
                imageType="hero"
                dataPath="hero_image"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  opacity: 0.3
                }}
              />
            </div>
          )}
          
          <div className="container" style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 20px',
            position: 'relative',
            zIndex: 1,
            width: '100%',
            boxSizing: 'border-box'
          }}>
            <EditableElement
              type="restaurant-name"
              value={restaurantName}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h1"
              className="hero-title"
              dataPath="website_name"
              placeholder="Restaurant Name"
            />
            <EditableElement
              type="hero-tagline"
              value={heroTagline}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="hero-tagline"
              dataPath="pages[0].sections.hero.tagline"
              placeholder="Your restaurant's tagline"
            />
            {heroDescription && (
              <EditableElement
                type="hero-description"
                value={heroDescription}
                onSave={handleContentSave}
                editMode={editMode}
                tag="p"
                className="hero-description"
                dataPath="pages[0].sections.hero.description"
                placeholder="Additional hero description"
              />
            )}
            <a href="#menu" className="btn" style={{
              display: 'inline-block',
              padding: '12px 24px',
              backgroundColor: 'var(--accent-color)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              fontWeight: 'bold',
              marginTop: '2rem'
            }}>
              View Our Menu
            </a>
          </div>
        </div>
        
        {/* About Section */}
        <div className="section" id="about" style={{ padding: '3rem 0', backgroundColor: 'var(--neutral-color)' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <EditableElement
              type="about-title"
              value={aboutTitle}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h2"
              className="section-title"
              dataPath="pages[0].sections.about.title"
              placeholder="About Section Title"
            />
            <EditableElement
              type="about-content"
              value={aboutContent}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="section-content"
              dataPath="pages[0].sections.about.content"
              placeholder="Tell your restaurant's story..."
            />
          </div>
        </div>
        
        {/* Menu Section */}
        <div className="section" id="menu" style={{ padding: '3rem 0' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <h2 style={{
              fontFamily: typography.headings_font || 'Georgia, serif',
              color: 'var(--primary-color)',
              marginBottom: '1rem'
            }}>
              Our Menu
            </h2>
            <p style={{ marginBottom: '2rem' }}>
              Discover our carefully crafted dishes that celebrate flavor and tradition.
            </p>
            <div className="menu-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '2rem'
            }}>
              {renderEditableMenuItems()}
            </div>
            
            {/* NEW: View Full Menu Button */}
            <div className="menu-actions" style={{ textAlign: 'center', marginTop: '2rem' }}>
              {editMode ? (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                    Full Menu URL (optional):
                  </label>
                  <input
                    type="url"
                    value={website.pages?.[0]?.sections?.menu?.menu_url || ''}
                    onChange={(e) => handleContentSave('menu-url', e.target.value, 'pages[0].sections.menu.menu_url')}
                    placeholder="https://order.restaurant.com"
                    className="menu-url-input"
                    style={{
                      width: '100%',
                      maxWidth: '400px',
                      padding: '0.75rem',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      textAlign: 'center',
                      fontSize: '0.9rem',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>
              ) : (
                website.pages?.[0]?.sections?.menu?.menu_url && (
                  <a
                    href={website.pages[0].sections.menu.menu_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn"
                    style={{
                      display: 'inline-block',
                      padding: '12px 24px',
                      backgroundColor: 'var(--accent-color)',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '5px',
                      fontWeight: 'bold',
                      transition: 'background-color 0.3s'
                    }}
                  >
                    View Full Menu
                  </a>
                )
              )}
            </div>
          </div>
        </div>
        
        {/* FAQ Section */}
        <div className="section faq-section" id="faq" style={{ padding: '3rem 0', backgroundColor: 'var(--neutral-color)' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <EditableElement
              type="faq-title"
              value={website.pages?.[0]?.sections?.faq?.title || 'Frequently Asked Questions'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h2"
              className="section-title"
              dataPath="pages[0].sections.faq.title"
              placeholder="FAQ Section Title"
              style={{
                fontFamily: typography.headings_font || 'Georgia, serif',
                color: 'var(--primary-color)',
                marginBottom: '2rem',
                textAlign: 'center'
              }}
            />
            
            <div className="faq-items" style={{ maxWidth: '800px', margin: '0 auto' }}>
              {(website.pages?.[0]?.sections?.faq?.items || [
                { question: "What are your hours?", answer: "We're open Monday-Sunday, 11:00 AM - 10:00 PM" },
                { question: "Do you take reservations?", answer: "Yes, call us at (555) 123-4567 or book online" },
                { question: "Do you offer delivery?", answer: "Yes, we offer delivery through our website and third-party apps" }
              ]).map((item, index) => (
                <div key={index} className="faq-item" style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '1.5rem',
                  marginBottom: '1rem',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  transition: 'transform 0.2s ease'
                }}>
                  <EditableElement
                    type="faq-question"
                    value={item.question}
                    onSave={handleContentSave}
                    editMode={editMode}
                    tag="h3"
                    className="faq-question"
                    dataPath={`pages[0].sections.faq.items[${index}].question`}
                    placeholder="Enter your question"
                    style={{
                      color: 'var(--primary-color)',
                      marginBottom: '0.75rem',
                      fontSize: '1.1rem',
                      fontWeight: '600'
                    }}
                  />
                  <EditableElement
                    type="faq-answer"
                    value={item.answer}
                    onSave={handleContentSave}
                    editMode={editMode}
                    tag="p"
                    className="faq-answer"
                    dataPath={`pages[0].sections.faq.items[${index}].answer`}
                    placeholder="Enter the answer"
                    style={{
                      color: 'var(--text-secondary)',
                      lineHeight: '1.6',
                      margin: '0'
                    }}
                  />
                </div>
              ))}
            </div>
            
            {editMode && (
              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                  className="btn btn-secondary"
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'transparent',
                    color: 'var(--primary-color)',
                    border: '2px solid var(--primary-color)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                  onClick={async () => {
                    // Add new FAQ item functionality with user prompts
                    const question = prompt('Enter the FAQ question:');
                    if (!question) return;
                    
                    const answer = prompt('Enter the FAQ answer:');
                    if (!answer) return;
                    
                    // Ensure the FAQ section exists and get current items
                    const faqSection = website.pages?.[0]?.sections?.faq;
                    const currentFAQ = (faqSection && Array.isArray(faqSection.items)) ? faqSection.items : [];
                    const newIndex = currentFAQ.length;
                    
                    // Add both question and answer for the new FAQ item
                    try {
                      // Create the complete new FAQ item in a single update
                      const contentUpdate = {
                        [`pages[0].sections.faq.items[${newIndex}].question`]: question,
                        [`pages[0].sections.faq.items[${newIndex}].answer`]: answer
                      };
                      
                      await websiteBuilderAPI.updateContent(id, contentUpdate);
                      
                      // Refresh data to show the new item
                      await fetchWebsiteData();
                      
                    } catch (error) {
                      console.error('Error adding FAQ item:', error);
                      alert('Error adding FAQ item. Please try again.');
                    }
                  }}
                >
                  + Add FAQ Item
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Gallery Section */}
        <div className="section gallery-section" id="gallery" style={{ padding: '3rem 0' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <EditableElement
              type="gallery-title"
              value={website.pages?.[0]?.sections?.gallery?.title || 'Gallery'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h2"
              className="section-title"
              dataPath="pages[0].sections.gallery.title"
              placeholder="Gallery Title"
              style={{
                fontFamily: typography.headings_font || 'Georgia, serif',
                color: 'var(--primary-color)',
                marginBottom: '1rem',
                textAlign: 'center'
              }}
            />
            
            <EditableElement
              type="gallery-description"
              value={website.pages?.[0]?.sections?.gallery?.description || 'Take a look at our restaurant and dishes'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="section-content"
              dataPath="pages[0].sections.gallery.description"
              placeholder="Gallery description"
              style={{
                textAlign: 'center',
                marginBottom: '2rem',
                color: 'var(--text-secondary)'
              }}
            />
            
            <div className="gallery-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1.5rem',
              marginTop: '2rem'
            }}>
              {(website.pages?.[0]?.sections?.gallery?.images || []).map((image, index) => (
                <div key={index} className="gallery-item" style={{
                  position: 'relative',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  transition: 'transform 0.3s ease'
                }}>
                  <EditableImageElement
                    src={image.url}
                    alt={image.alt || `Gallery image ${index + 1}`}
                    onImageUpload={handleImageUpload}
                    editMode={editMode}
                    placeholder="Add gallery image"
                    imageType="gallery"
                    dataPath={`pages[0].sections.gallery.images[${index}].url`}
                    className="gallery-image"
                    style={{
                      width: '100%',
                      height: '250px',
                      objectFit: 'cover'
                    }}
                  />
                  {(editMode || image.caption) && (
                    <EditableElement
                      type="gallery-caption"
                      value={image.caption || ''}
                      onSave={handleContentSave}
                      editMode={editMode}
                      tag="p"
                      className="gallery-caption"
                      dataPath={`pages[0].sections.gallery.images[${index}].caption`}
                      placeholder="Image caption"
                      style={{
                        position: 'absolute',
                        bottom: '0',
                        left: '0',
                        right: '0',
                        background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                        color: 'white',
                        padding: '1rem',
                        margin: '0'
                      }}
                    />
                  )}
                </div>
              ))}
              
              {editMode && (
                <div className="gallery-item add-image" style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: '250px',
                  border: '2px dashed var(--border-color)',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '12px'
                }}>
                  <button
                    className="btn btn-secondary"
                    style={{
                      padding: '1rem 2rem',
                      backgroundColor: 'transparent',
                      color: 'var(--primary-color)',
                      border: '2px solid var(--primary-color)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                    onClick={async () => {
                      // Add new gallery image functionality with file upload
                      const fileInput = document.createElement('input');
                      fileInput.type = 'file';
                      fileInput.accept = 'image/*';
                      fileInput.style.display = 'none';
                      
                      fileInput.onchange = async (e) => {
                        const file = e.target.files[0];
                        if (!file) return;
                        
                        const caption = prompt('Enter a caption for this image (optional):') || '';
                        
                        const currentImages = website.pages?.[0]?.sections?.gallery?.images || [];
                        const newIndex = currentImages.length;
                        
                        try {
                          // Upload the image first and get the URL
                          const uploadResult = await uploadImage(file, {
                            imageType: 'gallery',
                            websiteId: id,
                            validateOptions: {
                              maxSize: 5 * 1024 * 1024, // 5MB
                              acceptedFormats: ['image/jpeg', 'image/png', 'image/webp']
                            }
                          });
                          
                          // Create the complete gallery item in a single update
                          const contentUpdate = {
                            [`pages[0].sections.gallery.images[${newIndex}].url`]: uploadResult.url,
                            [`pages[0].sections.gallery.images[${newIndex}].caption`]: caption,
                            [`pages[0].sections.gallery.images[${newIndex}].alt`]: `Gallery image ${newIndex + 1}`
                          };
                          
                          await websiteBuilderAPI.updateContent(id, contentUpdate);
                          
                          // Refresh data to show the new image
                          await fetchWebsiteData();
                          
                        } catch (error) {
                          console.error('Error adding gallery image:', error);
                          alert('Error uploading image. Please try again.');
                        }
                        
                        // Clean up
                        document.body.removeChild(fileInput);
                      };
                      
                      document.body.appendChild(fileInput);
                      fileInput.click();
                    }}
                  >
                    + Add Image
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Reviews Section */}
        <div className="section reviews-section" id="reviews" style={{ padding: '3rem 0', backgroundColor: 'var(--neutral-color)' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <EditableElement
              type="reviews-title"
              value={website.pages?.[0]?.sections?.reviews?.title || 'What Our Customers Say'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h2"
              className="section-title"
              dataPath="pages[0].sections.reviews.title"
              placeholder="Reviews Section Title"
              style={{
                fontFamily: typography.headings_font || 'Georgia, serif',
                color: 'var(--primary-color)',
                marginBottom: '2rem',
                textAlign: 'center'
              }}
            />
            
            <div className="reviews-summary" style={{ textAlign: 'center', margin: '2rem 0' }}>
              <div className="overall-rating" style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '1rem',
                background: 'white',
                padding: '1rem 2rem',
                borderRadius: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <span className="rating-number" style={{
                  fontSize: '2rem',
                  fontWeight: 'bold',
                  color: 'var(--primary-color)'
                }}>
                  {website.pages?.[0]?.sections?.reviews?.overall_rating || 4.5}
                </span>
                <div className="stars" style={{ display: 'flex', gap: '0.25rem' }}>
                  {[1,2,3,4,5].map(star => (
                    <span
                      key={star}
                      className={`star ${star <= (website.pages?.[0]?.sections?.reviews?.overall_rating || 4.5) ? 'filled' : ''}`}
                      style={{
                        fontSize: '1.5rem',
                        color: star <= (website.pages?.[0]?.sections?.reviews?.overall_rating || 4.5) ? '#ffc107' : '#ddd'
                      }}
                    >
                      ★
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="reviews-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
              gap: '1.5rem',
              marginTop: '2rem'
            }}>
              {(website.pages?.[0]?.sections?.reviews?.items || [
                { name: "Sarah M.", rating: 5, text: "Amazing food and atmosphere! The service was exceptional.", date: "2024-01-15" },
                { name: "Mike R.", rating: 4, text: "Great service and delicious meals. Will definitely come back!", date: "2024-01-10" },
                { name: "Lisa K.", rating: 5, text: "Best restaurant in town! The pasta was incredible.", date: "2024-01-08" }
              ]).map((review, index) => (
                <div key={index} className="review-item" style={{
                  background: 'white',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <div className="review-header" style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '1rem'
                  }}>
                    <EditableElement
                      type="review-name"
                      value={review.name}
                      onSave={handleContentSave}
                      editMode={editMode}
                      tag="h4"
                      className="reviewer-name"
                      dataPath={`pages[0].sections.reviews.items[${index}].name`}
                      placeholder="Reviewer name"
                      style={{
                        color: 'var(--primary-color)',
                        margin: '0',
                        fontWeight: '600'
                      }}
                    />
                    <div className="review-rating" style={{ display: 'flex', gap: '0.25rem' }}>
                      {[1,2,3,4,5].map(star => (
                        <span
                          key={star}
                          className={`star ${star <= (review.rating || 5) ? 'filled' : ''}`}
                          style={{
                            fontSize: '1rem',
                            color: star <= (review.rating || 5) ? '#ffc107' : '#ddd'
                          }}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                  </div>
                  <EditableElement
                    type="review-text"
                    value={review.text}
                    onSave={handleContentSave}
                    editMode={editMode}
                    tag="p"
                    className="review-text"
                    dataPath={`pages[0].sections.reviews.items[${index}].text`}
                    placeholder="Review text"
                    style={{
                      color: 'var(--text-secondary)',
                      lineHeight: '1.6',
                      fontStyle: 'italic',
                      margin: '0'
                    }}
                  />
                </div>
              ))}
            </div>
            
            {editMode && (
              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                  className="btn btn-secondary"
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'transparent',
                    color: 'var(--primary-color)',
                    border: '2px solid var(--primary-color)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                  onClick={async () => {
                    // Add new review functionality with user prompts
                    const name = prompt('Enter the reviewer name:');
                    if (!name) return;
                    
                    const text = prompt('Enter the review text:');
                    if (!text) return;
                    
                    const ratingStr = prompt('Enter the rating (1-5):');
                    const rating = parseInt(ratingStr) || 5;
                    if (rating < 1 || rating > 5) {
                      alert('Rating must be between 1 and 5');
                      return;
                    }
                    
                    const currentReviews = website.pages?.[0]?.sections?.reviews?.items || [];
                    const newIndex = currentReviews.length;
                    
                    // Add all fields for the new review in a single update
                    try {
                      const contentUpdate = {
                        [`pages[0].sections.reviews.items[${newIndex}].name`]: name,
                        [`pages[0].sections.reviews.items[${newIndex}].text`]: text,
                        [`pages[0].sections.reviews.items[${newIndex}].rating`]: rating,
                        [`pages[0].sections.reviews.items[${newIndex}].date`]: new Date().toISOString().split('T')[0]
                      };
                      
                      await websiteBuilderAPI.updateContent(id, contentUpdate);
                      
                      // Refresh data to show the new item
                      await fetchWebsiteData();
                      
                    } catch (error) {
                      console.error('Error adding review:', error);
                      alert('Error adding review. Please try again.');
                    }
                  }}
                >
                  + Add Review
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Contact Section */}
        <div className="section" id="contact" style={{ padding: '3rem 0', backgroundColor: 'var(--neutral-color)' }}>
          <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', width: '100%', boxSizing: 'border-box' }}>
            <EditableElement
              type="contact-title"
              value={website.pages?.[0]?.sections?.contact?.title || 'Visit Us'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="h2"
              className="section-title"
              dataPath="pages[0].sections.contact.title"
              placeholder="Contact Section Title"
              style={{
                fontFamily: typography.headings_font || 'Georgia, serif',
                color: 'var(--primary-color)',
                marginBottom: '1rem'
              }}
            />
            <EditableElement
              type="contact-description"
              value={website.pages?.[0]?.sections?.contact?.description || `We'd love to welcome you to ${restaurantName}. Come experience the difference that passion makes.`}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="section-content"
              dataPath="pages[0].sections.contact.description"
              placeholder="Contact description..."
              style={{ marginBottom: '1rem' }}
            />
            <EditableElement
              type="contact-hours"
              value={website.pages?.[0]?.sections?.contact?.hours || 'Monday - Sunday, 11:00 AM - 10:00 PM'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="contact-hours"
              dataPath="pages[0].sections.contact.hours"
              placeholder="Business hours..."
              style={{ marginBottom: '0.5rem' }}
              prefix={<strong>Hours: </strong>}
            />
            <EditableElement
              type="contact-phone"
              value={website.pages?.[0]?.sections?.contact?.phone || '(555) 123-4567'}
              onSave={handleContentSave}
              editMode={editMode}
              tag="p"
              className="contact-phone"
              dataPath="pages[0].sections.contact.phone"
              placeholder="Phone number..."
              style={{ marginBottom: '2rem' }}
              prefix={<strong>Phone: </strong>}
            />
            <a href="#reservation" className="btn" style={{
              display: 'inline-block',
              padding: '12px 24px',
              backgroundColor: 'var(--accent-color)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              fontWeight: 'bold'
            }}>
              Make a Reservation
            </a>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="preview-loading">
        <div className="loading-spinner"></div>
        <p>Loading website preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-error">
        <div className="error-icon">⚠️</div>
        <h3>Error Loading Preview</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => navigate('/website-builder')}>
          Back to Website Builder
        </button>
      </div>
    );
  }

  return (
    <div className={`website-preview ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Enhanced Header with better controls */}
      <div className="preview-header">
        <div className="preview-header-left">
          <button
            className="back-btn"
            onClick={() => navigate('/website-builder')}
            title="Back to Website Builder"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m15 18-6-6 6-6"/>
            </svg>
            Back
          </button>
          <div className="title-info">
            <h1>{website?.website_name || 'Website Preview'}</h1>
            <div className="title-meta">
              <span className={`status-badge ${website?.status}`}>
                {website?.status || 'draft'}
              </span>
              <span className="preview-url">
                {website?.website_name?.toLowerCase().replace(/\s+/g, '-') || 'preview'}.example.com
              </span>
            </div>
          </div>
        </div>

        <div className="preview-header-right">
          <div className="device-selector">
            <button
              className={`device-btn ${previewMode === 'desktop' ? 'active' : ''}`}
              onClick={() => setPreviewMode('desktop')}
              title="Desktop View (1400px+)"
            >
              <svg width="20" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              <span>Desktop</span>
            </button>
            <button
              className={`device-btn ${previewMode === 'tablet' ? 'active' : ''}`}
              onClick={() => setPreviewMode('tablet')}
              title="Tablet View (768px)"
            >
              <svg width="16" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
              </svg>
              <span>Tablet</span>
            </button>
            <button
              className={`device-btn ${previewMode === 'mobile' ? 'active' : ''}`}
              onClick={() => setPreviewMode('mobile')}
              title="Mobile View (375px)"
            >
              <svg width="14" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
              </svg>
              <span>Mobile</span>
            </button>
          </div>

          <div className="preview-controls">
            <button
              className="control-btn"
              onClick={() => setIsFullscreen(!isFullscreen)}
              title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {isFullscreen ? (
                  <>
                    <path d="M8 3v3a2 2 0 0 1-2 2H3"/>
                    <path d="M21 8h-3a2 2 0 0 1-2-2V3"/>
                    <path d="M3 16h3a2 2 0 0 1 2 2v3"/>
                    <path d="M16 21v-3a2 2 0 0 1 2-2h3"/>
                  </>
                ) : (
                  <>
                    <path d="M15 3h6v6"/>
                    <path d="M9 21H3v-6"/>
                    <path d="M21 3l-7 7"/>
                    <path d="M3 21l7-7"/>
                  </>
                )}
              </svg>
            </button>
            <button
              className="control-btn"
              onClick={() => window.open(window.location.href, '_blank')}
              title="Open in New Tab"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15,3 21,3 21,9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </button>
          </div>

          <div className="action-buttons">
            <button
              className={`btn-secondary ${editMode ? 'active' : ''}`}
              onClick={() => setEditMode(!editMode)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              {editMode ? 'Exit Edit' : 'Edit'}
              {editMode && hasUnsavedChanges && (
                <span style={{
                  position: 'absolute',
                  top: '-5px',
                  right: '-5px',
                  width: '10px',
                  height: '10px',
                  backgroundColor: '#f59e0b',
                  borderRadius: '50%',
                  border: '2px solid white'
                }}></span>
              )}
            </button>
            {editMode && (
              <button
                className="btn-primary"
                onClick={handleSaveAll}
                disabled={saving}
                style={{
                  background: saving ? '#6b7280' : undefined,
                  cursor: saving ? 'not-allowed' : 'pointer',
                  position: 'relative'
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                  <polyline points="17,21 17,13 7,13 7,21"/>
                  <polyline points="7,3 7,8 15,8"/>
                </svg>
                {saving ? 'Saving...' : 'Save Changes'}
                {hasUnsavedChanges && !saving && (
                  <span style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '-5px',
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#10b981',
                    borderRadius: '50%',
                    border: '2px solid white'
                  }}></span>
                )}
              </button>
            )}
            {!editMode && (
              <button className="btn-secondary" onClick={handleEdit}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 20h9"/>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
                Advanced Edit
              </button>
            )}
            {website?.status !== 'published' && !editMode && (
              <button className="btn-primary" onClick={handlePublish}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
                  <path d="M12 15l8.5-8.5a2.83 2.83 0 0 0-4-4L8 11l4 4z"/>
                  <path d="M9 12l-2 2"/>
                  <path d="M16 6l2 2"/>
                </svg>
                Publish
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced info panel */}
      {!isFullscreen && (
        <div className="website-info-panel">
          <div className="info-section">
            <div className="info-item">
              <span className="info-icon">📅</span>
              <div className="info-content">
                <span className="info-label">Created</span>
                <span className="info-value">
                  {website?.created_at ? new Date(website.created_at).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
            </div>
            <div className="info-item">
              <span className="info-icon">🏷️</span>
              <div className="info-content">
                <span className="info-label">Category</span>
                <span className="info-value">
                  {website?.design_category?.replace('_', ' ') || 'General'}
                </span>
              </div>
            </div>
            <div className="info-item">
              <span className="info-icon">🔄</span>
              <div className="info-content">
                <span className="info-label">Last Updated</span>
                <span className="info-value">
                  {website?.updated_at ? new Date(website.updated_at).toLocaleDateString() : 'Never'}
                </span>
              </div>
            </div>
            
            {/* Compact Theme Tool */}
            {editMode && (
              <div className="info-item theme-tool-compact">
                <span className="info-icon">🎨</span>
                <div className="info-content">
                  <span className="info-label">Colors & Theme</span>
                  <div className="compact-theme-controls">
                    <div className="color-swatches">
                      <input
                        type="color"
                        value={website?.design_system?.color_palette?.primary || '#2c3e50'}
                        onChange={(e) => handleColorChange('primary', e.target.value, 'design_system.color_palette.primary')}
                        className="color-swatch"
                        title="Primary Color"
                      />
                      <input
                        type="color"
                        value={website?.design_system?.color_palette?.secondary || '#e74c3c'}
                        onChange={(e) => handleColorChange('secondary', e.target.value, 'design_system.color_palette.secondary')}
                        className="color-swatch"
                        title="Secondary Color"
                      />
                      <input
                        type="color"
                        value={website?.design_system?.color_palette?.accent || '#f39c12'}
                        onChange={(e) => handleColorChange('accent', e.target.value, 'design_system.color_palette.accent')}
                        className="color-swatch"
                        title="Accent Color"
                      />
                      <input
                        type="color"
                        value={website?.design_system?.color_palette?.neutral || '#ecf0f1'}
                        onChange={(e) => handleColorChange('neutral', e.target.value, 'design_system.color_palette.neutral')}
                        className="color-swatch"
                        title="Background Color"
                      />
                    </div>
                    <div className="theme-presets-compact">
                      <button
                        className="preset-btn-compact"
                        onClick={() => applyThemePreset('elegant')}
                        title="Elegant Theme"
                      >
                        Elegant
                      </button>
                      <button
                        className="preset-btn-compact"
                        onClick={() => applyThemePreset('modern')}
                        title="Modern Theme"
                      >
                        Modern
                      </button>
                      <button
                        className="preset-btn-compact"
                        onClick={() => applyThemePreset('warm')}
                        title="Warm Theme"
                      >
                        Warm
                      </button>
                      <button
                        className="preset-btn-compact"
                        onClick={() => applyThemePreset('fresh')}
                        title="Fresh Theme"
                      >
                        Fresh
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="preview-dimensions">
            <span className="dimensions-text">
              {previewMode === 'desktop' && '1400px × 900px (Full Width)'}
              {previewMode === 'tablet' && '768px × 1024px'}
              {previewMode === 'mobile' && '375px × 667px'}
            </span>
          </div>
        </div>
      )}

      {/* Enhanced preview container */}
      <div className="preview-container">
        <div className={`preview-frame ${previewMode} ${editMode ? 'edit-mode' : ''}`}>
          {renderWebsiteContent()}
        </div>
      </div>

      {/* Enhanced generation details */}
      {!isFullscreen && website?.generation_details && (
        <div className="generation-details">
          <div className="details-header">
            <h3>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 1v6m0 6v6"/>
                <path d="M21 12h-6m-6 0H3"/>
              </svg>
              Generation Details
            </h3>
          </div>
          <div className="details-grid">
            {website.generation_details.features_used && (
              <div className="detail-item">
                <div className="detail-header">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="9,11 12,14 22,4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  <strong>Features Used</strong>
                </div>
                <ul className="feature-list">
                  {website.generation_details.features_used.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            )}
            {website.generation_details.ai_model && (
              <div className="detail-item">
                <div className="detail-header">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
                    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
                  </svg>
                  <strong>AI Model</strong>
                </div>
                <span className="detail-value">{website.generation_details.ai_model}</span>
              </div>
            )}
            {website.generation_details.generation_time && (
              <div className="detail-item">
                <div className="detail-header">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12,6 12,12 16,14"/>
                  </svg>
                  <strong>Generation Time</strong>
                </div>
                <span className="detail-value">{website.generation_details.generation_time}s</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WebsitePreview;