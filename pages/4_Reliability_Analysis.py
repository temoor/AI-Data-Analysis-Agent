import streamlit as st
import pandas as pd
import numpy as np


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Reliability Analysis",
    page_icon="📋",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================
st.title("📋 Reliability Analysis")

st.write(
    "Calculate Cronbach's Alpha to assess the internal "
    "consistency of questionnaire items."
)


# =========================================================
# CHECK DATASET
# =========================================================
if "df" not in st.session_state:

    st.warning(
        "⚠️ Please upload a dataset on the Home page first."
    )

    st.stop()


df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")


# =========================================================
# DATASET INFORMATION
# =========================================================
st.subheader("📊 Dataset Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Respondents",
        df.shape[0]
    )

with col2:
    st.metric(
        "Variables",
        df.shape[1]
    )

with col3:
    numeric_count = len(
        df.select_dtypes(include="number").columns
    )

    st.metric(
        "Numeric Variables",
        numeric_count
    )


# =========================================================
# DATASET PREVIEW
# =========================================================
with st.expander("👀 View Dataset Preview"):

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# =========================================================
# CRONBACH'S ALPHA FUNCTION
# =========================================================
def cronbach_alpha(data):

    # Keep numeric data only
    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Remove rows with missing values
    data = data.dropna()

    # Need at least two items
    if data.shape[1] < 2:
        return np.nan

    # Need at least two respondents
    if data.shape[0] < 2:
        return np.nan

    item_variances = data.var(
        axis=0,
        ddof=1
    )

    total_score = data.sum(
        axis=1
    )

    total_variance = total_score.var(
        ddof=1
    )

    if pd.isna(total_variance) or total_variance == 0:
        return np.nan

    k = data.shape[1]

    alpha = (
        k / (k - 1)
    ) * (
        1
        -
        item_variances.sum()
        / total_variance
    )

    return float(alpha)


# =========================================================
# INTERPRETATION FUNCTION
# =========================================================
def interpret_alpha(alpha):

    if pd.isna(alpha):
        return "Unable to calculate"

    if alpha >= 0.90:
        return "Excellent internal consistency"

    elif alpha >= 0.80:
        return "Good internal consistency"

    elif alpha >= 0.70:
        return "Acceptable internal consistency"

    elif alpha >= 0.60:
        return "Questionable internal consistency"

    else:
        return "Poor internal consistency"


# =========================================================
# BUILD RELIABILITY STRUCTURE
# =========================================================
reliability_groups = []


# =========================================================
# OPTION 1:
# HIGHER-ORDER / EXCEL STRUCTURE
# =========================================================
if "pls_structure" in st.session_state:

    structure = st.session_state["pls_structure"]

    if isinstance(structure, pd.DataFrame):

        structure = structure.copy()

        # Standardize column names
        structure.columns = [
            str(col).strip()
            for col in structure.columns
        ]

        required_columns = [
            "Higher_Order_Construct",
            "Dimension",
            "Measurement_Type",
            "Indicator"
        ]

        if all(
            col in structure.columns
            for col in required_columns
        ):

            for _, row in structure.iterrows():

                hoc = str(
                    row["Higher_Order_Construct"]
                ).strip()

                dimension = str(
                    row["Dimension"]
                ).strip()

                measurement_type = str(
                    row["Measurement_Type"]
                ).strip()

                indicator = str(
                    row["Indicator"]
                ).strip()

                if (
                    hoc
                    and dimension
                    and indicator
                    and indicator in df.columns
                ):

                    reliability_groups.append({

                        "Model_Type": "Higher-Order",

                        "Construct": hoc,

                        "Dimension": dimension,

                        "Measurement_Type":
                            measurement_type,

                        "Indicator": indicator
                    })


# =========================================================
# OPTION 2:
# SIMPLE CONSTRUCT STRUCTURE
# =========================================================
if (
    not reliability_groups
    and "pls_constructs" in st.session_state
):

    simple_constructs = (
        st.session_state["pls_constructs"]
    )

    if isinstance(simple_constructs, dict):

        for construct, information in (
            simple_constructs.items()
        ):

            items = []

            measurement_type = "Reflective"

            if isinstance(information, dict):

                items = information.get(
                    "items",
                    []
                )

                measurement_type = information.get(
                    "type",
                    "Reflective"
                )

            elif isinstance(information, list):

                items = information

            for item in items:

                if item in df.columns:

                    reliability_groups.append({

                        "Model_Type": "Simple",

                        "Construct": construct,

                        "Dimension": construct,

                        "Measurement_Type":
                            measurement_type,

                        "Indicator": item
                    })


