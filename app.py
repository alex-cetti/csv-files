import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time

from iteract import apply_business_rules

def get_order_metrics(orders):
    qtd_orders = len(orders)
    all_dates = [o.get('order_date') for o in orders if o.get('order_date')]
    if not all_dates:
        first_order = "n/a"
        last_order = "n/a"
    else:
        first_order  = format_date(min(all_dates))
        last_order  = format_date(max(all_dates))

    total_amount = 0
    total_weight = 0

    for order in orders:
        for product in order.get('products', []):
            total_amount += product.get('final_price', 0)
            total_weight += product.get('weight', 0)
    
    avg_amount = (total_amount / qtd_orders) if qtd_orders > 0 else 0
    avg_weight = (total_weight / qtd_orders) if qtd_orders > 0 else 0
    
    return {
        "first": first_order,
        "last": last_order,
        "avg_amount_str": f"R$ {avg_amount:,.2f}",
        "avg_weight_str": f"{avg_weight:.1f} kg"
    }


def diff_dates(start, end):
    d_order = datetime.strptime(start, '%Y-%m-%d')
    d_delivery = datetime.strptime(end, '%Y-%m-%d')

    
    time_delta = d_delivery - d_order


    return time_delta.days


def trasnform_csv(file):
    file_contents = file.getvalue()
    df = pd.read_csv(io.BytesIO(file_contents))
    json_data = df.to_dict(orient='records')
    return apply_business_rules(json_data)


def format_customer_name(code):
    customer_data = st.session_state.customer_data
    customer_info =  customer_data.get(code, {})
    name = customer_info.get('consumer_name', "Sem Nome")
    
    return f"{name} ({code})"


def format_date(date):
    # 2. Parse it into a datetime object
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    
    day = date_obj.day                        
    month_name = date_obj.strftime('%B').lower() 
    year = date_obj.year                       

    pretty_date = f"{day}, {month_name} , {year}"
    return pretty_date

def main():

    if 'customer_data' not in st.session_state:
        st.session_state['customer_data'] = None


    st.title("JBS")
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 19px; /* Adjust this value as needed */
        }
        </style>
        """, unsafe_allow_html=True)

    if st.session_state.customer_data is None:
        @st.dialog("Carregue o Arquivo")
        def upload_dialog():
            st.write("Insira o arquivo")
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type="csv", 
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                data_dict = trasnform_csv(uploaded_file)
                if data_dict:
                    st.session_state.customer_data = data_dict


                    with st.spinner("Processando o arquivo..."):
                        time.sleep(1.5)
                    st.rerun()
        upload_dialog()
    else:
        
        customer_codes = list(st.session_state.customer_data.keys())
        with st.sidebar:
            st.subheader("Selecione o Cliente")
            selected_code =  st.selectbox(
                "Procure o Cliente: ",
                options=customer_codes,
                format_func=format_customer_name,
                index=None,
                placeholder="Digite para pesquisar"
            )

        if selected_code:
            selected = st.session_state.customer_data[selected_code]
            orders_dict = selected.get("orders")

            order_list = list(orders_dict.values())
            orders_metrics = get_order_metrics(order_list)
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
                   

            

            for order in sorted_orders:
                order_code = order.get('order_code', 'N/A')
                order_date = format_date(order.get('order_date'))
        
               

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
                        st.write(f"{diff_dates(order.get('order_date'), order.get('order_delivery_date'))} dias ")
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
                            "product_price": None 
                        },
                        hide_index=True,
                        use_container_width=True
                    )

        else:
            st.info("Selecione um cliente ao lado")

if __name__ == "__main__":
    main()