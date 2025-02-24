import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import data_manager as dm
import utils

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = []
if 'data_changed' not in st.session_state:
    st.session_state.data_changed = False
if 'editing_order' not in st.session_state:
    st.session_state.editing_order = None
if 'viewing_order' not in st.session_state:
    st.session_state.viewing_order = None

def main():
    st.title("📊 Sales Dashboard")

    # Create tabs
    tab1, tab2 = st.tabs(["Data Entry", "Dashboard"])

    with tab1:
        if st.session_state.editing_order:
            show_edit_form()
        else:
            show_data_entry_form()

    with tab2:
        show_dashboard()

def add_product_to_order(product_data):
    """Add product to current order in session state"""
    if all(product_data.values()):
        st.session_state.products.append(product_data)
        return True
    return False

def clear_form():
    """Reset the form through the session state"""
    st.session_state.products = []
    st.session_state.editing_order = None
    st.session_state.viewing_order = None

def show_order_details(order_number, order_summary, filtered_df):
    """Show detailed view of an order with edit and delete options"""
    st.subheader(f"Order Details: {order_number}")

    # Order information
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Date of Sale: {order_summary['date_of_sale']}")
        st.write(f"Customer Name: {order_summary['customer_name']}")
    with col2:
        st.write(f"Delivery Method: {order_summary['delivery_method']}")
        st.write(f"Total Price: ${order_summary['total_price']:.2f}")

    # Order products
    order_products = filtered_df[filtered_df['order_number'] == order_number]
    st.dataframe(
        order_products[[
            'product_name', 'size', 'type', 'sku', 'quantity',
            'price_per_unit', 'total_price', 'batch_number',
            'best_before', 'production_date', 'labelling_match',
            'checked_by'
        ]],
        use_container_width=True
    )

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Edit Order"):
            st.session_state.editing_order = order_number
            st.session_state.products = []  # Clear products to load from order
            st.rerun()
    with col2:
        if st.button("Delete Order"):
            if st.session_state.get('confirm_delete') == order_number:
                dm.delete_order(order_number)
                st.session_state.pop('confirm_delete')
                st.success("Order deleted successfully!")
                st.session_state.viewing_order = None
                st.rerun()
            else:
                st.session_state.confirm_delete = order_number
                st.warning("Click delete again to confirm")
    with col3:
        if st.button("Back to Orders List"):
            st.session_state.viewing_order = None
            st.rerun()

