import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Exploratory Data Analysis",
    page_icon="🔎",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("🔎 Exploratory Data Analysis")

st.write(
    "Explore the structure, distributions, variability, "
    "and relationships within your survey dataset."
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
# DATASET OVERVIEW
# ==========================================
st.subheader("📊 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Rows", df.shape[0])

with col2:
    st.metric("Columns", df.shape[1])

with col3:
    st.metric(
        "Missing Values",
        int(df.isnull().sum().sum())
    )

with col4:
    st.metric(
        "Duplicate Rows",
        int(df.duplicated().sum())
    )

# ==========================================
# NUMERIC VARIABLES
# ==========================================
numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

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
# SUMMARY STATISTICS
# ==========================================
st.subheader("📈 Summary of Questionnaire Variables")

if len(questionnaire_columns) > 0:

    summary = pd.DataFrame({
        "Variable": questionnaire_columns,
        "Mean": [
            round(df[col].mean(), 2)
            for col in questionnaire_columns
        ],
        "Standard Deviation": [
            round(df[col].std(), 2)
            for col in questionnaire_columns
        ],
        "Minimum": [
            df[col].min()
            for col in questionnaire_columns
        ],
        "Maximum": [
            df[col].max()
            for col in questionnaire_columns
        ]
    })

    st.dataframe(
        summary,
        use_container_width=True
    )

else:

    st.warning(
        "No questionnaire variables were detected."
    )

# ==========================================
# VARIABLE DISTRIBUTION
# ==========================================
st.subheader("📊 Variable Distribution")

if len(questionnaire_columns) > 0:

    selected_variable = st.selectbox(
        "Select a questionnaire variable:",
        questionnaire_columns
    )

    fig = px.histogram(
        df,
        x=selected_variable,
        nbins=5,
        title=f"Distribution of {selected_variable}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# CORRELATION ANALYSIS
# ==========================================
st.subheader("🔗 Correlation Analysis")

if len(questionnaire_columns) >= 2:

    correlation = df[questionnaire_columns].corr()

    fig = px.imshow(
        correlation,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix of Questionnaire Items"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# SKEWNESS AND KURTOSIS
# ==========================================
st.subheader("📐 Skewness and Kurtosis")

if len(questionnaire_columns) > 0:

    distribution_stats = pd.DataFrame({
        "Variable": questionnaire_columns,
        "Skewness": [
            round(df[col].skew(), 3)
            for col in questionnaire_columns
        ],
        "Kurtosis": [
            round(df[col].kurtosis(), 3)
            for col in questionnaire_columns
        ]
    })

    st.dataframe(
        distribution_stats,
        use_container_width=True
    )

# ==========================================
# OUTLIER CHECK
# ==========================================
st.subheader("📌 Outlier Check")

if len(questionnaire_columns) > 0:

    outlier_results = []

    for col in questionnaire_columns:

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[
            (df[col] < lower_bound) |
            (df[col] > upper_bound)
        ]

        outlier_results.append({
            "Variable": col,
            "Outlier Count": len(outliers)
        })

    outlier_df = pd.DataFrame(
        outlier_results
    )

    st.dataframe(
        outlier_df,
        use_container_width=True
    )

# ==========================================
# CONSTRUCT-LEVEL OVERVIEW
# ==========================================
st.subheader("🧩 Construct-Level Overview")

constructs = {
    "SD": [f"SD{i}" for i in range(1, 16)],
    "GI": [f"GI{i}" for i in range(1, 16)],
    "OP": [f"OP{i}" for i in range(1, 16)]
}

construct_summary = []

for construct, items in constructs.items():

    available_items = [
        item for item in items
        if item in df.columns
    ]

    if len(available_items) > 0:

        construct_score = df[
            available_items
        ].mean(axis=1)

        construct_summary.append({
            "Construct": construct,
            "Number of Items": len(available_items),
            "Mean Score": round(
                construct_score.mean(), 2
            ),
            "Standard Deviation": round(
                construct_score.std(), 2
            )
        })

if len(construct_summary) > 0:

    construct_df = pd.DataFrame(
        construct_summary
    )

    st.dataframe(
        construct_df,
        use_container_width=True
    )

else:

    st.info(
        "No predefined constructs were detected."
    )
