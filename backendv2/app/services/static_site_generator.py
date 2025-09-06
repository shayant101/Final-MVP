
"""
Static Site Generator Service
Converts restaurant website data into deployable static files
"""

import os
import json
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
import re
import base64
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class StaticSiteGenerator:
    """
    Comprehensive Static Site Generator for restaurant websites
    Converts website data into optimized static HTML, CSS, and JavaScript files
    """
    
    def __init__(self, base_path: str = "generated_sites"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates" / "static_sites"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Image sizes for responsive design
        self.image_sizes = {
            'hero': [(1920, 1080), (1200, 675), (800, 450), (400, 225)],
            'menu_item': [(800, 600), (400, 300), (200, 150)],
            'gallery': [(1200, 800), (600, 400), (300, 200)],
            'logo': [(400, 400), (200, 200), (100, 100)],
            'general': [(1200, 800), (600, 400), (300, 200)]
        }
        
        # CSS breakpoints
        self.breakpoints = {
            'mobile': '480px',
            'tablet': '768px',
            'desktop': '1024px',
            'large': '1200px'
        }
    
    async def generate_static_site(self, website_data: Dict[str, Any], output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate complete static site from website data
        
        Args:
            website_data: Complete website data from database
            output_dir: Optional custom output directory
            
        Returns:
            Dict with generation results and file paths
        """
        try:
            # Create output directory
            if output_dir:
                site_dir = Path(output_dir)
            else:
                site_dir = self.base_path / website_data.get('subdomain', website_data['website_id'])
            
            site_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate file structure
            await self._create_directory_structure(site_dir)
            
            # Generate HTML files
            html_files = await self._generate_html_files(website_data, site_dir)
            
            # Generate CSS files
            css_files = await self._generate_css_files(website_data, site_dir)
            
            # Generate JavaScript files
            js_files = await self._generate_js_files(website_data, site_dir)
            
            # Process and optimize assets
            asset_files = await self._process_assets(website_data, site_dir)
            
            # Generate SEO files
            seo_files = await self._generate_seo_files(website_data, site_dir)
            
            # Generate PWA files
            pwa_files = await self._generate_pwa_files(website_data, site_dir)
            
            return {
                'success': True,
                'site_directory': str(site_dir),
                'files_generated': {
                    'html': html_files,
                    'css': css_files,
                    'js': js_files,
                    'assets': asset_files,
                    'seo': seo_files,
                    'pwa': pwa_files
                },
                'total_files': len(html_files) + len(css_files) + len(js_files) + len(asset_files) + len(seo_files) + len(pwa_files),
                'generation_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Static site generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generation_time': datetime.utcnow().isoformat()
            }
    
    async def _create_directory_structure(self, site_dir: Path):
        """Create the standard directory structure for static sites"""
        directories = [
            'css',
            'js',
            'images',
            'images/hero',
            'images/menu',
            'images/gallery',
            'images/icons',
            'fonts',
            'assets'
        ]
        
        for directory in directories:
            (site_dir / directory).mkdir(parents=True, exist_ok=True)
    
    async def _generate_html_files(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Generate HTML files for all pages"""
        html_files = []
        
        # Get pages from website data
        pages = website_data.get('pages', [])
        if not pages:
            # Create default homepage if no pages exist
            pages = [self._create_default_homepage(website_data)]
        
        for page in pages:
            try:
                # Generate HTML content
                html_content = await self._generate_page_html(page, website_data)
                
                # Determine filename
                if page.get('is_homepage', False) or page.get('page_slug') == '/':
                    filename = 'index.html'
                else:
                    slug = page.get('page_slug', '').strip('/')
                    filename = f"{slug}.html" if slug else f"page-{page.get('page_id', 'unknown')}.html"
                
                # Write HTML file
                html_file = site_dir / filename
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_files.append(filename)
                logger.info(f"Generated HTML file: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to generate HTML for page {page.get('page_id')}: {str(e)}")
        
        return html_files
    
    async def _generate_page_html(self, page: Dict[str, Any], website_data: Dict[str, Any]) -> str:
        """Generate HTML content for a single page"""
        # Prepare template context
        context = {
            'page': page,
            'website': website_data,
            'seo': website_data.get('seo_settings', {}),
            'design': website_data.get('design_system', {}),
            'menu_items': website_data.get('menu_items', []),
            'hero_image': website_data.get('hero_image'),
            'current_year': datetime.now().year,
            'generation_date': datetime.utcnow().isoformat()
        }
        
        # Load and render template
        try:
            template = self.jinja_env.get_template('restaurant_page.html')
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            # Fallback to basic HTML generation
            return await self._generate_basic_html(page, website_data)
    
    async def _generate_basic_html(self, page: Dict[str, Any], website_data: Dict[str, Any]) -> str:
        """Generate basic HTML when template is not available"""
        seo = website_data.get('seo_settings', {})
        design = website_data.get('design_system', {})
        colors = design.get('color_palette', {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.get('page_title', seo.get('site_title', website_data.get('website_name', 'Restaurant')))}</title>
    <meta name="description" content="{page.get('meta_description', seo.get('site_description', ''))}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{page.get('page_title', seo.get('site_title', ''))}">
    <meta property="og:description" content="{page.get('meta_description', seo.get('site_description', ''))}">
    <meta property="og:image" content="{seo.get('og_image', '')}">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="{page.get('page_title', seo.get('site_title', ''))}">
    <meta property="twitter:description" content="{page.get('meta_description', seo.get('site_description', ''))}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/images/icons/favicon.ico">
    <link rel="apple-touch-icon" href="/images/icons/apple-touch-icon.png">
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="/css/main.css">
    <link rel="stylesheet" href="/css/responsive.css">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(self._generate_structured_data(website_data), indent=2)}
    </script>
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="container">
                <div class="nav-brand">
                    <h1>{website_data.get('website_name', 'Restaurant')}</h1>
                </div>
                <div class="nav-menu">
                    <a href="#home">Home</a>
                    <a href="#menu">Menu</a>
                    <a href="#about">About</a>
                    <a href="#contact">Contact</a>
                </div>
            </div>
        </nav>
    </header>
    
    <main class="main-content">
        {await self._generate_page_sections(page, website_data)}
    </main>
    
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{website_data.get('website_name', 'Restaurant')}</h3>
                    <p>Delicious food, exceptional service.</p>
                </div>
                <div class="footer-section">
                    <h4>Contact</h4>
                    <p>Phone: (555) 123-4567</p>
                    <p>Email: info@restaurant.com</p>
                </div>
                <div class="footer-section">
                    <h4>Hours</h4>
                    <p>Mon-Sun: 11:00 AM - 10:00 PM</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} {website_data.get('website_name', 'Restaurant')}. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <!-- Scripts -->
    <script src="/js/main.js"></script>
    <script src="/js/performance.js"></script>
</body>
</html>"""
        
        return html
    
    async def _generate_page_sections(self, page: Dict[str, Any], website_data: Dict[str, Any]) -> str:
        """Generate HTML sections for a page"""
        sections_html = []
        
        # Hero Section
        hero_image = website_data.get('hero_image', '')
        sections_html.append(f"""
        <section id="home" class="hero-section">
            <div class="hero-background" style="background-image: url('{hero_image}');">
                <div class="hero-overlay">
                    <div class="container">
                        <div class="hero-content">
                            <h1 class="hero-title">{website_data.get('website_name', 'Welcome to Our Restaurant')}</h1>
                            <p class="hero-subtitle">Experience exceptional dining with fresh ingredients and authentic flavors</p>
                            <div class="hero-actions">
                                <a href="#menu" class="btn btn-primary">View Menu</a>
                                <a href="#contact" class="btn btn-secondary">Make Reservation</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        """)
        
        # Menu Section
        menu_items = website_data.get('menu_items', [])
        if menu_items:
            menu_html = '<div class="menu-grid">'
            for item in menu_items[:12]:  # Limit to 12 items for performance
                menu_html += f"""
                <div class="menu-item">
                    <div class="menu-item-image">
                        <img src="{item.get('image', '/images/menu/default.jpg')}" alt="{item.get('name', 'Menu Item')}" loading="lazy">
                    </div>
                    <div class="menu-item-content">
                        <h3 class="menu-item-name">{item.get('name', 'Menu Item')}</h3>
                        <p class="menu-item-description">{item.get('description', 'Delicious dish made with fresh ingredients')}</p>
                        <span class="menu-item-price">${item.get('price', '0.00')}</span>
                    </div>
                </div>
                """
            menu_html += '</div>'
            
            sections_html.append(f"""
            <section id="menu" class="menu-section">
                <div class="container">
                    <div class="section-header">
                        <h2>Our Menu</h2>
                        <p>Discover our carefully crafted dishes</p>
                    </div>
                    {menu_html}
                </div>
            </section>
            """)
        
        # About Section
        sections_html.append(f"""
        <section id="about" class="about-section">
            <div class="container">
                <div class="about-content">
                    <div class="about-text">
                        <h2>About Us</h2>
                        <p>We are passionate about serving exceptional food made with the finest ingredients. Our commitment to quality and service has made us a favorite dining destination.</p>
                        <p>Come experience the perfect blend of traditional recipes and modern culinary techniques in a warm, welcoming atmosphere.</p>
                    </div>
                    <div class="about-image">
                        <img src="/images/gallery/restaurant-interior.jpg" alt="Restaurant Interior" loading="lazy">
                    </div>
                </div>
            </div>
        </section>
        """)
        
        # Contact Section
        sections_html.append(f"""
        <section id="contact" class="contact-section">
            <div class="container">
                <div class="section-header">
                    <h2>Contact Us</h2>
                    <p>Get in touch or make a reservation</p>
                </div>
                <div class="contact-content">
                    <div class="contact-info">
                        <div class="contact-item">
                            <h4>Address</h4>
                            <p>123 Restaurant Street<br>City, State 12345</p>
                        </div>
                        <div class="contact-item">
                            <h4>Phone</h4>
                            <p>(555) 123-4567</p>
                        </div>
                        <div class="contact-item">
                            <h4>Email</h4>
                            <p>info@restaurant.com</p>
                        </div>
                        <div class="contact-item">
                            <h4>Hours</h4>
                            <p>Monday - Sunday<br>11:00 AM - 10:00 PM</p>
                        </div>
                    </div>
                    <div class="contact-form">
                        <form class="reservation-form">
                            <div class="form-group">
                                <input type="text" name="name" placeholder="Your Name" required>
                            </div>
                            <div class="form-group">
                                <input type="email" name="email" placeholder="Your Email" required>
                            </div>
                            <div class="form-group">
                                <input type="tel" name="phone" placeholder="Your Phone">
                            </div>
                            <div class="form-group">
                                <textarea name="message" placeholder="Special requests or questions" rows="4"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Send Message</button>
                        </form>
                    </div>
                </div>
            </div>
        </section>
        """)
        
        return '\n'.join(sections_html)
    
    def _generate_structured_data(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD structured data for SEO"""
        return {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": website_data.get('website_name', 'Restaurant'),
            "description": website_data.get('seo_settings', {}).get('site_description', ''),
            "url": website_data.get('live_url', ''),
            "telephone": "(555) 123-4567",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Restaurant Street",
                "addressLocality": "City",
                "addressRegion": "State",
                "postalCode": "12345",
                "addressCountry": "US"
            },
            "openingHours": [
                "Mo-Su 11:00-22:00"
            ],
            "servesCuisine": "American",
            "priceRange": "$$",
            "image": website_data.get('hero_image', ''),
            "hasMenu": website_data.get('live_url', '') + "#menu"
        }
    
    def _create_default_homepage(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a default homepage when no pages exist"""
        return {
            'page_id': 'homepage',
            'page_name': 'Home',
            'page_slug': '/',
            'page_title': website_data.get('seo_settings', {}).get('site_title', website_data.get('website_name', 'Restaurant')),
            'meta_description': website_data.get('seo_settings', {}).get('site_description', 'Welcome to our restaurant'),
            'is_homepage': True,
            'published': True,
            'components': [],
            'sections': {}
        }
    
    async def _generate_css_files(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Generate CSS files with custom styling"""
        css_files = []
        
        # Generate main CSS file
        main_css = await self._generate_main_css(website_data)
        main_css_file = site_dir / 'css' / 'main.css'
        with open(main_css_file, 'w', encoding='utf-8') as f:
            f.write(main_css)
        css_files.append('css/main.css')
        
        # Generate responsive CSS file
        responsive_css = await self._generate_responsive_css(website_data)
        responsive_css_file = site_dir / 'css' / 'responsive.css'
        with open(responsive_css_file, 'w', encoding='utf-8') as f:
            f.write(responsive_css)
        css_files.append('css/responsive.css')
        
        return css_files
    
    async def _generate_main_css(self, website_data: Dict[str, Any]) -> str:
        """Generate main CSS with custom branding"""
        design = website_data.get('design_system', {})
        colors = design.get('color_palette', {})
        typography = design.get('typography', {})
        
        # Default colors if not provided
        primary_color = colors.get('primary', '#2c3e50')
        secondary_color = colors.get('secondary', '#3498db')
        accent_color = colors.get('accent', '#e74c3c')
        neutral_color = colors.get('neutral', '#ecf0f1')
        text_primary = colors.get('text_primary', '#2c3e50')
        text_secondary = colors.get('text_secondary', '#7f8c8d')
        
        # Default fonts
        headings_font = typography.get('headings_font', 'Georgia, serif')
        body_font = typography.get('body_font', 'Arial, sans-serif')
        
        css = f"""
/* CSS Variables for theming */
:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    --accent-color: {accent_color};
    --neutral-color: {neutral_color};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --headings-font: {headings_font};
    --body-font: {body_font};
    --border-radius: {design.get('border_radius', '8px')};
    --shadow-light: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-medium: 0 4px 8px rgba(0,0,0,0.15);
    --shadow-heavy: 0 8px 16px rgba(0,0,0,0.2);
    --transition: all 0.3s ease;
}}

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    font-size: 16px;
    scroll-behavior: smooth;
}}

body {{
    font-family: var(--body-font);
    line-height: 1.6;
    color: var(--text-primary);
    background-color: #ffffff;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--headings-font);
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
}}

h1 {{ font-size: 2.5rem; }}
h2 {{ font-size: 2rem; }}
h3 {{ font-size: 1.5rem; }}
h4 {{ font-size: 1.25rem; }}
h5 {{ font-size: 1.125rem; }}
h6 {{ font-size: 1rem; }}

p {{
    margin-bottom: 1rem;
    color: var(--text-secondary);
}}

a {{
    color: var(--primary-color);
    text-decoration: none;
    transition: var(--transition);
}}

a:hover {{
    color: var(--accent-color);
}}

/* Layout */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}}

.section-header {{
    text-align: center;
    margin-bottom: 3rem;
}}

.section-header h2 {{
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}}

.section-header p {{
    font-size: 1.125rem;
    color: var(--text-secondary);
}}

/* Header and Navigation */
.header {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    box-shadow: var(--shadow-light);
}}

.navbar {{
    padding: 1rem 0;
}}

.navbar .container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.nav-brand h1 {{
    color: var(--primary-color);
    font-size: 1.5rem;
    margin: 0;
}}

.nav-menu {{
    display: flex;
    gap: 2rem;
}}

.nav-menu a {{
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
}}

.nav-menu a:hover {{
    background-color: var(--neutral-color);
    color: var(--primary-color);
}}

/* Hero Section */
.hero-section {{
    height: 100vh;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}}

.hero-background {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

.hero-overlay {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
}}

.hero-content {{
    text-align: center;
    color: white;
    max-width: 600px;
    padding: 2rem;
}}

.hero-title {{
    font-size: 3.5rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}

.hero-subtitle {{
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

.hero-actions {{
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}}

/* Buttons */
.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    border: none;
    transition: var(--transition);
    text-decoration: none;
}}

.btn-primary {{
    background-color: var(--primary-color);
    color: white;
}}

.btn-primary:hover {{
    background-color: var(--accent-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
}}

.btn-secondary {{
    background-color: transparent;
    color: white;
    border: 2px solid white;
}}

.btn-secondary:hover {{
    background-color: white;
    color: var(--primary-color);
}}

/* Menu Section */
.menu-section {{
    padding: 5rem 0;
    background-color: #f8f9fa;
}}

.menu-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.menu-item {{
    background: white;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow-light);
    transition: var(--transition);
}}

.menu-item:hover {{
    transform: translateY(-5px);
    box-shadow: var(--shadow-medium);
}}

.menu-item-image {{
    height: 200px;
    overflow: hidden;
}}

.menu-item-image img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: var(--transition);
}}

.menu-item:hover .menu-item-image img {{
    transform: scale(1.05);
}}

.menu-item-content {{
    padding: 1.5rem;
}}

.menu-item-name {{
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}}

.menu-item-description {{
    margin-bottom: 1rem;
    font-size: 0.9rem;
}}

.menu-item-price {{
    font-weight: 700;
    color: var(--accent-color);
    font-size: 1.125rem;
}}

/* About Section */
.about-section {{
    padding: 5rem 0;
}}

.about-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
}}

.about-text h2 {{
    color: var(--primary-color);
    margin-bottom: 1rem;
}}

.about-image img {{
    width: 100%;
    height: 400px;
    object-fit: cover;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-medium);
}}

/* Contact Section */
.contact-section {{
    padding: 5rem 0;
    background-color: #f8f9fa;
}}

.contact-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin-top: 2rem;
}}

.contact-info {{
    display: grid;
    gap: 2rem;
}}

.contact-item h4 {{
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}}

.contact-form {{
    background: white;
    padding: 2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-light);
}}

.form-group {{
    margin-bottom: 1.5rem;
}}

.form-group input,
.form-group textarea {{
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: var(--border-radius);
    font-family: var(--body-font);
    transition: var(--transition);
}}

.form-group input:focus,
.form-group textarea:focus {{
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}}

/* Footer */
.footer {{
    background-color: var(--primary-color);
    color: white;
    padding: 3rem 0 1rem;
}}

.footer-content {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}}

.footer-section h3,
.footer-section h4 {{
    margin-bottom: 1rem;
    color: white;
}}

.footer-section p {{
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0.5rem;
}}

.footer-bottom {{
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding-top: 1rem;
    text-align: center;
}}

.footer-bottom p {{
    color: rgba(255, 255, 255, 0.6);
    margin: 0;
}}

/* Utility Classes */
.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}

.mb-1 {{ margin-bottom: 0.5rem; }}
.mb-2 {{ margin-bottom: 1rem; }}
.mb-3 {{ margin-bottom: 1.5rem; }}
.mb-4 {{ margin-bottom: 2rem; }}

.mt-1 {{ margin-top: 0.5rem; }}
.mt-2 {{ margin-top: 1rem; }}
.mt-3 {{ margin-top: 1.5rem; }}
.mt-4 {{ margin-top: 2rem; }}

/* Loading and Performance */
img {{
    max-width: 100%;
    height: auto;
}}

img[loading="lazy"] {{
    opacity: 0;
    transition: opacity 0.3s;
}}

img[loading="lazy"].loaded {{
    opacity: 1;
}}

/* Accessibility */
.sr-only {{
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}}

/* Focus styles for accessibility */
a:focus,
button:focus,
input:focus,
textarea:focus {{
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}}

/* Print styles */
@media print {{
    .header,
    .footer {{
        display: none;
    }}
    
    .hero-section {{
        height: auto;
        page-break-inside: avoid;
    }}
    
    .menu-item,
    .contact-section {{
        page-break-inside: avoid;
    }}
}}
"""
        
        return css
    
    async def _generate_responsive_css(self, website_data: Dict[str, Any]) -> str:
        """Generate responsive CSS for mobile and tablet devices"""
        css = f"""
/* Responsive Design - Mobile First Approach */

/* Large screens (desktops) */
@media (min-width: {self.breakpoints['large']}) {{
    .container {{
        max-width: 1200px;
    }}
    
    .hero-title {{
        font-size: 4rem;
    }}
    
    .menu-grid {{
        grid-template-columns: repeat(3, 1fr);
    }}
}}

/* Medium screens (tablets) */
@media (max-width: {self.breakpoints['desktop']}) {{
    .hero-title {{
        font-size: 3rem;
    }}
    
    .about-content {{
        grid-template-columns: 1fr;
        gap: 2rem;
    }}
    
    .contact-content {{
        grid-template-columns: 1fr;
        gap: 2rem;
    }}
    
    .menu-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

/* Small screens (mobile) */
@media (max-width: {self.breakpoints['tablet']}) {{
    .container {{
        padding: 0 1rem;
    }}
    
    .navbar .container {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .nav-menu {{
        flex-wrap: wrap;
        justify-content: center;
        gap: 1rem;
    }}
    
    .hero-title {{
        font-size: 2.5rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.125rem;
    }}
    
    .hero-actions {{
        flex-direction: column;
        align-items: center;
    }}
    
    .btn {{
        width: 100%;
        max-width: 300px;
    }}
    
    .menu-grid {{
        grid-template-columns: 1fr;
    }}
    
    .about-content {{
        grid-template-columns: 1fr;
        text-align: center;
    }}
    
    .contact-content {{
        grid-template-columns: 1fr;
    }}
    
    .footer-content {{
        grid-template-columns: 1fr;
        text-align: center;
    }}
    
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.75rem; }}
    h3 {{ font-size: 1.5rem; }}
}}

/* Extra small screens */
@media (max-width: {self.breakpoints['mobile']}) {{
    .hero-section {{
        height: 80vh;
    }}
    
    .hero-title {{
        font-size: 2rem;
    }}
    
    .hero-content {{
        padding: 1rem;
    }}
    
    .section-header h2 {{
        font-size: 1.5rem;
    }}
    
    .menu-item-content {{
        padding: 1rem;
    }}
    
    .contact-form {{
        padding: 1.5rem;
    }}
}}

/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {{
    .btn {{
        min-height: 44px;
        padding: 0.875rem 1.5rem;
    }}
    
    .nav-menu a {{
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .menu-item {{
        cursor: default;
    }}
    
    .menu-item:hover {{
        transform: none;
    }}
}}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {{
    .hero-background {{
        background-image: url('/images/hero/hero-2x.jpg');
    }}
}}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {{
    * {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
    
    .hero-section {{
        scroll-behavior: auto;
    }}
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
    :root {{
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
        --neutral-color: #2c3e50;
    }}
    
    body {{
        background-color: #1a1a1a;
        color: var(--text-primary);
    }}
    
    .header {{
        background: rgba(26, 26, 26, 0.95);
    }}
    
    .menu-section,
    .contact-section {{
        background-color: #2c3e50;
    }}
    
    .menu-item,
    .contact-form {{
        background-color: #34495e;
        color: var(--text-primary);
    }}
    
    .form-group input,
    .form-group textarea {{
        background-color: #2c3e50;
        color: var(--text-primary);
        border-color: #4a5568;
    }}
}}
"""
        
        return css
    
    async def _generate_js_files(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Generate JavaScript files for interactivity and performance"""
        js_files = []
        
        # Generate main JavaScript file
        main_js = await self._generate_main_js(website_data)
        main_js_file = site_dir / 'js' / 'main.js'
        with open(main_js_file, 'w', encoding='utf-8') as f:
            f.write(main_js)
        js_files.append('js/main.js')
        
        # Generate performance JavaScript file
        performance_js = await self._generate_performance_js(website_data)
        performance_js_file = site_dir / 'js' / 'performance.js'
        with open(performance_js_file, 'w', encoding='utf-8') as f:
            f.write(performance_js)
        js_files.append('js/performance.js')
        
        return js_files
    
    async def _generate_main_js(self, website_data: Dict[str, Any]) -> str:
        """Generate main JavaScript for site functionality"""
        js = """
// Main JavaScript for Restaurant Website
(function() {
    'use strict';
    
    // DOM Content Loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeNavigation();
        initializeSmoothScrolling();
        initializeFormHandling();
        initializeLazyLoading();
        initializeAnimations();
    });
    
    // Navigation functionality
    function initializeNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.nav-menu a');
        
        // Add scroll effect to navbar
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
        
        // Active link highlighting
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
        
        // Update active link on scroll
        window.addEventListener('scroll', updateActiveLink);
    }
    
    function updateActiveLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-menu a');
        
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }
    
    // Smooth scrolling for all anchor links
    function initializeSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // Form handling
    function initializeFormHandling() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });
    }
    
    function handleFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual endpoint)
        setTimeout(() => {
            showNotification('Thank you! Your message has been sent.', 'success');
            form.reset();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 2000);
    }
    
    // Lazy loading for images
    function initializeLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            const images = document.querySelectorAll('img[loading="lazy"]');
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    // Scroll animations
    function initializeAnimations() {
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });
            
            const animatedElements = document.querySelectorAll('.menu-item, .about-content, .contact-content');
            animatedElements.forEach(el => {
                el.classList.add('animate-on-scroll');
                animationObserver.observe(el);
            });
        }
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '9999',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
    
    // Menu item interactions
    document.addEventListener('click', function(e) {
        if (e.target.closest('.menu-item')) {
            const menuItem = e.target.closest('.menu-item');
            const itemName = menuItem.querySelector('.menu-item-name').textContent;
            console.log('Menu item clicked:', itemName);
            // Add analytics tracking here
        }
    });
    
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
    
    // Performance monitoring
    window.addEventListener('load', function() {
        // Log performance metrics
        if ('performance' in window) {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }
    });
    
})();
"""
        return js
    
    async def _generate_performance_js(self, website_data: Dict[str, Any]) -> str:
        """Generate performance optimization JavaScript"""
        js = """
