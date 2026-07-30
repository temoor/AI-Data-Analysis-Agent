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

    # ======================================
    # DESCRIPTIVE STATISTICS
    # ======================================
    st.header("📈 Descriptive Statistics")
    st.dataframe(df.describe(include="all"))

    # ======================================
    # VISUALISATION
    # ======================================
    st.header("📊 Data Visualisation")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_columns) > 0:

        selected_column = st.selectbox(
            "Select Numeric Column",
            numeric_columns
        )

        chart = st.selectbox(
            "Choose Chart",
            [
                "Bar Chart",
                "Histogram",
                "Box Plot",
                "Correlation Heatmap",
                "Scatter Plot",
                "Line Chart",
                "Pie Chart"
            ]
        )
                # ================================
        # BAR CHART
        # ================================
        if chart == "Bar Chart":

            value_counts = (
                df[selected_column]
                .value_counts()
                .sort_index()
                .reset_index()
            )

            value_counts.columns = [selected_column, "Count"]

            fig = px.bar(
                value_counts,
                x=selected_column,
                y="Count",
                title=f"Bar Chart - {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # HISTOGRAM
        # ================================
        elif chart == "Histogram":

            fig = px.histogram(
                df,
                x=selected_column,
                title=f"Histogram - {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # BOX PLOT
        # ================================
        elif chart == "Box Plot":

            fig = px.box(
                df,
                y=selected_column,
                title=f"Box Plot - {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # CORRELATION HEATMAP
        # ================================
        elif chart == "Correlation Heatmap":

            correlation = df[numeric_columns].corr()

            fig = px.imshow(
                correlation,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Correlation Heatmap"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # SCATTER PLOT
        # ================================
        elif chart == "Scatter Plot":

            x_axis = st.selectbox(
                "Select X-axis",
                numeric_columns,
                key="scatter_x"
            )

            y_axis = st.selectbox(
                "Select Y-axis",
                numeric_columns,
                key="scatter_y"
            )

            fig = px.scatter(
                df,
                x=x_axis,
                y=y_axis,
                title=f"Scatter Plot: {x_axis} vs {y_axis}"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # LINE CHART
        # ================================
        elif chart == "Line Chart":

            fig = px.line(
                df,
                y=selected_column,
                title=f"Line Chart - {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # PIE CHART
        # ================================
        elif chart == "Pie Chart":

            pie_data = (
                df[selected_column]
                .value_counts()
                .reset_index()
            )

            pie_data.columns = [selected_column, "Count"]

            fig = px.pie(
                pie_data,
                names=selected_column,
                values="Count",
                title=f"Pie Chart - {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No numeric columns found in this dataset.")