def show_edit_form():
    st.header(f"Edit Order: {st.session_state.editing_order}")

    # Load existing order data
    order_data = dm.get_order_details(st.session_state.editing_order)
    if order_data.empty:
        st.error("Order not found!")
        clear_form()
        st.rerun()
        return

    # Initialize products if empty
    if not st.session_state.products:
        st.session_state.products = order_data.to_dict('records')

    # Order details
    col1, col2 = st.columns(2)
    with col1:
        sale_date = st.date_input(
            "Date of Sale",
            value=order_data['date_of_sale'].iloc[0]
        )
        customer_name = st.text_input(
            "Customer Name",
            value=order_data['customer_name'].iloc[0]
        )
    with col2:
        delivery_method = st.selectbox(
            "Delivery Method",
            options=['Standard', 'Express', 'Pickup'],
            index=['Standard', 'Express', 'Pickup'].index(order_data['delivery_method'].iloc[0])
        )

    # Product details form
    st.subheader("Edit Products")
    with st.form(key='edit_product_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input("Product Name")
            size = st.text_input("Size")
            type = st.text_input("Type")
            sku = st.text_input("SKU")
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price_per_unit = st.number_input("Price per Unit", min_value=0.0, value=0.0, step=0.01)
            batch_number = st.text_input("Batch Number")
            checked_by = st.text_input("Checked By")
        with col3:
            production_date = st.date_input("Production Date", value=datetime.now())
            best_before = st.date_input("Best Before Date", value=datetime.now() + timedelta(days=30))
            labelling_match = st.selectbox("Labelling Match Specifications", options=['Yes', 'No'])

        if st.form_submit_button("Add Product"):
            product_data = {
                'product_name': product_name,
                'size': size,
                'type': type,
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
                st.success("Product added to order!")
            else:
                st.error("Please fill in all product details.")

    # Display current order products
    if st.session_state.products:
        st.subheader("Products in Order")
        products_df = pd.DataFrame(st.session_state.products)
        st.dataframe(products_df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Order"):
                order_data = {
                    'date_of_sale': sale_date,
                    'customer_name': customer_name,
                    'delivery_method': delivery_method,
                    'order_number': st.session_state.editing_order
                }
                dm.update_order(st.session_state.editing_order, order_data, st.session_state.products)
                clear_form()
                st.success("Order updated successfully!")
                st.session_state.data_changed = True
                st.rerun()

        with col2:
            if st.button("Cancel Edit"):
                clear_form()
                st.rerun()

def show_data_entry_form():
    st.header("New Sales Entry")

    # Order details
    col1, col2 = st.columns(2)
    with col1:
        sale_date = st.date_input(
            "Date of Sale",
            value=datetime.now()
        )
        customer_name = st.text_input("Customer Name")
    with col2:
        suggested_order = utils.generate_order_number()
        order_number = st.text_input("Order Number", value=suggested_order)
        delivery_method = st.selectbox(
            "Delivery Method",
            options=['Standard', 'Express', 'Pickup']
        )

    # Product details
    st.subheader("Add Products")
    with st.form(key='product_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input("Product Name")
            size = st.text_input("Size")
            type = st.text_input("Type")
            sku = st.text_input("SKU")
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price_per_unit = st.number_input("Price per Unit", min_value=0.0, value=0.0, step=0.01)
            batch_number = st.text_input("Batch Number")
            checked_by = st.text_input("Checked By")
        with col3:
            production_date = st.date_input("Production Date", value=datetime.now())
            best_before = st.date_input("Best Before Date", value=datetime.now() + timedelta(days=30))
            labelling_match = st.selectbox("Labelling Match Specifications", options=['Yes', 'No'])

        if st.form_submit_button("Add Product"):
            product_data = {
                'product_name': product_name,
                'size': size,
                'type': type,
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
                st.success("Product added to order!")
            else:
                st.error("Please fill in all product details.")

    # Display current order products
    if st.session_state.products:
        st.subheader("Products in Current Order")
        products_df = pd.DataFrame(st.session_state.products)
        st.dataframe(products_df, use_container_width=True)

        if st.button("Submit Order"):
            if len(st.session_state.products) > 0:
                order_data = {
                    'date_of_sale': sale_date,
                    'customer_name': customer_name,
                    'delivery_method': delivery_method,
                    'order_number': order_number
                }
                dm.add_products_to_order(order_data, st.session_state.products)
                clear_form()
                st.success("Order submitted successfully!")
                st.session_state.data_changed = True
                st.rerun()
            else:
                st.error("Please add at least one product to the order.")

    if st.button("Clear Order", on_click=clear_form):
        st.rerun()

def show_dashboard():
    st.header("Sales Overview")

    # Load data
    df = dm.load_data()

    if df.empty:
        st.warning("No sales data available.")
        return

    # Search and Filters
    st.subheader("Search and Filters")

    # Unified search interface
    col1, col2 = st.columns([2, 1])
    with col1:
        search_text = st.text_input("Search", placeholder="Enter search term...")
    with col2:
        search_type = st.selectbox(
            "Search by",
            options=["Order Number", "Product Name", "Batch Number", "Customer Name", "SKU"],
            key="search_type"
        )

    # Date filters in a separate section
    st.subheader("Date Filters")
    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input(
            "Sale Date Range",
            value=(df['date_of_sale'].min(), df['date_of_sale'].max())
        )
    with col2:
        best_before_range = st.date_input(
            "Best Before Range",
            value=(df['best_before'].min(), df['best_before'].max())
        )

    # Apply filters
    filtered_df = df.copy()

    # Apply text search based on selected type
    if search_text:
        search_column = {
            "Order Number": "order_number",
            "Product Name": "product_name",
            "Batch Number": "batch_number",
            "Customer Name": "customer_name",
            "SKU": "sku"
        }[search_type]
        filtered_df = filtered_df[filtered_df[search_column].str.contains(search_text, case=False, na=False)]

    # Date range filters
    filtered_df = filtered_df[
        (filtered_df['date_of_sale'] >= date_range[0]) &
        (filtered_df['date_of_sale'] <= date_range[1]) &
        (filtered_df['best_before'] >= best_before_range[0]) &
        (filtered_df['best_before'] <= best_before_range[1])
    ]

    # Statistics
    st.subheader("Quick Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", filtered_df['order_number'].nunique())
    with col2:
        st.metric("Total Products", filtered_df['quantity'].sum())
    with col3:
        st.metric("Total Revenue", f"${filtered_df['total_price'].sum():.2f}")
    with col4:
        st.metric("Unique Customers", filtered_df['customer_name'].nunique())

    # Orders overview
    st.subheader("Orders Overview")
    orders_summary = filtered_df.groupby('order_number').agg({
        'date_of_sale': 'first',
        'customer_name': 'first',
        'product_name': lambda x: ', '.join(x),
        'quantity': 'sum',
        'total_price': 'sum',
        'delivery_method': 'first'
    }).reset_index()

    # Check if we're viewing a specific order
    if st.session_state.viewing_order:
        order_summary = orders_summary[orders_summary['order_number'] == st.session_state.viewing_order].iloc[0]
        show_order_details(st.session_state.viewing_order, order_summary, filtered_df)
    else:
        # Display orders list with view details button
        if len(orders_summary) == 0:
            st.info("No orders found matching the search criteria.")
        else:
            for idx, order in orders_summary.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.write(f"Order: {order['order_number']}")
                        st.write(f"Customer: {order['customer_name']}")
                    with col2:
                        st.write(f"Date: {order['date_of_sale']}")
                        st.write(f"Delivery: {order['delivery_method']}")
                    with col3:
                        st.write(f"Items: {order['quantity']}")
                        st.write(f"Total: ${order['total_price']:.2f}")
                    with col4:
                        if st.button("View Details", key=f"view_{order['order_number']}"):
                            st.session_state.viewing_order = order['order_number']
                            st.rerun()

if __name__ == "__main__":
    main()