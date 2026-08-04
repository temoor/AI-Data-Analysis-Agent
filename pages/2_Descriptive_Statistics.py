import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Descriptive Statistics",
    page_icon="📈"
)

st.title("📈 Descriptive Statistics")

st.write("View descriptive statistics for the dataset uploaded on the Home page.")

# Check whether dataset exists
if "df" not in st.session_state:
    st.warning("⚠ Please upload a dataset on the Home page first.")
    st.stop()

# Load dataset
df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")

# Dataset Preview
st.subheader("👀 Dataset Preview")
st.dataframe(df, use_container_width=True)

# Descriptive Statistics
st.subheader("📊 Descriptive Statistics")

st.dataframe(
    df.describe(include="all"),
    use_container_width=True
)

# Numeric Columns
numeric_columns = df.select_dtypes(include="number").columns.tolist()

if len(numeric_columns) > 0:

    st.subheader("📈 Individual Column Statistics")

    selected_column = st.selectbox(
        "Select Numeric Column",
        numeric_columns
    )

    st.write(f"### Statistics for: {selected_column}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mean", round(df[selected_column].mean(), 2))
        st.metric("Median", round(df[selected_column].median(), 2))
        st.metric("Minimum", round(df[selected_column].min(), 2))
        st.metric("Maximum", round(df[selected_column].max(), 2))

    with col2:
        st.metric("Standard Deviation", round(df[selected_column].std(), 2))
        st.metric("Variance", round(df[selected_column].var(), 2))
        st.metric("Count", int(df[selected_column].count()))
        st.metric("Missing Values", int(df[selected_column].isna().sum()))

else:
    st.warning("No numeric columns found in this dataset.")
