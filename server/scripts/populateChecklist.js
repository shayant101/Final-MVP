const { db } = require('../models/database');

// Checklist Categories Data - Using Original Prompt Structure
const categories = [
  // Foundational Categories
  { 
    name: "A1. Google Business Profile (GBP)", 
    description: "Claim, verify, and optimize your Google Business Profile for maximum local visibility",
    icon: "🏢",
    type: "foundational", 
    order_in_list: 1 
  },
  { 
    name: "A2. Restaurant Website", 
    description: "Your digital hub - mobile-first, fast, and conversion-optimized",
    icon: "🌐",
    type: "foundational", 
    order_in_list: 2 
  },
  { 
    name: "A3. Social Media Presence", 
    description: "Establish and optimize profiles across key social platforms",
    icon: "📱",
    type: "foundational", 
    order_in_list: 3 
  },
  { 
    name: "A4. Online Ordering System (Innowi)", 
    description: "Complete menu setup and operational configuration for seamless ordering",
    icon: "🛒",
    type: "foundational", 
    order_in_list: 4 
  },
  { 
    name: "A5. Email Marketing Platform", 
    description: "Set up email marketing infrastructure for customer communication",
    icon: "📧",
    type: "foundational", 
    order_in_list: 5 
  },
  { 
    name: "A6. Loyalty & Rewards Program (Innowi)", 
    description: "Design and implement customer loyalty program to drive repeat business",
    icon: "🎁",
    type: "foundational", 
    order_in_list: 6 
  },
  { 
    name: "A7. Local Directory Listings & Citations", 
    description: "Ensure consistent NAP across all major directories and review sites",
    icon: "📍",
    type: "foundational", 
    order_in_list: 7 
  },
  
  // Ongoing Categories
  { 
    name: "B1. Content Creation & Engagement", 
    description: "Regular content creation and customer engagement across all channels",
    icon: "✨",
    type: "ongoing", 
    order_in_list: 8 
  },
  { 
    name: "B2. Reputation Management", 
    description: "Monitor and respond to reviews and customer feedback across all platforms",
    icon: "⭐",
    type: "ongoing", 
    order_in_list: 9 
  },
  { 
    name: "B3. Paid Advertising", 
    description: "Strategic paid advertising campaigns across social media and search platforms",
    icon: "🎯",
    type: "ongoing", 
    order_in_list: 10 
  },
  { 
    name: "B4. Analytics & Reporting", 
    description: "Monthly analysis and reporting across all marketing channels",
    icon: "📊",
    type: "ongoing", 
    order_in_list: 11 
  },
  { 
    name: "B5. Technical & Listing Maintenance", 
    description: "Quarterly maintenance of technical systems and directory listings",
    icon: "🔧",
    type: "ongoing", 
    order_in_list: 12 
  }
];

