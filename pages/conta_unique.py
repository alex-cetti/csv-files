import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time

import helpers

customer_codes = list(st.session_state.customer_data.keys())
with st.sidebar:
    st.subheader("Selecione o Cliente")
    selected_code =  st.selectbox(
        "Procure o Cliente: ",
        options=customer_codes,
        format_func=helpers.format_customer_name,
        index=None,
        placeholder="Digite para pesquisar"
    )

if selected_code:
    selected = st.session_state.customer_data[selected_code]
    orders_dict = selected.get("orders")

    order_list = list(orders_dict.values())
    orders_metrics = helpers.get_order_metrics(order_list)
        # 2. Sort the list. We use .get() as a safeguard in case 'order_date' is missing.
    try:
        sorted_orders = sorted(
            order_list,
            key=lambda o: o.get('order_date', '1900-01-01'),
            reverse=True  # Newest orders first
        )
    except Exception as e:
        st.error(f"Could not sort orders: {e}")
        sorted_orders = order_list

    
    
    name = selected.get('consumer_name', 'N/A')
    city = selected.get('consumer_city')
    qtd_orders = len(orders_dict)
    placeholder_first_order = orders_metrics["first"]  
    placeholder_last_order = orders_metrics["last"]  
    placeholder_avg_amount = orders_metrics["avg_amount_str"]
    placeholder_avg_weight = orders_metrics["avg_weight_str"]
    st.subheader(f"{name} - {city} ")
    st.write(selected_code)         
    

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Quantidade de Pedidos", value=qtd_orders)
        with col2:
            st.metric(label="Valor de Pedido Medio", value=placeholder_avg_amount)
            st.metric(label="Peso Medio", value=placeholder_avg_weight)
        with col3:
            st.metric(label="Primeiro Pedido", value=placeholder_first_order)
            st.metric(label="Ultimo Pedido", value=placeholder_last_order)
            

    with st.container():
        st.dataframe(orders_metrics['product_metrics'])
    

    for order in sorted_orders:
        order_code = order.get('order_code', 'N/A')
        order_date = helpers.format_date(order.get('order_date'))

        

        total_amount = 0
        total_weight = 0

        
        for product in order.get('products', []):
            total_amount += product.get('final_price', 0)
            total_weight += product.get('weight', 0)

        
        expander_title = f"**Pedido #{order_code}** ( {order_date}) Total: R$: {round(total_amount, 2)} | Peso: {round(total_weight,2)} Kg "

        with st.expander(expander_title):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Data do Pedido**")
                st.write(order.get('order_date', '---'))
            
            with col2:
                st.markdown("**Data de Entrega**")
                st.write(order.get('order_delivery_date', '---'))
                
            with col3:
                st.markdown("**Tempo de entrega**")
                st.write(f"{helpers.diff_dates(order.get('order_date'), order.get('order_delivery_date'))} dias ")
            st.markdown("##### Produtos do Pedido")
            products_list = order.get('products', [])
            
            if not products_list:
                st.write("No product data found for this order.")
                continue
                
            # st.dataframe is perfect for a list of dicts
            st.dataframe(
                products_list,
                column_config={
                    # Rename columns for display and set size
                    "product_name": st.column_config.TextColumn("Product", width="large"),
                    "product_category": None,
                    "product_quantity": "Qty",
                    "product_unit": None,
                    # Format price as currency (change "R$" if needed)
                    "final_price": st.column_config.NumberColumn(
                        "Total Price",
                        format="R$ %.2f"
                    ),
                    # Hide the single-unit price; it's less important
                    "product_price": "Total Caixa" 
                },
                hide_index=True,
                width='stretch'
            )

else:   
    st.info("Selecione um cliente ao lado")