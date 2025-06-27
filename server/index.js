const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const facebookAdsRoutes = require('./routes/facebook-ads');
const smsCampaignsRoutes = require('./routes/sms-campaigns');
const checklistRoutes = require('./routes/checklist');
const authRoutes = require('./routes/auth');
const dashboardRoutes = require('./routes/dashboard');
const { initializeDatabase, createDefaultAdmin } = require('./models/database');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// Create uploads directory if it doesn't exist
const fs = require('fs');
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/facebook-ads', facebookAdsRoutes);
app.use('/api/sms-campaigns', smsCampaignsRoutes);
app.use('/api/checklist', checklistRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Initialize database and start server
const startServer = async () => {
  try {
    // Initialize database tables
    await initializeDatabase();
    console.log('✅ Database initialized successfully');
    
    // Create default admin user
    await createDefaultAdmin();
    console.log('✅ Default admin user setup complete');
    
    // Start the server
    app.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
      console.log(`📱 Momentum Growth Starter API ready!`);
      console.log(`🔐 Authentication endpoints available at /api/auth`);
      console.log(`📊 Dashboard endpoints available at /api/dashboard`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

startServer();