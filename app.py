import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import data_manager as dm
import utils
import uuid

# Page configuration
st.set_page_config(
    page_title="Tea Inventory & Sales Dashboard",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #34495e;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stat-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f1f8e9;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #546e7a;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .order-container {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.8rem;
        background-color: white;
    }
    .error-msg {
        color: #d32f2f;
        background-color: #ffebee;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    .success-msg {
        color: #2e7d32;
        background-color: #e8f5e9;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .badge-success {
        background-color: #4caf50;
    }
    .badge-warning {
        background-color: #ff9800;
    }
    .badge-danger {
        background-color: #f44336;
    }
    .small-button {
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.8rem;
        color: #78909c;
    }
    .tab-content {
        padding: 1rem 0;
    }
    .color-primary {
        color: #1976d2;
    }
    .form-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .table-actions {
        display: flex;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []
if 'data_changed' not in st.session_state:
    st.session_state.data_changed = False
if 'editing_order' not in st.session_state:
    st.session_state.editing_order = None
if 'viewing_order' not in st.session_state:
    st.session_state.viewing_order = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "dashboard"
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'deleted_product_index' not in st.session_state:
    st.session_state.deleted_product_index = None

def add_notification(message, type="info"):
    """Add a notification to be displayed to the user"""
    notification_id = str(uuid.uuid4())
    st.session_state.notifications.append({
        "id": notification_id,
        "message": message,
        "type": type,
        "timestamp": datetime.now()
    })
    return notification_id

def show_notifications():
    """Display any active notifications and allow dismissal"""
    if st.session_state.notifications:
        with st.container():
            for i, note in enumerate(st.session_state.notifications):
                if note["type"] == "success":
                    st.success(note["message"], icon="✅")
                elif note["type"] == "error":
                    st.error(note["message"], icon="❌")
                elif note["type"] == "warning":
                    st.warning(note["message"], icon="⚠️")
                else:
                    st.info(note["message"], icon="ℹ️")
                
        # Clear notifications after displaying
        st.session_state.notifications = []

def add_product_to_order(product_data):
    """Add product to current order in session state"""
    # Validate essential fields
    required_fields = ['product_name', 'quantity', 'price_per_unit', 'batch_number']
    
    if all(product_data.get(field) for field in required_fields):
        # Calculate total price
        product_data['total_price'] = product_data['quantity'] * product_data['price_per_unit']
        # Convert labelling_match to boolean for consistency
        product_data['labelling_match'] = product_data['labelling_match'] == 'Yes'
        st.session_state.products.append(product_data)
        return True
    return False

def clear_form():
    """Reset the form through the session state"""
    st.session_state.products = []
    st.session_state.editing_order = None
    st.session_state.viewing_order = None

def remove_product(index):
    """Remove a product from the current order"""
    if 0 <= index < len(st.session_state.products):
        st.session_state.products.pop(index)
        add_notification("Product removed from order", "info")
        return True
    return False

def main():
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Tea+Shop+Logo", width=150)
        st.markdown("### 🍵 Tea Shop Inventory")
        
        # Main navigation
        st.markdown("### Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True, 
                   help="View sales data and analytics"):
            st.session_state.active_tab = "dashboard"
            st.session_state.viewing_order = None
            st.session_state.editing_order = None
            st.rerun()
            
        if st.button("📝 New Sales Entry", use_container_width=True,
                   help="Create a new sales order"):
            st.session_state.active_tab = "sales_entry"
            st.session_state.viewing_order = None
            st.session_state.editing_order = None
            st.rerun()
            
        if st.button("📦 Stock Management", use_container_width=True,
                   help="Manage inventory and stock"):
            st.session_state.active_tab = "stock"
            st.session_state.viewing_order = None
            st.session_state.editing_order = None
            st.rerun()
            
        if st.button("🔍 Search Orders", use_container_width=True,
                   help="Search and filter orders"):
            st.session_state.active_tab = "search"
            st.session_state.viewing_order = None
            st.session_state.editing_order = None
            st.rerun()
        
        # Additional info
        st.markdown("---")
        st.markdown("### System Info")
        products_count = len(dm.get_products())
        orders_count = len(dm.get_stock_out().drop_duplicates('order_number'))
        st.markdown(f"🏷️ **Products**: {products_count}")
        st.markdown(f"🛒 **Orders**: {orders_count}")
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.data_changed = True
            add_notification("Data refreshed", "info")
            st.rerun()

    # Display notifications at the top
    show_notifications()
    
    # Main content area based on active tab
    if st.session_state.active_tab == "dashboard":
        show_dashboard()
    elif st.session_state.active_tab == "sales_entry":
        if st.session_state.editing_order:
            show_edit_form()
        else:
            show_data_entry_form()
    elif st.session_state.active_tab == "stock":
        show_stock_management()
    elif st.session_state.active_tab == "search":
        show_search_page()
    else:
        show_dashboard()  # Default view

def show_order_details(order_number, order_summary, filtered_df):
    """Show detailed view of an order with edit and delete options"""
    # Header with back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", key="back_to_orders"):
            st.session_state.viewing_order = None
            st.rerun()
    with col2:
        st.markdown(f"### Order: {order_number}")
    
    # Order information card
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### Order Details")
            st.markdown(f"**Date:** {order_summary['date_of_sale']}")
            st.markdown(f"**Customer:** {order_summary['customer_name']}")
        with col2:
            st.markdown("#### Delivery Details")
            st.markdown(f"**Method:** {order_summary['delivery_method']}")
            # Add more delivery details if available
        with col3:
            st.markdown("#### Financial Details")
            st.markdown(f"**Total Items:** {order_summary['quantity']}")
            st.markdown(f"**Total Price:** ${order_summary['total_price']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Order products with better formatting
    st.markdown("### Order Items")
    order_products = filtered_df[filtered_df['order_number'] == order_number]
    
    # Display order items in a table
    st.dataframe(
        order_products[[
            'product_name', 'size', 'type', 'sku', 'quantity',
            'price_per_unit', 'total_price', 'batch_number', 
            'best_before'
        ]].style.format({
            'price_per_unit': '${:.2f}',
            'total_price': '${:.2f}'
        }),
        use_container_width=True,
        column_config={
            "product_name": "Product",
            "size": "Size",
            "type": "Type",
            "sku": "SKU",
            "quantity": "Qty",
            "price_per_unit": "Unit Price",
            "total_price": "Total",
            "batch_number": "Batch",
            "best_before": "Best Before"
        }
    )

    # Action buttons in a card
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Edit Order", key="edit_order_btn"):
                st.session_state.editing_order = order_number
                st.session_state.active_tab = "sales_entry"
                st.rerun()
        with col2:
            if st.button("🖨️ Print Invoice", key="print_invoice_btn"):
                add_notification("Invoice printing is not implemented yet", "warning")
        with col3:
            delete_btn = st.button("🗑️ Delete Order", key="delete_order_btn")
            if delete_btn:
                if st.session_state.get('confirm_delete') == order_number:
                    dm.delete_stock_out_by_order(order_number)
                    st.session_state.pop('confirm_delete')
                    add_notification("Order deleted successfully!", "success")
                    st.session_state.viewing_order = None
                    st.session_state.data_changed = True
                    st.rerun()
                else:
                    st.session_state.confirm_delete = order_number
                    st.warning("Click delete again to confirm")
        st.markdown('</div>', unsafe_allow_html=True)

def show_edit_form():
    """Display form for editing an existing order"""
    # Header with navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", key="back_from_edit"):
            clear_form()
            st.rerun()
    with col2:
        st.markdown(f"### Edit Order: {st.session_state.editing_order}")

    # Load existing order data
    order_data = dm.get_stock_out_by_order(st.session_state.editing_order)
    if order_data.empty:
        add_notification("Order not found!", "error")
        clear_form()
        st.rerun()
        return

    # Initialize products if empty
    if not st.session_state.products:
        # Convert pandas dataframe to list of dicts for session state
        st.session_state.products = order_data.to_dict('records')
    
    # Order details card
    with st.container():
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### Order Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            sale_date = st.date_input(
                "Date of Sale",
                value=pd.to_datetime(order_data['date'].iloc[0])
            )
        with col2:
            customer_name = st.text_input(
                "Customer Name",
                value=order_data['customer_name'].iloc[0]
            )
        with col3:
            delivery_options = ['Courier', 'Pickup', 'Post']
            current_method = order_data['delivery_method'].iloc[0]
            # Handle case if current method is not in the list
            if current_method not in delivery_options:
                delivery_options.append(current_method)
            
            delivery_method = st.selectbox(
                "Delivery Method",
                options=delivery_options,
                index=delivery_options.index(current_method)
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Display current order products with edit/delete capabilities
    if st.session_state.products:
        st.markdown("### Current Order Items")
        
        # Create a better styled table
        for i, product in enumerate(st.session_state.products):
            with st.container():
                st.markdown('<div class="order-container">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{product['product_name']}**")
                    if 'size' in product and product['size']:
                        st.markdown(f"Size: {product['size']}")
                    if 'batch_number' in product and product['batch_number']:
                        st.markdown(f"Batch: {product['batch_number']}")
                
                with col2:
                    st.markdown(f"Quantity: **{product['quantity']}**")
                    if 'best_before' in product and product['best_before']:
                        st.markdown(f"Best Before: {product['best_before']}")
                
                with col3:
                    price = product.get('price_per_unit', 0)
                    total = product.get('total_price', price * product.get('quantity', 0))
                    st.markdown(f"Unit Price: **${price:.2f}**")
                    st.markdown(f"Total: **${total:.2f}**")
                
                with col4:
                    if st.button("🗑️", key=f"delete_product_{i}", help="Remove this product"):
                        st.session_state.deleted_product_index = i
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle product deletion
        if st.session_state.deleted_product_index is not None:
            if remove_product(st.session_state.deleted_product_index):
                st.session_state.deleted_product_index = None
                st.rerun()

    # Add new product form
    with st.container():
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### Add New Product to Order")
        
        with st.form(key='edit_product_form'):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                product_name = st.text_input("Product Name", key="edit_prod_name")
                product_type = st.selectbox("Type", ["tea", "gear", "books"], key="edit_prod_type")
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, key="edit_quantity")
                size = st.text_input("Size/Weight", key="edit_size")
            with col3:
                price_per_unit = st.number_input("Price per Unit ($)", min_value=0.01, value=10.0, step=0.01, key="edit_price")
                sku = st.text_input("SKU", key="edit_sku")
            with col4:
                batch_number = st.text_input("Batch Number", key="edit_batch")
                best_before = st.date_input("Best Before", value=datetime.now() + timedelta(days=30), key="edit_best_before")

            # Hidden fields with default values
            production_date = datetime.now()
            labelling_match = "Yes"
            checked_by = customer_name  # Default to customer name
            
            submit = st.form_submit_button("Add Product to Order")
            
            if submit:
                product_data = {
                    'product_name': product_name,
                    'type': product_type,
                    'size': size,
                    'sku': sku,
                    'quantity': quantity,
                    'price_per_unit': price_per_unit,
                    'batch_number': batch_number,
                    'production_date': production_date,
                    'best_before': best_before,
                    'labelling_match': labelling_match,
                    'checked_by': checked_by
                }
                
                if add_product_to_order(product_data):
                    add_notification("Product added to order!", "success")
                    st.rerun()
                else:
                    add_notification("Please fill in required product details.", "error")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons for the entire order
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Update Order", key="update_order_btn", type="primary"):
            if len(st.session_state.products) > 0:
                order_data = {
                    'date': sale_date.strftime("%Y-%m-%d"),
                    'customer_name': customer_name,
                    'delivery_method': delivery_method,
                    'order_number': st.session_state.editing_order
                }
                # Update the order
                dm.delete_stock_out_by_order(st.session_state.editing_order)
                dm.add_stock_out_batch(order_data, st.session_state.products)
                
                add_notification("Order updated successfully!", "success")
                clear_form()
                st.session_state.data_changed = True
                st.session_state.active_tab = "dashboard"
                st.rerun()
            else:
                add_notification("Cannot save an order with no products.", "error")
    
    with col2:
        if st.button("❌ Cancel", key="cancel_edit_btn"):
            clear_form()
            st.session_state.active_tab = "dashboard"
            st.rerun()

def show_data_entry_form():
    """Display form for creating a new sales order"""
    st.markdown("## 📝 New Sales Entry")
    
    # Order details card
    with st.container():
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### Order Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sale_date = st.date_input(
                "Date of Sale",
                value=datetime.now()
            )
        
        with col2:
            customer_name = st.text_input("Customer Name")
        
        with col3:
            suggested_order = utils.generate_order_number()
            order_number = st.text_input("Order Number", value=suggested_order)
            delivery_method = st.selectbox(
                "Delivery Method",
                options=['Courier', 'Pickup', 'Post']
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Add product form
    with st.container():
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### Add Products")
        
        with st.form(key='product_form'):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                product_name = st.text_input("Product Name", key="new_prod_name")
                product_type = st.selectbox("Type", ["tea", "gear", "books"], key="new_prod_type")
            
            with col2:
                quantity = st.number_input("Quantity", min_value=1, value=1, key="new_quantity")
                size = st.text_input("Size/Weight", key="new_size")
            
            with col3:
                price_per_unit = st.number_input("Price per Unit ($)", min_value=0.01, value=10.0, step=0.01, key="new_price")
                sku = st.text_input("SKU", key="new_sku")
            
            with col4:
                batch_number = st.text_input("Batch Number", key="new_batch")
                best_before = st.date_input("Best Before", value=datetime.now() + timedelta(days=30), key="new_best_before")
            
            # Hidden fields with default values
            production_date = datetime.now()
            labelling_match = "Yes"
            checked_by = st.session_state.get('user_name', 'Staff')
            
            submit = st.form_submit_button("Add Product")
            
            if submit:
                product_data = {
                    'product_name': product_name,
                    'type': product_type,
                    'size': size,
                    'sku': sku,
                    'quantity': quantity,
                    'price_per_unit': price_per_unit,
                    'batch_number': batch_number,
                    'production_date': production_date,
                    'best_before': best_before,
                    'labelling_match': labelling_match,
                    'checked_by': checked_by
                }
                
                if add_product_to_order(product_data):
                    add_notification("Product added to order!", "success")
                    st.rerun()
                else:
                    add_notification("Please fill in all required product details.", "error")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Display current order products
    if st.session_state.products:
        st.markdown("### Current Order Items")
        
        # Calculate order total
        order_total = sum(p.get('price_per_unit', 0) * p.get('quantity', 0) for p in st.session_state.products)
        st.markdown(f"**Order Total: ${order_total:.2f}**")
        
        # Display products in a nicer format
        for i, product in enumerate(st.session_state.products):
            with st.container():
                st.markdown('<div class="order-container">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{product['product_name']}**")
                    if 'size' in product and product['size']:
                        st.markdown(f"Size: {product['size']}")
                    if 'batch_number' in product and product['batch_number']:
                        st.markdown(f"Batch: {product['batch_number']}")
                
                with col2:
                    st.markdown(f"Quantity: **{product['quantity']}**")
                    if 'best_before' in product and product['best_before']:
                        best_before_str = product['best_before'].strftime('%Y-%m-%d') if isinstance(product['best_before'], datetime) else product['best_before']
                        st.markdown(f"Best Before: {best_before_str}")
                
                with col3:
                    price = product.get('price_per_unit', 0)
                    total = product.get('total_price', price * product.get('quantity', 0))
                    st.markdown(f"Unit Price: **${price:.2f}**")
                    st.markdown(f"Total: **${total:.2f}**")
                
                with col4:
                    if st.button("🗑️", key=f"delete_product_{i}", help="Remove this product"):
                        st.session_state.deleted_product_index = i
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle product deletion
        if st.session_state.deleted_product_index is not None:
            if remove_product(st.session_state.deleted_product_index):
                st.session_state.deleted_product_index = None
                st.rerun()
        
        # Submit order button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Submit Order", type="primary", key="submit_order_btn"):
                if not customer_name:
                    add_notification("Please enter a customer name", "error")
                elif len(st.session_state.products) > 0:
                    order_data = {
                        'date': sale_date.strftime("%Y-%m-%d"),
                        'customer_name': customer_name,
                        'delivery_method': delivery_method,
                        'order_number': order_number
                    }
                    
                    dm.add_stock_out_batch(order_data, st.session_state.products)
                    add_notification("Order submitted successfully!", "success")
                    clear_form()
                    st.session_state.data_changed = True
                    st.session_state.active_tab = "dashboard"
                    st.rerun()
                else:
                    add_notification("Please add at least one product to the order.", "error")
        
        with col2:
            if st.button("❌ Clear Order", key="clear_order_btn", on_click=clear_form):
                st.rerun()

def show_stock_management():
    """Display stock management interface"""
    st.markdown("## 📦 Stock Management")
    
    # Create tabs for different stock functions
    stock_tab1, stock_tab2, stock_tab3 = st.tabs([
        "📦 Stock In", "🗑️ Wastage", "📝 Products"
    ])
    
    with stock_tab1:
        show_stock_in_form()
    
    with stock_tab2:
        show_wastage_form()
    
    with stock_tab3:
        show_products_management()

def show_stock_in_form():
    """Display form for adding new stock"""
    st.markdown("### Add New Stock")
    
    # Get existing stock data
    stock_df = dm.get_stock_in()
    
    # Display existing stock
    if not stock_df.empty:
        st.markdown("#### Current Stock")
        st.dataframe(
            stock_df[[
                'product_name', 'type', 'quantity', 'package_size', 
                'price_per_unit', 'batch_number', 'use_by_date', 
                'best_before', 'supplier_name'
            ]].style.format({
                'price_per_unit': '${:.2f}'
            }),
            use_container_width=True
        )
    
    # Add new stock form
    with st.form("stock_in_form"):
        st.markdown("#### Add Stock Entry")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input("📌 Product Name")
            type_options = ["tea", "gear", "books"]
            product_type = st.selectbox("🗂️ Type", type_options)
            supplier_name = st.text_input("🏭 Supplier Name")
        
        with col2:
            invoice_number = st.text_input("📜 Invoice Number")
            batch_number = st.text_input("🏷️ Batch Number")
            use_by_date = st.date_input("📅 Use By Date")
            best_before = st.date_input("🗓️ Best Before Date")
        
        with col3:
            quantity = st.number_input("📦 Quantity", min_value=1, value=1)
            package_size = st.number_input("📏 Package Size (kg)", min_value=0.01, value=0.5)
            price_per_unit = st.number_input("💰 Price per Unit", min_value=0.01, value=10.0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            product_free_from_damage = st.radio("🔍 Product Free from Damage?", ["Yes", "No"])
        with col2:
            labelling_match = st.radio("📋 Labelling Match?", ["Yes", "No"])
        with col3:
            product_status = st.radio("🛑 Product Accepted or Rejected?", ["Accepted", "Rejected"])
        
        checked_by = st.text_input("✅ Checked By")
        submit_button = st.form_submit_button("✅ Add Stock")

    # Handle Form Submission
    if submit_button:
        stock_data = {
            "product_name": product_name,
            "type": product_type,
            "supplier_name": supplier_name,
            "invoice_number": invoice_number,
            "batch_number": batch_number,
            "use_by_date": use_by_date.strftime("%Y-%m-%d"),
            "best_before": best_before.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "package_size": package_size,
            "price_per_unit": price_per_unit,
            "product_free_from_damage": True if product_free_from_damage == "Yes" else False,
            "labelling_match": True if labelling_match == "Yes" else False,
            "product_status": product_status.lower(),
            "checked_by": checked_by
        }
        
        dm.add_stock_in(stock_data)
        add_notification("✅ Stock added successfully!", "success")
        st.session_state.data_changed = True
        st.rerun()

def show_wastage_form():
    """Display form for recording wastage"""
    st.markdown("### 🗑️ Wastage Records")
    
    # Get existing wastage data
    wastage_df = dm.get_wastage()
    
    # Display existing wastage
    if not wastage_df.empty:
        st.markdown("#### Wastage History")
        st.dataframe(
            wastage_df[[
                'date', 'product_name', 'reason', 'quantity', 
                'package_size', 'total_cost', 'batch_number'
            ]].style.format({
                'total_cost': '${:.2f}'
            }),
            use_container_width=True
        )
    
    # Add new wastage form
    with st.form("wastage_form"):
        st.markdown("#### Record New Wastage")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("📅 Date")
            product_name = st.text_input("📌 Product Name")
            reason = st.text_input("⚠️ Reason for Wastage")
        
        with col2:
            batch_number = st.text_input("🏷️ Batch Number")
            use_by_date = st.date_input("📅 Use By Date")
            best_before = st.date_input("🗓️ Best Before Date")
        
        with col3:
            quantity = st.number_input("📦 Quantity", min_value=1, value=1)
            package_size = st.number_input("📏 Package Size (kg)", min_value=0.01, value=0.5)
            avg_price_kg = st.number_input("💰 Avg Price per KG", min_value=0.01, value=10.0)
        
        checked_by = st.text_input("✅ Checked By")
        
        submit_button = st.form_submit_button("✅ Record Wastage")

    if submit_button:
        wastage_data = {
            "date": date.strftime("%Y-%m-%d"),
            "product_name": product_name,
            "reason": reason,
            "batch_number": batch_number,
            "use_by_date": use_by_date.strftime("%Y-%m-%d"),
            "best_before": best_before.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "package_size": package_size,
            "avg_price_per_kg": avg_price_kg,
            "total_cost": avg_price_kg * quantity * package_size,
            "checked_by": checked_by
        }

        dm.add_wastage(wastage_data)
        add_notification("✅ Wastage recorded successfully!", "success")
        st.session_state.data_changed = True
        st.rerun()

def show_products_management():
    """Display products management interface"""
    st.markdown("### 📝 Products Catalog")
    
    # Get existing products
    products_df = dm.get_products()
    
    # Display products with edit/delete options
    if not products_df.empty:
        st.dataframe(
            products_df,
            use_container_width=True,
            column_config={
                "price": st.column_config.NumberColumn(
                    "Price",
                    format="$%.2f",
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "Created",
                    format="DD-MM-YYYY",
                ),
            }
        )
    else:
        st.info("No products found. Add your first product below.")
    
    # Add new product form
    with st.form("add_product_form"):
        st.markdown("#### Add New Product")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Product Name")
            category = st.selectbox("Category", options=["tea", "gear", "books"])
            sku = st.text_input("SKU")
        
        with col2:
            description = st.text_area("Description", height=100)
            price = st.number_input("Price ($)", min_value=0.01, value=10.0, step=0.01)
        
        with col3:
            stock_level = st.number_input("Initial Stock Level", min_value=0, value=10)
            size = st.text_input("Size/Weight")
            reorder_level = st.number_input("Reorder Level", min_value=0, value=5)
        
        submit = st.form_submit_button("Add Product")
        
        if submit:
            product_data = {
                "name": name,
                "category": category,
                "sku": sku,
                "description": description,
                "price": price,
                "stock_level": stock_level,
                "size": size,
                "reorder_level": reorder_level,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Call a function to add product (you'll need to implement this)
            add_notification("Product added successfully!", "success")
            st.session_state.data_changed = True
            st.rerun()

def show_search_page():
    """Display comprehensive search and filter interface"""
    st.markdown("## 🔍 Search & Reports")
    
    # Load data
    df = dm.get_stock_out()
    
    if df.empty:
        st.warning("No sales data available.")
        return
    
    # Create tabs for different search options
    search_tab1, search_tab2, search_tab3 = st.tabs([
        "🔍 Basic Search", "📊 Reports", "📅 Date Analysis"
    ])
    
    with search_tab1:
        st.markdown("### Search Orders")
        
        # Unified search interface
        col1, col2 = st.columns([3, 1])
        with col1:
            search_text = st.text_input("🔎 Search", placeholder="Enter order number, product, customer...")
        with col2:
            search_type = st.selectbox(
                "Search by",
                options=["All Fields", "Order Number", "Product Name", "Batch Number", "Customer Name", "SKU"],
                key="search_type"
            )
        
        # Date filters
        col1, col2 = st.columns(2)
        with col1:
            min_date = df['date'].min() if not df.empty else datetime.now() - timedelta(days=30)
            max_date = df['date'].max() if not df.empty else datetime.now()
            date_range = st.date_input(
                "Sale Date Range",
                value=(min_date, max_date)
            )
        
        with col2:
            min_bb = df['best_before'].min() if not df.empty else datetime.now()
            max_bb = df['best_before'].max() if not df.empty else datetime.now() + timedelta(days=90)
            best_before_range = st.date_input(
                "Best Before Range",
                value=(min_bb, max_bb)
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Apply text search
        if search_text:
            if search_type == "All Fields":
                # Search across multiple columns
                text_columns = ['order_number', 'product_name', 'batch_number', 'customer_name', 'sku']
                mask = pd.Series(False, index=filtered_df.index)
                for col in text_columns:
                    mask |= filtered_df[col].fillna('').str.contains(search_text, case=False, na=False)
                filtered_df = filtered_df[mask]
            else:
                # Search in specific column
                search_column = {
                    "Order Number": "order_number",
                    "Product Name": "product_name",
                    "Batch Number": "batch_number",
                    "Customer Name": "customer_name",
                    "SKU": "sku"
                }[search_type]
                filtered_df = filtered_df[filtered_df[search_column].fillna('').str.contains(search_text, case=False, na=False)]
        
        # Apply date range filters
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['date'] <= pd.to_datetime(date_range[1])) &
            (filtered_df['best_before'] >= pd.to_datetime(best_before_range[0])) &
            (filtered_df['best_before'] <= pd.to_datetime(best_before_range[1]))
        ]
        
        # Display search results
        if filtered_df.empty:
            st.info("No orders found matching your search criteria.")
        else:
            # Get unique order numbers from filtered data
            orders_summary = filtered_df.groupby('order_number').agg({
                'date': 'first',
                'customer_name': 'first',
                'product_name': lambda x: ', '.join(set(x)),
                'quantity': 'sum',
                'total_price': 'sum',
                'delivery_method': 'first'
            }).reset_index()
            
            st.markdown(f"### Found {len(orders_summary)} Orders")
            
            # Display orders with cards
            for idx, order in orders_summary.iterrows():
                with st.container():
                    st.markdown('<div class="order-container">', unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
                    
                    with col1:
                        st.markdown(f"**Order:** {order['order_number']}")
                        st.markdown(f"Customer: {order['customer_name']}")
                    
                    with col2:
                        st.markdown(f"Date: {order['date']}")
                        st.markdown(f"Delivery: {order['delivery_method']}")
                    
                    with col3:
                        # Truncate product list if too long
                        products = order['product_name']
                        if len(products) > 50:
                            products = products[:47] + "..."
                        st.markdown(f"Products: {products}")
                        st.markdown(f"Total: **${order['total_price']:.2f}**")
                    
                    with col4:
                        if st.button("View", key=f"view_{order['order_number']}"):
                            st.session_state.viewing_order = order['order_number']
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Check if we're viewing a specific order
            if st.session_state.viewing_order:
                order_summary = orders_summary[orders_summary['order_number'] == st.session_state.viewing_order].iloc[0]
                show_order_details(st.session_state.viewing_order, order_summary, filtered_df)
    
    with search_tab2:
        st.markdown("### Sales Reports")
        
        # Create report options
        report_type = st.selectbox(
            "Select Report Type",
            options=["Sales by Product", "Sales by Customer", "Sales Trends", "Stock Value"]
        )
        
        if report_type == "Sales by Product":
            # Product sales report
            if not df.empty:
                product_sales = df.groupby('product_name').agg({
                    'quantity': 'sum',
                    'total_price': 'sum'
                }).reset_index().sort_values('total_price', ascending=False)
                
                # Create bar chart
                fig = px.bar(
                    product_sales, 
                    x='product_name', 
                    y='total_price',
                    title='Sales by Product',
                    labels={'product_name': 'Product', 'total_price': 'Sales ($)'},
                    color='total_price',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                st.dataframe(
                    product_sales.style.format({
                        'total_price': '${:.2f}'
                    }),
                    use_container_width=True,
                    column_config={
                        "product_name": "Product",
                        "quantity": "Units Sold",
                        "total_price": "Revenue"
                    }
                )
            else:
                st.info("No sales data available for reporting.")
        
        elif report_type == "Sales by Customer":
            # Customer sales report
            if not df.empty:
                customer_sales = df.groupby('customer_name').agg({
                    'order_number': 'nunique',
                    'quantity': 'sum',
                    'total_price': 'sum'
                }).reset_index().sort_values('total_price', ascending=False)
                
                # Rename columns
                customer_sales.columns = ['Customer', 'Orders', 'Units', 'Total Sales']
                
                # Create visualization
                fig = px.pie(
                    customer_sales, 
                    names='Customer', 
                    values='Total Sales',
                    title='Sales by Customer'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                st.dataframe(
                    customer_sales.style.format({
                        'Total Sales': '${:.2f}'
                    }),
                    use_container_width=True
                )
            else:
                st.info("No customer sales data available for reporting.")
        
        elif report_type == "Sales Trends":
            # Time-based sales analysis
            if not df.empty:
                # Convert date column to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Create monthly sales data
                df['month'] = df['date'].dt.strftime('%Y-%m')
                monthly_sales = df.groupby('month').agg({
                    'order_number': 'nunique',
                    'total_price': 'sum'
                }).reset_index()
                
                # Create line chart
                fig = px.line(
                    monthly_sales, 
                    x='month', 
                    y='total_price',
                    markers=True,
                    title='Monthly Sales Trend',
                    labels={'month': 'Month', 'total_price': 'Sales ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Create order count chart
                fig2 = px.bar(
                    monthly_sales, 
                    x='month', 
                    y='order_number',
                    title='Monthly Order Count',
                    labels={'month': 'Month', 'order_number': 'Number of Orders'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No sales trend data available for reporting.")
        
        elif report_type == "Stock Value":
            # Stock value report
            stock_df = dm.get_stock_in()
            
            if not stock_df.empty:
                # Calculate stock value
                stock_df['stock_value'] = stock_df['quantity'] * stock_df['package_size'] * stock_df['price_per_unit']
                
                # Group by type
                stock_value_by_type = stock_df.groupby('type').agg({
                    'stock_value': 'sum',
                    'quantity': 'sum'
                }).reset_index()
                
                # Create pie chart
                fig = px.pie(
                    stock_value_by_type, 
                    names='type', 
                    values='stock_value',
                    title='Stock Value by Type'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show detailed stock value table
                st.markdown("#### Detailed Stock Value")
                stock_details = stock_df.groupby(['type', 'product_name']).agg({
                    'quantity': 'sum',
                    'stock_value': 'sum'
                }).reset_index().sort_values(['type', 'stock_value'], ascending=[True, False])
                
                st.dataframe(
                    stock_details.style.format({
                        'stock_value': '${:.2f}'
                    }),
                    use_container_width=True,
                    column_config={
                        "type": "Category",
                        "product_name": "Product",
                        "quantity": "Quantity",
                        "stock_value": "Stock Value"
                    }
                )
            else:
                st.info("No stock data available for reporting.")
    
    with search_tab3:
        st.markdown("### Date Analysis")
        
        # Date-based analysis options
        date_analysis = st.selectbox(
            "Select Analysis Type",
            options=["Expiration Analysis", "Sales by Day of Week", "Sales by Month"]
        )
        
        if date_analysis == "Expiration Analysis":
            # Expiration date analysis
            stock_df = dm.get_stock_in()
            
            if not stock_df.empty:
                # Convert dates to datetime
                stock_df['best_before'] = pd.to_datetime(stock_df['best_before'])
                stock_df['use_by_date'] = pd.to_datetime(stock_df['use_by_date'])
                
                # Calculate days until expiration
                today = pd.to_datetime(datetime.now().date())
                stock_df['days_to_best_before'] = (stock_df['best_before'] - today).dt.days
                stock_df['days_to_use_by'] = (stock_df['use_by_date'] - today).dt.days
                
                # Create expiration categories
                def get_expiration_category(days):
                    if days < 0:
                        return "Expired"
                    elif days < 30:
                        return "Expiring Soon (< 30 days)"
                    elif days < 90:
                        return "Medium Term (30-90 days)"
                    else:
                        return "Long Term (> 90 days)"
                
                stock_df['expiration_category'] = stock_df['days_to_best_before'].apply(get_expiration_category)
                
                # Create visualization
                expiration_summary = stock_df.groupby('expiration_category').agg({
                    'quantity': 'sum',
                    'stock_value': 'sum'  # Assuming stock_value is calculated
                }).reset_index()
                
                # Define category order
                category_order = ["Expired", "Expiring Soon (< 30 days)", "Medium Term (30-90 days)", "Long Term (> 90 days)"]
                
                # Create bar chart
                fig = px.bar(
                    expiration_summary, 
                    x='expiration_category', 
                    y='quantity',
                    title='Inventory by Expiration Status',
                    labels={'expiration_category': 'Expiration Status', 'quantity': 'Quantity'},
                    color='expiration_category',
                    color_discrete_map={
                        "Expired": "#d32f2f",
                        "Expiring Soon (< 30 days)": "#ff9800",
                        "Medium Term (30-90 days)": "#4caf50",
                        "Long Term (> 90 days)": "#2196f3"
                    },
                    category_orders={"expiration_category": category_order}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show items expiring soon
                if "Expiring Soon (< 30 days)" in stock_df['expiration_category'].values:
                    st.markdown("#### 🔴 Products Expiring Soon")
                    expiring_soon = stock_df[stock_df['expiration_category'] == "Expiring Soon (< 30 days)"].sort_values('days_to_best_before')
                    
                    st.dataframe(
                        expiring_soon[['product_name', 'batch_number', 'quantity', 'best_before', 'days_to_best_before']],
                        use_container_width=True,
                        column_config={
                            "product_name": "Product",
                            "batch_number": "Batch",
                            "quantity": "Quantity",
                            "best_before": "Best Before",
                            "days_to_best_before": "Days Left"
                        }
                    )
            else:
                st.info("No stock data available for expiration analysis.")
        
        elif date_analysis == "Sales by Day of Week":
            # Day of week analysis
            if not df.empty:
                # Convert to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Add day of week
                df['day_of_week'] = df['date'].dt.day_name()
                
                # Group by day of week
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                weekday_sales = df.groupby('day_of_week').agg({
                    'order_number': 'nunique',
                    'quantity': 'sum',
                    'total_price': 'sum'
                }).reindex(day_order).reset_index()
                
                # Create visualization
                fig = px.bar(
                    weekday_sales, 
                    x='day_of_week', 
                    y='total_price',
                    title='Sales by Day of Week',
                    labels={'day_of_week': 'Day', 'total_price': 'Sales ($)'},
                    color='day_of_week',
                    category_orders={"day_of_week": day_order}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Create order count visualization
                fig2 = px.line(
                    weekday_sales, 
                    x='day_of_week', 
                    y='order_number',
                    markers=True,
                    title='Orders by Day of Week',
                    labels={'day_of_week': 'Day', 'order_number': 'Number of Orders'},
                    category_orders={"day_of_week": day_order}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No sales data available for day of week analysis.")
        
        elif date_analysis == "Sales by Month":
            # Monthly analysis
            if not df.empty:
                # Convert to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Extract month and year
                df['month_year'] = df['date'].dt.strftime('%Y-%m')
                
                # Group by month
                monthly_sales = df.groupby('month_year').agg({
                    'order_number': 'nunique',
                    'quantity': 'sum',
                    'total_price': 'sum'
                }).reset_index()
                
                # Create monthly sales visualization
                fig = px.bar(
                    monthly_sales, 
                    x='month_year', 
                    y='total_price',
                    title='Sales by Month',
                    labels={'month_year': 'Month', 'total_price': 'Sales ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Create monthly items sold visualization
                fig2 = px.line(
                    monthly_sales, 
                    x='month_year', 
                    y='quantity',
                    markers=True,
                    title='Items Sold by Month',
                    labels={'month_year': 'Month', 'quantity': 'Quantity Sold'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No sales data available for monthly analysis.")

def show_dashboard():
    """Display main dashboard with key metrics and charts"""
    st.markdown("## 📊 Tea Shop Dashboard")
    
    # Load data
    sales_df = dm.get_stock_out()
    stock_df = dm.get_stock_in()
    products_df = dm.get_products()
    wastage_df = dm.get_wastage()
    
    if sales_df.empty:
        st.info("No sales data available yet. Begin by adding sales orders.")
        return
    
    # Calculate key metrics
    total_revenue = sales_df['total_price'].sum()
    total_orders = sales_df['order_number'].nunique()
    total_customers = sales_df['customer_name'].nunique()
    total_products_sold = sales_df['quantity'].sum()
    
    # Key performance metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total Revenue</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${total_revenue:.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total Orders</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{total_orders}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Unique Customers</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{total_customers}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Products Sold</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{total_products_sold}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity and trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sales Trend")
        # Convert date to datetime
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        
        # Group by date
        daily_sales = sales_df.groupby('date').agg({
            'total_price': 'sum'
        }).reset_index()
        
        # Create a date range for the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Create a dataframe with all dates
        all_dates = pd.DataFrame({'date': date_range})
        
        # Merge with sales data
        complete_daily_sales = all_dates.merge(daily_sales, on='date', how='left').fillna(0)
        
        # Create trends chart
        fig = px.line(
            complete_daily_sales, 
            x='date', 
            y='total_price',
            markers=True,
            title='Daily Sales (Last 30 Days)',
            labels={'date': 'Date', 'total_price': 'Sales ($)'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Top Products")
        # Group sales by product
        product_sales = sales_df.groupby('product_name').agg({
            'quantity': 'sum',
            'total_price': 'sum'
        }).reset_index().sort_values('total_price', ascending=False).head(5)
        
        # Create bar chart
        fig = px.bar(
            product_sales, 
            x='product_name', 
            y='total_price',
            title='Top 5 Products by Revenue',
            labels={'product_name': 'Product', 'total_price': 'Revenue ($)'},
            color='total_price',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent orders
    st.markdown("### Recent Orders")
    
    # Get unique order numbers
    recent_orders = sales_df.sort_values('date', ascending=False)
    recent_order_numbers = recent_orders['order_number'].unique()[:5]
    
    # Display recent orders
    for order_num in recent_order_numbers:
        order_data = sales_df[sales_df['order_number'] == order_num]
        
        # Get order summary
        order_date = order_data['date'].iloc[0]
        customer = order_data['customer_name'].iloc[0]
        total = order_data['total_price'].sum()
        items = order_data['quantity'].sum()
        
        # Create order card
        with st.container():
            st.markdown('<div class="order-container">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"
