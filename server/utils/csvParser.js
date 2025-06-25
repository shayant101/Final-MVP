const csv = require('csv-parser');
const fs = require('fs');

const parseCustomerCSV = (filePath) => {
  return new Promise((resolve, reject) => {
    const customers = [];
    const errors = [];
    let rowCount = 0;

    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        rowCount++;
        const validationResult = validateCustomerRow(row, rowCount);
        
        if (validationResult.valid) {
          customers.push(validationResult.customer);
        } else {
          errors.push(validationResult.error);
        }
      })
      .on('end', () => {
        // Clean up uploaded file
        fs.unlink(filePath, (err) => {
          if (err) console.error('Error deleting uploaded file:', err);
        });

        resolve({
          success: true,
          customers,
          errors,
          totalRows: rowCount,
          validRows: customers.length,
          errorRows: errors.length
        });
      })
      .on('error', (error) => {
        reject({
          success: false,
          error: 'Failed to parse CSV file',
          details: error.message
        });
      });
  });
};

const validateCustomerRow = (row, rowNumber) => {
  const requiredFields = ['customer_name', 'phone_number', 'last_order_date'];
  const missingFields = [];

  // Check for required fields
  requiredFields.forEach(field => {
    if (!row[field] || row[field].trim() === '') {
      missingFields.push(field);
    }
  });

  if (missingFields.length > 0) {
    return {
      valid: false,
      error: {
        row: rowNumber,
        message: `Missing required fields: ${missingFields.join(', ')}`,
        data: row
      }
    };
  }

  // Validate phone number format
  const phoneNumber = row.phone_number.trim();
  if (!isValidPhoneNumber(phoneNumber)) {
    return {
      valid: false,
      error: {
        row: rowNumber,
        message: 'Invalid phone number format',
        data: row
      }
    };
  }

  // Validate date format
  const lastOrderDate = row.last_order_date.trim();
  if (!isValidDate(lastOrderDate)) {
    return {
      valid: false,
      error: {
        row: rowNumber,
        message: 'Invalid date format (expected YYYY-MM-DD)',
        data: row
      }
    };
  }

  return {
    valid: true,
    customer: {
      customer_name: row.customer_name.trim(),
      phone_number: phoneNumber,
      last_order_date: lastOrderDate,
      email: row.email ? row.email.trim() : null,
      notes: row.notes ? row.notes.trim() : null
    }
  };
};

const isValidPhoneNumber = (phoneNumber) => {
  // Basic phone number validation - accepts various formats
  const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
  return phoneRegex.test(phoneNumber);
};

const isValidDate = (dateString) => {
  // Check YYYY-MM-DD format
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(dateString)) {
    return false;
  }

  // Check if it's a valid date
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date) && date.toISOString().slice(0, 10) === dateString;
};

const filterLapsedCustomers = (customers, daysThreshold = 30) => {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysThreshold);

  return customers.filter(customer => {
    const lastOrderDate = new Date(customer.last_order_date);
    return lastOrderDate < cutoffDate;
  });
};

const generateSampleCSV = () => {
  const sampleData = [
    'customer_name,phone_number,last_order_date,email',
    'John Smith,+1-555-123-4567,2023-10-15,john@email.com',
    'Sarah Johnson,(555) 234-5678,2023-09-22,sarah@email.com',
    'Mike Davis,555.345.6789,2023-08-30,mike@email.com',
    'Lisa Wilson,+15554567890,2023-11-05,lisa@email.com',
    'Tom Brown,555-567-8901,2023-07-18,tom@email.com'
  ];

  return sampleData.join('\n');
};

module.exports = {
  parseCustomerCSV,
  validateCustomerRow,
  filterLapsedCustomers,
  generateSampleCSV,
  isValidPhoneNumber,
  isValidDate
};