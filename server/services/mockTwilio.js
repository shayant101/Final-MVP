// Mock Twilio API service for sending SMS campaigns

const sendSMSCampaign = async (customers, smsMessage, offerCode) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1800));

  const results = {
    success: true,
    campaign: {
      id: `sms_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      offerCode: offerCode,
      message: smsMessage,
      createdAt: new Date().toISOString()
    },
    delivery: {
      totalCustomers: customers.length,
      sent: 0,
      failed: 0,
      pending: 0
    },
    details: [],
    costs: {
      perMessage: 0.0075, // $0.0075 per SMS
      totalCost: 0
    }
  };

  // Simulate sending to each customer
  for (const customer of customers) {
    const deliveryStatus = simulateDelivery();
    
    const messageResult = {
      customerName: customer.customer_name,
      phoneNumber: customer.phone_number,
      status: deliveryStatus.status,
      messageId: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      sentAt: new Date().toISOString(),
      errorCode: deliveryStatus.errorCode || null,
      errorMessage: deliveryStatus.errorMessage || null
    };

    results.details.push(messageResult);

    // Update counters
    if (deliveryStatus.status === 'sent') {
      results.delivery.sent++;
    } else if (deliveryStatus.status === 'failed') {
      results.delivery.failed++;
    } else {
      results.delivery.pending++;
    }
  }

  // Calculate total cost
  results.costs.totalCost = (results.delivery.sent * results.costs.perMessage).toFixed(4);

  return results;
};

const simulateDelivery = () => {
  const random = Math.random();
  
  // 85% success rate
  if (random < 0.85) {
    return { status: 'sent' };
  }
  // 10% pending
  else if (random < 0.95) {
    return { status: 'pending' };
  }
  // 5% failed
  else {
    const errorCodes = [
      { code: 21211, message: 'Invalid phone number' },
      { code: 21610, message: 'Message blocked by carrier' },
      { code: 21614, message: 'Message body is required' }
    ];
    const error = errorCodes[Math.floor(Math.random() * errorCodes.length)];
    return {
      status: 'failed',
      errorCode: error.code,
      errorMessage: error.message
    };
  }
};

const validatePhoneNumber = (phoneNumber) => {
  // Basic phone number validation
  const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
  return phoneRegex.test(phoneNumber);
};

const formatPhoneNumber = (phoneNumber) => {
  // Remove all non-digit characters
  const digits = phoneNumber.replace(/\D/g, '');
  
  // Add +1 if it's a 10-digit US number
  if (digits.length === 10) {
    return `+1${digits}`;
  }
  
  // Add + if it doesn't start with it
  if (!phoneNumber.startsWith('+')) {
    return `+${digits}`;
  }
  
  return phoneNumber;
};

const getSMSDeliveryReport = async (campaignId) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 600));

  return {
    success: true,
    campaignId: campaignId,
    report: {
      totalMessages: Math.floor(Math.random() * 100) + 20,
      delivered: Math.floor(Math.random() * 80) + 15,
      failed: Math.floor(Math.random() * 5) + 1,
      pending: Math.floor(Math.random() * 3),
      deliveryRate: '92.5%',
      avgDeliveryTime: '2.3 seconds',
      totalCost: (Math.random() * 2 + 0.5).toFixed(4)
    },
    generatedAt: new Date().toISOString()
  };
};

module.exports = {
  sendSMSCampaign,
  validatePhoneNumber,
  formatPhoneNumber,
  getSMSDeliveryReport
};