const express = require('express');
const router = express.Router();
const { db } = require('../models/database');

// GET /api/checklist/categories - Get all categories with optional type filter
router.get('/categories', async (req, res) => {
  try {
    const { type } = req.query; // 'foundational' or 'ongoing'
    
    let query = 'SELECT * FROM checklist_categories ORDER BY order_in_list';
    let params = [];
    
    if (type) {
      query = 'SELECT * FROM checklist_categories WHERE type = ? ORDER BY order_in_list';
      params = [type];
    }
    
    db.all(query, params, (err, categories) => {
      if (err) {
        console.error('Error fetching categories:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to fetch categories'
        });
      }
      
      res.json({
        success: true,
        categories: categories
      });
    });
  } catch (error) {
    console.error('Error in categories route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// GET /api/checklist/items/:categoryId - Get items for a specific category
router.get('/items/:categoryId', async (req, res) => {
  try {
    const { categoryId } = req.params;
    
    const query = `
      SELECT * FROM checklist_items 
      WHERE category_id = ? 
      ORDER BY order_in_category
    `;
    
    db.all(query, [categoryId], (err, items) => {
      if (err) {
        console.error('Error fetching items:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to fetch items'
        });
      }
      
      res.json({
        success: true,
        items: items
      });
    });
  } catch (error) {
    console.error('Error in items route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// GET /api/checklist/status/:restaurantId - Get checklist status for restaurant
router.get('/status/:restaurantId', async (req, res) => {
  try {
    const { restaurantId } = req.params;
    
    const query = `
      SELECT 
        rcs.*,
        ci.title,
        ci.category_id,
        cc.name as category_name,
        cc.type as category_type
      FROM restaurant_checklist_status rcs
      JOIN checklist_items ci ON rcs.item_id = ci.item_id
      JOIN checklist_categories cc ON ci.category_id = cc.category_id
      WHERE rcs.restaurant_id = ?
    `;
    
    db.all(query, [restaurantId], (err, statuses) => {
      if (err) {
        console.error('Error fetching status:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to fetch status'
        });
      }
      
      res.json({
        success: true,
        statuses: statuses
      });
    });
  } catch (error) {
    console.error('Error in status route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// PUT /api/checklist/status/:restaurantId/:itemId - Update item status
router.put('/status/:restaurantId/:itemId', async (req, res) => {
  try {
    const { restaurantId, itemId } = req.params;
    const { status, notes } = req.body;
    
    // Validate status
    const validStatuses = ['pending', 'in_progress', 'completed', 'not_applicable'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid status value'
      });
    }
    
    const query = `
      INSERT OR REPLACE INTO restaurant_checklist_status 
      (restaurant_id, item_id, status, notes, last_updated_at)
      VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    `;
    
    db.run(query, [restaurantId, itemId, status, notes || null], function(err) {
      if (err) {
        console.error('Error updating status:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to update status'
        });
      }
      
      res.json({
        success: true,
        message: 'Status updated successfully',
        statusId: this.lastID
      });
    });
  } catch (error) {
    console.error('Error in update status route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// GET /api/checklist/progress/:restaurantId - Get progress statistics
router.get('/progress/:restaurantId', async (req, res) => {
  try {
    const { restaurantId } = req.params;
    const { type } = req.query; // 'foundational' or 'ongoing'
    
    let categoryFilter = '';
    let params = [restaurantId];
    
    if (type) {
      categoryFilter = 'AND cc.type = ?';
      params.push(type);
    }
    
    const query = `
      SELECT 
        cc.type,
        COUNT(ci.item_id) as total_items,
        COUNT(CASE WHEN rcs.status = 'completed' THEN 1 END) as completed_items,
        COUNT(CASE WHEN ci.is_critical = 1 THEN 1 END) as critical_items,
        COUNT(CASE WHEN ci.is_critical = 1 AND rcs.status = 'completed' THEN 1 END) as completed_critical_items
      FROM checklist_items ci
      JOIN checklist_categories cc ON ci.category_id = cc.category_id
      LEFT JOIN restaurant_checklist_status rcs ON ci.item_id = rcs.item_id AND rcs.restaurant_id = ?
      WHERE 1=1 ${categoryFilter}
      GROUP BY cc.type
    `;
    
    db.all(query, params, (err, results) => {
      if (err) {
        console.error('Error calculating progress:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to calculate progress'
        });
      }
      
      const progress = {};
      results.forEach(result => {
        const completionPercentage = result.total_items > 0 
          ? Math.round((result.completed_items / result.total_items) * 100)
          : 0;
        
        const criticalCompletionPercentage = result.critical_items > 0
          ? Math.round((result.completed_critical_items / result.critical_items) * 100)
          : 0;
        
        progress[result.type] = {
          totalItems: result.total_items,
          completedItems: result.completed_items,
          completionPercentage: completionPercentage,
          criticalItems: result.critical_items,
          completedCriticalItems: result.completed_critical_items,
          criticalCompletionPercentage: criticalCompletionPercentage
        };
      });
      
      res.json({
        success: true,
        progress: progress
      });
    });
  } catch (error) {
    console.error('Error in progress route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// GET /api/checklist/categories-with-items - Get all categories with their items
router.get('/categories-with-items', async (req, res) => {
  try {
    const { type, restaurantId } = req.query;
    
    let categoryFilter = '';
    let params = [];
    
    if (type) {
      categoryFilter = 'WHERE cc.type = ?';
      params.push(type);
    }
    
    const categoriesQuery = `
      SELECT * FROM checklist_categories cc
      ${categoryFilter}
      ORDER BY cc.order_in_list
    `;
    
    db.all(categoriesQuery, params, (err, categories) => {
      if (err) {
        console.error('Error fetching categories:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to fetch categories'
        });
      }
      
      // Get items for each category
      const categoryPromises = categories.map(category => {
        return new Promise((resolve, reject) => {
          let itemsQuery, itemsParams;
          
          if (restaurantId) {
            itemsQuery = `
              SELECT
                ci.*,
                rcs.status,
                rcs.notes,
                rcs.last_updated_at as status_updated_at
              FROM checklist_items ci
              LEFT JOIN restaurant_checklist_status rcs ON ci.item_id = rcs.item_id AND rcs.restaurant_id = ?
              WHERE ci.category_id = ?
              ORDER BY ci.order_in_category
            `;
            itemsParams = [restaurantId, category.category_id];
          } else {
            itemsQuery = `
              SELECT
                ci.*,
                NULL as status,
                NULL as notes,
                NULL as status_updated_at
              FROM checklist_items ci
              WHERE ci.category_id = ?
              ORDER BY ci.order_in_category
            `;
            itemsParams = [category.category_id];
          }
          
          db.all(itemsQuery, itemsParams, (err, items) => {
            if (err) {
              console.error('Error fetching items for category', category.category_id, ':', err);
              reject(err);
            } else {
              console.log(`Category ${category.category_id}: Found ${items.length} items`);
              if (items.length === 0) {
                console.log('Query:', itemsQuery);
                console.log('Params:', itemsParams);
              }
              resolve({
                ...category,
                items: items
              });
            }
          });
        });
      });
      
      Promise.all(categoryPromises)
        .then(categoriesWithItems => {
          res.json({
            success: true,
            categories: categoriesWithItems
          });
        })
        .catch(error => {
          console.error('Error fetching items:', error);
          res.status(500).json({
            success: false,
            error: 'Failed to fetch items'
          });
        });
    });
  } catch (error) {
    console.error('Error in categories-with-items route:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

module.exports = router;