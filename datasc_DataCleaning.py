import streamlit as st
import pandas as pd
import numpy as np
import io 

st.set_page_config(page_title="Data Cleaning Apps",page_icon="🫧",layout="wide")

st.title("🛁 Data Cleaning Application")
st.write("🗂️ Upload A **CSV** Or An **Excel** File To Perform Data Cleaning")

# for uploading file
uploaded_file = st.file_uploader("Upload A CSV Or An Excel File",type=['csv','xls','xlsx'])

# Mapping file extensions to pandas reader functions
READERS = {"csv": pd.read_csv,
           "xls": pd.read_excel,
           "xlsx": pd.read_excel}

if uploaded_file is not None:
    try:       
        file_extension = uploaded_file.name.split(".")[-1].lower()
        reader = READERS.get(file_extension)

        if reader is None:
            st.error("Unsupported file type")
        else:
            data = reader(uploaded_file)
                   
        # converting bool columns as str
        bool_cols = data.select_dtypes(include=['bool']).columns
        data[bool_cols] = data[bool_cols].astype('str')
    except Exception as e:
        st.error("Could Not Read Excel / CSV File. Please Check The File Format")
        st.exception(e)
        st.stop()
    st.success("✔️ File Uploaded Successfully !")
    st.write("### Preview Of Data")
    st.dataframe(data.head())

    
    # Keep a copy for cleaning
    if "clean_data" not in st.session_state:
        st.session_state.clean_data = data.copy()

    clean_data = st.session_state.clean_data


    st.write("### 📋 Data Overview")
    st.write("Number Of Rows: ",data.shape[0])
    st.write("Number Of Colums: ",data.shape[1])
    st.write("Number Of Missing Values: ",data.isnull().sum().sum())
    st.write("Number Of Duplicate Records: ",data.duplicated().sum())

    st.write("### 📝 Complete Summary Of Dataset")
    buffer = io.StringIO()      
    data.info(buf=buffer)       
    i = buffer.getvalue()
    st.text(i)

    # -------------------- Cleaning Action --------------------
    st.write("### 🛠 Data Cleaning Options")

    col1, col2, col3 = st.columns(3)

    # Remove missing values
    with col1:
        if st.button("🗑 Remove Missing Values"):
            clean_data = clean_data.dropna()
            st.session_state.clean_data = clean_data
            st.success("Missing values removed!")

    # Handle missing values
    with col2:
        if st.button("🩹 Handle Missing Values"):
            for col in clean_data.columns:
                if clean_data[col].dtype in ["int64", "float64"]:
                    clean_data[col].fillna(clean_data[col].mean(), inplace=True)
                else:
                    clean_data[col].fillna(clean_data[col].mode()[0], inplace=True)
            st.session_state.clean_data = clean_data
            st.success("Missing values handled successfully!")

    # Remove duplicates
    with col3:
        if st.button("📉 Remove Duplicate Values"):
            clean_data = clean_data.drop_duplicates()
            st.session_state.clean_data = clean_data
            st.success("Duplicate rows removed!")

   
    st.divider()

    # Summary
    st.write("### 🧩 Summary Record")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number Of Rows", clean_data.shape[0])
    col2.metric("Number Of Columns", clean_data.shape[1])
    col3.metric(" ❗ Missing Value", clean_data.isnull().sum().sum())
    col4.metric("Duplicate Records", clean_data.duplicated().sum())

# Download File
    st.write("⏬ Download Cleaned File")

    if "clean_data" in st.session_state and not st.session_state.clean_data.empty:

    # CSV download
        csv = st.session_state.clean_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
            )

    # Excel download
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:  # use openpyxl to avoid xlsxwriter
            st.session_state.clean_data.to_excel(writer, index=False, sheet_name="Cleaned Data")
            excel_data = output.getvalue()

        st.download_button(
            label="📥 Download Cleaned Excel",
            data=excel_data,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.warning("⚠️ No data available to download. Please upload and clean data first.")