// Checklist Items Data - Using EXACT Original Prompt Titles
const items = [
  // A1. Google Business Profile (GBP) - category_id: 1
  {
    category_id: 1,
    title: "Claim & Verify Listing",
    description: "Ensure sole ownership or appropriate manager access to your Google Business Profile",
    guidance_link: "https://www.google.com/business/",
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 1,
    title: "Core Profile Information (100% Accuracy & Completeness)",
    description: "Complete all essential profile fields: Name, Category, Address, Hours, Phone, Website, Menu Link, Order Links",
    guidance_link: "https://support.google.com/business/answer/3038177",
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 1,
    title: "Attributes & Highlights Configured",
    description: "Set up service options, health & safety, accessibility, offerings, dining options, atmosphere, and identity attributes",
    guidance_link: "https://support.google.com/business/answer/6208386",
    order_in_category: 3,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Business Description Written & Optimized",
    description: "Write compelling 750-character description highlighting unique selling propositions",
    guidance_link: "https://support.google.com/business/answer/3038177",
    order_in_category: 4,
    is_critical: true
  },
  {
    category_id: 1,
    title: "Photos & Videos Uploaded (Logo, Cover, Interior, Exterior, Food)",
    description: "Upload high-quality photos and videos showcasing your restaurant experience",
    guidance_link: "https://support.google.com/business/answer/6123536",
    order_in_category: 5,
    is_critical: true
  },
  {
    category_id: 1,
    title: "Products Section Utilized (if applicable)",
    description: "Add key products with photos, descriptions, and prices",
    guidance_link: "https://support.google.com/business/answer/9681433",
    order_in_category: 6,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Services Section Detailed",
    description: "Detail specific services offered beyond general categories",
    guidance_link: "https://support.google.com/business/answer/9681433",
    order_in_category: 7,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Questions & Answers (Q&A) Seeded",
    description: "Proactively add common questions and answers; upvote helpful existing Q&As",
    guidance_link: "https://support.google.com/business/answer/4596773",
    order_in_category: 8,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Messaging Feature Enabled & Configured",
    description: "Enable messaging with welcome message and FAQ automation",
    guidance_link: "https://support.google.com/business/answer/9109320",
    order_in_category: 9,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Initial Google Posts Strategy Implemented",
    description: "Create initial 'What's New' or welcome post",
    guidance_link: "https://support.google.com/business/answer/7342169",
    order_in_category: 10,
    is_critical: false
  },
  {
    category_id: 1,
    title: "Review Management Setup Complete",
    description: "Set up notifications for new reviews and response strategy",
    guidance_link: "https://support.google.com/business/answer/3474050",
    order_in_category: 11,
    is_critical: true
  },

  // A2. Restaurant Website - category_id: 2
  {
    category_id: 2,
    title: "Domain & Hosting Secured",
    description: "Secure domain name registered and reliable, fast web hosting",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Mobile-First & Responsive Design Implemented",
    description: "Flawless performance on all devices with intuitive navigation",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Essential Content Present (Homepage, NAP, Menu, About, Contact)",
    description: "All essential pages with compelling content and clear calls-to-action",
    guidance_link: null,
    order_in_category: 3,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Online Ordering Integration Prominent",
    description: "Clearly visible links/buttons to Innowi ordering system",
    guidance_link: null,
    order_in_category: 4,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Technical SEO Foundation Laid (SSL, Sitemap, Titles, Metas, Schema)",
    description: "Complete technical SEO setup including Restaurant, Menu, and LocalBusiness schema",
    guidance_link: "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
    order_in_category: 5,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Analytics & Tracking Installed (GA4, Search Console, Pixel)",
    description: "Google Analytics 4, Search Console, and Meta Pixel installed and configured",
    guidance_link: "https://analytics.google.com/",
    order_in_category: 6,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Legal & Compliance Basics Covered (Privacy Policy, Cookie Consent)",
    description: "Required legal pages and GDPR/CCPA compliance measures",
    guidance_link: null,
    order_in_category: 7,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Fast Loading Speed Achieved",
    description: "Optimized images, caching, good server response (test with PageSpeed Insights)",
    guidance_link: "https://pagespeed.web.dev/",
    order_in_category: 8,
    is_critical: true
  },
  {
    category_id: 2,
    title: "Accessibility (WCAG AA Basics) Considered",
    description: "Alt text for images, keyboard navigation, sufficient color contrast, ARIA labels",
    guidance_link: "https://www.w3.org/WAI/WCAG21/quickref/",
    order_in_category: 9,
    is_critical: false
  },

  // A3. Social Media Presence - category_id: 3
  {
    category_id: 3,
    title: "Facebook Business Page Optimized",
    description: "Complete About section, NAP, website, hours, story, CTA button, cover/profile photos",
    guidance_link: "https://www.facebook.com/business/pages/set-up",
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 3,
    title: "Instagram Business Profile Optimized",
    description: "Convert to Business account with optimized bio, contact options, and action buttons",
    guidance_link: "https://business.instagram.com/getting-started",
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 3,
    title: "TikTok Profile Setup (if relevant)",
    description: "If relevant to target audience, set up with optimized bio and branded profile",
    guidance_link: "https://www.tiktok.com/business/",
    order_in_category: 3,
    is_critical: false
  },
  {
    category_id: 3,
    title: "X (Twitter) Profile Setup (if relevant)",
    description: "If relevant, optimized bio, header, profile picture, website link",
    guidance_link: "https://business.twitter.com/",
    order_in_category: 4,
    is_critical: false
  },
  {
    category_id: 3,
    title: "LinkedIn Company Page Setup (if relevant)",
    description: "If focus on B2B/Catering/Corporate, fully completed company page",
    guidance_link: "https://business.linkedin.com/marketing-solutions/company-pages",
    order_in_category: 5,
    is_critical: false
  },
  {
    category_id: 3,
    title: "Consistent Branding Applied Across Platforms",
    description: "Ensure consistent logo, colors, messaging across all social platforms",
    guidance_link: null,
    order_in_category: 6,
    is_critical: true
  },

  // A4. Online Ordering System (Innowi) - category_id: 4
  {
    category_id: 4,
    title: "Full Menu Accurately Configured (Pricing, Descriptions, Modifiers, Photos)",
    description: "Complete menu with current pricing, clear descriptions, modifiers, and high-quality photos",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 4,
    title: "Operational Setup Tested (Payments, Notifications, Prep Times, Delivery/Pickup)",
    description: "Payment processing, notifications, prep times, and delivery/pickup parameters tested",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 4,
    title: "Promotions & Upselling Features Configured (if available)",
    description: "Setup for promotional codes and upselling features tested and working",
    guidance_link: null,
    order_in_category: 3,
    is_critical: false
  },

  // A5. Email Marketing Platform - category_id: 5
  {
    category_id: 5,
    title: "Account Setup & Sending Domain Authenticated (DKIM, SPF)",
    description: "Email marketing platform account set up with domain authentication for better deliverability",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 5,
    title: "Main Customer List Created & Website Opt-in Forms Deployed",
    description: "Primary customer email list established with newsletter signup forms on website",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 5,
    title: "Branded Master Email Template & Welcome Email Created",
    description: "Professional email template with logo, brand colors, and welcome email sequence",
    guidance_link: null,
    order_in_category: 3,
    is_critical: true
  },

  // A6. Loyalty & Rewards Program (Innowi) - category_id: 6
  {
    category_id: 6,
    title: "Program Design & Reward Structure Defined",
    description: "Points per dollar, specific rewards, tiers, and terms clearly defined",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 6,
    title: "Sign-up Bonus & Promotional Materials Ready",
    description: "Attractive incentive for customers to join and in-store promotional materials prepared",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 6,
    title: "Staff Trained on Program Promotion",
    description: "Team knows how to explain and enroll customers in the loyalty program",
    guidance_link: null,
    order_in_category: 3,
    is_critical: true
  },

  // A7. Local Directory Listings & Citations - category_id: 7
  {
    category_id: 7,
    title: "Yelp Profile Claimed & Optimized",
    description: "Complete Yelp profile with NAP, hours, photos, menu link, attributes",
    guidance_link: "https://biz.yelp.com/",
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 7,
    title: "TripAdvisor Profile Claimed & Optimized",
    description: "Complete TripAdvisor profile optimization",
    guidance_link: "https://www.tripadvisor.com/Owners",
    order_in_category: 2,
    is_critical: false
  },
  {
    category_id: 7,
    title: "Apple Maps Listing Claimed/Corrected",
    description: "Apple Business Connect listing claimed and accurate",
    guidance_link: "https://mapsconnect.apple.com/",
    order_in_category: 3,
    is_critical: false
  },
  {
    category_id: 7,
    title: "Bing Places for Business Claimed & Optimized",
    description: "Bing Places listing optimized",
    guidance_link: "https://www.bingplaces.com/",
    order_in_category: 4,
    is_critical: false
  },
  {
    category_id: 7,
    title: "Key Niche Directories Updated",
    description: "Local Chamber of Commerce, city tourism sites, food-specific directories",
    guidance_link: null,
    order_in_category: 5,
    is_critical: false
  },
  {
    category_id: 7,
    title: "NAP Consistency Audit Performed (Top 20+ Citations)",
    description: "Comprehensive audit of Name, Address, Phone consistency across citations",
    guidance_link: null,
    order_in_category: 6,
    is_critical: true
  },

  // B1. Content Creation & Engagement - category_id: 8
  {
    category_id: 8,
    title: "Weekly: Plan Social Media Content Calendar",
    description: "Strategic content planning for consistent messaging across platforms",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 8,
    title: "Daily/Weekly: Post to Social Media Platforms (Facebook, Instagram, etc.)",
    description: "High-quality food photos, behind-the-scenes, UGC, staff spotlights, offers, events",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 8,
    title: "Daily/Weekly: Post Instagram/Facebook Stories",
    description: "Instagram/Facebook Stories with informal content, polls, Q&A",
    guidance_link: null,
    order_in_category: 3,
    is_critical: false
  },
  {
    category_id: 8,
    title: "Daily: Engage with Social Media Comments & DMs",
    description: "Authentic, timely responses to customer interactions",
    guidance_link: null,
    order_in_category: 4,
    is_critical: true
  },
  {
    category_id: 8,
    title: "Weekly: Create Google Business Profile Posts (What's New, Offers, Events)",
    description: "Regular Google Posts with call-to-action buttons",
    guidance_link: null,
    order_in_category: 5,
    is_critical: false
  },
  {
    category_id: 8,
    title: "Monthly/Bi-Weekly: Send Email Newsletter/Promotions",
    description: "Updates, specials, events, new menu items via email",
    guidance_link: null,
    order_in_category: 6,
    is_critical: false
  },
  {
    category_id: 8,
    title: "As Needed: Update Website Menu/Specials/Events",
    description: "Keep website current with latest offerings and events",
    guidance_link: null,
    order_in_category: 7,
    is_critical: true
  },

  // B2. Reputation Management - category_id: 9
  {
    category_id: 9,
    title: "Daily: Monitor Review Sites (Google, Yelp, TripAdvisor, Facebook)",
    description: "Check all major review platforms for new reviews daily",
    guidance_link: null,
    order_in_category: 1,
    is_critical: true
  },
  {
    category_id: 9,
    title: "Daily/Promptly: Respond to ALL New Reviews",
    description: "Professional, personal responses to both positive and negative reviews",
    guidance_link: null,
    order_in_category: 2,
    is_critical: true
  },
  {
    category_id: 9,
    title: "Weekly: Manage GBP Q&A",
    description: "Answer new Google Business Profile questions promptly",
    guidance_link: null,
    order_in_category: 3,
    is_critical: false
  },

  // B3. Paid Advertising - category_id: 10
  {
    category_id: 10,
    title: "Weekly/Monthly: Review & Optimize Active Ad Campaigns (Social, Search)",
    description: "Monitor and optimize Facebook/Instagram and Google Ads campaigns",
    guidance_link: null,
    order_in_category: 1,
    is_critical: false
  },
  {
    category_id: 10,
    title: "As Needed: Launch New Ad Campaigns for Promotions/Events",
    description: "Create targeted campaigns for special promotions and events",
    guidance_link: null,
    order_in_category: 2,
    is_critical: false
  },

  // B4. Analytics & Reporting - category_id: 11
  {
    category_id: 11,
    title: "Monthly: Review Website Analytics (GA4 & Search Console)",
    description: "Track traffic, sources, user behavior, bounce rate, goal completions",
    guidance_link: null,
    order_in_category: 1,
    is_critical: false
  },
  {
    category_id: 11,
    title: "Monthly: Review GBP Insights",
    description: "Track search types, actions taken, search queries, photo views",
    guidance_link: null,
    order_in_category: 2,
    is_critical: false
  },
  {
    category_id: 11,
    title: "Monthly: Review Social Media Analytics",
    description: "Track reach, impressions, engagement rate, follower growth, top content",
    guidance_link: null,
    order_in_category: 3,
    is_critical: false
  },
  {
    category_id: 11,
    title: "Monthly: Review Email Marketing Analytics",
    description: "Track open rates, click-through rates, unsubscribe rates, conversion rates",
    guidance_link: null,
    order_in_category: 4,
    is_critical: false
  },
  {
    category_id: 11,
    title: "Monthly: Synthesize All Data & Adjust Marketing Strategy",
    description: "Use insights to refine marketing efforts and strategy",
    guidance_link: null,
    order_in_category: 5,
    is_critical: false
  },

  // B5. Technical & Listing Maintenance - category_id: 12
  {
    category_id: 12,
    title: "Quarterly: Check Website for Broken Links & Test Forms",
    description: "Quarterly audit of website links and functionality",
    guidance_link: null,
    order_in_category: 1,
    is_critical: false
  },
  {
    category_id: 12,
    title: "As Needed: Update Website Software/Plugins",
    description: "Keep WordPress/CMS software updated for security",
    guidance_link: null,
    order_in_category: 2,
    is_critical: false
  },
  {
    category_id: 12,
    title: "Quarterly: Verify NAP Consistency Across Key Listings",
    description: "Quarterly audit of business information consistency",
    guidance_link: null,
    order_in_category: 3,
    is_critical: false
  }
];