// Performance Optimization Script
(function() {
    'use strict';
    
    // Critical CSS loading
    function loadCSS(href) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.media = 'print';
        link.onload = function() {
            this.media = 'all';
        };
        document.head.appendChild(link);
    }
    
    // Preload critical resources
    function preloadResources() {
        const criticalImages = [
            '/images/hero/hero.jpg',
            '/images/logo.png'
        ];
        
        criticalImages.forEach(src => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = src;
            document.head.appendChild(link);
        });
    }
    
    // Image optimization
    function optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            // Add loading attribute if not present
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // Add error handling
            img.addEventListener('error', function() {
                this.src = '/images/placeholder.jpg';
            });
        });
    }
    
    // Service Worker registration
    function registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                        console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
    }
    
    // Web Vitals monitoring
    function monitorWebVitals() {
        // Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'largest-contentful-paint') {
                        console.log('LCP:', entry.startTime);
                    }
                }
            });
            observer.observe({entryTypes: ['largest-contentful-paint']});
        }
        
        // First Input Delay
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'first-input') {
                        console.log('FID:', entry.processingStart - entry.startTime);
                    }
                }
            });
            observer.observe({entryTypes: ['first-input']});
        }
    }
    
    // Initialize performance optimizations
    document.addEventListener('DOMContentLoaded', function() {
        preloadResources();
        optimizeImages();
        monitorWebVitals();
        registerServiceWorker();
    });
    
    // Intersection Observer polyfill fallback
    if (!('IntersectionObserver' in window)) {
        const script = document.createElement('script');
        script.src = 'https://polyfill.io/v3/polyfill.min.js?features=IntersectionObserver';
        document.head.appendChild(script);
    }
    
})();
"""
        return js
    
    async def _process_assets(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Process and optimize website assets (images, fonts, etc.)"""
        asset_files = []
        
        try:
            # Process hero image
            hero_image = website_data.get('hero_image')
            if hero_image:
                processed_hero = await self._process_image(hero_image, 'hero', site_dir)
                if processed_hero:
                    asset_files.extend(processed_hero)
            
            # Process menu item images
            menu_items = website_data.get('menu_items', [])
            for item in menu_items:
                if item.get('image'):
                    processed_menu = await self._process_image(item['image'], 'menu_item', site_dir)
                    if processed_menu:
                        asset_files.extend(processed_menu)
            
            # Create placeholder images if needed
            await self._create_placeholder_images(site_dir)
            asset_files.extend(['images/placeholder.jpg', 'images/hero/default.jpg'])
            
            # Copy default favicon and icons
            await self._create_default_icons(site_dir)
            asset_files.extend(['images/icons/favicon.ico', 'images/icons/apple-touch-icon.png'])
            
        except Exception as e:
            logger.error(f"Asset processing failed: {str(e)}")
        
        return asset_files
    
    async def _process_image(self, image_url: str, image_type: str, site_dir: Path) -> List[str]:
        """Process and optimize a single image"""
        try:
            # For now, we'll create placeholder logic
            # In a real implementation, you'd download and process the actual image
            processed_files = []
            
            sizes = self.image_sizes.get(image_type, [(800, 600)])
            for width, height in sizes:
                filename = f"{image_type}_{width}x{height}.jpg"
                filepath = site_dir / 'images' / image_type / filename
                
                # Create a placeholder image
                img = Image.new('RGB', (width, height), color='#f0f0f0')
                filepath.parent.mkdir(parents=True, exist_ok=True)
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                processed_files.append(f"images/{image_type}/{filename}")
            
            return processed_files
            
        except Exception as e:
            logger.error(f"Image processing failed for {image_url}: {str(e)}")
            return []
    
    async def _create_placeholder_images(self, site_dir: Path):
        """Create placeholder images for missing assets"""
        placeholders = [
            ('placeholder.jpg', (800, 600), '#e9ecef'),
            ('hero/default.jpg', (1920, 1080), '#6c757d'),
            ('menu/default.jpg', (400, 300), '#adb5bd'),
            ('gallery/default.jpg', (600, 400), '#ced4da')
        ]
        
        for filename, size, color in placeholders:
            filepath = site_dir / 'images' / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            img = Image.new('RGB', size, color=color)
            img.save(filepath, 'JPEG', quality=85)
    
    async def _create_default_icons(self, site_dir: Path):
        """Create default favicon and app icons"""
        icons_dir = site_dir / 'images' / 'icons'
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Create favicon
        favicon = Image.new('RGB', (32, 32), color='#2c3e50')
        favicon.save(icons_dir / 'favicon.ico', 'ICO')
        
        # Create apple touch icon
        apple_icon = Image.new('RGB', (180, 180), color='#2c3e50')
        apple_icon.save(icons_dir / 'apple-touch-icon.png', 'PNG')
        
        # Create various PWA icons
        icon_sizes = [192, 512]
        for size in icon_sizes:
            icon = Image.new('RGB', (size, size), color='#2c3e50')
            icon.save(icons_dir / f'icon-{size}x{size}.png', 'PNG')
    
    async def _generate_seo_files(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Generate SEO-related files (robots.txt, sitemap.xml)"""
        seo_files = []
        
        # Generate robots.txt
        robots_content = await self._generate_robots_txt(website_data)
        robots_file = site_dir / 'robots.txt'
        with open(robots_file, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        seo_files.append('robots.txt')
        
        # Generate sitemap.xml
        sitemap_content = await self._generate_sitemap_xml(website_data)
        sitemap_file = site_dir / 'sitemap.xml'
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        seo_files.append('sitemap.xml')
        
        return seo_files
    
    async def _generate_robots_txt(self, website_data: Dict[str, Any]) -> str:
        """Generate robots.txt content"""
        seo_settings = website_data.get('seo_settings', {})
        custom_robots = seo_settings.get('robots_txt')
        
        if custom_robots:
            return custom_robots
        
        base_url = website_data.get('live_url', '')
        
        return f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Disallow admin and private areas
Disallow: /admin/
Disallow: /private/
Disallow: /*.json$

# Allow search engines to crawl images
Allow: /images/
"""
    
    async def _generate_sitemap_xml(self, website_data: Dict[str, Any]) -> str:
        """Generate sitemap.xml content"""
        base_url = website_data.get('live_url', '')
        pages = website_data.get('pages', [])
        
        sitemap_urls = []
        
        # Add homepage
        sitemap_urls.append({
            'loc': base_url,
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '1.0'
        })
        
        # Add other pages
        for page in pages:
            if not page.get('is_homepage', False) and page.get('published', True):
                slug = page.get('page_slug', '').strip('/')
                if slug:
                    sitemap_urls.append({
                        'loc': f"{base_url}/{slug}",
                        'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
                        'changefreq': 'monthly',
                        'priority': '0.8'
                    })
        
        # Generate XML
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in sitemap_urls:
            xml_content += '  <url>\n'
            xml_content += f'    <loc>{url["loc"]}</loc>\n'
            xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
            xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
            xml_content += f'    <priority>{url["priority"]}</priority>\n'
            xml_content += '  </url>\n'
        
        xml_content += '</urlset>'
        
        return xml_content
    
    async def _generate_pwa_files(self, website_data: Dict[str, Any], site_dir: Path) -> List[str]:
        """Generate Progressive Web App files"""
        pwa_files = []
        
        # Generate manifest.json
        manifest_content = await self._generate_manifest_json(website_data)
        manifest_file = site_dir / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(manifest_content, indent=2))
        pwa_files.append('manifest.json')
        
        # Generate service worker
        sw_content = await self._generate_service_worker(website_data)
        sw_file = site_dir / 'sw.js'
        with open(sw_file, 'w', encoding='utf-8') as f:
            f.write(sw_content)
        pwa_files.append('sw.js')
        
        return pwa_files
    
    async def _generate_manifest_json(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PWA manifest.json"""
        seo_settings = website_data.get('seo_settings', {})
        design_system = website_data.get('design_system', {})
        colors = design_system.get('color_palette', {})
        
        return {
            "name": website_data.get('website_name', 'Restaurant'),
            "short_name": website_data.get('website_name', 'Restaurant')[:12],
            "description": seo_settings.get('site_description', 'A great restaurant experience'),
            "start_url": "/",
            "display": "standalone",
            "background_color": colors.get('neutral', '#ffffff'),
            "theme_color": colors.get('primary', '#2c3e50'),
            "icons": [
                {
                    "src": "/images/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/images/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "categories": ["food", "restaurant", "dining"],
            "lang": "en",
            "dir": "ltr",
            "orientation": "portrait-primary"
        }
    
    async def _generate_service_worker(self, website_data: Dict[str, Any]) -> str:
        """Generate service worker for PWA functionality"""
        return """
// Service Worker for Restaurant Website
const CACHE_NAME = 'restaurant-v1';
const urlsToCache = [
    '/',
    '/css/main.css',
    '/css/responsive.css',
    '/js/main.js',
    '/js/performance.js',
    '/images/icons/icon-192x192.png',
    '/images/icons/icon-512x512.png',
    '/manifest.json'
];

// Install event
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            }
        )
    );
});

// Activate event
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
"""