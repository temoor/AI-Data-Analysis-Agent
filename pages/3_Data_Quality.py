import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Data Quality",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Data Quality Assessment")

st.write(
    "Check the uploaded survey dataset for common data-quality "
    "problems before proceeding to further analysis."
)

# ==========================================
# CHECK DATASET
# ==========================================
if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset on the Home page first.")
    st.stop()

df = st.session_state["df"].copy()

st.success("✅ Dataset loaded successfully.")

# ==========================================
# DATASET OVERVIEW
# ==========================================
st.subheader("📊 Dataset Overview")

total_rows = len(df)
total_columns = len(df.columns)

missing_values = int(df.isnull().sum().sum())
duplicate_rows = int(df.duplicated().sum())

empty_rows = int(df.isnull().all(axis=1).sum())
empty_columns = int(df.isnull().all(axis=0).sum())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Respondents", total_rows)

with col2:
    st.metric("Variables / Items", total_columns)

with col3:
    st.metric("Missing Values", missing_values)

with col4:
    st.metric("Duplicate Rows", duplicate_rows)

# ==========================================
# OVERALL DATA QUALITY
# ==========================================
st.subheader("🟢 Overall Data Quality")

quality_issues = 0

if missing_values > 0:
    quality_issues += 1

if duplicate_rows > 0:
    quality_issues += 1

if empty_rows > 0:
    quality_issues += 1

if empty_columns > 0:
    quality_issues += 1

if quality_issues == 0:
    st.success(
        "✅ No major structural data-quality problems were detected."
    )
elif quality_issues <= 2:
    st.warning(
        "⚠️ Some data-quality issues were detected. "
        "Review the sections below before analysis."
    )
else:
    st.error(
        "❌ Several data-quality issues were detected. "
        "The dataset should be reviewed before analysis."
    )

# ==========================================
# DATASET PREVIEW
# ==========================================
st.subheader("👀 Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)

# ==========================================
# MISSING VALUES
# ==========================================
st.subheader("❗ Missing Values")

missing_table = pd.DataFrame({
    "Variable / Item": df.columns,
    "Missing Values": df.isnull().sum().values,
    "Missing Percentage (%)": (
        df.isnull().sum() / len(df) * 100
    ).round(2).values
})

missing_table = missing_table[
    missing_table["Missing Values"] > 0
]

if missing_table.empty:
    st.success("✅ No missing values were detected.")
else:
    st.warning(
        f"⚠️ Missing values were detected in "
        f"{len(missing_table)} variable(s)."
    )

    st.dataframe(
        missing_table,
        use_container_width=True
    )

# ==========================================
# DUPLICATE RESPONSES
# ==========================================
st.subheader("🔁 Duplicate Responses")

if duplicate_rows == 0:
    st.success("✅ No completely duplicated responses were detected.")
else:
    st.warning(
        f"⚠️ {duplicate_rows} duplicate response(s) were detected."
    )

# ==========================================
# EMPTY ROWS / COLUMNS
# ==========================================
st.subheader("🗑️ Empty Rows and Columns")

col1, col2 = st.columns(2)

with col1:
    if empty_rows == 0:
        st.success("✅ No completely empty rows.")
    else:
        st.warning(
            f"⚠️ {empty_rows} completely empty row(s) detected."
        )

with col2:
    if empty_columns == 0:
        st.success("✅ No completely empty columns.")
    else:
        st.warning(
            f"⚠️ {empty_columns} completely empty column(s) detected."
        )

# ==========================================
# DATA TYPES
# ==========================================
st.subheader("📋 Variable Types")

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_columns = df.select_dtypes(
    exclude="number"
).columns.tolist()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Numeric Variables",
        len(numeric_columns)
    )

with col2:
    st.metric(
        "Non-Numeric Variables",
        len(categorical_columns)
    )

datatype_table = pd.DataFrame({
    "Variable / Item": df.columns,
    "Data Type": df.dtypes.astype(str).values
})

st.dataframe(
    datatype_table,
    use_container_width=True
)

# ==========================================
# LIKERT SCALE CHECK
# ==========================================
st.subheader("📏 Likert-Scale Value Check")

st.write(
    "Select the response scale used in your questionnaire. "
    "The system will identify numeric values outside the selected range."
)

likert_scale = st.selectbox(
    "Select Likert Scale",
    [
        "1–5",
        "1–7",
        "1–4",
        "1–6",
        "1–10",
        "Do not check Likert range"
    ]
)

if likert_scale != "Do not check Likert range":

    scale_parts = likert_scale.split("–")
    minimum_value = int(scale_parts[0])
    maximum_value = int(scale_parts[1])

    invalid_results = []

    for column in numeric_columns:

        values = df[column].dropna()

        invalid_values = values[
            (values < minimum_value) |
            (values > maximum_value)
        ]

        if len(invalid_values) > 0:

            invalid_results.append({
                "Variable / Item": column,
                "Invalid Values": len(invalid_values),
                "Observed Values": ", ".join(
                    map(
                        str,
                        sorted(
                            invalid_values.unique()
                        )
                    )
                )
            })

    if len(invalid_results) == 0:

        st.success(
            f"✅ No values outside the selected "
            f"{minimum_value}–{maximum_value} range were detected."
        )

    else:

        st.error(
            f"❌ Values outside the selected "
            f"{minimum_value}–{maximum_value} range were detected."
        )

        invalid_table = pd.DataFrame(
            invalid_results
        )

        st.dataframe(
            invalid_table,
            use_container_width=True
        )

# ==========================================
# CONSTANT VARIABLES
# ==========================================
st.subheader("⚠️ Variables With No Variation")

constant_variables = []

for column in numeric_columns:

    if df[column].nunique(dropna=True) <= 1:

        constant_variables.append(column)

if len(constant_variables) == 0:

    st.success(
        "✅ No numeric variables with zero variation were detected."
    )

else:

    st.warning(
        "⚠️ The following variables contain only one "
        "observed value and should be reviewed:"
    )

    st.write(constant_variables)

# ==========================================
# ITEM COMPLETENESS
# ==========================================
st.subheader("📈 Item Completeness")

completeness_table = pd.DataFrame({
    "Variable / Item": df.columns,
    "Valid Responses": df.notnull().sum().values,
    "Missing Responses": df.isnull().sum().values,
    "Completeness (%)": (
        df.notnull().sum() / len(df) * 100
    ).round(2).values
})

st.dataframe(
    completeness_table,
    use_container_width=True
)

# ==========================================
# DATA QUALITY SUMMARY
# ==========================================
st.subheader("📝 Data Quality Summary")

summary = []

summary.append({
    "Check": "Missing Values",
    "Result": (
        "No issues detected"
        if missing_values == 0
        else f"{missing_values} missing value(s)"
    )
})

summary.append({
    "Check": "Duplicate Responses",
    "Result": (
        "No duplicates detected"
        if duplicate_rows == 0
        else f"{duplicate_rows} duplicate row(s)"
    )
})

summary.append({
    "Check": "Empty Rows",
    "Result": (
        "No empty rows"
        if empty_rows == 0
        else f"{empty_rows} empty row(s)"
    )
})

summary.append({
    "Check": "Empty Columns",
    "Result": (
        "No empty columns"
        if empty_columns == 0
        else f"{empty_columns} empty column(s)"
    )
})

summary_table = pd.DataFrame(summary)

st.dataframe(
    summary_table,
    use_container_width=True
)

st.info(
    "ℹ️ This page identifies potential data-quality problems. "
    "The researcher should review the flagged cases before "
    "making decisions about data cleaning or exclusion."
)
