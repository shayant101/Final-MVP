# System Dependencies Reference Guide

## 🚀 Project Overview
**Restaurant Marketing Platform - Final MVP**
- **Backend**: FastAPI (Python)
- **Frontend**: React (JavaScript/TypeScript)
- **Database**: MongoDB
- **Image Upload**: V2 System (Robust)

---

## 🐍 BACKEND DEPENDENCIES (Python/FastAPI)

### **Core Framework**
- **FastAPI**: `0.103.2` - Modern, fast web framework for building APIs
- **Uvicorn**: `0.22.0` - ASGI server for FastAPI
- **Python-multipart**: `0.0.6` - File upload handling

### **Database & Storage**
- **Motor**: `3.3.2` - Async MongoDB driver for Python
- **PyMongo**: `4.5.0` - MongoDB driver for Python
- **MongoDB**: External service (Atlas/Local)

### **Authentication & Security**
- **Python-jose[cryptography]**: `3.3.0` - JWT token handling
- **Passlib[bcrypt]**: `1.7.4` - Password hashing
- **Email-validator**: `2.1.1` - Email validation

### **External Services Integration**
- **OpenAI**: `>=1.0.0` - AI content generation
- **Twilio**: `9.6.3` - SMS/messaging service
- **Stripe**: `7.8.0` - Payment processing

### **Web Scraping & Data Processing**
- **BeautifulSoup4**: `4.12.2` - HTML parsing
- **Requests**: `2.31.0` - HTTP requests
- **Selenium**: `>=4.15.0` - Web automation
- **LXML**: `>=4.9.3` - XML/HTML processing
- **Webdriver-manager**: `4.0.1` - Browser driver management

### **Image Processing**
- **Pillow**: `>=10.0.0` - Image manipulation and processing

### **Utilities**
- **Python-dotenv**: `0.21.1` - Environment variable management
- **HTTPx**: `0.24.1` - Async HTTP client
- **Jinja2**: `>=3.1.0` - Template engine

### **Backend File Structure**
```
backendv2/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # MongoDB connection and setup
│   ├── auth.py                 # Authentication middleware
│   ├── models.py               # Database models
│   ├── core/
│   │   └── config.py           # Configuration management
│   ├── routes/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── dashboard.py        # Dashboard endpoints
│   │   ├── website_builder.py  # Website builder endpoints
│   │   ├── media_upload.py     # Original image upload (legacy)
│   │   └── media_upload_v2.py  # New robust image upload system
│   ├── services/
│   │   ├── openai_service.py   # OpenAI integration
│   │   ├── twilio_service.py   # SMS service
│   │   └── email_service.py    # Email service
│   └── utils/
├── requirements.txt            # Python dependencies
└── uploads/images/             # Image storage directory
```

---

## ⚛️ FRONTEND DEPENDENCIES (React/Node.js)

### **Core Framework**
- **React**: `^18.2.0` - UI library
- **React-DOM**: `^18.2.0` - DOM rendering for React
- **React-Scripts**: `^5.0.1` - Build tools and development server

### **Routing & Navigation**
- **React-Router-DOM**: `^6.30.1` - Client-side routing

### **HTTP & API Communication**
- **Axios**: `^1.11.0` - HTTP client for API calls

### **Data Visualization**
- **Chart.js**: `^4.5.0` - Chart library
- **React-Chartjs-2**: `^5.3.0` - React wrapper for Chart.js

### **Testing Framework**
- **@testing-library/jest-dom**: `^5.16.4` - Jest DOM matchers
- **@testing-library/react**: `^13.3.0` - React testing utilities
- **@testing-library/user-event**: `^13.5.0` - User interaction testing

### **Performance & Analytics**
- **Web-vitals**: `^2.1.4` - Core web vitals measurement

### **Development Configuration**
- **Proxy**: `http://localhost:8000` - Backend API proxy
- **ESLint**: React app configuration
- **Browserslist**: Modern browser support

### **Frontend File Structure**
```
client/
├── public/
│   └── index.html              # Main HTML template
├── src/
│   ├── index.js                # Application entry point
│   ├── App.js                  # Main application component
│   ├── index.css               # Global styles
│   ├── components/
│   │   ├── Login.js            # Authentication component
│   │   ├── RestaurantDashboard.js # Main dashboard
│   │   └── WebsiteBuilder/
│   │       ├── WebsiteBuilder.js    # Website builder main
│   │       ├── MediaUploader.js     # Image upload component
│   │       ├── EditableImageElement.js # Image editing
│   │       └── TemplateCustomizer.js # Template customization
│   ├── contexts/
│   │   ├── AuthContext.js      # Authentication state
│   │   └── ThemeContext.js     # Theme management
│   ├── services/
│   │   ├── api.js              # General API service
│   │   └── websiteBuilderAPI.js # Website builder API (includes V2 upload)
│   └── styles/
│       ├── DesignSystem.css    # Design system
│       └── GlobalTheme.css     # Global theme styles
├── package.json                # Node.js dependencies
└── package-lock.json           # Dependency lock file
```

