import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time

import helpers







customer_codes = st.session_state.customer_data

#st.json(customer_codes)


# data = {
#     orders_metrics['product_metrics'],

# }




for c in customer_codes.values():
    st.write(c["consumer_name"])
    #st.json(c["orders"])
    order_list = list(c["orders"].values())
    orders_metrics = helpers.orders_chart(order_list)
    chart_data = helpers.summarize_monthly_orders(orders_metrics)
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(c["consumer_city"])
    with st.container():
        st.json(orders_metrics)
        # for order in orders_metrics:
        #     st.write(f"Mes : {order}")
        #     summarize_monthly_orders
        st.header('Summary Data')
        st.dataframe(chart_data)

        st.subheader('Total Orders by Month')
        # Use st.bar_chart for a great comparison of discrete categories (months)
            # st.bar_chart(
            #     chart_data['Total_Orders'],
            #    )

        st.subheader('Total Product Quantity by Month')
        # Use st.line_chart to show the trend of quantity
        st.line_chart(
            chart_data['Total_Products_Quantity']
        )   
 
