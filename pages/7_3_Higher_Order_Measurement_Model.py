import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Higher-Order Measurement Model",
    page_icon="📐",
    layout="wide"
)

st.title("📐 Higher-Order Measurement Model")

st.write(
    "This page evaluates the dimensions and indicators of the "
    "Higher-Order Construct already defined in the previous step."
)


# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:
    st.warning(
        "⚠️ Please upload your dataset on the Home page first."
    )
    st.stop()

df = st.session_state["df"].copy()

st.success("✅ Dataset loaded successfully.")


# ============================================================
# CHECK HIGHER-ORDER MODEL
# ============================================================

if "pls_higher_order_model" not in st.session_state:
    st.warning(
        "⚠️ No Higher-Order Construct model has been saved yet."
    )

    st.info(
        "Please go to Higher-Order Construct Setup, define the "
        "model, and save it first."
    )

    st.stop()


model = st.session_state["pls_higher_order_model"]

hoc_name = model.get(
    "name",
    "Higher-Order Construct"
)

hoc_type = model.get(
    "type",
    "Reflective"
)

dimensions = model.get(
    "dimensions",
    {}
)


if not dimensions:
    st.error(
        "❌ No dimensions were found in the saved model."
    )
    st.stop()


# ============================================================
# DATASET INFORMATION
# ============================================================

st.divider()

st.subheader("📋 Dataset Information")

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
    st.metric(
        "Dimensions",
        len(dimensions)
    )


# ============================================================
# HIGHER-ORDER MODEL
# ============================================================

st.divider()

st.subheader("🏗️ Higher-Order Construct")

st.markdown(
    "### " + str(hoc_name)
)

st.write(
    "**Higher-Order Measurement Type:** "
    + str(hoc_type)
)


# ============================================================
# MODEL STRUCTURE
# ============================================================

model_rows = []

for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    dimension_type = information.get(
        "type",
        "Reflective"
    )

    model_rows.append(
        {
            "Dimension": dimension_name,
            "Dimension Type": dimension_type,
            "Number of Indicators": len(items),
            "Indicators": ", ".join(items)
        }
    )


model_table = pd.DataFrame(model_rows)

