const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { db } = require('../models/database');
const { authenticateToken, requireAdmin, JWT_SECRET } = require('../middleware/auth');

const router = express.Router();

// Register new user (restaurant)
router.post('/register', async (req, res) => {
  try {
    const { email, password, restaurantName, address, phone } = req.body;

    if (!email || !password || !restaurantName) {
      return res.status(400).json({ error: 'Email, password, and restaurant name are required' });
    }

    // Check if user already exists
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, existingUser) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      if (existingUser) {
        return res.status(400).json({ error: 'User already exists with this email' });
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 10);

      // Create user
      db.run(
        'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
        [email, hashedPassword, 'restaurant'],
        function(err) {
          if (err) {
            return res.status(500).json({ error: 'Failed to create user' });
          }

          const userId = this.lastID;

          // Create restaurant
          db.run(
            'INSERT INTO restaurants (user_id, name, address, phone) VALUES (?, ?, ?, ?)',
            [userId, restaurantName, address || '', phone || ''],
            function(err) {
              if (err) {
                return res.status(500).json({ error: 'Failed to create restaurant' });
              }

              const restaurantId = this.lastID;

              // Create default checklist items
              const defaultChecklistItems = [
                'Complete your Google Business Profile setup',
                'Upload high-quality photos of your dishes',
                'Set up your social media accounts',
                'Create your first customer list'
              ];

              const insertPromises = defaultChecklistItems.map(item => {
                return new Promise((resolve, reject) => {
                  db.run(
                    'INSERT INTO checklist_status (restaurant_id, checklist_item_name, is_complete) VALUES (?, ?, ?)',
                    [restaurantId, item, false],
                    (err) => {
                      if (err) reject(err);
                      else resolve();
                    }
                  );
                });
              });

              Promise.all(insertPromises)
                .then(() => {
                  // Generate JWT token
                  const token = jwt.sign(
                    { user_id: userId, email, role: 'restaurant' },
                    JWT_SECRET,
                    { expiresIn: '24h' }
                  );

                  res.status(201).json({
                    message: 'User and restaurant created successfully',
                    token,
                    user: {
                      user_id: userId,
                      email,
                      role: 'restaurant',
                      restaurant: {
                        restaurant_id: restaurantId,
                        name: restaurantName,
                        address,
                        phone
                      }
                    }
                  });
                })
                .catch(() => {
                  res.status(500).json({ error: 'Failed to create default checklist items' });
                });
            }
          );
        }
      );
    });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Login
router.post('/login', (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    // Find user
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Check password
      const isValidPassword = await bcrypt.compare(password, user.password_hash);
      if (!isValidPassword) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      // Generate JWT token
      const token = jwt.sign(
        { user_id: user.user_id, email: user.email, role: user.role },
        JWT_SECRET,
        { expiresIn: '24h' }
      );

      // Get restaurant info if user is restaurant owner
      if (user.role === 'restaurant') {
        db.get('SELECT * FROM restaurants WHERE user_id = ?', [user.user_id], (err, restaurant) => {
          if (err) {
            return res.status(500).json({ error: 'Database error' });
          }

          res.json({
            message: 'Login successful',
            token,
            user: {
              user_id: user.user_id,
              email: user.email,
              role: user.role,
              restaurant: restaurant || null
            }
          });
        });
      } else {
        res.json({
          message: 'Login successful',
          token,
          user: {
            user_id: user.user_id,
            email: user.email,
            role: user.role
          }
        });
      }
    });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Get current user info
router.get('/me', authenticateToken, (req, res) => {
  const userId = req.user.user_id;

  db.get('SELECT user_id, email, role FROM users WHERE user_id = ?', [userId], (err, user) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    if (user.role === 'restaurant') {
      db.get('SELECT * FROM restaurants WHERE user_id = ?', [userId], (err, restaurant) => {
        if (err) {
          return res.status(500).json({ error: 'Database error' });
        }

        res.json({
          user: {
            ...user,
            restaurant: restaurant || null,
            impersonating_restaurant_id: req.user.impersonating_restaurant_id || null
          }
        });
      });
    } else {
      res.json({
        user: {
          ...user,
          impersonating_restaurant_id: req.user.impersonating_restaurant_id || null
        }
      });
    }
  });
});

// Admin impersonation
router.post('/impersonate/:restaurantId', authenticateToken, requireAdmin, (req, res) => {
  const restaurantId = parseInt(req.params.restaurantId);

  // Verify restaurant exists
  db.get('SELECT * FROM restaurants WHERE restaurant_id = ?', [restaurantId], (err, restaurant) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    if (!restaurant) {
      return res.status(404).json({ error: 'Restaurant not found' });
    }

    // Generate new token with impersonation
    const token = jwt.sign(
      { 
        user_id: req.user.user_id, 
        email: req.user.email, 
        role: req.user.role,
        impersonating_restaurant_id: restaurantId
      },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      message: 'Impersonation started',
      token,
      impersonating_restaurant: restaurant
    });
  });
});

// End impersonation
router.post('/end-impersonation', authenticateToken, requireAdmin, (req, res) => {
  // Generate new token without impersonation
  const token = jwt.sign(
    { 
      user_id: req.user.user_id, 
      email: req.user.email, 
      role: req.user.role
    },
    JWT_SECRET,
    { expiresIn: '24h' }
  );

  res.json({
    message: 'Impersonation ended',
    token
  });
});

module.exports = router;