// Mock Facebook Marketing API service for creating ad campaigns

const createAdCampaign = async (campaignData) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  const { restaurantName, itemToPromote, offer, budget, adCopy, promoCode } = campaignData;

  // Generate realistic campaign ID
  const campaignId = `camp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const adSetId = `adset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const adId = `ad_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Simulate campaign creation response
  const campaignResponse = {
    success: true,
    campaign: {
      id: campaignId,
      name: `${restaurantName} - ${itemToPromote} Promotion`,
      objective: 'STORE_TRAFFIC',
      status: 'ACTIVE',
      created_time: new Date().toISOString(),
      budget_remaining: budget * 100, // Convert to cents
      daily_budget: budget * 100
    },
    adSet: {
      id: adSetId,
      name: `${restaurantName} Local Audience`,
      targeting: {
        geo_locations: {
          custom_locations: [
            {
              radius: 2,
              distance_unit: 'mile',
              address_string: 'Restaurant Location' // Hardcoded for MVP
            }
          ]
        },
        age_min: 18,
        age_max: 65
      },
      optimization_goal: 'REACH',
      billing_event: 'IMPRESSIONS'
    },
    ad: {
      id: adId,
      name: `${itemToPromote} Special Ad`,
      creative: {
        title: `${restaurantName} Special Offer`,
        body: adCopy,
        call_to_action_type: 'LEARN_MORE'
      },
      status: 'ACTIVE'
    },
    tracking: {
      promoCode: promoCode,
      expectedReach: Math.floor(Math.random() * 5000) + 1000,
      estimatedImpressions: Math.floor(Math.random() * 10000) + 2000,
      campaignUrl: `https://facebook.com/ads/manager/campaigns/${campaignId}`
    },
    metadata: {
      createdAt: new Date().toISOString(),
      platform: 'Facebook Marketing API',
      version: 'v18.0'
    }
  };

  return campaignResponse;
};

const getCampaignStatus = async (campaignId) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800));

  const statuses = ['ACTIVE', 'PAUSED', 'PENDING_REVIEW'];
  const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

  return {
    success: true,
    campaignId: campaignId,
    status: randomStatus,
    metrics: {
      impressions: Math.floor(Math.random() * 5000) + 500,
      clicks: Math.floor(Math.random() * 200) + 20,
      reach: Math.floor(Math.random() * 3000) + 300,
      spend: (Math.random() * 50 + 10).toFixed(2)
    },
    lastUpdated: new Date().toISOString()
  };
};

const validateBudget = (budget) => {
  const minBudget = 5;
  const maxBudget = 1000;
  
  if (budget < minBudget) {
    return {
      valid: false,
      error: `Minimum daily budget is $${minBudget}`
    };
  }
  
  if (budget > maxBudget) {
    return {
      valid: false,
      error: `Maximum daily budget is $${maxBudget}`
    };
  }
  
  return { valid: true };
};

module.exports = {
  createAdCampaign,
  getCampaignStatus,
  validateBudget
};