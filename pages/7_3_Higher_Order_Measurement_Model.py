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
    "Evaluate the measurement model of a higher-order construct "
    "using the dimensions and indicators already defined in the "
    "Higher-Order Construct Setup."
)

# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:

    st.warning(
        "⚠️ Please upload your questionnaire dataset on the Home page first."
    )

    st.stop()

df = st.session_state["df"].copy()

# ============================================================
# CHECK HIGHER-ORDER MODEL
# ============================================================

if "pls_higher_order_model" not in st.session_state:

    st.warning(
        "⚠️ No Higher-Order Construct model was found."
    )

    st.info(
        "Please first configure and save your model on the "
        "Higher-Order Construct Setup page."
    )

    st.stop()

higher_order_model = st.session_state[
    "pls_higher_order_model"
]

hoc_name = higher_order_model.get(
    "name",
    "Higher-Order Construct"
)

hoc_type = higher_order_model.get(
    "type",
    "Reflective"
)

dimensions = higher_order_model.get(
    "dimensions",
    {}
)

if not dimensions:

    st.error(
        "❌ No dimensions were found in the saved Higher-Order model."
    )

    st.stop()

# ============================================================
# DATASET INFORMATION
# ============================================================

st.success(
    "✅ Dataset and Higher-Order Construct model loaded successfully."
)

st.divider()

st.subheader("📋 Analysis Information")

col1, col2, col3, col4 = st.columns(4)

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

with col4:
    st.metric(
        "HOC Type",
        hoc_type
    )

# ============================================================
# MODEL SUMMARY
# ============================================================

st.divider()

st.subheader("🏗️ Higher-Order Model")

st.markdown(
    f"### {hoc_name}"
)

st.write(
    f"**Higher-Order Measurement Type:** {hoc_type}"
)

model_rows = []

for dimension_name, information in dimensions.items():

    model_rows.append(
        {
            "Dimension":
                dimension_name,

            "Dimension Type":
                information.get(
                    "type",
                    "Reflective"
                ),

            "Number of Indicators":
                len(
                    information.get(
                        "items",
                        []
                    )
                ),

            "Indicators":
                ", ".join(
                    information.get(
                        "items",
                        []
                    )
                )
        }
    )

model_summary_df = pd.DataFrame(
    model_rows
)

