const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Create database connection
const dbPath = path.join(__dirname, '../database.sqlite');
const db = new sqlite3.Database(dbPath);

// Initialize database tables
const initializeDatabase = () => {
  return new Promise((resolve, reject) => {
    db.serialize(() => {
      // Users table
      db.run(`
        CREATE TABLE IF NOT EXISTS users (
          user_id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL CHECK (role IN ('restaurant', 'admin')),
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Restaurants table
      db.run(`
        CREATE TABLE IF NOT EXISTS restaurants (
          restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          address TEXT,
          phone TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
      `);

      // Campaigns table
      db.run(`
        CREATE TABLE IF NOT EXISTS campaigns (
          campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
          restaurant_id INTEGER NOT NULL,
          campaign_type TEXT NOT NULL CHECK (campaign_type IN ('ad', 'sms')),
          status TEXT NOT NULL CHECK (status IN ('active', 'draft', 'completed', 'paused')),
          name TEXT NOT NULL,
          details TEXT,
          budget DECIMAL(10,2),
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
        )
      `);

      // Checklist Status table
      db.run(`
        CREATE TABLE IF NOT EXISTS checklist_status (
          status_id INTEGER PRIMARY KEY AUTOINCREMENT,
          restaurant_id INTEGER NOT NULL,
          checklist_item_name TEXT NOT NULL,
          is_complete BOOLEAN DEFAULT FALSE,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
        )
      `);

      // Sessions table for session management
      db.run(`
        CREATE TABLE IF NOT EXISTS sessions (
          session_id TEXT PRIMARY KEY,
          user_id INTEGER NOT NULL,
          impersonating_restaurant_id INTEGER,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          expires_at DATETIME NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users (user_id),
          FOREIGN KEY (impersonating_restaurant_id) REFERENCES restaurants (restaurant_id)
        )
      `, (err) => {
        if (err) {
          reject(err);
        } else {
          console.log('✅ Database tables initialized successfully');
          resolve();
        }
      });
    });
  });
};

// Create default admin user if it doesn't exist
const createDefaultAdmin = async () => {
  const bcrypt = require('bcryptjs');
  
  return new Promise((resolve, reject) => {
    // Check if admin exists
    db.get('SELECT * FROM users WHERE role = "admin" LIMIT 1', (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      
      if (!row) {
        // Create default admin
        const defaultEmail = 'admin@momentum.com';
        const defaultPassword = 'admin123'; // Should be changed in production
        const hashedPassword = bcrypt.hashSync(defaultPassword, 10);
        
        db.run(
          'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
          [defaultEmail, hashedPassword, 'admin'],
          function(err) {
            if (err) {
              reject(err);
            } else {
              console.log('✅ Default admin user created:', defaultEmail, '/ Password:', defaultPassword);
              resolve();
            }
          }
        );
      } else {
        console.log('✅ Admin user already exists');
        resolve();
      }
    });
  });
};

module.exports = {
  db,
  initializeDatabase,
  createDefaultAdmin
};