---

## 🔧 DEVELOPMENT ENVIRONMENT

### **System Requirements**
- **Node.js**: v16+ (for React 18)
- **Python**: 3.9+ (for FastAPI)
- **MongoDB**: 4.4+ (Atlas or local)

### **Development Servers**
- **Backend**: `http://localhost:8000` (FastAPI/Uvicorn)
- **Frontend**: `http://localhost:3000` (React Dev Server)

### **Package Managers**
- **Backend**: pip (Python)
- **Frontend**: npm (Node.js) - **Use npm only, avoid yarn mixing**

---

## 📸 IMAGE UPLOAD SYSTEM V2

### **Backend Endpoints**
- **Upload**: `POST /api/website-builder/upload-image-v2`
- **Serve**: `GET /api/website-builder/images-v2/{filename}`

### **Frontend API Methods**
```javascript
// In websiteBuilderAPI.js
uploadImageV2(file, imageType, onProgress)  // Upload with progress
getImageV2(filename)                        // Get image URL
```

### **Supported Image Types**
- `hero` - Hero/banner images
- `menu_item` - Food photos
- `gallery` - Photo galleries  
- `logo` - Brand logos
- `general` - Other images

### **File Specifications**
- **Formats**: JPEG, PNG, WebP, GIF
- **Max Size**: 10MB
- **Storage**: `uploads/images/`
- **Naming**: `{uuid}_{image_type}.{extension}`

---

## 🛠️ DEVELOPMENT COMMANDS

### **Backend Setup**
```bash
cd backendv2
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Frontend Setup**
```bash
cd client
npm install
npm start
```

### **Environment Validation**
```bash
# Run before development
./validate-frontend.sh
```

### **Testing**
```bash
# Backend image upload test
python3 backendv2/test_image_upload_v2.py

# Frontend test interface
open test_image_upload_frontend.html
```

---

## 🚨 TROUBLESHOOTING GUIDE

### **Common Frontend Issues**
1. **React hooks not found**: Clean install with `rm -rf node_modules package-lock.json && npm install`
2. **Port 3000 in use**: Kill process with `lsof -i :3000` then `kill <PID>`
3. **Mixed package managers**: Remove `yarn.lock` if using npm

### **Common Backend Issues**
1. **MongoDB connection**: Check connection string and network access
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Port 8000 in use**: Kill process or use different port

### **Image Upload Issues**
1. **Files not saving**: Check `uploads/images/` directory permissions
2. **Images not serving**: Verify file paths and UPLOAD_DIR configuration
3. **CORS errors**: Check CORS middleware in FastAPI

---

## 📋 VERSION COMPATIBILITY MATRIX

| Component | Version | Compatibility Notes |
|-----------|---------|-------------------|
| Python | 3.9+ | Required for FastAPI and modern libraries |
| Node.js | 16+ | Required for React 18 |
| React | 18.2.0 | Latest stable with concurrent features |
| FastAPI | 0.103.2 | Latest stable with async support |
| MongoDB | 4.4+ | Required for modern query features |
| npm | 8+ | Comes with Node.js 16+ |

---

## 🔄 UPDATE PROCEDURES

### **Backend Updates**
```bash
cd backendv2
pip install --upgrade -r requirements.txt
```

### **Frontend Updates**
```bash
cd client
npm update
npm audit fix  # Fix security vulnerabilities
```

### **Dependency Auditing**
```bash
# Backend security check
pip-audit

# Frontend security check
npm audit
```

---

## 📝 MAINTENANCE NOTES

### **Regular Tasks**
1. **Weekly**: Run `npm audit` and `pip-audit` for security updates
2. **Monthly**: Update non-breaking dependencies
3. **Quarterly**: Review and update major versions

### **Before Major Changes**
1. Run `./validate-frontend.sh`
2. Test image upload system with `python3 backendv2/test_image_upload_v2.py`
3. Verify both servers start successfully
4. Test critical user flows

### **Backup Procedures**
- **Database**: Regular MongoDB backups
- **Images**: Backup `uploads/images/` directory
- **Code**: Git commits before dependency changes

This reference guide should be updated whenever dependencies are modified or new services are added.