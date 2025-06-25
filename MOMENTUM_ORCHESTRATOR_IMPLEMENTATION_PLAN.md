# Momentum Orchestrator Implementation Plan

## Phase 1: Database Schema & Data Population

### 1. Database Schema Updates

#### New Tables to Add to `server/models/database.js`:

```sql
-- ChecklistCategory Table
CREATE TABLE IF NOT EXISTS checklist_categories (
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('foundational', 'ongoing')),
  order_in_list INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ChecklistItem Table  
CREATE TABLE IF NOT EXISTS checklist_items (
  item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL,
  parent_item_id INTEGER,
  title TEXT NOT NULL,
  description TEXT,
  guidance_link TEXT,
  order_in_category INTEGER NOT NULL,
  is_critical BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES checklist_categories (category_id),
  FOREIGN KEY (parent_item_id) REFERENCES checklist_items (item_id)
);

-- RestaurantChecklistStatus Table (replaces existing checklist_status)
CREATE TABLE IF NOT EXISTS restaurant_checklist_status (
  status_id INTEGER PRIMARY KEY AUTOINCREMENT,
  restaurant_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'not_applicable')),
  notes TEXT,
  last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id),
  FOREIGN KEY (item_id) REFERENCES checklist_items (item_id),
  UNIQUE(restaurant_id, item_id)
);
```

### 2. Data Population Script

#### Categories (Foundational - type: 'foundational'):
1. **A1. Google Business Profile (GBP)** - order_in_list: 1
2. **A2. Restaurant Website** - order_in_list: 2  
3. **A3. Social Media Presence** - order_in_list: 3
4. **A4. Online Ordering System (Innowi)** - order_in_list: 4
5. **A5. Email Marketing Platform** - order_in_list: 5
6. **A6. Loyalty & Rewards Program (Innowi)** - order_in_list: 6
7. **A7. Local Directory Listings & Citations** - order_in_list: 7

#### Categories (Ongoing - type: 'ongoing'):
8. **B1. Content Creation & Engagement** - order_in_list: 8
9. **B2. Reputation Management** - order_in_list: 9
10. **B3. Paid Advertising** - order_in_list: 10
11. **B4. Analytics & Reporting** - order_in_list: 11
12. **B5. Technical & Listing Maintenance** - order_in_list: 12

#### Checklist Items (Foundational):

**A1. Google Business Profile (GBP):**
- Claim & Verify Listing
- Core Profile Information (100% Accuracy & Completeness)
- Attributes & Highlights Configured
- Business Description Written & Optimized
- Photos & Videos Uploaded (Logo, Cover, Interior, Exterior, Food)
- Products Section Utilized (if applicable)
- Services Section Detailed
- Questions & Answers (Q&A) Seeded
- Messaging Feature Enabled & Configured
- Initial Google Posts Strategy Implemented
- Review Management Setup Complete

**A2. Restaurant Website:**
- Domain & Hosting Secured
- Mobile-First & Responsive Design Implemented
- Essential Content Present (Homepage, NAP, Menu, About, Contact)
- Online Ordering Integration Prominent
- Technical SEO Foundation Laid (SSL, Sitemap, Titles, Metas, Schema)
- Analytics & Tracking Installed (GA4, Search Console, Pixel)
- Legal & Compliance Basics Covered (Privacy Policy, Cookie Consent)
- Fast Loading Speed Achieved
- Accessibility (WCAG AA Basics) Considered

**A3. Social Media Presence:**
- Facebook Business Page Optimized
- Instagram Business Profile Optimized
- TikTok Profile Setup (if relevant)
- X (Twitter) Profile Setup (if relevant)
- LinkedIn Company Page Setup (if relevant)
- Consistent Branding Applied Across Platforms

**A4. Online Ordering System (Innowi):**
- Full Menu Accurately Configured (Pricing, Descriptions, Modifiers, Photos)
- Operational Setup Tested (Payments, Notifications, Prep Times, Delivery/Pickup)
- Promotions & Upselling Features Configured (if available)

