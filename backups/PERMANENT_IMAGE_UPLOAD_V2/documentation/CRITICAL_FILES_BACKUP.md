# CRITICAL FILES BACKUP & PRESERVATION GUIDE

## 🚨 CRITICAL FILES - DO NOT DELETE

### **Image Upload System V2 - Core Files**
```
backendv2/app/routes/media_upload_v2.py     # NEW V2 BACKEND ROUTES
client/src/services/websiteBuilderAPI.js    # FRONTEND API WITH V2 METHODS
backendv2/test_image_upload_v2.py          # V2 TESTING SCRIPT
test_image_upload_frontend.html             # STANDALONE TEST INTERFACE
```

### **Documentation & Fixes**
```
fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md  # FRONTEND FIX GUIDE
SYSTEM_DEPENDENCIES_REFERENCE.md                # COMPLETE SYSTEM DOCS
validate-frontend.sh                             # ENVIRONMENT VALIDATION
```

### **Configuration Files**
```
backendv2/requirements.txt                  # PYTHON DEPENDENCIES
client/package.json                         # NODE.JS DEPENDENCIES
backendv2/app/main.py                      # FASTAPI APP WITH V2 ROUTES
```

---

## 🛡️ PROTECTION MEASURES

### **1. Git Protection**
Add to `.gitignore` to ensure these are NEVER ignored:
```
# CRITICAL FILES - NEVER IGNORE
!backendv2/app/routes/media_upload_v2.py
!client/src/services/websiteBuilderAPI.js
!fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md
!SYSTEM_DEPENDENCIES_REFERENCE.md
!validate-frontend.sh
!CRITICAL_FILES_BACKUP.md
```

### **2. Multiple Backup Locations**
Create backups in different directories:
```bash
# Create backup directory
mkdir -p backups/image-upload-v2-system/

# Copy critical files
cp backendv2/app/routes/media_upload_v2.py backups/image-upload-v2-system/
cp client/src/services/websiteBuilderAPI.js backups/image-upload-v2-system/
cp fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md backups/image-upload-v2-system/
cp SYSTEM_DEPENDENCIES_REFERENCE.md backups/image-upload-v2-system/
cp validate-frontend.sh backups/image-upload-v2-system/
```

### **3. File Checksums for Integrity**
```bash
# Generate checksums to detect changes
md5 backendv2/app/routes/media_upload_v2.py > backups/checksums.txt
md5 client/src/services/websiteBuilderAPI.js >> backups/checksums.txt
md5 fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md >> backups/checksums.txt
md5 SYSTEM_DEPENDENCIES_REFERENCE.md >> backups/checksums.txt
```

---

## 📋 RECOVERY PROCEDURES

### **If Files Are Accidentally Deleted**

#### **1. Check Git History**
```bash
git log --oneline --follow <filename>
git checkout <commit-hash> -- <filename>
```

#### **2. Restore from Backups**
```bash
cp backups/image-upload-v2-system/<filename> <original-location>
```

#### **3. Recreate from Documentation**
All critical code is documented in this guide with exact content.

---

## 🔒 PERMANENT PRESERVATION

### **Critical Code Snippets Preserved Here**

#### **Backend V2 Upload Endpoint (Key Function)**
```python
@router.post("/upload-image-v2")
async def upload_image_v2(
    file: UploadFile = File(...),
    image_type: str = Form("general")
):
    # Generate unique filename
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}_{image_type}.{file_ext}"
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    contents = await file.read()
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    return {
        "message": "File uploaded successfully", 
        "filename": unique_filename, 
        "image_url": f"/api/website-builder/images-v2/{unique_filename}"
    }
```

#### **Frontend V2 Upload Method (Key Function)**
```javascript
uploadImageV2: async (file, imageType = 'general', onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('image_type', imageType);

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
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
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`Upload failed: ${xhr.statusText}`));
            }
        });

        xhr.open('POST', `${API_BASE_URL}/website-builder/upload-image-v2`);
        xhr.send(formData);
    });
}
```

#### **Main.py Router Registration**
```python
from .routes.media_upload_v2 import router as media_router_v2
app.include_router(media_router_v2)
```

---

## 🚨 EMERGENCY CONTACT INFO

### **If System Breaks**
1. **Check**: [`fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md`](fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md)
2. **Run**: `./validate-frontend.sh`
3. **Reference**: [`SYSTEM_DEPENDENCIES_REFERENCE.md`](SYSTEM_DEPENDENCIES_REFERENCE.md)
4. **Test**: `python3 backendv2/test_image_upload_v2.py`

### **Quick Recovery Commands**
```bash
# Backend
cd backendv2 && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (if broken)
cd client && rm -rf node_modules package-lock.json && npm install && npm start

# Validation
./validate-frontend.sh
```

---

## 📅 MAINTENANCE SCHEDULE

### **Weekly**
- [ ] Verify both servers start successfully
- [ ] Run image upload tests
- [ ] Check for security updates

### **Monthly**
- [ ] Update non-breaking dependencies
- [ ] Refresh backups
- [ ] Validate all documentation

### **Before Major Changes**
- [ ] Create additional backups
- [ ] Test all critical functionality
- [ ] Update documentation if needed

---

**⚠️ WARNING: These files contain the complete working image upload system V2. Loss of these files would require complete reimplementation. Keep multiple backups and never delete without verification.**