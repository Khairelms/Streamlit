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

# Visualization type buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: line_btn = st.button('Line Graph')
    with col2: scatter_btn = st.button('Scatter Graph')
    with col3: bar_btn = st.button('Bar Graph')
    with col4: pie_btn = st.button('Pie Chart')
    with col5: heat_btn = st.button('Heatmap')

    # Generate line graph
    if line_btn:
        try:
            st.write('### 📉 Line Graph')
            # Convert columns to numeric, handling errors
            x_data = pd.to_numeric(data[x_axis], errors='coerce')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            # Remove rows with missing values
            clean_data = pd.DataFrame({x_axis: x_data, y_axis: y_data}).dropna()
            
            if len(clean_data) > 0:
                fig, ax = plt.subplots()
                ax.plot(clean_data[x_axis], clean_data[y_axis])
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
            else:
                st.error("No valid numeric data for line plot.")
        except Exception as e:
            st.error(f"Could not generate line plot: {str(e)}")

    # Generate scatter plot
    if scatter_btn:
        try:
            st.write('### 🏁 Scatter Plot')
            x_data = pd.to_numeric(data[x_axis], errors='coerce')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            clean_data = pd.DataFrame({x_axis: x_data, y_axis: y_data}).dropna()
            
            if len(clean_data) > 0:
                fig, ax = plt.subplots()
                ax.scatter(clean_data[x_axis], clean_data[y_axis])
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
            else:
                st.error("No valid numeric data for scatter plot.")
        except Exception as e:
            st.error(f"Could not generate scatter plot: {str(e)}")

    # Generate bar chart
    if bar_btn:
        try:
            st.write('### 📊 Bar Chart')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            if not y_data.isnull().all():
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Limit display for columns with many unique values
                if data[x_axis].nunique() > 20:
                    st.warning(f"Showing first 20 of {data[x_axis].nunique()} categories")
                    unique_vals = data[x_axis].value_counts().head(20).index
                    filtered_data = data[data[x_axis].isin(unique_vals)]
                    ax.bar(filtered_data[x_axis].astype(str), 
                          pd.to_numeric(filtered_data[y_axis], errors='coerce'))
                    plt.xticks(rotation=45, ha='right')
                else:
                    ax.bar(data[x_axis].astype(str), y_data)
                
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.error(f"Column '{y_axis}' must contain numeric data.")
        except Exception as e:
            st.error(f"Could not generate bar chart: {str(e)}")

    # Generate pie chart
    if pie_btn:
        try:
            st.write('### 🥧 Pie Chart')
            # Verify Y-axis is numeric
            if pd.api.types.is_numeric_dtype(data[y_axis]):
                # Limit to top 10 categories for readability
                if data[x_axis].nunique() > 10:
                    st.warning(f"Showing top 10 of {data[x_axis].nunique()} categories")
                    top_categories = data[x_axis].value_counts().head(10).index
                    filtered_data = data[data[x_axis].isin(top_categories)]
                    values = filtered_data.groupby(x_axis)[y_axis].sum()
                    labels = values.index
                else:
                    values = data.groupby(x_axis)[y_axis].sum()
                    labels = values.index
                
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                ax.set_title(f'{y_axis} Distribution by {x_axis}')
                st.pyplot(fig)
            else:
                st.error(f"Y-axis column must be numeric for pie chart.")
        except Exception as e:
            st.error(f"Could not generate pie chart: {str(e)}")

    # Generate correlation heatmap
    if heat_btn:
        try:
            st.write('### ♨️ Correlation Heatmap')
            # Select only numeric columns
            numeric_df = data.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                # Warn if many columns
                if len(numeric_df.columns) > 15:
                    st.warning(f"Showing correlation for {len(numeric_df.columns)} numeric columns")
                
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(numeric_df.corr(), annot=True, cmap='cividis', ax=ax, 
                           fmt='.2f', linewidths=0.5, center=0)
                plt.title('Correlation Between Numeric Columns')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No numeric columns available for correlation heatmap.")
        except Exception as e:
            st.error(f"Could not generate heatmap: {str(e)}")

# Display when no file is uploaded
else:
    st.info('Upload a CSV or Excel file to begin analysis.')