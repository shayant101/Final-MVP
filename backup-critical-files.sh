#!/bin/bash
# Critical Files Backup Script
# Run this to create backups of all important files

echo "🛡️ Creating backups of critical files..."

# Create timestamp for backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/backup_$TIMESTAMP"

# Create backup directories
mkdir -p "$BACKUP_DIR/backend"
mkdir -p "$BACKUP_DIR/frontend" 
mkdir -p "$BACKUP_DIR/documentation"
mkdir -p "$BACKUP_DIR/scripts"

# Backup Backend Files
echo "📁 Backing up backend files..."
cp backendv2/app/routes/media_upload_v2.py "$BACKUP_DIR/backend/"
cp backendv2/app/main.py "$BACKUP_DIR/backend/"
cp backendv2/requirements.txt "$BACKUP_DIR/backend/"
cp backendv2/test_image_upload_v2.py "$BACKUP_DIR/backend/"

# Backup Frontend Files
echo "📁 Backing up frontend files..."
cp client/src/services/websiteBuilderAPI.js "$BACKUP_DIR/frontend/"
cp client/package.json "$BACKUP_DIR/frontend/"
cp client/src/index.js "$BACKUP_DIR/frontend/"
cp client/src/contexts/ThemeContext.js "$BACKUP_DIR/frontend/"

# Backup Documentation
echo "📁 Backing up documentation..."
cp fixes/REACT_FRONTEND_DEPENDENCY_FIX_SUMMARY.md "$BACKUP_DIR/documentation/"
cp SYSTEM_DEPENDENCIES_REFERENCE.md "$BACKUP_DIR/documentation/"
cp CRITICAL_FILES_BACKUP.md "$BACKUP_DIR/documentation/"

# Backup Scripts
echo "📁 Backing up scripts..."
cp validate-frontend.sh "$BACKUP_DIR/scripts/"
cp backup-critical-files.sh "$BACKUP_DIR/scripts/"
cp test_image_upload_frontend.html "$BACKUP_DIR/scripts/"

# Create checksums
echo "🔐 Creating checksums..."
find "$BACKUP_DIR" -type f -exec md5 {} \; > "$BACKUP_DIR/checksums.txt"

# Create backup manifest
echo "📋 Creating backup manifest..."
cat > "$BACKUP_DIR/BACKUP_MANIFEST.md" << EOF
# Backup Manifest - $TIMESTAMP

## Files Backed Up
- Backend: media_upload_v2.py, main.py, requirements.txt, test_image_upload_v2.py
- Frontend: websiteBuilderAPI.js, package.json, index.js, ThemeContext.js
- Documentation: All fix summaries and system references
- Scripts: All validation and backup scripts

## Restore Instructions
1. Copy files back to original locations
2. Run ./validate-frontend.sh
3. Test with python3 backendv2/test_image_upload_v2.py
4. Verify both servers start successfully

## Backup Created: $(date)
## System Status: Both backend and frontend operational
EOF

echo "✅ Backup completed: $BACKUP_DIR"
echo "📋 Manifest created: $BACKUP_DIR/BACKUP_MANIFEST.md"
echo "🔐 Checksums saved: $BACKUP_DIR/checksums.txt"

# Also create a permanent backup in a fixed location
PERMANENT_BACKUP="backups/PERMANENT_IMAGE_UPLOAD_V2"
mkdir -p "$PERMANENT_BACKUP"
cp -r "$BACKUP_DIR"/* "$PERMANENT_BACKUP/"
echo "🏛️ Permanent backup updated: $PERMANENT_BACKUP"