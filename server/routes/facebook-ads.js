const express = require('express');
const multer = require('multer');
const path = require('path');
const router = express.Router();

const { generateAdCopy, generatePromoCode } = require('../services/mockOpenAI');
const { createAdCampaign, validateBudget } = require('../services/mockFacebook');

// Configure multer for photo uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'dish-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed (jpeg, jpg, png, gif)'));
    }
  }
});

// POST /api/facebook-ads/create-campaign
router.post('/create-campaign', upload.single('dishPhoto'), async (req, res) => {
  try {
    const { restaurantName, itemToPromote, offer, budget } = req.body;

    // Validate required fields
    if (!restaurantName || !itemToPromote || !offer || !budget) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields',
        required: ['restaurantName', 'itemToPromote', 'offer', 'budget']
      });
    }

    // Validate budget
    const budgetValidation = validateBudget(parseFloat(budget));
    if (!budgetValidation.valid) {
      return res.status(400).json({
        success: false,
        error: budgetValidation.error
      });
    }

    // Generate promo code
    const promoCode = generatePromoCode(itemToPromote);

    // Generate ad copy using mock OpenAI
    const adCopyResult = await generateAdCopy(restaurantName, itemToPromote, offer);
    
    if (!adCopyResult.success) {
      return res.status(500).json({
        success: false,
        error: 'Failed to generate ad copy'
      });
    }

    // Create Facebook ad campaign
    const campaignData = {
      restaurantName,
      itemToPromote,
      offer,
      budget: parseFloat(budget),
      adCopy: adCopyResult.adCopy,
      promoCode,
      dishPhoto: req.file ? req.file.filename : null
    };

    const campaignResult = await createAdCampaign(campaignData);

    if (!campaignResult.success) {
      return res.status(500).json({
        success: false,
        error: 'Failed to create Facebook ad campaign'
      });
    }

    // Return success response
    res.json({
      success: true,
      message: `Your Facebook ad for ${itemToPromote} is now being created! Check your Facebook Ads Manager in a few minutes.`,
      data: {
        promoCode: promoCode,
        campaignId: campaignResult.campaign.id,
        adCopy: adCopyResult.adCopy,
        expectedReach: campaignResult.tracking.expectedReach,
        estimatedImpressions: campaignResult.tracking.estimatedImpressions,
        campaignUrl: campaignResult.tracking.campaignUrl,
        budget: parseFloat(budget),
        createdAt: campaignResult.metadata.createdAt
      }
    });

  } catch (error) {
    console.error('Error creating Facebook ad campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message
    });
  }
});

// GET /api/facebook-ads/campaign-status/:campaignId
router.get('/campaign-status/:campaignId', async (req, res) => {
  try {
    const { campaignId } = req.params;

    if (!campaignId) {
      return res.status(400).json({
        success: false,
        error: 'Campaign ID is required'
      });
    }

    // This would normally fetch from Facebook API
    // For now, return mock status
    const status = {
      success: true,
      campaignId: campaignId,
      status: 'ACTIVE',
      metrics: {
        impressions: Math.floor(Math.random() * 5000) + 500,
        clicks: Math.floor(Math.random() * 200) + 20,
        reach: Math.floor(Math.random() * 3000) + 300,
        spend: (Math.random() * 50 + 10).toFixed(2)
      },
      lastUpdated: new Date().toISOString()
    };

    res.json(status);

  } catch (error) {
    console.error('Error fetching campaign status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch campaign status'
    });
  }
});

// POST /api/facebook-ads/generate-preview
router.post('/generate-preview', async (req, res) => {
  try {
    const { restaurantName, itemToPromote, offer } = req.body;

    if (!restaurantName || !itemToPromote || !offer) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields for preview'
      });
    }

    // Generate ad copy preview
    const adCopyResult = await generateAdCopy(restaurantName, itemToPromote, offer);
    const promoCode = generatePromoCode(itemToPromote);

    res.json({
      success: true,
      preview: {
        adCopy: adCopyResult.adCopy,
        promoCode: promoCode,
        characterCount: adCopyResult.metadata.characterCount
      }
    });

  } catch (error) {
    console.error('Error generating ad preview:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate preview'
    });
  }
});

module.exports = router;