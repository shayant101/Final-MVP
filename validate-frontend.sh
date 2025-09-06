#!/bin/bash
# Frontend Environment Validation Script
# Run this before starting development to ensure clean environment

echo "🔍 Validating Frontend Environment..."

cd client

# Check if node_modules exists and has React
if [ ! -d "node_modules/react" ]; then
    echo "❌ React not found in node_modules"
    echo "🔧 Running: npm install"
    npm install
fi

# Check if react-scripts exists
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo "❌ react-scripts not found"
    echo "🔧 Running: npm install react-scripts --save"
    npm install react-scripts --save
fi

# Check port availability
if lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠️  Port 3000 is in use:"
    lsof -i :3000
    echo "💡 Kill the process with: kill <PID>"
    echo "💡 Or choose a different port when prompted"
else
    echo "✅ Port 3000 is available"
fi

# Check for mixed package managers
if [ -f "yarn.lock" ] && [ -f "package-lock.json" ]; then
    echo "⚠️  Both yarn.lock and package-lock.json found"
    echo "💡 Remove one to avoid conflicts:"
    echo "   rm yarn.lock  # If using npm"
    echo "   rm package-lock.json  # If using yarn"
fi

# Validate React installation
if node -e "require('react')" 2>/dev/null; then
    echo "✅ React is properly installed"
else
    echo "❌ React installation is corrupted"
    echo "🔧 Fixing with clean install..."
    rm -rf node_modules package-lock.json yarn.lock
    npm install
fi

echo "✅ Frontend environment validation complete"
echo "🚀 Ready to run: npm start"