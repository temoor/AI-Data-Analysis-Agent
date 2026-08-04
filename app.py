import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("🤖 AI Data Analysis Agent")

st.markdown("""
Welcome to the **AI Data Analysis Agent**.

Upload an Excel (.xlsx) or CSV (.csv) file to analyse your data.
""")

# ==========================================
# FILE UPLOAD
# ==========================================
uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # ======================================
    # READ FILE
    # ======================================
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    # Save dataset for all pages
    st.session_state["df"] = df
    st.success("✅ File uploaded successfully!")

    # ======================================
    # DATASET PREVIEW
    # ======================================
    st.header("👀 Dataset Preview")
    st.dataframe(df, use_container_width=True)

    # ======================================
    # DATASET INFORMATION
    # ======================================
    st.header("📊 Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    st.write("### Column Names")
    st.write(list(df.columns))
    
