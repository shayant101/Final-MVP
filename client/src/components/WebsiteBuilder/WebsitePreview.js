import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './WebsitePreview.css';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';
import EditableElement from './EditableElement';
import EditableImageElement from './EditableImageElement';
import EditableColorElement from './EditableColorElement';
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
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [activeColorType, setActiveColorType] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Media uploader hook
  const { uploadImage, uploading, progress, error: uploadError } = useMediaUploader();

  const fetchWebsiteData = useCallback(async () => {
    try {
      console.log('🔍 DEBUG: WebsitePreview - Starting fetchWebsiteData using centralized API service');
      
      // Use the centralized API service
      const data = await websiteBuilderAPI.getWebsiteDetails(id);
      console.log('🔍 DEBUG: WebsitePreview - Response data:', data);
      console.log('🔍 DEBUG: WebsitePreview - Has generated_content?', !!data?.generated_content);
      console.log('🔍 DEBUG: WebsitePreview - Data keys:', Object.keys(data || {}));
      console.log('🔍 DEBUG: WebsitePreview - Pages:', data?.pages);
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
    'menu-item-price': 'menu_items[INDEX].price'
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

      return menuItems.map(item => `
        <div class="menu-item">
          <h3>${item.name || 'Menu Item'}</h3>
          <p>${item.description || 'Delicious dish description'}</p>
          <div class="price">${item.price || '$0.00'}</div>
        </div>
      `).join('');
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
      
      return `
        <div class="hero-section">
          ${absoluteHeroImage ? `<img src="${absoluteHeroImage}" alt="Hero background" class="hero-background-image" />` : ''}
          <div class="container hero-content">
            <h1>${restaurantName}</h1>
            <p>Experience exceptional dining with authentic flavors and warm hospitality</p>
            <a href="#menu" class="btn">View Our Menu</a>
          </div>
        </div>
        
        <div class="section" id="about">
          <div class="container">
            <h2>About Us</h2>
            <p>Welcome to ${restaurantName}, where culinary excellence meets warm hospitality. Our passionate chefs create memorable dining experiences using the finest ingredients and time-honored techniques.</p>
          </div>
        </div>
        
        <div class="section" id="menu">
          <div class="container">
            <h2>Our Menu</h2>
            <p>Discover our carefully crafted dishes that celebrate flavor and tradition.</p>
            <div class="menu-grid">
              ${generateMenuItemsHTML()}
            </div>
          </div>
        </div>
        
        <div class="section" id="contact">
          <div class="container">
            <h2>Visit Us</h2>
            <p>We'd love to welcome you to ${restaurantName}. Come experience the difference that passion makes.</p>
            <p><strong>Hours:</strong> Monday - Sunday, 11:00 AM - 10:00 PM</p>
            <p><strong>Phone:</strong> (555) 123-4567</p>
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

    return menuItems.map((item, index) => (
      <div key={index} className="menu-item" style={{
        background: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
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