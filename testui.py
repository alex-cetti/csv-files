import streamlit as st
import pandas as pd
from datetime import datetime
import json

# --- 1. Mock Data (Unchanged) ---
def get_data_from_json():
    """
    Returns a mock JSON structure with MULTIPLE customers.
    """
    return {
        "customers": [
            {
                "customer_info": {
                    "name": "Acme Widgets Inc.",
                    "code": "CUST-452B",
                    "qtd_orders": 3,
                    "first_order": "2023-09-05",
                    "last_order": "2023-11-15",
                    "average_amount": 475.33,
                    "average_weight": 17.5
                },
                "orders": [
                    {"code": "ORD-001", "total": 350.50, "weight": 12.0, "emission_date": "2023-09-05", "delivered_date": "2023-09-10", "items": [...]},
                    {"code": "ORD-002", "total": 200.00, "weight": 5.5, "emission_date": "2023-10-20", "delivered_date": "2023-10-25", "items": [...]},
                    {"code": "ORD-003", "total": 875.50, "weight": 35.0, "emission_date": "2023-10-28", "delivered_date": "2023-11-03", "items": [...]},
                ]
            },
            {
                "customer_info": {
                    "name": "Global Hypertech",
                    "code": "CUST-981G",
                    "qtd_orders": 2,
                    "first_order": "2023-11-01",
                    "last_order": "2023-12-05",
                    "average_amount": 1250.00,
                    "average_weight": 75.0
                },
                "orders": [
                    {"code": "ORD-A88", "total": 1500.00, "weight": 100.0, "emission_date": "2023-11-01", "delivered_date": "2023-11-05", "items": [...]},
                    {"code": "ORD-A92", "total": 1000.00, "weight": 50.0, "emission_date": "2023-12-05", "delivered_date": "2023-12-10", "items": [...]},
                ]
            },
            {
                "customer_info": {
                    "name": "Quick Logistics",
                    "code": "CUST-334F",
                    "qtd_orders": 1,
                    "first_order": "2023-12-15",
                    "last_order": "2023-12-15",
                    "average_amount": 120.00,
                    "average_weight": 4.0
                },
                "orders": [
                    {"code": "ORD-B01", "total": 120.00, "weight": 4.0, "emission_date": "2023-12-15", "delivered_date": "2023-12-20", "items": [
                        {"name": "Maintenance Kit", "quantity": 3, "unity_price": 40.00, "total_price": 120.00, "category": "Kits"}
                    ]}
                ]
            }
        ]
    }

# --- 2. Helper Functions (Unchanged) ---

def calculate_date_diff(start_date_str, end_date_str):
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d")
        end = datetime.strptime(end_date_str, "%Y-%m-%d")
        return (end - start).days
    except (ValueError, TypeError):
        return "N/A"

def get_month_year(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %Y")
    except (ValueError, TypeError):
        return "Unknown Month"

# --- 3. Data Processing (Unchanged) ---

def process_data(data):
    """Groups orders by month for a SINGLE customer."""
    orders_by_month = {}
    sorted_orders = sorted(data.get("orders", []), key=lambda x: x["emission_date"])
    
    for order in sorted_orders:
        month_year = get_month_year(order["emission_date"])
        order["diff_date"] = calculate_date_diff(order["emission_date"], order["delivered_date"])
        if month_year not in orders_by_month:
            orders_by_month[month_year] = []
        orders_by_month[month_year].append(order)
        
    return data.get("customer_info", {}), orders_by_month

# --- 4. Streamlit App UI (The Dashboard function is Unchanged) ---

def display_customer_dashboard(customer_data):
    """
    Renders the full UI (Card and Orders) for a single customer.
    (This function is identical to the previous version)
    """
    customer_info, orders_by_month = process_data(customer_data)

    # 1. Customer Card
    st.header(f"Customer Card: {customer_info.get('name', 'N/A')}")
    st.caption(f"Code: {customer_info.get('code', 'N/A')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", customer_info.get("qtd_orders", 0))
    col2.metric("First Order", customer_info.get("first_order", "N/A"))
    col3.metric("Last Order", customer_info.get("last_order", "N/A"))

    col4, col5 = st.columns(2)
    col4.metric("Average Amount", f"${customer_info.get('average_amount', 0):.2f}")
    col5.metric("Average Weight", f"{customer_info.get('average_weight', 0):.1f} kg")

    st.divider()

    # 2. Orders (Separated by month)
    st.header("Order History")
    if not orders_by_month:
        st.info("No orders found for this customer.")
        return

    month_keys = list(orders_by_month.keys())
    month_tabs = st.tabs(month_keys)
    
    for i, month_key in enumerate(month_keys):
        with month_tabs[i]:
            st.subheader(f"Orders in {month_key}")
            month_orders = orders_by_month[month_key]
            for order in month_orders:
                expander_title = (
                    f"**Order:** {order['code']}  |  "
                    f"**Emitted:** {order['emission_date']}  |  "
                    f"**Total:** ${order['total']:.2f}"
                )
                with st.expander(expander_title):
                    st.markdown("#### Order Details")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Order Total", f"${order['total']:.2f}")
                    c2.metric("Order Weight", f"{order['weight']} kg")
                    c3.metric("Delivery Time", f"{order['diff_date']} days")
                    st.caption(f"Emitted: {order['emission_date']} | Delivered: {order['delivered_date']}")
                    st.divider()
                    st.markdown("#### Order Items")
                    items_df = pd.DataFrame(order.get("items", []))
                    required_cols = ["name", "quantity", "unity_price", "total_price", "category"]
                    for col in required_cols:
                        if col not in items_df.columns:
                            items_df[col] = None
                    st.dataframe(items_df[required_cols], hide_index=True, use_container_width=True)

# ----------------------------------------------------------------------
# NEW: The main function is the only part that really changes.
# ----------------------------------------------------------------------
def main():
    st.set_page_config(layout="wide")
    
    # Load the new JSON structure
    raw_data = get_data_from_json()
    all_customers = raw_data.get("customers", [])

    if not all_customers:
        st.error("No customers found in the JSON data.")
        return

    # --- This is the new logic ---
    
    # 1. Create a dictionary for easy lookup: {Customer Name: Customer Data}
    # This is more efficient than looping to find the customer later.
    customer_data_map = {
        customer.get("customer_info", {}).get("name", f"Unnamed Customer {i}"): customer
        for i, customer in enumerate(all_customers)
    }
    
    # 2. Get a list of just the names for the dropdown
    customer_names = list(customer_data_map.keys())
    
    # 3. Create the dropdown (selectbox)
    # We place this at the top of the page, perhaps in a column for neatness
    st.sidebar.title("Customer Navigation")
    selected_customer_name = st.sidebar.selectbox(
        label="Select a Customer:",
        options=customer_names
    )

    # 4. Use the selected name to get the correct customer's data
    selected_customer_data = customer_data_map[selected_customer_name]
    
    # 5. Call our (unchanged) display function for *only* that customer
    display_customer_dashboard(selected_customer_data)
    
    # --- End of new logic ---

if __name__ == "__main__":
    main()