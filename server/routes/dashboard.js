const express = require('express');
const { db } = require('../models/database');
const { authenticateToken, requireAdmin, requireRestaurant, getRestaurantContext } = require('../middleware/auth');

const router = express.Router();

// Restaurant Dashboard Data
router.get('/restaurant', authenticateToken, requireRestaurant, getRestaurantContext, (req, res) => {
  const restaurantId = req.restaurantId;

  // Get restaurant info
  db.get('SELECT * FROM restaurants WHERE restaurant_id = ?', [restaurantId], (err, restaurant) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    if (!restaurant) {
      return res.status(404).json({ error: 'Restaurant not found' });
    }

    // Get active campaigns
    db.all(
      'SELECT * FROM campaigns WHERE restaurant_id = ? AND status = "active" ORDER BY created_at DESC LIMIT 3',
      [restaurantId],
      (err, campaigns) => {
        if (err) {
          return res.status(500).json({ error: 'Database error' });
        }

        // Get pending checklist items
        db.all(
          'SELECT * FROM checklist_status WHERE restaurant_id = ? AND is_complete = FALSE ORDER BY created_at ASC',
          [restaurantId],
          (err, pendingTasks) => {
            if (err) {
              return res.status(500).json({ error: 'Database error' });
            }

            // Get campaign counts for last 7 days
            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
            
            db.get(
              'SELECT COUNT(*) as campaign_count FROM campaigns WHERE restaurant_id = ? AND created_at >= ?',
              [restaurantId, sevenDaysAgo.toISOString()],
              (err, campaignStats) => {
                if (err) {
                  return res.status(500).json({ error: 'Database error' });
                }

                res.json({
                  restaurant,
                  performanceSnapshot: {
                    newCustomersAcquired: Math.floor(Math.random() * 50) + 10, // Placeholder
                    customersReengaged: Math.floor(Math.random() * 30) + 5, // Placeholder
                    period: 'Last 7 Days'
                  },
                  activeCampaigns: campaigns,
                  pendingTasks: pendingTasks.slice(0, 3), // Show top 3 pending tasks
                  campaignStats: {
                    recentCampaigns: campaignStats.campaign_count
                  }
                });
              }
            );
          }
        );
      }
    );
  });
});

// Admin Dashboard Data
router.get('/admin', authenticateToken, requireAdmin, (req, res) => {
  // Get total restaurants count
  db.get('SELECT COUNT(*) as total_restaurants FROM restaurants', (err, restaurantCount) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    // Get campaigns launched in last 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    db.get(
      'SELECT COUNT(*) as recent_campaigns FROM campaigns WHERE created_at >= ?',
      [sevenDaysAgo.toISOString()],
      (err, campaignStats) => {
        if (err) {
          return res.status(500).json({ error: 'Database error' });
        }

        // Get restaurants with incomplete setup (those with pending checklist items)
        db.get(
          `SELECT COUNT(DISTINCT restaurant_id) as incomplete_setups 
           FROM checklist_status 
           WHERE is_complete = FALSE`,
          (err, incompleteSetups) => {
            if (err) {
              return res.status(500).json({ error: 'Database error' });
            }

            res.json({
              platformStats: {
                totalRestaurants: restaurantCount.total_restaurants,
                recentCampaigns: campaignStats.recent_campaigns,
                period: 'Last 7 Days'
              },
              needsAttention: {
                incompleteSetups: incompleteSetups.incomplete_setups
              }
            });
          }
        );
      }
    );
  });
});

// Get all restaurants (for admin)
router.get('/restaurants', authenticateToken, requireAdmin, (req, res) => {
  const { search } = req.query;
  
  let query = `
    SELECT r.*, u.email, u.created_at as signup_date 
    FROM restaurants r 
    JOIN users u ON r.user_id = u.user_id 
  `;
  let params = [];

  if (search) {
    query += ' WHERE r.name LIKE ? ';
    params.push(`%${search}%`);
  }

  query += ' ORDER BY r.created_at DESC';

  db.all(query, params, (err, restaurants) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    res.json({ restaurants });
  });
});

// Get restaurant campaigns
router.get('/campaigns', authenticateToken, requireRestaurant, getRestaurantContext, (req, res) => {
  const restaurantId = req.restaurantId;

  db.all(
    'SELECT * FROM campaigns WHERE restaurant_id = ? ORDER BY created_at DESC',
    [restaurantId],
    (err, campaigns) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      res.json({ campaigns });
    }
  );
});

// Update checklist item
router.put('/checklist/:itemId', authenticateToken, requireRestaurant, getRestaurantContext, (req, res) => {
  const itemId = parseInt(req.params.itemId);
  const { is_complete } = req.body;
  const restaurantId = req.restaurantId;

  // Verify the checklist item belongs to this restaurant
  db.get(
    'SELECT * FROM checklist_status WHERE status_id = ? AND restaurant_id = ?',
    [itemId, restaurantId],
    (err, item) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      if (!item) {
        return res.status(404).json({ error: 'Checklist item not found' });
      }

      // Update the item
      db.run(
        'UPDATE checklist_status SET is_complete = ?, updated_at = CURRENT_TIMESTAMP WHERE status_id = ?',
        [is_complete, itemId],
        function(err) {
          if (err) {
            return res.status(500).json({ error: 'Failed to update checklist item' });
          }

          res.json({ message: 'Checklist item updated successfully' });
        }
      );
    }
  );
});

module.exports = router;