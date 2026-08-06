import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Data Quality",
    page_icon="🔍"
)

st.title("🔍 Data Quality")

st.write("Check the quality of the dataset uploaded on the Home page.")

# Check whether dataset exists
if "df" not in st.session_state:
    st.warning("⚠ Please upload a dataset on the Home page first.")
    st.stop()

# Load dataset
df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")

# ==========================================
# Dataset Preview
# ==========================================
st.subheader("👀 Dataset Preview")
st.dataframe(df, use_container_width=True)

# ==========================================
# Data Quality Summary
# ==========================================
st.subheader("📋 Data Quality Summary")

total_rows = df.shape[0]
total_columns = df.shape[1]
missing_values = df.isnull().sum().sum()
duplicate_rows = df.duplicated().sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Rows", total_rows)
    st.metric("Columns", total_columns)

with col2:
    st.metric("Missing Values", int(missing_values))
    st.metric("Duplicate Rows", int(duplicate_rows))

# ==========================================
# Missing Values by Column
# ==========================================
st.subheader("❗ Missing Values by Column")

missing_table = pd.DataFrame({
    "Column": df.columns,
    "Missing Values": df.isnull().sum().values,
    "Missing Percentage (%)": (
        df.isnull().sum() / len(df) * 100
    ).round(2).values
})

st.dataframe(missing_table, use_container_width=True)

# ==========================================
# Data Types
# ==========================================
st.subheader("📊 Data Types")

datatype_table = pd.DataFrame({
    "Column": df.columns,
    "Data Type": df.dtypes.astype(str).values
})

st.dataframe(datatype_table, use_container_width=True)

# ==========================================
# Numeric & Categorical Summary
# ==========================================
numeric_columns = df.select_dtypes(include="number").columns.tolist()
categorical_columns = df.select_dtypes(exclude="number").columns.tolist()

st.subheader("📈 Variable Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Numeric Columns", len(numeric_columns))

with col2:
    st.metric("Categorical Columns", len(categorical_columns))
