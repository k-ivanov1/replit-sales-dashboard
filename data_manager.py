import os
from supabase import create_client
import pandas as pd

# Supabase credentials (replace with your actual keys)
SUPABASE_URL = "https://hqhwaopnbyjhhcixxoer.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhxaHdhb3BuYnlqaGhjaXh4b2VyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA0ODgyNTksImV4cCI6MjA1NjA2NDI1OX0.LZuBIBlYXKbToF71Arh8P2_5fS8DUfifkAl4jurOmWg"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

### STOCK OUT (SALES ORDERS) ###

def get_stock_out():
    """Fetch all stock-out (sales) records from Supabase."""
    response = supabase.table("stock_out").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def add_stock_out(order_data):
    """Insert new sales (stock-out) record into Supabase."""
    response = supabase.table("stock_out").insert(order_data).execute()
    return response

def delete_stock_out(order_id):
    """Delete a stock-out entry by ID."""
    supabase.table("stock_out").delete().eq("id", order_id).execute()


### STOCK IN (TEA & OTHER PRODUCTS) ###

def get_stock_in():
    """Fetch all stock-in entries from Supabase."""
    response = supabase.table("stock_in").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def add_stock_in(stock_data):
    """Insert new stock-in record into Supabase."""
    response = supabase.table("stock_in").insert(stock_data).execute()
    return response

def delete_stock_in(stock_id):
    """Delete a stock-in entry by ID."""
    supabase.table("stock_in").delete().eq("id", stock_id).execute()


### WASTAGE TRACKING ###

def get_wastage():
    """Fetch all wastage records from Supabase."""
    response = supabase.table("wastage").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def add_wastage(wastage_data):
    """Insert new wastage record into Supabase."""
    response = supabase.table("wastage").insert(wastage_data).execute()
    return response

def delete_wastage(wastage_id):
    """Delete a wastage entry by ID."""
    supabase.table("wastage").delete().eq("id", wastage_id).execute()


### PRODUCTS & RECIPES ###

def get_products():
    """Fetch all product details from Supabase."""
    response = supabase.table("products").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def add_product(product_data):
    """Insert a new product into Supabase."""
    response = supabase.table("products").insert(product_data).execute()
    return response

def delete_product(product_id):
    """Delete a product by ID."""
    supabase.table("products").delete().eq("id", product_id).execute()
