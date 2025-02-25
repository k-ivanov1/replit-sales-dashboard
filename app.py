import streamlit as st
import data_manager as dm

st.set_page_config(page_title="📦 Inventory Management", layout="wide")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Stock In", "📤 Stock Out", "🗑️ Wastage", "📜 Products", "📊 Analytics"])

### STOCK IN FORM ###
with tab1:
    st.header("📦 Add New Stock")

    # Input Form
    with st.form("stock_in_form"):
        product_name = st.text_input("📌 Product Name")
        type_options = ["tea", "gear", "books"]
        product_type = st.selectbox("🗂️ Type", type_options)
        supplier_name = st.text_input("🏭 Supplier Name")
        invoice_number = st.text_input("📜 Invoice Number")
        batch_number = st.text_input("🏷️ Batch Number")
        use_by_date = st.date_input("📅 Use By Date")
        best_before = st.date_input("🗓️ Best Before Date")
        quantity = st.number_input("📦 Quantity", min_value=1, value=1)
        package_size = st.number_input("📏 Package Size (kg)", min_value=0.01, value=0.5)
        price_per_unit = st.number_input("💰 Price per Unit", min_value=0.01, value=10.0)
        product_free_from_damage = st.radio("🔍 Product Free from Damage?", ["Yes", "No"])
        labelling_match = st.radio("📋 Labelling Match?", ["Yes", "No"])
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
        st.success("✅ Stock added successfully!")
        st.rerun()

### STOCK OUT (SALES) ###
with tab2:
    st.header("📤 Sales / Stock Out")

    df = dm.get_stock_out()
    st.dataframe(df)

    with st.form("sales_form"):
        date_of_sale = st.date_input("📅 Date of Sale")
        product_name = st.text_input("📌 Product Name")
        size = st.text_input("📏 Size")
        sku = st.text_input("🔢 SKU")
        customer_name = st.text_input("👤 Customer Name")
        order_number = st.text_input("🛒 Order Number")
        batch_number = st.text_input("🏷️ Batch Number")
        best_before = st.date_input("🗓️ Best Before Date")
        production_date = st.date_input("🏭 Production Date")
        quantity = st.number_input("📦 Quantity", min_value=1, value=1)
        price_per_unit = st.number_input("💰 Price per Unit", min_value=0.01, value=10.0)
        delivery_method = st.selectbox("🚚 Delivery Method", ["Courier", "Pickup", "Post"])
        labelling_match = st.radio("📋 Labelling Match?", ["Yes", "No"])

        submit_button = st.form_submit_button("✅ Add Sale")

    if submit_button:
        order_data = {
            "date": date_of_sale.strftime("%Y-%m-%d"),
            "product_name": product_name,
            "size": size,
            "sku": sku,
            "customer_name": customer_name,
            "order_number": order_number,
            "batch_number": batch_number,
            "best_before": best_before.strftime("%Y-%m-%d"),
            "production_date": production_date.strftime("%Y-%m-%d"),
            "quantity": quantity,
            "price_per_unit": price_per_unit,
            "total_price": quantity * price_per_unit,
            "delivery_method": delivery_method,
            "labelling_match": True if labelling_match == "Yes" else False
        }

        dm.add_stock_out(order_data)
        st.success("✅ Sale recorded successfully!")
        st.rerun()

### WASTAGE ###
with tab3:
    st.header("🗑️ Wastage Records")

    df = dm.get_wastage()
    st.dataframe(df)

    with st.form("wastage_form"):
        date = st.date_input("📅 Date")
        product_name = st.text_input("📌 Product Name")
        reason = st.text_input("⚠️ Reason")
        batch_number = st.text_input("🏷️ Batch Number")
        use_by_date = st.date_input("📅 Use By Date")
        best_before = st.date_input("🗓️ Best Before Date")
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
        st.success("✅ Wastage recorded!")
        st.rerun()

### PRODUCTS ###
with tab4:
    st.header("📜 Products")
    df = dm.get_products()
    st.dataframe(df)

### ANALYTICS ###
with tab5:
    st.header("📊 Analytics & Reports")
    st.write("Coming Soon!")
