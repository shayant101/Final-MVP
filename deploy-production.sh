#!/bin/bash

# Production Deployment Script for Final-MVP
# This script helps automate the production deployment process

set -e  # Exit on any error

echo "🚀 Final-MVP Production Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    print_success "All dependencies are installed!"
}

# Validate environment variables
validate_env() {
    print_status "Validating environment configuration..."
    
    if [ ! -f "backendv2/.env.production" ]; then
        print_warning ".env.production file not found!"
        print_status "Creating .env.production from example..."
        cp backendv2/.env.production.example backendv2/.env.production
        print_warning "Please edit backendv2/.env.production with your actual values before continuing."
        read -p "Press Enter after you've configured the environment variables..."
    fi
    
    # Check if critical variables are set
    source backendv2/.env.production
    
    if [ -z "$MONGODB_URL" ] || [ "$MONGODB_URL" = "mongodb+srv://username:password@cluster.mongodb.net/momentum_growth_prod?retryWrites=true&w=majority" ]; then
        print_error "MONGODB_URL is not configured in .env.production"
        exit 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
        print_error "OPENAI_API_KEY is not configured in .env.production"
        exit 1
    fi
    
    if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "your-super-secure-jwt-secret-key-here-minimum-32-characters" ]; then
        print_error "JWT_SECRET is not configured in .env.production"
        exit 1
    fi
    
    print_success "Environment variables validated!"
}

# Build and test the application
build_and_test() {
    print_status "Building and testing the application..."
    
    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backendv2
    pip install -r requirements.txt
    cd ..
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd client
    npm install
    
    # Build frontend
    print_status "Building frontend..."
    npm run build
    cd ..
    
    # Run basic tests
    print_status "Running basic health checks..."
    cd backendv2
    python -c "
import sys
sys.path.append('.')
from app.main import app
print('✅ Backend imports successfully')
"
    cd ..
    
    print_success "Build and tests completed!"
}

# Deploy to Render (Backend)
deploy_backend() {
    print_status "Preparing backend deployment to Render..."
    
    # Check if render.yaml exists
    if [ ! -f "render.yaml" ]; then
        print_error "render.yaml not found! Please ensure the file exists."
        exit 1
    fi
    
    print_status "Backend deployment configuration:"
    echo "  - Service: final-mvp-backend"
    echo "  - Plan: starter ($7/month) - upgrade to standard ($25) for production"
    echo "  - Health check: /api/health"
    echo "  - Auto-deploy: enabled"
    
    print_warning "Manual steps required for Render:"
    echo "1. Go to https://render.com and create an account"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Use the render.yaml configuration"
    echo "5. Set environment variables in Render dashboard:"
    echo "   - MONGODB_URL"
    echo "   - OPENAI_API_KEY"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo "   - JWT_SECRET"
    
    read -p "Press Enter after you've set up Render backend deployment..."
    print_success "Backend deployment configured!"
}

# Deploy to Vercel (Frontend)
deploy_frontend() {
    print_status "Preparing frontend deployment to Vercel..."
    
    # Check if vercel.json exists
    if [ ! -f "vercel.json" ]; then
        print_error "vercel.json not found! Please ensure the file exists."
        exit 1
    fi
    
    print_status "Frontend deployment configuration:"
    echo "  - Platform: Vercel"
    echo "  - Plan: Hobby (free) or Pro ($20/month)"
    echo "  - Build: React static build"
    echo "  - CDN: Global edge network"
    
    print_warning "Manual steps required for Vercel:"
    echo "1. Go to https://vercel.com and create an account"
    echo "2. Connect your GitHub repository"
    echo "3. Import the project"
    echo "4. Set root directory to 'client'"
    echo "5. Configure environment variables:"
    echo "   - REACT_APP_API_URL=https://your-render-app.onrender.com"
    echo "6. Deploy!"
    
    read -p "Press Enter after you've set up Vercel frontend deployment..."
    print_success "Frontend deployment configured!"
}

