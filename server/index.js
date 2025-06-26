const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const facebookAdsRoutes = require('./routes/facebook-ads');
const smsCampaignsRoutes = require('./routes/sms-campaigns');
const checklistRoutes = require('./routes/checklist');

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

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📱 Momentum Growth Starter API ready!`);
});