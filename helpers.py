import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time
from iteract import apply_business_rules

def summarize_monthly_orders(monthly_grouped_data):
    """
    Converts the month-name-keyed dictionary into a flat DataFrame
    suitable for charting.
    """
    summary_list = []
    for month_name, orders_list in monthly_grouped_data.items():
        total_orders = len(orders_list)
        total_products = sum(
            sum(p['product_quantity'] for p in order['order-products']) 
            for order in orders_list
        )
        
        summary_list.append({
            'Month': month_name,
            'Total_Orders': total_orders,
            'Total_Products_Quantity': total_products
        })
    
    # Create the DataFrame for charting
    return pd.DataFrame(summary_list).set_index('Month')


# --- Boilerplate Data (Using the result from the previous step) ---
# monthly_grouped_data = {
#     "January": [
#         {
#             "order-code": 59739779,
#             "order-products": [
#                 {"product_name": "CARNE CONSERVA TARGET...", "product_quantity": 76},
#                 {"product_name": "FIAMBRE KITUT...", "product_quantity": 16},
#             ],
#             "account": "N/A"
#         },
#         {
#             "order-code": 60012346,
#             "order-products": [
#                 {"product_name": "FIAMBRE BORDON...", "product_quantity": 10},
#             ],
#             "account": "N/A"
#         }
#     ],
#     "February": [
#         {
#             "order-code": 60012345,
#             "order-products": [
#                 {"product_name": "SALSICHA BORDON...", "product_quantity": 50},
#             ],
#             "account": "N/A"
#         }
#     ]
# }



def orders_chart(orders):

    
    months = {}
    for order in orders:
        date_obj = pd.to_datetime(order["order_date"])

        month_name = date_obj.strftime('%B')
        order_obj = {
            "order-code": order["order_code"],
            # Rename 'products' to 'order-products' as requested
            "order-products": order["products"], 
            "order_date": order["order_date"],
            "order_delivery_date": order["order_delivery_date"],
            "order_stage": order["order_stage"],
        }

        if month_name not in months:
            months[month_name] = []
        
        months[month_name].append(order_obj)


    return months



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
    product_list = []

    for order in orders:
        for product in order.get('products', []):
            
            total_amount += product.get('final_price', 0)
            total_weight += product.get('weight', 0)
            found = False
            obj = { 'id': product.get('jbs_id'), 
                   'name': product.get('product_name'),
                   'categoria': product.get('product_category')
                }

            for p_list in product_list:
                if p_list['id'] == obj['id']:
                    p_list['count'] += 1
                    p_list['sum_quantity'] += int(product.get('product_quantity'))
                    found = True

            if not found:
                    obj['count'] = 1
                    obj['sum_quantity'] = int(product.get('product_quantity'))
                    product_list.append(obj) 
               
    avg_amount = (total_amount / qtd_orders) if qtd_orders > 0 else 0
    avg_weight = (total_weight / qtd_orders) if qtd_orders > 0 else 0
    
    return {
        "first": first_order,
        "last": last_order,
        "all_dates": all_dates,
        "avg_amount_str": f"R$ {avg_amount:,.2f}",
        "avg_weight_str": f"{avg_weight:.1f} kg",
        "product_metrics": product_list 
    }


def diff_dates(start, end):
    d_order = datetime.strptime(start, '%Y-%m-%d')
    d_delivery = datetime.strptime(end, '%Y-%m-%d')

    
    time_delta = d_delivery - d_order


    return time_delta.days


def transform_csv(file):
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
