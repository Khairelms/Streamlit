import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Analyze Your Data",page_icon="📡",layout="wide")

st.title("📊 Analyze Your Data")
st.write("🗂️ Upload A **CSV** Or An **Excel** File To Explore Your Data Interactively")

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

    st.write("### 📋 Data Overview")
    st.write("Number Of Rows: ",data.shape[0])
    st.write("Number Of Colums: ",data.shape[1])
    st.write("Number Of Missing Values: ",data.isnull().sum().sum())
    st.write("Number Of Duplicate Records: ",data.duplicated().sum())


    st.write("### 📝 Complete Summary Of Dataset")
    buffer = io.StringIO()      # data.info() method return plain text can't be capture --> use class io.string & create object 'buffer'
    data.info(buf=buffer)       # store text into buffer
    i = buffer.getvalue()
    st.text(i)

    st.write("### ⚖️ Statistical Summary Of Dataset")
    st.dataframe(data.describe())

    st.write("### 📎 Statistical Summary For Non-Numerical Of Dataset")
    non_numeric_cols = data.select_dtypes(include=["object", "bool"])

    if not non_numeric_cols.empty:
        st.dataframe(non_numeric_cols.describe())
    else:
        st.info("No non-numerical features found in this dataset.")

    st.write("### ✂️ Select The Desired Columns For Analysis")
    selected_columns = st.multiselect("Choose Columns",data.columns.tolist())

    if selected_columns:
        st.dataframe(data[selected_columns].head())
    else:
        st.info("No Columns Selected. Showing Full Dataset")
        st.dataframe(data.head())
    
    st.write("### 🔮 Data Visualization")
    st.write("Select **Columns** For Data Visualization")
    columns = data.columns.tolist()
    x_axis = st.selectbox("Select Column For X-Axis",options=columns)
    y_axis = st.selectbox("Select Column For Y-Axis",options=columns)

    # Create Buttons For Different Charts
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        line_btn = st.button("Click Here To Generate The Line Graph")
    with col2:
        scatter_btn = st.button("Click Here To Generate The Scatter Graph")
    with col3:
        bar_btn = st.button("Click Here To Generate Bar Graph")
    with col4:
        pie_btn = st.button("Click Here To Generate Pie Chart")
    
    if line_btn:
            st.write("### Showing A Line Graph")
            fig,ax = plt.subplots()
            ax.plot(data[x_axis],data[y_axis])
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.set_title(f"Line Graph of {x_axis} Vs {y_axis}")
            plt.xticks(rotation=65)
            st.pyplot(fig)  # show the graph

    if scatter_btn:
            st.write("### Showing A Scatter Graph")
            fig,ax = plt.subplots()
            ax.scatter(data[x_axis],data[y_axis])
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.set_title(f"Scatter Graph of {x_axis} Vs {y_axis}")
            plt.xticks(rotation=65)
            st.pyplot(fig)  # show the graph

    if bar_btn:
            st.write("### Showing A Bar Graph")
            fig,ax = plt.subplots()
            ax.bar(data[x_axis],data[y_axis])
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.set_title(f"Bar Graph of {x_axis} vs {y_axis}")
            plt.xticks(rotation=65)  
            st.pyplot(fig)  # show the graph
    
    if pie_btn:
        if data[x_axis].dtype not in ['object', 'bool']:
            st.warning("Selected data does not meet pie chart requirements.")
        else:
            st.write('### Showing a Pie Graph')

            pie_data = data[x_axis].value_counts()

            fig, ax = plt.subplots()
            ax.pie(
            pie_data.values,
            labels=pie_data.index,
            autopct='%1.1f%%',
            startangle=90)
            ax.set_title(f'Pie Chart of {x_axis}')
            ax.axis('equal')
            st.pyplot(fig)
else:
    st.info("Please Upload A CSV Or An Excel File To Get Started")

 