# =========================================================
# NO STRUCTURE FOUND
# =========================================================
if not reliability_groups:

    st.error(
        "❌ No valid questionnaire structure was found."
    )

    st.info(
        "Please upload your dataset through the Home page "
        "and make sure the PLS-SEM structure sheet is available, "
        "or define a Simple PLS-SEM model first."
    )

    st.stop()


# =========================================================
# CREATE STRUCTURE DATAFRAME
# =========================================================
reliability_structure = pd.DataFrame(
    reliability_groups
)


# Remove duplicate indicator assignments
reliability_structure = (
    reliability_structure
    .drop_duplicates()
    .reset_index(drop=True)
)


# =========================================================
# SUMMARY OF DETECTED STRUCTURE
# =========================================================
st.subheader("🧩 Detected Questionnaire Structure")

summary_constructs = (
    reliability_structure[
        [
            "Model_Type",
            "Construct",
            "Dimension",
            "Measurement_Type"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

summary_constructs["Number of Indicators"] = (
    reliability_structure
    .groupby(
        [
            "Model_Type",
            "Construct",
            "Dimension"
        ]
    )["Indicator"]
    .transform("count")
)

summary_constructs = (
    summary_constructs
    .drop_duplicates()
    .reset_index(drop=True)
)

st.dataframe(
    summary_constructs,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# RELIABILITY CALCULATION
# =========================================================
reliability_results = []


group_columns = [
    "Model_Type",
    "Construct",
    "Dimension",
    "Measurement_Type"
]


for group_values, group_data in (
    reliability_structure.groupby(
        group_columns,
        dropna=False
    )
):

    model_type = group_values[0]

    construct = group_values[1]

    dimension = group_values[2]

    measurement_type = group_values[3]

    items = (
        group_data["Indicator"]
        .dropna()
        .astype(str)
        .tolist()
    )

    # Keep only columns actually present in dataset
    valid_items = [
        item
        for item in items
        if item in df.columns
    ]

    alpha = np.nan

    if (
        measurement_type.lower()
        == "reflective"
        and len(valid_items) >= 2
    ):

        alpha = cronbach_alpha(
            df[valid_items]
        )

    reliability_results.append({

        "Model Type":
            model_type,

        "Construct":
            construct,

        "Dimension":
            dimension,

        "Measurement Type":
            measurement_type,

        "Number of Items":
            len(valid_items),

        "Cronbach's Alpha":
            (
                round(alpha, 3)
                if not pd.isna(alpha)
                else np.nan
            ),

        "Interpretation":
            interpret_alpha(alpha)

    })


reliability_results_df = pd.DataFrame(
    reliability_results
)


# =========================================================
# MAIN RELIABILITY RESULTS
# =========================================================
st.divider()

st.subheader(
    "📊 Cronbach's Alpha Results"
)


st.dataframe(
    reliability_results_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# OVERALL SUMMARY
# =========================================================
reflective_results = (
    reliability_results_df[
        reliability_results_df[
            "Measurement Type"
        ]
        .astype(str)
        .str.lower()
        == "reflective"
    ]
    .copy()
)


if not reflective_results.empty:

    valid_alpha_results = (
        reflective_results[
            reflective_results[
                "Cronbach's Alpha"
            ].notna()
        ]
    )

    acceptable_count = (
        valid_alpha_results[
            valid_alpha_results[
                "Cronbach's Alpha"
            ] >= 0.70
        ].shape[0]
    )

    total_count = (
        valid_alpha_results.shape[0]
    )

    st.subheader(
        "📈 Reliability Overview"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Reflective Dimensions",
            total_count
        )

    with col2:

        st.metric(
            "Alpha ≥ 0.70",
            acceptable_count
        )

    with col3:

        if total_count > 0:

            percentage = (
                acceptable_count
                / total_count
                * 100
            )

            st.metric(
                "Acceptable (%)",
                f"{percentage:.1f}%"
            )

        else:

            st.metric(
                "Acceptable (%)",
                "N/A"
            )


# =========================================================
# SELECT INDIVIDUAL DIMENSION
# =========================================================
st.divider()

st.subheader(
    "🔍 Detailed Reliability Analysis"
)


dimension_options = (
    reliability_structure[
        [
            "Model_Type",
            "Construct",
            "Dimension",
            "Measurement_Type"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)


dimension_labels = []

for _, row in dimension_options.iterrows():

    label = (
        f"{row['Construct']} → "
        f"{row['Dimension']}"
    )

    dimension_labels.append(label)


if dimension_labels:

    selected_label = st.selectbox(
        "Select a dimension:",
        dimension_labels
    )

    selected_index = (
        dimension_labels.index(
            selected_label
        )
    )

    selected_row = (
        dimension_options.iloc[
            selected_index
        ]
    )

    selected_construct = (
        selected_row["Construct"]
    )

    selected_dimension = (
        selected_row["Dimension"]
    )

    selected_measurement_type = (
        selected_row["Measurement_Type"]
    )

    selected_items = (
        reliability_structure[
            (
                reliability_structure[
                    "Construct"
                ]
                == selected_construct
            )
            &
            (
                reliability_structure[
                    "Dimension"
                ]
                == selected_dimension
            )
        ]["Indicator"]
        .dropna()
        .astype(str)
        .tolist()
    )

    selected_items = [
        item
        for item in selected_items
        if item in df.columns
    ]

    st.write(
        f"**Construct:** {selected_construct}"
    )

    st.write(
        f"**Dimension:** {selected_dimension}"
    )

    st.write(
        f"**Measurement Type:** "
        f"{selected_measurement_type}"
    )

    st.write(
        f"**Number of Items:** "
        f"{len(selected_items)}"
    )

    st.write(
        "Items: "
        + ", ".join(selected_items)
    )

    # -----------------------------------------------------
    # SELECTED ALPHA
    # -----------------------------------------------------
    if (
        selected_measurement_type.lower()
        == "reflective"
        and len(selected_items) >= 2
    ):

        selected_alpha = cronbach_alpha(
            df[selected_items]
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Cronbach's Alpha",
                (
                    f"{selected_alpha:.3f}"
                    if not pd.isna(selected_alpha)
                    else "N/A"
                )
            )

        with col2:

            st.metric(
                "Number of Items",
                len(selected_items)
            )

        if not pd.isna(selected_alpha):

            interpretation = interpret_alpha(
                selected_alpha
            )

            if selected_alpha >= 0.70:

                st.success(
                    f"✅ {interpretation}"
                )

            else:

                st.warning(
                    f"⚠️ {interpretation}"
                )

    elif (
        selected_measurement_type.lower()
        == "formative"
    ):

        st.info(
            "ℹ️ Cronbach's Alpha is generally not "
            "the primary reliability assessment for "
            "formative measurement. VIF and indicator "
            "weights/significance should be considered "
            "instead."
        )

    else:

        st.warning(
            "⚠️ At least two valid indicators are "
            "required to calculate Cronbach's Alpha."
        )


# =========================================================
# ITEM STATISTICS
# =========================================================
if selected_items:

    st.subheader(
        "📋 Item Statistics"
    )

    item_statistics = pd.DataFrame({

        "Item":
            selected_items,

        "Mean": [
            round(
                pd.to_numeric(
                    df[item],
                    errors="coerce"
                ).mean(),
                3
            )
            for item in selected_items
        ],

        "Standard Deviation": [
            round(
                pd.to_numeric(
                    df[item],
                    errors="coerce"
                ).std(),
                3
            )
            for item in selected_items
        ],

        "Valid Responses": [
            pd.to_numeric(
                df[item],
                errors="coerce"
            ).notna().sum()
            for item in selected_items
        ],

        "Missing Responses": [
            pd.to_numeric(
                df[item],
                errors="coerce"
            ).isna().sum()
            for item in selected_items
        ]

    })

    st.dataframe(
        item_statistics,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# SAVE RESULTS FOR PROJECT MANAGER
# =========================================================
st.session_state[
    "reliability_results"
] = reliability_results_df.to_dict(
    orient="records"
)


# =========================================================
# METHODOLOGICAL NOTE
# =========================================================
st.divider()

with st.expander(
    "ℹ️ Methodological Note"
):

    st.write(
        """
        Cronbach's Alpha is used here to assess the internal
        consistency of reflective questionnaire dimensions.

        A commonly used rule of thumb is that values of 0.70
        or higher indicate acceptable internal consistency,
        although interpretation should consider the research
        context, number of items, and measurement model.

        For formative measurement, Cronbach's Alpha is not
        treated as the primary reliability assessment.

        This page is designed to read the researcher's
        questionnaire structure automatically rather than
        depending on fixed questionnaire column names.
        """
    )
