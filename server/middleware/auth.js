const jwt = require('jsonwebtoken');
const { db } = require('../models/database');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Middleware to verify JWT token
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Middleware to check if user has admin role
const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};

// Middleware to check if user has restaurant role or is admin impersonating
const requireRestaurant = (req, res, next) => {
  if (req.user.role !== 'restaurant' && !req.user.impersonating_restaurant_id) {
    return res.status(403).json({ error: 'Restaurant access required' });
  }
  next();
};

// Middleware to get current restaurant context
const getRestaurantContext = async (req, res, next) => {
  try {
    let restaurantId = null;
    
    if (req.user.role === 'restaurant') {
      // Get restaurant for this user
      db.get(
        'SELECT restaurant_id FROM restaurants WHERE user_id = ?',
        [req.user.user_id],
        (err, row) => {
          if (err) {
            return res.status(500).json({ error: 'Database error' });
          }
          if (!row) {
            return res.status(404).json({ error: 'Restaurant not found for user' });
          }
          req.restaurantId = row.restaurant_id;
          next();
        }
      );
    } else if (req.user.impersonating_restaurant_id) {
      // Admin is impersonating a restaurant
      req.restaurantId = req.user.impersonating_restaurant_id;
      next();
    } else {
      return res.status(403).json({ error: 'No restaurant context available' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};

module.exports = {
  authenticateToken,
  requireAdmin,
  requireRestaurant,
  getRestaurantContext,
  JWT_SECRET
};