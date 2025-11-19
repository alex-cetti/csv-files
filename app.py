import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time


from iteract import apply_business_rules
import helpers

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
                data_dict = helpers.transform_csv(uploaded_file)
                if data_dict:
                    st.session_state.customer_data = data_dict


                    with st.spinner("Processando o arquivo..."):
                        time.sleep(1.5)
                    st.rerun()
        upload_dialog()
    
        
if __name__ == "__main__":
    main()