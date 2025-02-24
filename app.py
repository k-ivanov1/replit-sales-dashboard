import streamlit as st
import pandas as pd
from data_manager import load_data, get_orders_summary

st.title("Replit Sales Dashboard")

# Load data
df = load_data()

# Show summary
st.subheader("Orders Summary")
summary_df = get_orders_summary()
st.dataframe(summary_df)

# Allow user to filter by order number
order_number = st.selectbox("Select Order Number", summary_df["order_number"].unique())
order_details = df[df["order_number"] == order_number]
st.subheader(f"Details for Order: {order_number}")
st.dataframe(order_details)
