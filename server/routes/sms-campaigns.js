const express = require('express');
const multer = require('multer');
const router = express.Router();

const { generateSMSMessage } = require('../services/mockOpenAI');
const { sendSMSCampaign } = require('../services/mockTwilio');
const { parseCustomerCSV, filterLapsedCustomers, generateSampleCSV } = require('../utils/csvParser');

// Configure multer for CSV uploads
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 2 * 1024 * 1024 // 2MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) {
      cb(null, true);
    } else {
      cb(new Error('Only CSV files are allowed'));
    }
  }
});

// POST /api/sms-campaigns/create-campaign
router.post('/create-campaign', upload.single('customerList'), async (req, res) => {
  try {
    const { offer, offerCode, restaurantName } = req.body;

    // Validate required fields
    if (!offer || !offerCode || !restaurantName) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields',
        required: ['offer', 'offerCode', 'restaurantName']
      });
    }

    // Validate CSV file upload
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'Customer list CSV file is required'
      });
    }

    // Parse CSV file
    const parseResult = await parseCustomerCSV(req.file.path);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        error: 'Failed to parse CSV file',
        details: parseResult.error
      });
    }

    // Check if any valid customers were found
    if (parseResult.customers.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'No valid customers found in CSV file',
        details: parseResult.errors
      });
    }

    // Filter for lapsed customers (last order > 30 days ago)
    const lapsedCustomers = filterLapsedCustomers(parseResult.customers, 30);

    if (lapsedCustomers.length === 0) {
      return res.json({
        success: true,
        message: 'No lapsed customers found (all customers have ordered within the last 30 days)',
        data: {
          totalCustomers: parseResult.customers.length,
          lapsedCustomers: 0,
          offerCode: offerCode
        }
      });
    }

    // Generate personalized SMS messages for each customer
    const smsResults = [];
    for (const customer of lapsedCustomers) {
      try {
        const smsResult = await generateSMSMessage(
          restaurantName,
          customer.customer_name,
          offer,
          offerCode
        );
        
        smsResults.push({
          customer: customer,
          smsMessage: smsResult.smsMessage,
          characterCount: smsResult.metadata.characterCount
        });
      } catch (error) {
        console.error(`Error generating SMS for ${customer.customer_name}:`, error);
        smsResults.push({
          customer: customer,
          error: 'Failed to generate SMS message'
        });
      }
    }

    // Send SMS campaign using mock Twilio
    const campaignResult = await sendSMSCampaign(
      lapsedCustomers,
      smsResults[0]?.smsMessage || `Hi! We miss you at ${restaurantName}! ${offer} Use code ${offerCode}`,
      offerCode
    );

    // Return success response
    res.json({
      success: true,
      message: `SMS campaign sent to ${campaignResult.delivery.sent} lapsed customers! Track redemptions using code ${offerCode}.`,
      data: {
        campaignId: campaignResult.campaign.id,
        offerCode: offerCode,
        totalCustomersUploaded: parseResult.customers.length,
        lapsedCustomersFound: lapsedCustomers.length,
        messagesSent: campaignResult.delivery.sent,
        messagesFailed: campaignResult.delivery.failed,
        messagesPending: campaignResult.delivery.pending,
        totalCost: campaignResult.costs.totalCost,
        sampleMessage: smsResults[0]?.smsMessage,
        deliveryRate: `${Math.round((campaignResult.delivery.sent / lapsedCustomers.length) * 100)}%`,
        createdAt: campaignResult.campaign.createdAt,
        csvErrors: parseResult.errors
      }
    });

  } catch (error) {
    console.error('Error creating SMS campaign:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message
    });
  }
});

// POST /api/sms-campaigns/preview
router.post('/preview', upload.single('customerList'), async (req, res) => {
  try {
    const { offer, offerCode, restaurantName } = req.body;

    if (!offer || !offerCode || !restaurantName) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields for preview'
      });
    }

    let customers = [];
    let csvStats = null;

    // If CSV file is provided, parse it for preview
    if (req.file) {
      const parseResult = await parseCustomerCSV(req.file.path);
      if (parseResult.success) {
        customers = filterLapsedCustomers(parseResult.customers, 30);
        csvStats = {
          totalUploaded: parseResult.customers.length,
          lapsedCustomers: customers.length,
          errors: parseResult.errors.length
        };
      }
    }

    // Generate sample SMS message
    const sampleCustomerName = customers.length > 0 ? customers[0].customer_name : 'Sarah';
    const smsResult = await generateSMSMessage(restaurantName, sampleCustomerName, offer, offerCode);

    res.json({
      success: true,
      preview: {
        sampleMessage: smsResult.smsMessage,
        characterCount: smsResult.metadata.characterCount,
        offerCode: offerCode,
        estimatedCost: customers.length > 0 ? (customers.length * 0.0075).toFixed(4) : '0.0000',
        targetCustomers: customers.length,
        csvStats: csvStats
      }
    });

  } catch (error) {
    console.error('Error generating SMS preview:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate preview'
    });
  }
});

// GET /api/sms-campaigns/sample-csv
router.get('/sample-csv', (req, res) => {
  try {
    const sampleCSV = generateSampleCSV();
    
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="sample-customer-list.csv"');
    res.send(sampleCSV);

  } catch (error) {
    console.error('Error generating sample CSV:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate sample CSV'
    });
  }
});

// GET /api/sms-campaigns/campaign-status/:campaignId
router.get('/campaign-status/:campaignId', async (req, res) => {
  try {
    const { campaignId } = req.params;

    if (!campaignId) {
      return res.status(400).json({
        success: false,
        error: 'Campaign ID is required'
      });
    }

    // Mock campaign status - in real implementation, this would fetch from database
    const status = {
      success: true,
      campaignId: campaignId,
      status: 'COMPLETED',
      metrics: {
        totalSent: Math.floor(Math.random() * 100) + 20,
        delivered: Math.floor(Math.random() * 80) + 15,
        failed: Math.floor(Math.random() * 5) + 1,
        deliveryRate: '92.5%',
        totalCost: (Math.random() * 2 + 0.5).toFixed(4)
      },
      lastUpdated: new Date().toISOString()
    };

    res.json(status);

  } catch (error) {
    console.error('Error fetching SMS campaign status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch campaign status'
    });
  }
});

module.exports = router;