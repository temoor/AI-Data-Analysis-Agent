import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Data Visualization",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("📊 Data Visualization")

st.write(
    "Explore and visualize your questionnaire and Likert-scale survey data."
)

# ==========================================
# CHECK DATASET
# ==========================================
if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset on the Home page first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")

# ==========================================
# DATASET PREVIEW
# ==========================================
st.subheader("👀 Dataset Preview")

st.dataframe(
    df,
    use_container_width=True
)

# ==========================================
# IDENTIFY QUESTIONNAIRE VARIABLES
# ==========================================
numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

# Remove ID-type columns
questionnaire_columns = [
    col for col in numeric_columns
    if not any(
        word in str(col).lower()
        for word in [
            "id",
            "respondent",
            "participant"
        ]
    )
]

# ==========================================
# CHECK QUESTIONNAIRE VARIABLES
# ==========================================
if len(questionnaire_columns) == 0:

    st.warning(
        "⚠️ No questionnaire variables were found."
    )

else:

    st.subheader("📝 Select Questionnaire Item")

    selected_column = st.selectbox(
        "Choose a Likert-scale question/item:",
        questionnaire_columns
    )

    # ======================================
    # SELECTED ITEM STATISTICS
    # ======================================
    st.subheader(
        f"📈 Statistics for {selected_column}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mean",
            round(df[selected_column].mean(), 2)
        )

    with col2:
        st.metric(
            "Standard Deviation",
            round(df[selected_column].std(), 2)
        )

    with col3:
        st.metric(
            "Minimum",
            round(df[selected_column].min(), 2)
        )

    with col4:
        st.metric(
            "Maximum",
            round(df[selected_column].max(), 2)
        )

    # ======================================
    # CHART SELECTION
    # ======================================
    st.subheader("📊 Choose Visualization")

    chart = st.selectbox(
        "Select a chart type:",
        [
            "Likert Response Distribution",
            "Histogram",
            "Box Plot",
            "Pie Chart",
            "Correlation Heatmap",
            "Scatter Plot",
            "Line Chart"
        ]
    )

    # ======================================
    # LIKERT RESPONSE DISTRIBUTION
    # ======================================
    if chart == "Likert Response Distribution":

        frequency = (
            df[selected_column]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        frequency.columns = [
            "Likert Score",
            "Frequency"
        ]

        fig = px.bar(
            frequency,
            x="Likert Score",
            y="Frequency",
            text="Frequency",
            title=f"Likert Response Distribution - {selected_column}"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Response Frequencies")

        st.dataframe(
            frequency,
            use_container_width=True
        )

    # ======================================
    # HISTOGRAM
    # ======================================
    elif chart == "Histogram":

        fig = px.histogram(
            df,
            x=selected_column,
            nbins=5,
            title=f"Histogram - {selected_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======================================
    # BOX PLOT
    # ======================================
    elif chart == "Box Plot":

        fig = px.box(
            df,
            y=selected_column,
            title=f"Box Plot - {selected_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======================================
    # PIE CHART
    # ======================================
    elif chart == "Pie Chart":

        pie_data = (
            df[selected_column]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        pie_data.columns = [
            "Likert Score",
            "Frequency"
        ]

        fig = px.pie(
            pie_data,
            names="Likert Score",
            values="Frequency",
            title=f"Likert Response Distribution - {selected_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======================================
    # CORRELATION HEATMAP
    # ======================================
    elif chart == "Correlation Heatmap":

        correlation = df[questionnaire_columns].corr()

        fig = px.imshow(
            correlation,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap of Questionnaire Items"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======================================
    # SCATTER PLOT
    # ======================================
    elif chart == "Scatter Plot":

        col1, col2 = st.columns(2)

        with col1:

            x_axis = st.selectbox(
                "Select X-axis item:",
                questionnaire_columns,
                key="scatter_x"
            )

        with col2:

            y_axis = st.selectbox(
                "Select Y-axis item:",
                questionnaire_columns,
                key="scatter_y"
            )

        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            title=f"Scatter Plot: {x_axis} vs {y_axis}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======================================
    # LINE CHART
    # ======================================
    elif chart == "Line Chart":

        plot_data = df[selected_column].reset_index()

        plot_data.columns = [
            "Respondent",
            "Response"
        ]

        fig = px.line(
            plot_data,
            x="Respondent",
            y="Response",
            title=f"Responses Across Respondents - {selected_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
