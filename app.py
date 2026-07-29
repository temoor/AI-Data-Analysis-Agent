import streamlit as st
import pandas as pd

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="🤖",
    layout="wide"
)

# ------------------------------
# Title
# ------------------------------
st.title("🤖 AI Data Analysis Agent")

st.markdown("""
Welcome to the **AI Data Analysis Agent**.

Upload an **Excel (.xlsx)** or **CSV (.csv)** dataset to begin analysing your data.
""")

# ------------------------------
# File Upload
# ------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload an Excel or CSV File",
    type=["xlsx", "csv"]
)

# ------------------------------
# Read File
# ------------------------------
if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    # ------------------------------
    # Dataset Preview
    # ------------------------------
    st.subheader("👀 Dataset Preview")

    st.dataframe(df)

    # ------------------------------
    # Dataset Information
    # ------------------------------
    st.subheader("📊 Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    st.write("### Column Names")

    st.write(list(df.columns))

    # ------------------------------
    # Descriptive Statistics
    # ------------------------------
    st.subheader("📈 Descriptive Statistics")

    st.dataframe(df.describe(include="all"))
    # ------------------------------
    # Charts
    # ------------------------------

    st.subheader("📊 Data Visualisation")
    

    
    

    numeric_columns = df.select_dtypes(include="number").columns
    

    if len(numeric_columns) > 0:

        selected_column = st.selectbox(
            "Select a Numeric Column",
            numeric_columns
        )

        chart = st.selectbox(
    "Choose Chart",
    [
        "Bar Chart",
        "Histogram",
        "Box Plot",
        "Correlation Heatmap"
    ]
)

        import plotly.express as px

        if chart == "Bar Chart":

            fig = px.bar(
                df[selected_column].value_counts().sort_index(),
                title=f"Bar Chart of {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        elif chart == "Histogram":

            fig = px.histogram(
                df,
                x=selected_column,
                title=f"Histogram of {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

                      elif chart == "Box Plot":

            fig = px.box(
                df,
                y=selected_column,
                title=f"Box Plot of {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        elif chart == "Correlation Heatmap":

            correlation = df[numeric_columns].corr()

            fig = px.imshow(
                correlation,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                title="Correlation Heatmap"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.plotly_chart(fig, use_container_width=True)
         
