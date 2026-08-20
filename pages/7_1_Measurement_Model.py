import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Measurement Model",
    page_icon="📐",
    layout="wide"
)

st.title("📐 Measurement Model Assessment")

st.write(
    "Assess indicator reliability, internal consistency, "
    "and convergent validity for the defined constructs."
)

# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:
    st.warning(
        "⚠️ Please upload a questionnaire dataset on the Home page first."
    )
    st.stop()

df = st.session_state["df"].copy()

# ============================================================
# CHECK CONSTRUCT SETUP
# ============================================================

if "pls_constructs" not in st.session_state:
    st.warning(
        "⚠️ Please define and save your constructs first "
        "on the PLS-SEM Analysis page."
    )
    st.stop()

constructs = st.session_state["pls_constructs"]

if not constructs:
    st.warning(
        "⚠️ No measurement constructs have been saved yet."
    )
    st.stop()

st.success(
    "✅ Dataset and measurement model loaded."
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def cronbach_alpha(data):

    data = data.dropna()

    if data.shape[1] < 2:
        return np.nan

    item_variances = data.var(
        axis=0,
        ddof=1
    )

    total_variance = data.sum(
        axis=1
    ).var(ddof=1)

    if total_variance == 0:
        return np.nan

    k = data.shape[1]

    alpha = (
        k / (k - 1)
    ) * (
        1 -
        item_variances.sum()
        / total_variance
    )

    return alpha


def standardized_loadings(data):

    """
    Approximate standardized indicator loadings
    using the first principal component.

    This is a measurement-model diagnostic and
    should not be interpreted as a complete
    SmartPLS PLS algorithm result.
    """

    data = data.dropna()

    if data.shape[1] < 2:
        return pd.Series(
            [np.nan] * data.shape[1],
            index=data.columns
        )

    # Standardize indicators
    standardized = (
        data - data.mean()
    ) / data.std(ddof=0)

    # Correlation matrix
    correlation_matrix = (
        standardized.corr()
    )

    # Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(
        correlation_matrix
    )

    # First principal component
    first_vector = eigenvectors[:, -1]

    # Make direction positive where possible
    if first_vector.sum() < 0:
        first_vector = -first_vector

    loadings = (
        first_vector
        * np.sqrt(
            eigenvalues[-1]
        )
    )

    loadings = np.abs(
        loadings
    )

    return pd.Series(
        loadings,
        index=data.columns
    )


def composite_reliability(loadings):

    loadings = np.array(
        loadings,
        dtype=float
    )

    loadings = loadings[
        ~np.isnan(loadings)
    ]

    if len(loadings) < 2:
        return np.nan

    error_variances = (
        1 - loadings ** 2
    )

    denominator = (
        np.sum(loadings) ** 2
        + np.sum(error_variances)
    )

    if denominator == 0:
        return np.nan

    return (
        np.sum(loadings) ** 2
        / denominator
    )


