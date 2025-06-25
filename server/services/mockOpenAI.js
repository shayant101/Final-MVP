// Mock OpenAI API service for generating ad copy and SMS messages

const generateAdCopy = async (restaurantName, itemToPromote, offer) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  const emojis = ['🍕', '🍔', '🌮', '🍜', '🥗', '🍰', '☕', '🥘'];
  const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
  
  const adTemplates = [
    {
      headline: `${randomEmoji} Craving something special? ${restaurantName} has you covered!`,
      body: `Get our famous ${itemToPromote} with this amazing deal: ${offer}\nFresh ingredients, authentic flavors, unbeatable value!\nDon't miss out - limited time only!`,
      cta: `📍 Visit us or order online today!`
    },
    {
      headline: `${randomEmoji} ${restaurantName} Alert: ${itemToPromote} Special!`,
      body: `${offer} - because you deserve the best!\nMade fresh daily with premium ingredients.\nYour taste buds will thank you!`,
      cta: `🚗 Dine in, takeout, or delivery available!`
    },
    {
      headline: `${randomEmoji} Local Favorite Alert! ${restaurantName}`,
      body: `Our signature ${itemToPromote} is calling your name!\n${offer}\nTaste the difference quality makes!`,
      cta: `📞 Order now or visit us today!`
    }
  ];

  const selectedTemplate = adTemplates[Math.floor(Math.random() * adTemplates.length)];
  
  return {
    success: true,
    adCopy: `${selectedTemplate.headline}\n\n${selectedTemplate.body}\n\n${selectedTemplate.cta}`,
    metadata: {
      characterCount: (selectedTemplate.headline + selectedTemplate.body + selectedTemplate.cta).length,
      generatedAt: new Date().toISOString(),
      model: 'gpt-4-turbo'
    }
  };
};

const generateSMSMessage = async (restaurantName, customerName, offer, offerCode) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1200));

  const smsTemplates = [
    `Hi ${customerName}! We miss you at ${restaurantName}! ${offer} Use code ${offerCode}. Valid thru Sunday!`,
    `${customerName}, come back to ${restaurantName}! ${offer} Code: ${offerCode}. Limited time!`,
    `Hey ${customerName}! ${restaurantName} misses you. ${offer} Use ${offerCode} - expires soon!`,
    `${customerName}, special offer from ${restaurantName}: ${offer} Code ${offerCode}. Don't wait!`
  ];

  const selectedMessage = smsTemplates[Math.floor(Math.random() * smsTemplates.length)];
  
  // Ensure message is under 160 characters
  const finalMessage = selectedMessage.length > 160 
    ? selectedMessage.substring(0, 157) + '...' 
    : selectedMessage;

  return {
    success: true,
    smsMessage: finalMessage,
    metadata: {
      characterCount: finalMessage.length,
      generatedAt: new Date().toISOString(),
      model: 'gpt-3.5-turbo'
    }
  };
};

const generatePromoCode = (itemToPromote) => {
  const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
  const today = new Date();
  const dayCode = days[today.getDay()];
  
  // Clean item name and take first 6 characters
  const itemCode = itemToPromote.replace(/[^a-zA-Z]/g, '').toUpperCase().substring(0, 6);
  
  return `${itemCode}${dayCode}`;
};

module.exports = {
  generateAdCopy,
  generateSMSMessage,
  generatePromoCode
};