# Setup MongoDB Atlas
setup_database() {
    print_status "Database setup instructions..."
    
    print_warning "Manual steps required for MongoDB Atlas:"
    echo "1. Go to https://cloud.mongodb.com and create an account"
    echo "2. Create a new cluster (M2 Shared - $9/month recommended)"
    echo "3. Create a database user"
    echo "4. Configure IP whitelist (add 0.0.0.0/0 for Render)"
    echo "5. Get connection string and update MONGODB_URL in environment"
    echo "6. Create database: momentum_growth_prod"
    
    read -p "Press Enter after you've set up MongoDB Atlas..."
    print_success "Database setup instructions provided!"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring and alerts..."
    
    print_warning "Recommended monitoring setup:"
    echo "1. Sentry for error tracking:"
    echo "   - Go to https://sentry.io"
    echo "   - Create account and project"
    echo "   - Add SENTRY_DSN to environment variables"
    echo ""
    echo "2. Set up cost alerts:"
    echo "   - OpenAI: Set billing alerts at $50, $100, $150"
    echo "   - Twilio: Set usage alerts at $25, $50, $75"
    echo "   - MongoDB: Set up usage alerts"
    echo "   - Render: Monitor resource usage"
    echo ""
    echo "3. Health monitoring:"
    echo "   - Use Render's built-in monitoring"
    echo "   - Set up Vercel analytics"
    echo "   - Configure uptime monitoring"
    
    read -p "Press Enter to continue..."
    print_success "Monitoring setup instructions provided!"
}

# Generate deployment summary
generate_summary() {
    print_status "Generating deployment summary..."
    
    cat > DEPLOYMENT_SUMMARY.md << EOF
# Production Deployment Summary
Generated on: $(date)

## 🚀 Deployment Status

### Infrastructure
- **Frontend**: Vercel (https://your-domain.vercel.app)
- **Backend**: Render (https://final-mvp-backend.onrender.com)
- **Database**: MongoDB Atlas
- **CDN**: Vercel Edge Network

### Estimated Monthly Costs
- **Vercel**: \$0-20 (Hobby/Pro plan)
- **Render**: \$25-85 (Standard/Pro plan)
- **MongoDB**: \$9-57 (M2-M10 plan)
- **OpenAI**: \$50-150 (usage-based)
- **Twilio**: \$20-75 (usage-based)
- **Total**: \$104-387/month

### Next Steps
1. ✅ Configure custom domain
2. ✅ Set up SSL certificates (automatic)
3. ✅ Configure monitoring alerts
4. ✅ Test all functionality
5. ✅ Set up backup procedures
6. ✅ Document support procedures

### Important URLs
- **Frontend**: https://your-domain.com
- **Backend API**: https://final-mvp-backend.onrender.com
- **API Health**: https://final-mvp-backend.onrender.com/api/health
- **API Docs**: https://final-mvp-backend.onrender.com/docs

### Support Contacts
- **Primary**: your-email@domain.com
- **Render Support**: help@render.com
- **Vercel Support**: support@vercel.com
- **MongoDB Support**: support@mongodb.com

### Security Checklist
- [ ] Environment variables secured
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error handling configured

### Monitoring Checklist
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Cost alerts configured
- [ ] Uptime monitoring
- [ ] Backup verification
- [ ] Security scanning

EOF

    print_success "Deployment summary generated: DEPLOYMENT_SUMMARY.md"
}

# Main deployment flow
main() {
    echo ""
    print_status "Starting production deployment process..."
    echo ""
    
    # Step 1: Check dependencies
    check_dependencies
    echo ""
    
    # Step 2: Validate environment
    validate_env
    echo ""
    
    # Step 3: Build and test
    build_and_test
    echo ""
    
    # Step 4: Setup database
    setup_database
    echo ""
    
    # Step 5: Deploy backend
    deploy_backend
    echo ""
    
    # Step 6: Deploy frontend
    deploy_frontend
    echo ""
    
    # Step 7: Setup monitoring
    setup_monitoring
    echo ""
    
    # Step 8: Generate summary
    generate_summary
    echo ""
    
    print_success "🎉 Production deployment process completed!"
    print_status "Please review DEPLOYMENT_SUMMARY.md for next steps."
    print_warning "Remember to:"
    echo "  1. Test all functionality in production"
    echo "  2. Set up monitoring alerts"
    echo "  3. Configure backup procedures"
    echo "  4. Update DNS records for custom domain"
    echo "  5. Notify stakeholders of go-live"
}

# Run main function
main "$@"