"""
CSV parser utility for customer data processing
"""
import csv
import io
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import UploadFile

async def parse_customer_csv(file: UploadFile) -> Dict[str, Any]:
    """Parse customer CSV file and validate data"""
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        customers = []
        errors = []
        row_count = 0
        
        for row in csv_reader:
            row_count += 1
            validation_result = validate_customer_row(row, row_count)
            
            if validation_result["valid"]:
                customers.append(validation_result["customer"])
            else:
                errors.append(validation_result["error"])
        
        return {
            "success": True,
            "customers": customers,
            "errors": errors,
            "total_rows": row_count,
            "valid_rows": len(customers),
            "error_rows": len(errors)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": "Failed to parse CSV file",
            "details": str(e)
        }

def validate_customer_row(row: Dict[str, str], row_number: int) -> Dict[str, Any]:
    """Validate a single customer row"""
    required_fields = ['customer_name', 'phone_number', 'last_order_date']
    missing_fields = []
    
    # Check for required fields
    for field in required_fields:
        if not row.get(field) or not row[field].strip():
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "valid": False,
            "error": {
                "row": row_number,
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "data": row
            }
        }
    
    # Validate phone number format
    phone_number = row['phone_number'].strip()
    if not is_valid_phone_number(phone_number):
        return {
            "valid": False,
            "error": {
                "row": row_number,
                "message": "Invalid phone number format",
                "data": row
            }
        }
    
    # Validate date format
    last_order_date = row['last_order_date'].strip()
    if not is_valid_date(last_order_date):
        return {
            "valid": False,
            "error": {
                "row": row_number,
                "message": "Invalid date format (expected YYYY-MM-DD)",
                "data": row
            }
        }
    
    return {
        "valid": True,
        "customer": {
            "customer_name": row['customer_name'].strip(),
            "phone_number": phone_number,
            "last_order_date": last_order_date,
            "email": row.get('email', '').strip() if row.get('email') else None,
            "notes": row.get('notes', '').strip() if row.get('notes') else None
        }
    }

def is_valid_phone_number(phone_number: str) -> bool:
    """Basic phone number validation - accepts various formats"""
    phone_regex = r'^[\+]?[\d\s\-\(\)]{10,}$'
    return bool(re.match(phone_regex, phone_number))

def is_valid_date(date_string: str) -> bool:
    """Check if date string is in YYYY-MM-DD format and valid"""
    date_regex = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_regex, date_string):
        return False
    
    try:
        # Check if it's a valid date
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
        return parsed_date.strftime('%Y-%m-%d') == date_string
    except ValueError:
        return False

def filter_lapsed_customers(customers: List[Dict[str, Any]], days_threshold: int = 30) -> List[Dict[str, Any]]:
    """Filter customers who haven't ordered in the specified number of days"""
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    lapsed_customers = []
    for customer in customers:
        try:
            last_order_date = datetime.strptime(customer['last_order_date'], '%Y-%m-%d')
            if last_order_date < cutoff_date:
                lapsed_customers.append(customer)
        except ValueError:
            # Skip customers with invalid dates
            continue
    
    return lapsed_customers

def generate_sample_csv() -> str:
    """Generate sample CSV content for download"""
    sample_data = [
        'customer_name,phone_number,last_order_date,email',
        'John Smith,+1-555-123-4567,2023-10-15,john@email.com',
        'Sarah Johnson,(555) 234-5678,2023-09-22,sarah@email.com',
        'Mike Davis,555.345.6789,2023-08-30,mike@email.com',
        'Lisa Wilson,+15554567890,2023-11-05,lisa@email.com',
        'Tom Brown,555-567-8901,2023-07-18,tom@email.com'
    ]
    
    return '\n'.join(sample_data)

def validate_csv_headers(file_content: str) -> Dict[str, Any]:
    """Validate CSV headers before processing"""
    try:
        csv_reader = csv.DictReader(io.StringIO(file_content))
        headers = csv_reader.fieldnames
        
        required_headers = ['customer_name', 'phone_number', 'last_order_date']
        missing_headers = [h for h in required_headers if h not in headers]
        
        if missing_headers:
            return {
                "valid": False,
                "error": f"Missing required headers: {', '.join(missing_headers)}",
                "found_headers": headers,
                "required_headers": required_headers
            }
        
        return {
            "valid": True,
            "headers": headers
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Failed to read CSV headers: {str(e)}"
        }

def estimate_sms_cost(customer_count: int, cost_per_sms: float = 0.0075) -> Dict[str, Any]:
    """Estimate SMS campaign cost"""
    total_cost = customer_count * cost_per_sms
    
    return {
        "customer_count": customer_count,
        "cost_per_sms": cost_per_sms,
        "estimated_total": round(total_cost, 4),
        "currency": "USD"
    }