**A5. Email Marketing Platform:**
- Account Setup & Sending Domain Authenticated (DKIM, SPF)
- Main Customer List Created & Website Opt-in Forms Deployed
- Branded Master Email Template & Welcome Email Created

**A6. Loyalty & Rewards Program (Innowi):**
- Program Design & Reward Structure Defined
- Sign-up Bonus & Promotional Materials Ready
- Staff Trained on Program Promotion

**A7. Local Directory Listings & Citations:**
- Yelp Profile Claimed & Optimized
- TripAdvisor Profile Claimed & Optimized
- Apple Maps Listing Claimed/Corrected
- Bing Places for Business Claimed & Optimized
- Key Niche Directories Updated
- NAP Consistency Audit Performed (Top 20+ Citations)

#### Checklist Items (Ongoing):

**B1. Content Creation & Engagement:**
- Weekly: Plan Social Media Content Calendar
- Daily/Weekly: Post to Social Media Platforms (Facebook, Instagram, etc.)
- Daily/Weekly: Post Instagram/Facebook Stories
- Daily: Engage with Social Media Comments & DMs
- Weekly: Create Google Business Profile Posts (What's New, Offers, Events)
- Monthly/Bi-Weekly: Send Email Newsletter/Promotions
- As Needed: Update Website Menu/Specials/Events

**B2. Reputation Management:**
- Daily: Monitor Review Sites (Google, Yelp, TripAdvisor, Facebook)
- Daily/Promptly: Respond to ALL New Reviews
- Weekly: Manage GBP Q&A

**B3. Paid Advertising:**
- Weekly/Monthly: Review & Optimize Active Ad Campaigns (Social, Search)
- As Needed: Launch New Ad Campaigns for Promotions/Events

**B4. Analytics & Reporting:**
- Monthly: Review Website Analytics (GA4 & Search Console)
- Monthly: Review GBP Insights
- Monthly: Review Social Media Analytics
- Monthly: Review Email Marketing Analytics
- Monthly: Synthesize All Data & Adjust Marketing Strategy

**B5. Technical & Listing Maintenance:**
- Quarterly: Check Website for Broken Links & Test Forms
- As Needed: Update Website Software/Plugins
- Quarterly: Verify NAP Consistency Across Key Listings

## Phase 2: Backend API Implementation

### 3. New API Routes to Create

#### File: `server/routes/checklist.js`

```javascript
// GET /api/checklist/categories - Get all categories
// GET /api/checklist/items/:categoryId - Get items for a category
// GET /api/checklist/status/:restaurantId - Get checklist status for restaurant
// PUT /api/checklist/status/:restaurantId/:itemId - Update item status
// GET /api/checklist/progress/:restaurantId - Get progress statistics
```

### 4. Database Helper Functions

#### File: `server/models/checklistModel.js`

```javascript
// getCategories(type) - Get categories by type (foundational/ongoing)
// getItemsByCategory(categoryId) - Get items for a category
// getRestaurantStatus(restaurantId) - Get all status for restaurant
// updateItemStatus(restaurantId, itemId, status, notes) - Update status
// calculateProgress(restaurantId, type) - Calculate completion percentage
```

## Phase 3: Frontend Component Overhaul

### 5. Component Structure Updates

#### File: `client/src/components/MarketingFoundations.js`

**New Component Structure:**
```jsx
<div className="momentum-orchestrator">
  <div className="section-header">
    <h2>📋 Momentum Orchestrator</h2>
    <p>Essential marketing setup checklist for restaurant success</p>
  </div>

  <div className="progress-section">
    <div className="progress-overview">
      <div className="foundational-progress">
        <h3>Foundational Setup</h3>
        <ProgressBar percentage={foundationalProgress} />
        <span>{completedFoundational} of {totalFoundational} completed ({foundationalProgress}%)</span>
      </div>
      <div className="ongoing-progress">
        <h3>Ongoing Activities</h3>
        <ProgressBar percentage={ongoingProgress} />
        <span>{completedOngoing} of {totalOngoing} completed ({ongoingProgress}%)</span>
      </div>
    </div>
  </div>

  <div className="checklist-container">
    <div className="category-tabs">
      <button className={activeType === 'foundational' ? 'active' : ''}>
        Foundational Setup
      </button>
      <button className={activeType === 'ongoing' ? 'active' : ''}>
        Ongoing Activities
      </button>
    </div>

    <div className="categories-list">
      {categories.map(category => (
        <CategorySection 
          key={category.category_id}
          category={category}
          items={categoryItems[category.category_id]}
          statuses={itemStatuses}
          onStatusUpdate={handleStatusUpdate}
        />
      ))}
    </div>
  </div>
</div>
```

#### New Sub-Components:

**CategorySection Component:**
```jsx
<div className="category-section">
  <div className="category-header" onClick={toggleExpanded}>
    <h3>{category.name}</h3>
    <div className="category-progress">
      <span>{completedItems}/{totalItems}</span>
      <ProgressBar percentage={categoryProgress} />
    </div>
    <ChevronIcon expanded={isExpanded} />
  </div>
  
  {isExpanded && (
    <div className="category-items">
      {items.map(item => (
        <ChecklistItem 
          key={item.item_id}
          item={item}
          status={statuses[item.item_id]}
          onStatusUpdate={onStatusUpdate}
        />
      ))}
    </div>
  )}
</div>
```

**ChecklistItem Component:**
```jsx
<div className="checklist-item">
  <div className="item-checkbox">
    <input 
      type="checkbox"
      checked={status?.status === 'completed'}
      onChange={handleStatusChange}
    />
  </div>
  <div className="item-content">
    <h4 className="item-title">{item.title}</h4>
    {item.description && (
      <p className="item-description">{item.description}</p>
    )}
    {item.guidance_link && (
      <a href={item.guidance_link} target="_blank" className="guidance-link">
        Learn More →
      </a>
    )}
  </div>
  <div className="item-status">
    <StatusDropdown 
      value={status?.status || 'pending'}
      onChange={handleStatusChange}
    />
  </div>
</div>
```

### 6. CSS Updates

#### File: `client/src/components/MarketingFoundations.css`

**New Styles Needed:**
- Category section styling with expand/collapse animations
- Progress bars for categories and overall progress
- Status dropdown styling
- Responsive design for mobile devices
- Hover states and interactive feedback
- Achievement celebration animations

## Phase 4: API Integration

### 7. Frontend API Service Updates

#### File: `client/src/services/api.js`

```javascript
// Add new checklist API functions:
export const checklistAPI = {
  getCategories: async (type) => { /* ... */ },
  getCategoryItems: async (categoryId) => { /* ... */ },
  getRestaurantStatus: async (restaurantId) => { /* ... */ },
  updateItemStatus: async (restaurantId, itemId, status, notes) => { /* ... */ },
  getProgress: async (restaurantId) => { /* ... */ }
};
```

## Implementation Order

1. **Database Schema** - Update `server/models/database.js`
2. **Data Population Script** - Create `server/scripts/populateChecklist.js`
3. **Backend Models** - Create `server/models/checklistModel.js`
4. **Backend Routes** - Create `server/routes/checklist.js`
5. **Frontend API** - Update `client/src/services/api.js`
6. **Frontend Components** - Update `client/src/components/MarketingFoundations.js`
7. **Frontend Styles** - Update `client/src/components/MarketingFoundations.css`
8. **Testing & Refinement** - Test all functionality and refine UX

## Success Metrics

- ✅ All 7 foundational categories with 40+ items populated
- ✅ All 5 ongoing categories with 20+ items populated
- ✅ Functional checkboxes that persist state per restaurant
- ✅ Real-time progress tracking and visualization
- ✅ Collapsible category sections with smooth animations
- ✅ Mobile-responsive design
- ✅ Status options: pending, in_progress, completed, not_applicable
- ✅ Notes field for each item
- ✅ Guidance links for external resources

This comprehensive implementation will transform the static checklist into a dynamic, motivational, and highly functional marketing orchestration tool.