// Function to clear existing data
const clearData = () => {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      db.run('DELETE FROM restaurant_checklist_status', (err) => {
        if (err) console.error('Error clearing status:', err);
      });
      db.run('DELETE FROM checklist_items', (err) => {
        if (err) console.error('Error clearing items:', err);
      });
      db.run('DELETE FROM checklist_categories', (err) => {
        if (err) {
          reject(err);
        } else {
          console.log('✅ Existing data cleared');
          resolve();
        }
      });
    });
  });
};

// Function to populate categories
const populateCategories = () => {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO checklist_categories (name, description, icon, type, order_in_list)
      VALUES (?, ?, ?, ?, ?)
    `);

    db.serialize(() => {
      categories.forEach(category => {
        stmt.run([category.name, category.description, category.icon, category.type, category.order_in_list]);
      });
      
      stmt.finalize((err) => {
        if (err) {
          reject(err);
        } else {
          console.log('✅ Categories populated successfully');
          resolve();
        }
      });
    });
  });
};

// Function to populate items
const populateItems = () => {
  return new Promise((resolve, reject) => {
    // First, get the actual category IDs from the database
    db.all('SELECT category_id, order_in_list FROM checklist_categories ORDER BY order_in_list', (err, categories) => {
      if (err) {
        reject(err);
        return;
      }

      // Create a mapping from order_in_list to actual category_id
      const categoryIdMap = {};
      categories.forEach(cat => {
        categoryIdMap[cat.order_in_list] = cat.category_id;
      });

      const stmt = db.prepare(`
        INSERT INTO checklist_items
        (category_id, title, description, guidance_link, order_in_category, is_critical)
        VALUES (?, ?, ?, ?, ?, ?)
      `);

      db.serialize(() => {
        items.forEach(item => {
          // Map the hardcoded category_id to the actual database category_id
          const actualCategoryId = categoryIdMap[item.category_id];
          if (!actualCategoryId) {
            console.error(`No category found for order ${item.category_id}`);
            return;
          }

          stmt.run([
            actualCategoryId,  // Use the actual category_id from database
            item.title,
            item.description,
            item.guidance_link,
            item.order_in_category,
            item.is_critical
          ]);
        });
        
        stmt.finalize((err) => {
          if (err) {
            reject(err);
          } else {
            console.log('✅ Items populated successfully');
            resolve();
          }
        });
      });
    });
  });
};

// Main population function
const populateChecklist = async () => {
  try {
    console.log('🚀 Starting fresh checklist population...');
    await clearData();
    await populateCategories();
    await populateItems();
    console.log('🎉 Checklist population completed successfully!');
    console.log(`📊 Populated ${categories.length} categories and ${items.length} items`);
  } catch (error) {
    console.error('❌ Error populating checklist:', error);
  }
};

module.exports = {
  populateChecklist,
  populateCategories,
  populateItems,
  clearData
};

// Run if called directly
if (require.main === module) {
  populateChecklist().then(() => {
    process.exit(0);
  }).catch((error) => {
    console.error(error);
    process.exit(1);
  });
}