st.dataframe(
    model_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FUNCTIONS
# ============================================================

def cronbach_alpha(data):

    data = data.dropna()

    if data.shape[1] < 2:
        return np.nan

    item_variance = data.var(
        axis=0,
        ddof=1
    )

    total_score = data.sum(
        axis=1
    )

    total_variance = total_score.var(
        ddof=1
    )

    if total_variance == 0:
        return np.nan

    k = data.shape[1]

    alpha = (
        k / (k - 1)
    ) * (
        1 -
        item_variance.sum() /
        total_variance
    )

    return alpha


def calculate_loadings(data):

    data = data.dropna()

    if data.shape[1] == 1:

        return pd.Series(
            [1.0],
            index=data.columns
        )

    standardized = (
        data - data.mean()
    ) / data.std(
        ddof=0
    )

    standardized = standardized.dropna()

    if standardized.empty:

        return pd.Series(
            np.nan,
            index=data.columns
        )

    score = standardized.mean(
        axis=1
    )

    results = {}

    for column in standardized.columns:

        correlation = standardized[
            column
        ].corr(score)

        results[column] = abs(
            correlation
        )

    return pd.Series(results)


def composite_reliability(loadings):

    values = np.asarray(
        loadings,
        dtype=float
    )

    values = values[
        ~np.isnan(values)
    ]

    if len(values) == 0:
        return np.nan

    error_variance = (
        1 -
        values ** 2
    )

    numerator = (
        values.sum()
    ) ** 2

    denominator = (
        numerator +
        error_variance.sum()
    )

    if denominator == 0:
        return np.nan

    return (
        numerator /
        denominator
    )


def calculate_ave(loadings):

    values = np.asarray(
        loadings,
        dtype=float
    )

    values = values[
        ~np.isnan(values)
    ]

    if len(values) == 0:
        return np.nan

    return np.mean(
        values ** 2
    )


# ============================================================
# FIRST-ORDER MEASUREMENT MODEL
# ============================================================

st.divider()

st.subheader(
    "1️⃣ First-Order Dimension Measurement"
)

st.write(
    "The indicators belonging to each dimension are evaluated "
    "according to the measurement type specified in the model."
)


dimension_results = []

all_loading_rows = []


# ============================================================
# PROCESS DIMENSIONS
# ============================================================

for dimension_name, information in dimensions.items():

    dimension_type = information.get(
        "type",
        "Reflective"
    )

    items = information.get(
        "items",
        []
    )

    valid_items = [
        item
        for item in items
        if item in df.columns
    ]

    if not valid_items:

        continue

    data = df[
        valid_items
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )


    # ========================================================
    # REFLECTIVE DIMENSION
    # ========================================================

    if dimension_type == "Reflective":

        loadings = calculate_loadings(
            data
        )

        alpha = cronbach_alpha(
            data
        )

        cr = composite_reliability(
            loadings.values
        )

        ave = calculate_ave(
            loadings.values
        )

        dimension_results.append(
            {
                "Dimension": dimension_name,
                "Type": "Reflective",
                "Indicators": len(valid_items),
                "Cronbach Alpha": alpha,
                "Composite Reliability": cr,
                "AVE": ave
            }
        )

        for item, loading in loadings.items():

            if loading >= 0.708:
                status = "Good"

            elif loading >= 0.40:
                status = "Review"

            else:
                status = "Weak"

            all_loading_rows.append(
                {
                    "Dimension": dimension_name,
                    "Indicator": item,
                    "Loading": loading,
                    "Status": status
                }
            )


    # ========================================================
    # FORMATIVE DIMENSION
    # ========================================================

    else:

        dimension_results.append(
            {
                "Dimension": dimension_name,
                "Type": "Formative",
                "Indicators": len(valid_items),
                "Cronbach Alpha": np.nan,
                "Composite Reliability": np.nan,
                "AVE": np.nan
            }
        )


# ============================================================
# DIMENSION RESULTS
# ============================================================

st.subheader(
    "📊 Dimension Reliability and Validity"
)

if dimension_results:

    results_df = pd.DataFrame(
        dimension_results
    )

    st.dataframe(
        results_df.style.format(
            {
                "Cronbach Alpha": "{:.3f}",
                "Composite Reliability": "{:.3f}",
                "AVE": "{:.3f}"
            },
            na_rep="—"
        ),
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "⚠️ No dimension results could be calculated."
    )


# ============================================================
# INDICATOR LOADINGS
# ============================================================

st.divider()

st.subheader(
    "📊 Reflective Indicator Loadings"
)

if all_loading_rows:

    loading_df = pd.DataFrame(
        all_loading_rows
    )

    st.dataframe(
        loading_df.style.format(
            {
                "Loading": "{:.3f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No reflective dimensions are available."
    )


# ============================================================
# DIMENSION SCORES
# ============================================================

st.divider()

st.subheader(
    "📈 Dimension Scores"
)

dimension_scores = {}

for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    valid_items = [
        item
        for item in items
        if item in df.columns
    ]

    if valid_items:

        data = df[
            valid_items
        ].apply(
            pd.to_numeric,
            errors="coerce"
        )

        dimension_scores[
            dimension_name
        ] = data.mean(
            axis=1
        )


if dimension_scores:

    score_df = pd.DataFrame(
        dimension_scores
    )

    st.dataframe(
        score_df.describe().T[
            [
                "count",
                "mean",
                "std",
                "min",
                "max"
            ]
        ].round(3),
        use_container_width=True
    )


# ============================================================
# DIMENSION CORRELATION
# ============================================================

if len(dimension_scores) >= 2:

    st.divider()

    st.subheader(
        "🔗 Dimension Correlations"
    )

    score_df = pd.DataFrame(
        dimension_scores
    )

    correlation_df = score_df.corr()

    st.dataframe(
        correlation_df.round(3),
        use_container_width=True
    )


# ============================================================
# HIGHER-ORDER CONSTRUCT
# ============================================================

st.divider()

st.subheader(
    "2️⃣ Higher-Order Construct"
)

st.markdown(
    "### " + str(hoc_name)
)

st.write(
    "**Measurement Type:** "
    + str(hoc_type)
)


if len(dimension_scores) < 2:

    st.warning(
        "⚠️ At least two dimensions are needed for "
        "higher-order construct assessment."
    )

else:

    score_df = pd.DataFrame(
        dimension_scores
    )

    # ========================================================
    # REFLECTIVE HOC
    # ========================================================

    if hoc_type == "Reflective":

        st.info(
            "The dimensions are treated as reflective "
            "indicators of the higher-order construct."
        )

        hoc_loadings = calculate_loadings(
            score_df
        )

        hoc_alpha = cronbach_alpha(
            score_df
        )

        hoc_cr = composite_reliability(
            hoc_loadings.values
        )

        hoc_ave = calculate_ave(
            hoc_loadings.values
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Cronbach Alpha",
                (
                    f"{hoc_alpha:.3f}"
                    if not pd.isna(hoc_alpha)
                    else "—"
                )
            )

        with col2:

            st.metric(
                "Composite Reliability",
                (
                    f"{hoc_cr:.3f}"
                    if not pd.isna(hoc_cr)
                    else "—"
                )
            )

        with col3:

            st.metric(
                "AVE",
                (
                    f"{hoc_ave:.3f}"
                    if not pd.isna(hoc_ave)
                    else "—"
                )
            )

        hoc_rows = []

        for dimension_name, loading in hoc_loadings.items():

            if loading >= 0.708:
                status = "Good"

            elif loading >= 0.40:
                status = "Review"

            else:
                status = "Weak"

            hoc_rows.append(
                {
                    "Dimension": dimension_name,
                    "HOC Loading": loading,
                    "Status": status
                }
            )

        hoc_df = pd.DataFrame(
            hoc_rows
        )

        st.dataframe(
            hoc_df.style.format(
                {
                    "HOC Loading": "{:.3f}"
                }
            ),
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # FORMATIVE HOC
    # ========================================================

    else:

        st.info(
            "The dimensions are treated as forming the "
            "higher-order construct."
        )

        st.warning(
            "For a formative higher-order construct, "
            "Cronbach's Alpha, Composite Reliability, and "
            "AVE are not used as the primary validity criteria."
        )

        st.write(
            "The formative HOC requires additional assessment "
            "such as collinearity and significance/relevance "
            "of formative relationships."
        )


# ============================================================
# RESEARCHER DECISION
# ============================================================

st.divider()

st.subheader(
    "📝 Researcher Decision"
)

st.write(
    "Statistical results should support the researcher's "
    "theoretical decision. The software will not automatically "
    "remove indicators."
)


decision_options = [
    "Pending Review",
    "Retain",
    "Consider Removal",
    "Remove",
    "Keep for Theoretical Reason"
]


decision_rows = []


for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    for item in items:

        decision = st.selectbox(
            f"{dimension_name} → {item}",
            decision_options,
            key=(
                "ho_decision_"
                + dimension_name
                + "_"
                + item
            )
        )

        decision_rows.append(
            {
                "Dimension": dimension_name,
                "Indicator": item,
                "Decision": decision
            }
        )


if st.button(
    "💾 Save Measurement Decisions",
    type="primary"
):

    st.session_state[
        "higher_order_measurement_decisions"
    ] = decision_rows

    st.success(
        "✅ Measurement decisions saved successfully."
    )


# ============================================================
# STATUS
# ============================================================

st.divider()

st.subheader(
    "🔎 Measurement Model Status"
)

st.success(
    "✅ Higher-Order Construct: "
    + str(hoc_name)
)

st.success(
    "✅ Higher-Order Type: "
    + str(hoc_type)
)

st.success(
    "✅ Dimensions evaluated: "
    + str(len(dimensions))
)


for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    dimension_type = information.get(
        "type",
        "Reflective"
    )

    if dimension_type == "Reflective":

        if len(items) >= 3:

            st.success(
                f"✅ {dimension_name}: "
                f"{len(items)} reflective indicators."
            )

        else:

            st.warning(
                f"⚠️ {dimension_name}: "
                f"{len(items)} reflective indicators. "
                "Review the specification."
            )

    else:

        if len(items) >= 2:

            st.success(
                f"✅ {dimension_name}: "
                f"{len(items)} formative indicators."
            )

        else:

            st.warning(
                f"⚠️ {dimension_name}: "
                f"{len(items)} formative indicator(s). "
                "Review the specification."
            )


# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.subheader(
    "📚 Methodological Note"
)

st.info(
    "This page provides research-support diagnostics for the "
    "higher-order measurement model. Reflective and formative "
    "measurement models require different assessment procedures."
)

st.warning(
    "⚠️ The loading calculations provided here are simplified "
    "PLS-style diagnostics. They should not be described as an "
    "exact reproduction of SmartPLS."
)

st.warning(
    "⚠️ Measurement decisions remain theory-driven. The "
    "software does not automatically delete indicators or "
    "declare a construct valid or invalid."
)
