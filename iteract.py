import pandas as pd
from datetime import datetime



def apply_business_rules(data_list: list) -> dict:

    consumers_dict = {}
    
    for record in data_list:
        try:
            consumer_code = record.get('Terceiro Centralizador')
            order_code = record.get('Pedido')

            if not consumer_code or not order_code:
                continue

            # --- 1. Cliente ---
            if consumer_code not in consumers_dict:
                consumers_dict[consumer_code] = {
                    'consumer_name': record.get('Nome do Terceiro Centralizador'),
                    'consumer_city': record.get('Cidade'),
                    'orders': {} # Initialize an empty dict for their orders
                }

            # --- 2. Pedido --- 
            consumer_orders = consumers_dict[consumer_code]['orders']

            if order_code not in consumer_orders:
                consumer_orders[order_code] = {
                    'order_code': order_code,
                    'order_date': format_date(record.get('Data Emissão Pedido')),
                    'order_delivery_date': format_date(record.get('Data de Entrega')),
                    'order_stage': record.get('Situação do Pedido'),
                    'products': [] # Initialize an empty list for products
                }

            # --- 3. Produto ---
            product_info = {
                'product_name': record.get('Nome Produto'),
                'product_category': record.get('FAMILIA'),
                'product_quantity': record.get('Qtde'),
                'product_price': product_price(format_price(record.get(' PREÇO ')), record.get('Nome Produto')),
                'weight': float(record.get('Peso Líquido Estimado')),
                'final_price': float(record.get('Total')),
                'jbs_id': record.get('Produto')
            }
            
            consumer_orders[order_code]['products'].append(product_info)

            
            # amount = 0
            # for item in consumer_orders[order_code]['products']:
            #       amount  = item["final_price"] + amount
            
            # consumer_orders[order_code]["order_total"] = amount
        
        
        except Exception as e:
            #print(f"Error processing record {record}: {e}")
            pass

    # --- END OF YOUR BUSINESS LOGIC ---
    
    return consumers_dict



def format_price(price_str):
    try:
        
        p = price_str.replace("R$", "").strip()
        return float(p)

    except ValueError:
        return 0.0


def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        new_date = date_obj.strftime("%Y-%m-%d")
        return new_date
    except ValueError:
        return "0000-00-00"
    

def product_price(box_price, item_str):
    print("Iteasdasdam str")
    print(item_str)
    print(box_price)
    if "X" not in item_str:
        value = 12
    else:
        try:
            part_before_x = item_str.split('X')[0]
            print(part_before_x)
            x = float(part_before_x.split(' ')[-1])
            print(x)
            print()
            value = round(float(box_price/x), 3)
            print(value)
            
        
        except ValueError:
            value = 12
        
    print(value)
    return float(value)