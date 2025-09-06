import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import './TemplateCustomizer.css';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';
import { dashboardAPI } from '../../services/api';

const TemplateCustomizer = () => {
  const { templateId } = useParams();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('content');
  const [previewMode, setPreviewMode] = useState('desktop');

  // Template data (in a real app, this would come from an API)
  const templateData = {
    'fine-dining-1': {
      name: 'Elegant Fine Dining',
      category: 'fine_dining',
      baseHtml: `
        <div class="restaurant-site">
          <header class="hero-section">
            <nav class="navbar">
              <div class="logo">{{restaurant_name}}</div>
              <ul class="nav-menu">
                <li><a href="#about">About</a></li>
                <li><a href="#menu">Menu</a></li>
                <li><a href="#reservations">Reservations</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </nav>
            <div class="hero-content">
              <h1>{{restaurant_name}}</h1>
              <p class="hero-subtitle">{{restaurant_tagline}}</p>
              <button class="cta-button">Make a Reservation</button>
            </div>
          </header>
          
          <section id="about" class="about-section">
            <div class="container">
              <h2>About Us</h2>
              <p>{{about_description}}</p>
            </div>
          </section>
          
          <section id="menu" class="menu-section">
            <div class="container">
              <h2>Our Menu</h2>
              <div class="menu-grid">
                {{menu_items}}
              </div>
            </div>
          </section>
          
          <section id="contact" class="contact-section">
            <div class="container">
              <h2>Contact Us</h2>
              <div class="contact-info">
                <p><strong>Address:</strong> {{restaurant_address}}</p>
                <p><strong>Phone:</strong> {{restaurant_phone}}</p>
                <p><strong>Email:</strong> {{restaurant_email}}</p>
              </div>
            </div>
          </section>
        </div>
      `,
      baseCss: `
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Georgia', serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        .hero-section { 
          background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><rect fill="%23{{primary_color_hex}}" width="1200" height="600"/></svg>');
          height: 100vh; color: white; display: flex; flex-direction: column;
        }
        
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav-menu { display: flex; list-style: none; gap: 2rem; }
        .nav-menu a { color: white; text-decoration: none; }
        
        .hero-content { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
        .hero-content h1 { font-size: 4rem; margin-bottom: 1rem; }
        .hero-subtitle { font-size: 1.5rem; margin-bottom: 2rem; }
        .cta-button { padding: 1rem 2rem; background: {{primary_color}}; color: white; border: none; border-radius: 5px; font-size: 1.1rem; cursor: pointer; }
        
        .about-section, .menu-section, .contact-section { padding: 4rem 0; }
        .about-section h2, .menu-section h2, .contact-section h2 { text-align: center; margin-bottom: 2rem; font-size: 2.5rem; color: {{primary_color}}; }
        
        .menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .menu-item { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; }
        .menu-item h3 { color: {{primary_color}}; margin-bottom: 0.5rem; }
        
        .contact-info { text-align: center; font-size: 1.1rem; }
        .contact-info p { margin-bottom: 1rem; }
      `
    },
    'casual-dining-1': {
      name: 'Modern Casual',
      category: 'casual_dining',
      baseHtml: `
        <div class="restaurant-site">
          <header class="header">
            <div class="container">
              <div class="logo">{{restaurant_name}}</div>
              <nav class="nav">
                <a href="#menu">Menu</a>
                <a href="#about">About</a>
                <a href="#location">Location</a>
                <a href="#contact">Contact</a>
              </nav>
            </div>
          </header>
          
          <section class="hero">
            <div class="hero-content">
              <h1>{{restaurant_name}}</h1>
              <p>{{restaurant_tagline}}</p>
              <button class="order-btn">Order Online</button>
            </div>
          </section>
          
          <section id="about" class="about">
            <div class="container">
              <h2>About Us</h2>
              <p>{{about_description}}</p>
            </div>
          </section>
          
          <section id="menu" class="menu">
            <div class="container">
              <h2>Our Menu</h2>
              <div class="menu-categories">
                {{menu_items}}
              </div>
            </div>
          </section>
          
          <footer class="footer">
            <div class="container">
              <div class="footer-content">
                <div class="contact-info">
                  <h3>Contact</h3>
                  <p>{{restaurant_address}}</p>
                  <p>{{restaurant_phone}}</p>
                  <p>{{restaurant_email}}</p>
                </div>
              </div>
            </div>
          </footer>
        </div>
      `,
      baseCss: `
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        .header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; width: 100%; top: 0; z-index: 1000; }
        .header .container { display: flex; justify-content: space-between; align-items: center; padding: 1rem 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: {{primary_color}}; }
        .nav { display: flex; gap: 2rem; }
        .nav a { text-decoration: none; color: #333; font-weight: 500; }
        
        .hero { 
          background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
          height: 100vh; display: flex; align-items: center; justify-content: center; color: white; text-align: center; margin-top: 80px;
        }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.3rem; margin-bottom: 2rem; }
        .order-btn { padding: 1rem 2rem; background: white; color: {{primary_color}}; border: none; border-radius: 25px; font-size: 1.1rem; cursor: pointer; }
        
        .about, .menu { padding: 4rem 0; }
        .about h2, .menu h2 { text-align: center; margin-bottom: 2rem; font-size: 2.5rem; color: {{primary_color}}; }
        .about p { text-align: center; font-size: 1.1rem; max-width: 800px; margin: 0 auto; }
        
        .menu-categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
        .menu-item { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center; }
        .menu-item h3 { color: {{primary_color}}; margin-bottom: 1rem; }
        
        .footer { background: #2c3e50; color: white; padding: 2rem 0; }
        .footer h3 { margin-bottom: 1rem; }
      `
    }
    // Add more templates as needed
  };

  const [customization, setCustomization] = useState({
    restaurant_name: 'Your Restaurant Name',
    restaurant_tagline: 'Delicious food, great atmosphere',
    about_description: 'We are passionate about serving the finest cuisine with exceptional service in a warm and welcoming atmosphere.',
    restaurant_address: '123 Main Street, City, State 12345',
    restaurant_phone: '(555) 123-4567',
    restaurant_email: 'info@yourrestaurant.com',
    primary_color: '#2c3e50',
    secondary_color: '#e74c3c',
    menu_items: [
      { name: 'Signature Dish', description: 'Our chef\'s special creation', price: '$24.99' },
      { name: 'Popular Item', description: 'Customer favorite', price: '$18.99' },
      { name: 'Seasonal Special', description: 'Fresh seasonal ingredients', price: '$22.99' }
    ]
  });

  const currentTemplate = templateData[templateId as keyof typeof templateData];

  useEffect(() => {
    if (!currentTemplate) {
      router.push('/website-builder/templates');
    }
  }, [templateId, currentTemplate, router]);

  const handleCustomizationChange = (field: string, value: string) => {
    setCustomization(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMenuItemChange = (index: number, field: string, value: string) => {
    const newMenuItems = [...customization.menu_items];
    newMenuItems[index] = { ...newMenuItems[index], [field]: value };
    setCustomization(prev => ({
      ...prev,
      menu_items: newMenuItems
    }));
  };

  const addMenuItem = () => {
    setCustomization(prev => ({
      ...prev,
      menu_items: [...prev.menu_items, { name: '', description: '', price: '' }]
    }));
  };

  const removeMenuItem = (index: number) => {
    setCustomization(prev => ({
      ...prev,
      menu_items: prev.menu_items.filter((_, i) => i !== index)
    }));
  };

  const generatePreviewHtml = () => {
    if (!currentTemplate) return '';

    let html = currentTemplate.baseHtml;
    let css = currentTemplate.baseCss;

    // Replace placeholders in HTML
    Object.keys(customization).forEach(key => {
      if (key === 'menu_items') {
        const menuHtml = customization.menu_items.map(item => `
          <div class="menu-item">
            <h3>${item.name}</h3>
            <p>${item.description}</p>
            <span class="price">${item.price}</span>
          </div>
        `).join('');
        html = html.replace('{{menu_items}}', menuHtml);
      } else {
        const regex = new RegExp(`{{${key}}}`, 'g');
        html = html.replace(regex, (customization as any)[key]);
      }
    });

    // Replace placeholders in CSS
    css = css.replace(/{{primary_color}}/g, customization.primary_color);
    css = css.replace(/{{secondary_color}}/g, customization.secondary_color);
    css = css.replace(/{{primary_color_hex}}/g, customization.primary_color.replace('#', ''));

    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${customization.restaurant_name}</title>
        <style>${css}</style>
      </head>
      <body>
        ${html}
      </body>
      </html>
    `;
  };

  const handleSaveAndPreview = async () => {
    setLoading(true);
    try {
      console.log('🔍 DEBUG: TemplateCustomizer - Starting save using centralized API service');
      
      // Get restaurant data using the same successful method as working features
      const restaurantData = await dashboardAPI.getRestaurantDashboard();
      console.log('🔍 DEBUG: TemplateCustomizer - Restaurant data from dashboard API:', restaurantData);
      
      if (!restaurantData || !restaurantData.restaurant || !restaurantData.restaurant.restaurant_id) {
        console.error('🔍 DEBUG: TemplateCustomizer - Invalid restaurant data structure');
        alert('No restaurant found. Please create a restaurant first.');
        return;
      }
      
      const restaurant_id = restaurantData.restaurant.restaurant_id;
      console.log('🔍 DEBUG: TemplateCustomizer - Using restaurant_id:', restaurant_id);

      // Create website from template
      const websiteData = {
        restaurant_id: restaurant_id,
        website_name: customization.restaurant_name,
        template_id: templateId,
        template_customizations: customization,
        generated_content: {
          html: generatePreviewHtml().match(/<body>(.*?)<\/body>/)?.[1] || '',
          css: currentTemplate.baseCss.replace(/{{primary_color}}/g, customization.primary_color).replace(/{{secondary_color}}/g, customization.secondary_color)
        },
        design_category: currentTemplate.category,
        status: 'ready'
      };

      // Use the centralized API service
      const result = await websiteBuilderAPI.createFromTemplate(websiteData);
      console.log('🔍 DEBUG: TemplateCustomizer - Template creation result:', result);
      
      router.push(`/website-builder/preview/${result.website_id}`);
    } catch (error) {
      console.error('🔍 DEBUG: TemplateCustomizer - Error creating website:', error);
      alert('Error creating website: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!currentTemplate) {
    return (
      <div className="customizer-loading">
        <div className="loading-spinner"></div>
        <p>Loading template...</p>
      </div>
    );
  }

  return (
    <div className="template-customizer">
      {/* Header */}
      <div className="customizer-header">
        <button 
          className="back-btn"
          onClick={() => router.push('/website-builder/templates')}
        >
          ← Back to Templates
        </button>
        <div className="header-info">
          <h1>Customize: {currentTemplate.name}</h1>
          <p>Personalize your website template</p>
        </div>
        <button 
          className="save-preview-btn"
          onClick={handleSaveAndPreview}
          disabled={loading}
        >
          {loading ? 'Creating...' : '🚀 Save & Preview'}
        </button>
      </div>

      <div className="customizer-content">
        {/* Sidebar with customization options */}
        <div className="customizer-sidebar">
          <div className="sidebar-tabs">
            <button 
              className={`tab-btn ${activeTab === 'content' ? 'active' : ''}`}
              onClick={() => setActiveTab('content')}
            >
              📝 Content
            </button>
            <button 
              className={`tab-btn ${activeTab === 'design' ? 'active' : ''}`}
              onClick={() => setActiveTab('design')}
            >
              🎨 Design
            </button>
            <button 
              className={`tab-btn ${activeTab === 'menu' ? 'active' : ''}`}
              onClick={() => setActiveTab('menu')}
            >
              🍽️ Menu
            </button>
          </div>

          <div className="sidebar-content">
            {activeTab === 'content' && (
              <div className="content-tab">
                <div className="form-group">
                  <label>Restaurant Name</label>
                  <input
                    type="text"
                    value={customization.restaurant_name}
                    onChange={(e) => handleCustomizationChange('restaurant_name', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Tagline</label>
                  <input
                    type="text"
                    value={customization.restaurant_tagline}
                    onChange={(e) => handleCustomizationChange('restaurant_tagline', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>About Description</label>
                  <textarea
                    value={customization.about_description}
                    onChange={(e) => handleCustomizationChange('about_description', e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    value={customization.restaurant_address}
                    onChange={(e) => handleCustomizationChange('restaurant_address', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="text"
                    value={customization.restaurant_phone}
                    onChange={(e) => handleCustomizationChange('restaurant_phone', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={customization.restaurant_email}
                    onChange={(e) => handleCustomizationChange('restaurant_email', e.target.value)}
                  />
                </div>
              </div>
            )}

            {activeTab === 'design' && (
              <div className="design-tab">
                <div className="form-group">
                  <label>Primary Color</label>
                  <input
                    type="color"
                    value={customization.primary_color}
                    onChange={(e) => handleCustomizationChange('primary_color', e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Secondary Color</label>
                  <input
                    type="color"
                    value={customization.secondary_color}
                    onChange={(e) => handleCustomizationChange('secondary_color', e.target.value)}
                  />
                </div>
              </div>
            )}

            {activeTab === 'menu' && (
              <div className="menu-tab">
                <div className="menu-items">
                  {customization.menu_items.map((item, index) => (
                    <div key={index} className="menu-item-editor">
                      <div className="menu-item-header">
                        <h4>Menu Item {index + 1}</h4>
                        <button 
                          className="remove-btn"
                          onClick={() => removeMenuItem(index)}
                        >
                          ×
                        </button>
                      </div>
                      
                      <div className="form-group">
                        <label>Name</label>
                        <input
                          type="text"
                          value={item.name}
                          onChange={(e) => handleMenuItemChange(index, 'name', e.target.value)}
                        />
                      </div>

                      <div className="form-group">
                        <label>Description</label>
                        <textarea
                          value={item.description}
                          onChange={(e) => handleMenuItemChange(index, 'description', e.target.value)}
                          rows={2}
                        />
                      </div>

                      <div className="form-group">
                        <label>Price</label>
                        <input
                          type="text"
                          value={item.price}
                          onChange={(e) => handleMenuItemChange(index, 'price', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <button className="add-menu-item-btn" onClick={addMenuItem}>
                  + Add Menu Item
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Preview area */}
        <div className="preview-area">
          <div className="preview-controls">
            <div className="device-selector">
              <button 
                className={`device-btn ${previewMode === 'desktop' ? 'active' : ''}`}
                onClick={() => setPreviewMode('desktop')}
              >
                🖥️
              </button>
              <button 
                className={`device-btn ${previewMode === 'tablet' ? 'active' : ''}`}
                onClick={() => setPreviewMode('tablet')}
              >
                📱
              </button>
              <button 
                className={`device-btn ${previewMode === 'mobile' ? 'active' : ''}`}
                onClick={() => setPreviewMode('mobile')}
              >
                📱
              </button>
            </div>
          </div>

          <div className="preview-container">
            <iframe
              className={`preview-iframe ${previewMode}`}
              srcDoc={generatePreviewHtml()}
              title="Template Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateCustomizer;