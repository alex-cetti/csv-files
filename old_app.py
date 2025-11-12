import streamlit as st
import pandas as pd
import json
import requests
import io

from iteract import apply_business_rules

st.set_page_config(layout="wide")
st.title("CSV File Processor and API Sender")

st.header("1. Upload your CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # To be able to read the file multiple times, we read it into memory
    file_contents = uploaded_file.getvalue()
    
    try:
        # --- 3. Create a dataframe using pandas ---
        # Use io.BytesIO to read the bytes content as a file
        df = pd.read_csv(io.BytesIO(file_contents))

        # --- 2. Iterate the file and count how many lines have ---
        # We count the rows in the DataFrame
        num_lines = len(df)
        st.success(f"File uploaded successfully! It has **{num_lines}** lines (rows) of data (excluding the header).")

        # --- 4. Display the dataframe with filters ---
        st.header("4. View and Filter Data")
        st.info("You can sort and filter the dataframe directly below.")
        # st.dataframe provides interactive filtering and sorting
        st.dataframe(df, width='stretch')

        # --- 5. Create a JSON with the values ---
        st.header("5. Convert to JSON")
        # Convert DataFrame to JSON (orient='records'       `creates a list of dicts)
        json_data = df.to_dict(orient='records')
        processed_data =  apply_business_rules(json_data)

        with st.expander("Click to see the generated JSON data"):
            st.json(json_data)

        with st.expander("Json Tratado"):
           st.json(processed_data)

        ## Iteracao com o Json
        
                    
    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file to begin.")