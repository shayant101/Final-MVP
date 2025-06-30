# 🎯 Digital Presence Grader - Scoring Logic Explained

## 📊 Overall Scoring System

The Digital Presence Grader uses a **weighted scoring system** that evaluates 5 key components of a restaurant's digital presence:

### 🏆 Component Weights
```
Website Analysis:        25% (0.25)
Google Business Profile: 25% (0.25) 
Social Media:           20% (0.20)
Menu Optimization:      15% (0.15)
Marketing Strategy:     15% (0.15)
```

### 📈 Grade Scale
- **A (90-100)**: Excellent - Low Priority
- **B (80-89)**: Good - Low Priority  
- **C (70-79)**: Average - Medium Priority
- **D (60-69)**: Below Average - High Priority
- **F (0-59)**: Needs Improvement - High Priority

---

## 🌐 Website Analysis (25% Weight)

### 📊 Scoring Breakdown (100 points total):

#### **1. Website Accessibility (40 points)**
- ✅ **Accessible (HTTP 200)**: +40 points
- ❌ **Not accessible**: 0 points, adds issue

#### **2. SSL Certificate (20 points)**
- ✅ **HTTPS enabled**: +20 points
- ❌ **No SSL**: 0 points, adds security issue

#### **3. Response Time (20 points)**
- ⚡ **≤ 2.0 seconds**: +20 points
- 🐌 **2.1-4.0 seconds**: +15 points, adds "slow loading" issue
- 🐢 **> 4.0 seconds**: +5 points, adds "very slow" issue

#### **4. Accessibility Bonus (20 points)**
- ✅ **Website accessible**: +10 points + standard recommendations
- ❌ **Not accessible**: 0 points

### 🔍 Real Scraping Analysis (Advanced Mode):
When real website data is available, additional scoring includes:

#### **Title Optimization (20 points)**
- ✅ **Has title**: +15 points
- ✅ **Optimal length (30-60 chars)**: +5 bonus points
- ❌ **Missing/poor title**: Issues added

#### **Meta Description (15 points)**
- ✅ **Has description**: +10 points
- ✅ **Optimal length (120-160 chars)**: +5 bonus points

#### **Restaurant Content (25 points)**
- 🍽️ **Menu found**: +8 points
- 📞 **Contact info**: +8 points
- 🕒 **Business hours**: +5 points
- 🛒 **Online ordering**: +4 points

---

## 📍 Google Business Profile (25% Weight)

### 📊 Scoring Breakdown (100 points total):

#### **1. Basic Profile Setup (30 points)**
- 🏪 **Business name**: +10 points
- 📍 **Address**: +10 points  
- 📞 **Phone number**: +10 points

#### **2. Verification Status (20 points)**
- ✅ **Verified business**: +20 points
- ❌ **Not verified**: 0 points, high priority issue

#### **3. Reviews & Ratings (25 points)**
**Rating Score:**
- ⭐ **4.5+ stars**: +25 points
- ⭐ **4.0-4.4 stars**: +20 points
- ⭐ **3.5-3.9 stars**: +15 points
- ⭐ **3.0-3.4 stars**: +10 points
- ⭐ **< 3.0 stars**: +5 points, adds quality issue

**Review Count:**
- 💬 **100+ reviews**: +15 points
- 💬 **50-99 reviews**: +12 points
- 💬 **20-49 reviews**: +8 points
- 💬 **5-19 reviews**: +5 points
- 💬 **< 5 reviews**: +2 points, adds engagement issue

#### **4. Business Categories (20 points)**
- ✅ **Categories present**: +20 points
- ✅ **Food-related categories**: +5 bonus points

#### **5. Profile Accessibility (15 points)**
- ✅ **Profile accessible**: +15 points

---

## 📱 Social Media Analysis (20% Weight)

### 📊 Scoring Breakdown (100 points total):

#### **1. Essential Platform Coverage (40 points)**
- 📘 **Facebook**: +13 points
- 📸 **Instagram**: +13 points  
- 🗺️ **Google My Business**: +13 points
- ✅ **All 3 essential**: Full 40 points

#### **2. Additional Platforms (20 points)**
- 🐦 **Twitter**: +4 points
- 💼 **LinkedIn**: +4 points
- 📺 **YouTube**: +4 points
- 🎵 **TikTok**: +4 points
- ⭐ **Yelp**: +4 points
- **Maximum**: 20 points total

#### **3. Platform Consistency (20 points)**
- 🎯 **3+ platforms**: +20 points
- 🎯 **2 platforms**: +10 points
- 🎯 **< 2 platforms**: 0 points, adds expansion issue

#### **4. Website Integration (20 points)**
- 🔗 **Social links on website**: +20 points
- ❌ **No website integration**: 0 points, adds integration issue

---

## 🍽️ Menu Optimization (15% Weight)

### 📊 AI-Powered Analysis (100 points total):

Uses OpenAI to analyze:
- 📝 **Item descriptions quality**
- 📸 **Photo availability**
- 💰 **Pricing strategy**
- 📋 **Menu organization**
- 🎯 **Promotional opportunities**
- 🥗 **Dietary information**

**Scoring based on AI assessment of menu digital readiness**

---

## 📈 Marketing Strategy (15% Weight)

### 📊 AI-Powered Analysis (100 points total):

Evaluates:
- 🎯 **Campaign diversity**
- 💰 **Budget allocation**
- 👥 **Target audience definition**
- 📊 **Marketing channel mix**
- 📈 **ROI tracking capabilities**
- 🗓️ **Seasonal strategies**

---

## 🧮 Final Score Calculation

### Formula:
```
Overall Score = (Website × 0.25) + (Google × 0.25) + (Social × 0.20) + (Menu × 0.15) + (Marketing × 0.15)
```

### Example Calculation:
```
Website: 75 points × 0.25 = 18.75
Google: 80 points × 0.25 = 20.00  
Social: 60 points × 0.20 = 12.00
Menu: 70 points × 0.15 = 10.50
Marketing: 65 points × 0.15 = 9.75

Total: 71.0 points = Grade C (Average)
```

---

## 💰 Revenue Impact Estimation

### Calculation Logic:
```
Monthly Impact = Improvement Potential × $25-$75 per point
Annual Impact = Monthly Impact × 12

Example: 30 points improvement potential
- Conservative: 30 × $25 = $750/month = $9,000/year
- Optimistic: 30 × $75 = $2,250/month = $27,000/year
```

---

## 🎯 Priority & Action Plan Logic

### Priority Assignment:
- **HIGH**: Scores < 70, critical missing elements
- **MEDIUM**: Scores 70-79, optimization needed
- **LOW**: Scores 80+, minor improvements

### Impact Estimation:
- **HIGH Impact**: Website, Google, Reviews, SEO, Online Ordering
- **MEDIUM Impact**: Social Media, Content, Photos, Menu
- **LOW Impact**: Minor optimizations

### Effort Estimation:
- **HIGH Effort**: Create, Build, Develop, Redesign, Implement
- **LOW Effort**: Update, Add, Optimize, Improve, Respond
- **MEDIUM Effort**: Everything else

---

## 🔄 Real-Time Scraping Integration

The system now uses **real web scraping** instead of mock data:

1. **Website Validation**: HTTP requests to check accessibility, SSL, response time
2. **Content Analysis**: HTML parsing for titles, descriptions, contact info
3. **Google Business Scraping**: Real profile data extraction
4. **Social Media Detection**: Automatic discovery of social links
5. **AI Enhancement**: OpenAI analysis of scraped content

This provides **accurate, data-driven scores** based on actual digital presence rather than estimates.