import random
import string
from datetime import datetime

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{timestamp}-{random_chars}"

def validate_date_format(date_str):
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def format_date(date_obj):
    """Format date object to string"""
    return date_obj.strftime('%Y-%m-%d')