st.dataframe(
    model_summary_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def cronbach_alpha(data):
    """
    Calculate Cronbach's Alpha.
    """

    data = data.dropna()

    if data.shape[1] < 2:
        return np.nan

    item_variances = data.var(
        axis=0,
        ddof=1
    )

    total_variance = data.sum(
        axis=1
    ).var(
        ddof=1
    )

    if total_variance == 0:
        return np.nan

    k = data.shape[1]

    alpha = (
        k / (k - 1)
    ) * (
        1 -
        item_variances.sum() /
        total_variance
    )

    return alpha


def standardized_loadings(data):
    """
    PLS-style iterative Mode A loading approximation.

    This is a research-support diagnostic and is not claimed
    to reproduce SmartPLS internal algorithms exactly.
    """

    data = data.copy()

    if data.shape[1] < 2:
        return pd.Series(
            np.ones(data.shape[1]),
            index=data.columns
        )

    # Standardize indicators
    z = (
        data - data.mean()
    ) / data.std(
        ddof=0
    )

    z = z.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if z.empty:
        return pd.Series(
            np.nan,
            index=data.columns
        )

    # Initial equal weights
    weights = np.ones(
        z.shape[1]
    ) / z.shape[1]

    for _ in range(100):

        score = np.dot(
            z.values,
            weights
        )

        new_weights = []

        for column_index in range(
            z.shape[1]
        ):

            correlation = np.corrcoef(
                z.iloc[:, column_index],
                score
            )[0, 1]

            if np.isnan(correlation):
                correlation = 0

            new_weights.append(
                correlation
            )

        new_weights = np.array(
            new_weights
        )

        norm = np.linalg.norm(
            new_weights
        )

        if norm != 0:
            new_weights = (
                new_weights / norm
            )

        if np.allclose(
            weights,
            new_weights,
            atol=0.0001
        ):
            weights = new_weights
            break

        weights = new_weights

    final_score = np.dot(
        z.values,
        weights
    )

    loadings = {}

    for column in z.columns:

        correlation = np.corrcoef(
            z[column],
            final_score
        )[0, 1]

        loadings[column] = abs(
            correlation
        )

    return pd.Series(
        loadings
    )


def composite_reliability(loadings):
    """
    Composite Reliability using standardized loadings.
    """

    loadings = np.asarray(
        loadings,
        dtype=float
    )

    loadings = loadings[
        ~np.isnan(loadings)
    ]

    if len(loadings) == 0:
        return np.nan

    error_variance = (
        1 -
        loadings ** 2
    )

    numerator = (
        loadings.sum()
    ) ** 2

    denominator = (
        numerator +
        error_variance.sum()
    )

    if denominator == 0:
        return np.nan

    return numerator / denominator


def ave_value(loadings):
    """
    Average Variance Extracted.
    """

    loadings = np.asarray(
        loadings,
        dtype=float
    )

    loadings = loadings[
        ~np.isnan(loadings)
    ]

    if len(loadings) == 0:
        return np.nan

    return np.mean(
        loadings ** 2
    )


def vif_values(data):
    """
    Calculate VIF for formative indicators.

    VIF is calculated by regressing each indicator
    on all remaining indicators.
    """

    from sklearn.linear_model import LinearRegression

    results = {}

    data = data.dropna()

    if data.shape[1] < 2:
        return {
            column: np.nan
            for column in data.columns
        }

    for column in data.columns:

        y = data[column].values

        other_columns = [
            c
            for c in data.columns
            if c != column
        ]

        if not other_columns:

            results[column] = np.nan
            continue

        X = data[
            other_columns
        ].values

        try:

            model = LinearRegression()

            model.fit(
                X,
                y
            )

            r_squared = model.score(
                X,
                y
            )

            if r_squared >= 0.999999:

                results[column] = np.inf

            else:

                results[column] = (
                    1 /
                    (1 - r_squared)
                )

        except Exception:

            results[column] = np.nan

    return results


# ============================================================
# FIRST-ORDER DIMENSION MEASUREMENT MODEL
# ============================================================

st.divider()

st.subheader(
    "1️⃣ First-Order Dimension Measurement Model"
)

st.write(
    "Each dimension is evaluated according to its specified "
    "measurement type."
)

dimension_results = []

dimension_scores = {}

dimension_loadings = {}

# ============================================================
# PROCESS EACH DIMENSION
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

    dimension_data = df[
        valid_items
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # DIMENSION SCORE
    # --------------------------------------------------------

    dimension_scores[
        dimension_name
    ] = dimension_data.mean(
        axis=1
    )

    # ========================================================
    # REFLECTIVE DIMENSION
    # ========================================================

    if dimension_type == "Reflective":

        loadings = standardized_loadings(
            dimension_data
        )

        dimension_loadings[
            dimension_name
        ] = loadings

        alpha = cronbach_alpha(
            dimension_data
        )

        cr = composite_reliability(
            loadings.values
        )

        ave = ave_value(
            loadings.values
        )

        dimension_results.append(
            {
                "Dimension":
                    dimension_name,

                "Type":
                    "Reflective",

                "Indicators":
                    len(valid_items),

                "Cronbach Alpha":
                    alpha,

                "Composite Reliability":
                    cr,

                "AVE":
                    ave
            }
        )

    # ========================================================
    # FORMATIVE DIMENSION
    # ========================================================

    else:

        vifs = vif_values(
            dimension_data
        )

        dimension_loadings[
            dimension_name
        ] = pd.Series(
            dtype=float
        )

        for item, vif in vifs.items():

            dimension_results.append(
                {
                    "Dimension":
                        dimension_name,

                    "Type":
                        "Formative",

                    "Indicators":
                        len(valid_items),

                    "Cronbach Alpha":
                        np.nan,

                    "Composite Reliability":
                        np.nan,

                    "AVE":
                        np.nan
                }
            )

            break

# ============================================================
# DISPLAY DIMENSION RESULTS
# ============================================================

if dimension_results:

    dimension_results_df = pd.DataFrame(
        dimension_results
    )

    st.dataframe(
        dimension_results_df.style.format(
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

# ============================================================
# REFLECTIVE INDICATOR LOADINGS
# ============================================================

st.divider()

st.subheader(
    "📊 Reflective Indicator Loadings"
)

reflective_loading_rows = []

for dimension_name, information in dimensions.items():

    if information.get(
        "type",
        "Reflective"
    ) != "Reflective":

        continue

    loadings = dimension_loadings.get(
        dimension_name
    )

    if loadings is None:
        continue

    for item, loading in loadings.items():

        if loading >= 0.708:

            status = "Good"

        elif loading >= 0.40:

            status = "Review"

        else:

            status = "Weak"

        reflective_loading_rows.append(
            {
                "Dimension":
                    dimension_name,

                "Indicator":
                    item,

                "Loading":
                    loading,

                "Status":
                    status
            }
        )

if reflective_loading_rows:

    loadings_df = pd.DataFrame(
        reflective_loading_rows
    )

    st.dataframe(
        loadings_df.style.format(
            {
                "Loading": "{:.3f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Loading values are research-support diagnostics based on "
        "a PLS-style Mode A approximation; they are not claimed "
        "to exactly reproduce SmartPLS loadings."
    )

else:

    st.info(
        "No reflective indicator loadings are available."
    )

# ============================================================
# FORMATIVE INDICATOR VIF
# ============================================================

st.divider()

st.subheader(
    "📐 Formative Indicator Collinearity"

formative_dimensions = [
    (
        name,
        info
    )
    for name, info in dimensions.items()
    if info.get(
        "type",
        "Reflective"
    ) == "Formative"
]

if formative_dimensions:

    formative_vif_rows = []

    for dimension_name, information in formative_dimensions:

        items = [
            item
            for item in information.get(
                "items",
                []
            )
            if item in df.columns
        ]

        if len(items) < 2:

            continue

        data = df[
            items
        ].apply(
            pd.to_numeric,
            errors="coerce"
        )

        vifs = vif_values(
            data
        )

        for item, vif in vifs.items():

            if pd.isna(vif):

                status = "Not available"

            elif vif < 3.3:

                status = "Good"

            elif vif < 5:

                status = "Review"

            else:

                status = "High"

            formative_vif_rows.append(
                {
                    "Dimension":
                        dimension_name,

                    "Indicator":
                        item,

                    "VIF":
                        vif,

                    "Status":
                        status
                }
            )

    if formative_vif_rows:

        formative_vif_df = pd.DataFrame(
            formative_vif_rows
        )

        st.dataframe(
            formative_vif_df.style.format(
                {
                    "VIF": "{:.3f}"
                },
                na_rep="—"
            ),
            use_container_width=True,
            hide_index=True
        )

else:

    st.info(
        "No formative dimensions are defined in the current model."
    )

# ============================================================
# DIMENSION SCORES
# ============================================================

st.divider()

st.subheader(
    "📊 Dimension Scores"
)

if dimension_scores:

    dimension_score_df = pd.DataFrame(
        dimension_scores
    )

    st.dataframe(
        dimension_score_df.describe().T[
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

    dimension_score_df = pd.DataFrame(
        dimension_scores
    )

    correlation_df = dimension_score_df.corr()

    st.dataframe(
        correlation_df.round(3),
        use_container_width=True
    )

# ============================================================
# HIGHER-ORDER CONSTRUCT ASSESSMENT
# ============================================================

st.divider()

st.subheader(
    "2️⃣ Higher-Order Construct Assessment"
)

st.markdown(
    f"### {hoc_name}"
)

st.write(
    f"**Measurement Type:** {hoc_type}"
)

if len(dimension_scores) < 2:

    st.warning(
        "⚠️ At least two dimensions are required for a meaningful "
        "higher-order construct assessment."
    )

else:

    dimension_score_df = pd.DataFrame(
        dimension_scores
    )

    # ========================================================
    # REFLECTIVE HOC
    # ========================================================

    if hoc_type == "Reflective":

        st.markdown(
            "#### Reflective Higher-Order Construct"
        )

        st.write(
            "The dimensions are treated as manifestations of "
            "the higher-order construct."
        )

        hoc_loadings = standardized_loadings(
            dimension_score_df
        )

        hoc_alpha = cronbach_alpha(
            dimension_score_df
        )

        hoc_cr = composite_reliability(
            hoc_loadings.values
        )

        hoc_ave = ave_value(
            hoc_loadings.values
        )

        hoc_col1, hoc_col2, hoc_col3 = st.columns(3)

        with hoc_col1:

            st.metric(
                "Cronbach Alpha",
                (
                    f"{hoc_alpha:.3f}"
                    if not pd.isna(hoc_alpha)
                    else "—"
                )
            )

        with hoc_col2:

            st.metric(
                "Composite Reliability",
                (
                    f"{hoc_cr:.3f}"
                    if not pd.isna(hoc_cr)
                    else "—"
                )
            )

        with hoc_col3:

            st.metric(
                "AVE",
                (
                    f"{hoc_ave:.3f}"
                    if not pd.isna(hoc_ave)
                    else "—"
                )
            )

        hoc_loading_rows = []

        for dimension_name, loading in (
            hoc_loadings.items()
        ):

            if loading >= 0.708:

                status = "Good"

            elif loading >= 0.40:

                status = "Review"

            else:

                status = "Weak"

            hoc_loading_rows.append(
                {
                    "Dimension":
                        dimension_name,

                    "HOC Loading":
                        loading,

                    "Status":
                        status
                }
            )

        hoc_loading_df = pd.DataFrame(
            hoc_loading_rows
        )

        st.dataframe(
            hoc_loading_df.style.format(
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

        st.markdown(
            "#### Formative Higher-Order Construct"
        )

        st.write(
            "The dimensions are treated as forming the "
            "higher-order construct."
        )

        dimension_vif = vif_values(
            dimension_score_df
        )

        hoc_vif_rows = []

        for dimension_name, vif in (
            dimension_vif.items()
        ):

            if pd.isna(vif):

                status = "Not available"

            elif vif < 3.3:

                status = "Good"

            elif vif < 5:

                status = "Review"

            else:

                status = "High"

            hoc_vif_rows.append(
                {
                    "Dimension":
                        dimension_name,

                    "Dimension VIF":
                        vif,

                    "Status":
                        status
                }
            )

        hoc_vif_df = pd.DataFrame(
            hoc_vif_rows
        )

        st.dataframe(
            hoc_vif_df.style.format(
                {
                    "Dimension VIF": "{:.3f}"
                },
                na_rep="—"
            ),
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "For a formative higher-order construct, reliability "
            "statistics such as Cronbach's Alpha, Composite "
            "Reliability, and AVE are not automatically used as "
            "the primary assessment of the formative HOC."
        )

# ============================================================
# RESEARCHER DECISIONS
# ============================================================

st.divider()

st.subheader(
    "📝 Researcher Measurement Decisions"
)

st.write(
    "Statistical diagnostics should support, not replace, "
    "the researcher's theoretical decision."
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

        decision_key = (
            f"higher_order_decision_"
            f"{dimension_name}_"
            f"{item}"
        )

        decision = st.selectbox(
            f"{dimension_name} → {item}",
            decision_options,
            key=decision_key
        )

        decision_rows.append(
            {
                "Dimension":
                    dimension_name,

                "Indicator":
                    item,

                "Researcher Decision":
                    decision
            }
        )

if decision_rows:

    decision_df = pd.DataFrame(
        decision_rows
    )

    if st.button(
        "💾 Save Researcher Decisions",
        type="primary"
    ):

        st.session_state[
            "higher_order_measurement_decisions"
        ] = decision_rows

        st.success(
            "✅ Researcher measurement decisions saved."
        )

# ============================================================
# OVERALL STATUS
# ============================================================

st.divider()

st.subheader(
    "🔎 Measurement Model Status"
)

st.success(
    f"✅ Higher-Order Construct: {hoc_name}"
)

st.success(
    f"✅ Higher-Order Type: {hoc_type}"
)

st.success(
    f"✅ Dimensions evaluated: {len(dimensions)}"
)

for dimension_name, information in dimensions.items():

    item_count = len(
        information.get(
            "items",
            []
        )
    )

    dimension_type = information.get(
        "type",
        "Reflective"
    )

    if dimension_type == "Reflective":

        if item_count >= 3:

            st.success(
                f"✅ {dimension_name}: "
                f"{item_count} reflective indicators."
            )

        else:

            st.warning(
                f"⚠️ {dimension_name}: "
                f"{item_count} reflective indicators. "
                "Review the measurement specification."
            )

    else:

        if item_count >= 2:

            st.success(
                f"✅ {dimension_name}: "
                f"{item_count} formative indicators."
            )

        else:

            st.warning(
                f"⚠️ {dimension_name}: "
                f"{item_count} formative indicator(s). "
                "Review the specification."
            )

# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.subheader(
    "📚 Methodological Notes"
)

st.info(
    "This page provides research-support diagnostics for a "
    "higher-order PLS-SEM measurement model. Reflective and "
    "formative constructs are evaluated differently."
)

st.warning(
    "⚠️ The loading calculations on this page are PLS-style "
    "approximations for research support and should not be "
    "described as an exact reproduction of SmartPLS's proprietary "
    "PLS algorithm."
)

st.warning(
    "⚠️ Measurement-model decisions remain theory-driven. "
    "The software does not automatically delete indicators or "
    "declare a construct valid or invalid."
)