def ave_value(loadings):

    loadings = np.array(
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


def result_status(
    value,
    good_threshold,
    review_threshold
):

    if pd.isna(value):
        return "⚪ Not available"

    if value >= good_threshold:
        return "🟢 Good"

    if value >= review_threshold:
        return "🟡 Review"

    return "🔴 Weak"


# ============================================================
# MEASUREMENT MODEL RESULTS
# ============================================================

st.subheader(
    "📊 Measurement Model Results"
)

st.info(
    "The results below are diagnostic calculations based on "
    "your selected indicators. Review the flagged results "
    "before making any item-removal decision."
)

all_construct_results = []
all_loading_results = []

# ============================================================
# PROCESS EACH CONSTRUCT
# ============================================================

for construct_name, information in constructs.items():

    items = information["items"]

    measurement_type = information["type"]

    st.divider()

    st.markdown(
        f"## {construct_name}"
    )

    st.caption(
        f"Measurement type: {measurement_type}"
    )

    if len(items) < 2:

        st.warning(
            "⚠️ At least two indicators are required "
            "for these reliability calculations."
        )

        continue

    # Make sure columns exist
    available_items = [
        item
        for item in items
        if item in df.columns
    ]

    missing_items = [
        item
        for item in items
        if item not in df.columns
    ]

    if missing_items:

        st.error(
            "❌ The following selected indicators "
            "are not present in the dataset:"
        )

        st.write(
            missing_items
        )

        continue

    construct_data = df[
        available_items
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # LOADINGS
    # --------------------------------------------------------

    loadings = standardized_loadings(
        construct_data
    )

    loading_table = []

    for item in available_items:

        loading = loadings.get(
            item,
            np.nan
        )

        if pd.isna(loading):

            status = "⚪ Not available"

        elif loading >= 0.708:

            status = "🟢 Good"

        elif loading >= 0.40:

            status = "🟡 Review"

        else:

            status = "🔴 Weak"

        loading_table.append(
            {
                "Indicator": item,
                "Outer Loading": (
                    round(
                        loading,
                        3
                    )
                    if not pd.isna(loading)
                    else np.nan
                ),
                "Status": status
            }
        )

        all_loading_results.append(
            {
                "Construct": construct_name,
                "Indicator": item,
                "Outer Loading": loading,
                "Status": status
            }
        )

    loading_df = pd.DataFrame(
        loading_table
    )

    st.markdown(
        "### 🔗 Indicator Reliability"
    )

    st.dataframe(
        loading_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # RELIABILITY
    # --------------------------------------------------------

    alpha = cronbach_alpha(
        construct_data
    )

    cr = composite_reliability(
        loadings.values
    )

    ave = ave_value(
        loadings.values
    )

    # rho_A diagnostic approximation
    # based on the relationship between alpha and CR
    if not pd.isna(alpha) and not pd.isna(cr):

        rho_a = (
            alpha + cr
        ) / 2

    else:

        rho_a = np.nan

    construct_result = {

        "Construct":
            construct_name,

        "Cronbach's Alpha":
            alpha,

        "rho_A":
            rho_a,

        "Composite Reliability":
            cr,

        "AVE":
            ave,

        "Alpha Status":
            result_status(
                alpha,
                0.70,
                0.60
            ),

        "CR Status":
            result_status(
                cr,
                0.70,
                0.60
            ),

        "AVE Status":
            result_status(
                ave,
                0.50,
                0.40
            )
    }

    all_construct_results.append(
        construct_result
    )

    # --------------------------------------------------------
    # CONSTRUCT METRICS
    # --------------------------------------------------------

    st.markdown(
        "### 📐 Construct Reliability and Validity"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Cronbach's Alpha",
            (
                f"{alpha:.3f}"
                if not pd.isna(alpha)
                else "N/A"
            )
        )

        if not pd.isna(alpha):

            if alpha >= 0.70:
                st.success("🟢 Good")
            elif alpha >= 0.60:
                st.warning("🟡 Review")
            else:
                st.error("🔴 Weak")

    with c2:

        st.metric(
            "rho_A",
            (
                f"{rho_a:.3f}"
                if not pd.isna(rho_a)
                else "N/A"
            )
        )

    with c3:

        st.metric(
            "Composite Reliability",
            (
                f"{cr:.3f}"
                if not pd.isna(cr)
                else "N/A"
            )
        )

        if not pd.isna(cr):

            if cr >= 0.70:
                st.success("🟢 Good")
            elif cr >= 0.60:
                st.warning("🟡 Review")
            else:
                st.error("🔴 Weak")

    with c4:

        st.metric(
            "AVE",
            (
                f"{ave:.3f}"
                if not pd.isna(ave)
                else "N/A"
            )
        )

        if not pd.isna(ave):

            if ave >= 0.50:
                st.success("🟢 Good")
            elif ave >= 0.40:
                st.warning("🟡 Review")
            else:
                st.error("🔴 Weak")


# ============================================================
# OVERALL CONSTRUCT SUMMARY
# ============================================================

if all_construct_results:

    st.divider()

    st.subheader(
        "📋 Construct-Level Summary"
    )

    summary_df = pd.DataFrame(
        all_construct_results
    )

    display_summary = summary_df[
        [
            "Construct",
            "Cronbach's Alpha",
            "rho_A",
            "Composite Reliability",
            "AVE",
            "Alpha Status",
            "CR Status",
            "AVE Status"
        ]
    ].copy()

    for column in [
        "Cronbach's Alpha",
        "rho_A",
        "Composite Reliability",
        "AVE"
    ]:

        display_summary[column] = (
            display_summary[column]
            .round(3)
        )

    st.dataframe(
        display_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# WEAK INDICATORS
# ============================================================

if all_loading_results:

    loading_results_df = pd.DataFrame(
        all_loading_results
    )

    weak_indicators = loading_results_df[
        loading_results_df[
            "Outer Loading"
        ] < 0.40
    ]

    review_indicators = loading_results_df[
        (
            loading_results_df[
                "Outer Loading"
            ] >= 0.40
        )
        &
        (
            loading_results_df[
                "Outer Loading"
            ] < 0.708
        )
    ]

    st.divider()

    st.subheader(
        "🚦 Indicators Requiring Researcher Review"
    )

    if weak_indicators.empty:

        st.success(
            "✅ No indicators with outer loading below 0.40 were detected."
        )

    else:

        st.error(
            f"🔴 {len(weak_indicators)} indicator(s) "
            "have outer loading below 0.40."
        )

        st.dataframe(
            weak_indicators[
                [
                    "Construct",
                    "Indicator",
                    "Outer Loading"
                ]
            ].round(3),
            use_container_width=True,
            hide_index=True
        )

    if review_indicators.empty:

        st.success(
            "✅ No borderline indicators were detected."
        )

    else:

        st.warning(
            f"🟡 {len(review_indicators)} indicator(s) "
            "fall between 0.40 and 0.708 and should be reviewed."
        )

        st.dataframe(
            review_indicators[
                [
                    "Construct",
                    "Indicator",
                    "Outer Loading"
                ]
            ].round(3),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# RESEARCHER DECISION
# ============================================================

if all_loading_results:

    st.divider()

    st.subheader(
        "👨‍🏫 Researcher Decision for Indicators"
    )

    st.write(
        "The software does not automatically delete indicators. "
        "The researcher makes the final methodological decision."
    )

    decision_options = [
        "Retain",
        "Consider Removal",
        "Remove",
        "Keep for Theoretical Reason",
        "Pending Review"
    ]

    decision_records = []

    for index, result in enumerate(
        all_loading_results
    ):

        loading = result[
            "Outer Loading"
        ]

        # Only ask for decisions on indicators
        # requiring review
        if pd.isna(loading):
            needs_review = True

        else:
            needs_review = loading < 0.708

        if needs_review:

            col1, col2, col3 = st.columns(
                [2, 2, 3]
            )

            with col1:

                st.write(
                    f"**{result['Construct']}**"
                )

                st.write(
                    f"Indicator: **{result['Indicator']}**"
                )

            with col2:

                st.write(
                    "Outer Loading"
                )

                st.write(
                    (
                        f"{loading:.3f}"
                        if not pd.isna(loading)
                        else "N/A"
                    )
                )

            with col3:

                decision = st.selectbox(
                    "Researcher Decision",
                    decision_options,
                    key=f"measurement_decision_{index}"
                )

            decision_records.append(
                {
                    "Construct":
                        result["Construct"],

                    "Indicator":
                        result["Indicator"],

                    "Outer Loading":
                        loading,

                    "Researcher Decision":
                        decision
                }
            )

    if decision_records:

        if st.button(
            "💾 Save Researcher Decisions",
            type="primary"
        ):

            st.session_state[
                "measurement_model_decisions"
            ] = decision_records

            st.success(
                "✅ Researcher decisions saved."
            )


# ============================================================
# SAVED DECISIONS
# ============================================================

if "measurement_model_decisions" in st.session_state:

    st.divider()

    st.subheader(
        "📌 Saved Researcher Decisions"
    )

    decisions_df = pd.DataFrame(
        st.session_state[
            "measurement_model_decisions"
        ]
    )

    decisions_df[
        "Outer Loading"
    ] = decisions_df[
        "Outer Loading"
    ].round(3)

    st.dataframe(
        decisions_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.info(
    "ℹ️ Thresholds shown here are screening/diagnostic "
    "guidelines. Indicator removal should not be based on "
    "a loading value alone. The researcher should also "
    "consider theoretical relevance, construct validity, "
    "reliability, and the overall measurement model."
)
