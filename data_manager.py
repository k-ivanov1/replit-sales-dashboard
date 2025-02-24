import pandas as pd
import os
from datetime import datetime

DATA_FILE = "data/sales.csv"

def initialize_data_file():
    """Create data file if it doesn't exist"""
    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'date_of_sale',
            'product_name',
            'size',
            'type',
            'sku',
            'customer_name',
            'order_number',
            'batch_number',
            'best_before',
            'production_date',
            'quantity',
            'price_per_unit',
            'total_price',
            'delivery_method',
            'labelling_match',
            'checked_by'
        ])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    """Load data from CSV file"""
    initialize_data_file()
    df = pd.read_csv(DATA_FILE)

    # Convert date columns
    date_columns = ['date_of_sale', 'best_before', 'production_date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col]).dt.date

    return df

def add_products_to_order(order_data, products_data):
    """Add multiple products to an order"""
    df = load_data()

    new_records = []
    for product in products_data:
        record = {
            'date_of_sale': order_data['date_of_sale'],
            'product_name': product['product_name'],
            'size': product['size'],
            'type': product['type'],
            'sku': product['sku'],
            'customer_name': order_data['customer_name'],
            'order_number': order_data['order_number'],
            'batch_number': product['batch_number'],
            'best_before': product['best_before'],
            'production_date': product['production_date'],
            'quantity': product['quantity'],
            'price_per_unit': product['price_per_unit'],
            'total_price': product['quantity'] * product['price_per_unit'],
            'delivery_method': order_data['delivery_method'],
            'labelling_match': product['labelling_match'],
            'checked_by': product['checked_by']
        }
        new_records.append(record)

    new_df = pd.DataFrame(new_records)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def get_orders_summary():
    """Get summary of orders with their products"""
    df = load_data()
    return df.groupby('order_number').agg({
        'date_of_sale': 'first',
        'customer_name': 'first',
        'product_name': lambda x: ', '.join(x),
        'quantity': 'sum',
        'total_price': 'sum',
        'delivery_method': 'first'
    }).reset_index()

def get_order_details(order_number):
    """Get all products in a specific order"""
    df = load_data()
    return df[df['order_number'] == order_number]

def delete_order(order_number):
    """Delete an entire order and its products"""
    df = load_data()
    df = df[df['order_number'] != order_number]
    df.to_csv(DATA_FILE, index=False)

def update_order(order_number, order_data, products_data):
    """Update an existing order with new data"""
    df = load_data()
    # Remove existing order
    df = df[df['order_number'] != order_number]

    # Add updated order data
    new_records = []
    for product in products_data:
        record = {
            'date_of_sale': order_data['date_of_sale'],
            'product_name': product['product_name'],
            'size': product['size'],
            'type': product['type'],
            'sku': product['sku'],
            'customer_name': order_data['customer_name'],
            'order_number': order_number,
            'batch_number': product['batch_number'],
            'best_before': product['best_before'],
            'production_date': product['production_date'],
            'quantity': product['quantity'],
            'price_per_unit': product['price_per_unit'],
            'total_price': product['quantity'] * product['price_per_unit'],
            'delivery_method': order_data['delivery_method'],
            'labelling_match': product['labelling_match'],
            'checked_by': product['checked_by']
        }
        new_records.append(record)

    new_df = pd.DataFrame(new_records)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)