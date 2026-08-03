import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Visualization", page_icon="📊")

st.title("📊 Data Visualization")

st.write("Visualize the dataset uploaded on the Home page.")

# Check if a dataset has been uploaded on the Home page
if "df" not in st.session_state:
    st.warning("⚠ Please upload a dataset on the Home page first.")
    st.stop()

# Load dataset from session state
df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")

# Preview dataset
st.subheader("Dataset Preview")
st.dataframe(df, use_container_width=True)

# Find numeric columns
numeric_columns = df.select_dtypes(include="number").columns.tolist()

if len(numeric_columns) == 0:
    st.warning("No numeric columns found.")

else:

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

    # ==========================
    # BAR CHART
    # ==========================
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

    # ==========================
    # HISTOGRAM
    # ==========================
    elif chart == "Histogram":

        fig = px.histogram(
            df,
            x=selected_column,
            title=f"Histogram - {selected_column}"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # BOX PLOT
    # ==========================
    elif chart == "Box Plot":

        fig = px.box(
            df,
            y=selected_column,
            title=f"Box Plot - {selected_column}"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # CORRELATION HEATMAP
    # ==========================
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

    # ==========================
    # SCATTER PLOT
    # ==========================
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

    # ==========================
    # LINE CHART
    # ==========================
    elif chart == "Line Chart":

        fig = px.line(
            df,
            y=selected_column,
            title=f"Line Chart - {selected_column}"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # PIE CHART
    # ==========================
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
