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
    "Assess the measurement quality of reflective and formative "
    "constructs using the indicators defined in the PLS-SEM model."
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

st.success("✅ Dataset and measurement model loaded.")

# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("📋 Dataset Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Respondents", df.shape[0])

with col2:
    st.metric("Variables", df.shape[1])

with col3:
    st.metric(
        "Constructs",
        len(constructs)
    )

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_numeric_data(data):
    return data.apply(
        pd.to_numeric,
        errors="coerce"
    )


def cronbach_alpha(data):
    """
    Calculate Cronbach's Alpha.
    """

    data = data.dropna()

    if data.shape[1] < 2:
        return np.nan

    if data.shape[0] < 2:
        return np.nan

    item_variances = data.var(
        axis=0,
        ddof=1
    )

    total_scores = data.sum(axis=1)

    total_variance = total_scores.var(
        ddof=1
    )

    if pd.isna(total_variance) or total_variance == 0:
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


def pls_style_loadings(data, max_iterations=300, tolerance=1e-7):
    """
    PLS-style Mode A iterative loading diagnostic.

    This provides a PLS-style measurement diagnostic.
    It should not be interpreted as an exact SmartPLS
    algorithm reproduction.
    """

    data = clean_numeric_data(data)

    data = data.dropna()

    if data.shape[0] < 3:
        return pd.Series(
            [np.nan] * data.shape[1],
            index=data.columns
        )

    if data.shape[1] < 2:
        return pd.Series(
            [np.nan] * data.shape[1],
            index=data.columns
        )

    # Remove zero-variance indicators
    valid_columns = []

    for column in data.columns:
        if data[column].std(ddof=1) > 0:
            valid_columns.append(column)

    if len(valid_columns) < 2:
        return pd.Series(
            [np.nan] * data.shape[1],
            index=data.columns
        )

    data = data[valid_columns]

    # Standardize indicators
    X = (
        data - data.mean()
    ) / data.std(ddof=1)

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if X.shape[0] < 3:
        return pd.Series(
            [np.nan] * len(valid_columns),
            index=valid_columns
        )

    # Initial equal weights
    weights = np.ones(
        X.shape[1]
    )

    weights = weights / np.linalg.norm(weights)

    for _ in range(max_iterations):

        construct_score = X.values @ weights

        score_std = np.std(
            construct_score,
            ddof=1
        )

        if score_std == 0:
            break

        construct_score = (
            construct_score -
            np.mean(construct_score)
        ) / score_std

        new_weights = []

        for column in X.columns:

            correlation = np.corrcoef(
                X[column].values,
                construct_score
            )[0, 1]

            if pd.isna(correlation):
                correlation = 0

            new_weights.append(
                correlation
            )

        new_weights = np.array(
            new_weights,
            dtype=float
        )

        norm = np.linalg.norm(
            new_weights
        )

        if norm == 0:
            break

        new_weights = (
            new_weights / norm
        )

        difference = np.max(
            np.abs(
                new_weights - weights
            )
        )

        weights = new_weights

        if difference < tolerance:
            break

    # Final construct score
    construct_score = X.values @ weights

    score_std = np.std(
        construct_score,
        ddof=1
    )

    if score_std == 0:
        return pd.Series(
            [np.nan] * len(valid_columns),
            index=valid_columns
        )

    construct_score = (
        construct_score -
        np.mean(construct_score)
    ) / score_std

    loadings = {}

    for column in X.columns:

        correlation = np.corrcoef(
            X[column].values,
            construct_score
        )[0, 1]

        loadings[column] = abs(
            correlation
        )

    return pd.Series(
        loadings
    )


def composite_reliability(loadings):
    """
    Composite Reliability based on standardized loadings.
    """

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
        +
        np.sum(error_variances)
    )

    if denominator <= 0:
        return np.nan

    return (
        np.sum(loadings) ** 2
        /
        denominator
    )


def ave_value(loadings):
    """
    Average Variance Extracted.
    """

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


def loading_status(value):

    if pd.isna(value):
        return "⚪ Not available"

    if value >= 0.708:
        return "🟢 Good"

    if value >= 0.40:
        return "🟡 Review"

    return "🔴 Weak"


def reliability_status(value):

    if pd.isna(value):
        return "⚪ Not available"

    if value >= 0.70:
        return "🟢 Good"

    if value >= 0.60:
        return "🟡 Review"

    return "🔴 Weak"


def ave_status(value):

    if pd.isna(value):
        return "⚪ Not available"

    if value >= 0.50:
        return "🟢 Good"

    if value >= 0.40:
        return "🟡 Review"

    return "🔴 Weak"


def calculate_vif(data):
    """
    Calculate indicator VIF using ordinary least squares
    without requiring an additional package.
    """

    data = clean_numeric_data(data)

    results = []

    for column in data.columns:

        others = [
            c for c in data.columns
            if c != column
        ]

        temp = data[
            [column] + others
        ].dropna()

        if len(others) == 0:
            vif = np.nan

        elif temp.shape[0] <= len(others) + 1:
            vif = np.nan

        else:

            y = temp[column].values.astype(float)

            X = temp[others].values.astype(float)

            X = np.column_stack(
                [
                    np.ones(
                        len(X)
                    ),
                    X
                ]
            )

            try:

                coefficients = np.linalg.lstsq(
                    X,
                    y,
                    rcond=None
                )[0]

                predictions = X @ coefficients

                ss_residual = np.sum(
                    (y - predictions) ** 2
                )

                ss_total = np.sum(
                    (y - np.mean(y)) ** 2
                )

                if ss_total == 0:
                    vif = np.nan

                else:

                    r_squared = (
                        1 -
                        ss_residual /
                        ss_total
                    )

                    if r_squared >= 0.999999:
                        vif = np.inf

                    else:
                        vif = (
                            1 /
                            (1 - r_squared)
                        )

            except Exception:
                vif = np.nan

        results.append(
            {
                "Indicator": column,
                "VIF": vif
            }
        )

    return pd.DataFrame(results)


def interpret_vif(vif):

    if pd.isna(vif):
        return "⚪ Not available"

    if vif < 3:
        return "🟢 Good"

    if vif < 5:
        return "🟡 Review"

    return "🔴 High"


def construct_score(data):
    """
    Create a simple standardized mean score for
    construct-level diagnostic calculations.
    """

    data = clean_numeric_data(data)

    standardized = (
        data - data.mean()
    ) / data.std(ddof=1)

    return standardized.mean(
        axis=1
    )


def calculate_htmt(construct_data_1, construct_data_2):
    """
    HTMT diagnostic between two constructs.
    """

    data_1 = clean_numeric_data(
        construct_data_1
    )

    data_2 = clean_numeric_data(
        construct_data_2
    )

    combined = pd.concat(
        [
            data_1,
            data_2
        ],
        axis=1
    ).dropna()

    if combined.shape[0] < 3:
        return np.nan

    items_1 = list(
        data_1.columns
    )

    items_2 = list(
        data_2.columns
    )

    heterotrait_correlations = []

    for item_1 in items_1:

        for item_2 in items_2:

            correlation = combined[
                [item_1, item_2]
            ].corr().iloc[0, 1]

            if not pd.isna(correlation):
                heterotrait_correlations.append(
                    abs(correlation)
                )

    if not heterotrait_correlations:
        return np.nan

    monotrait_1 = []
    monotrait_2 = []

    for i in range(len(items_1)):

        for j in range(
            i + 1,
            len(items_1)
        ):

            correlation = combined[
                [items_1[i], items_1[j]]
            ].corr().iloc[0, 1]

            if not pd.isna(correlation):
                monotrait_1.append(
                    abs(correlation)
                )

    for i in range(len(items_2)):

        for j in range(
            i + 1,
            len(items_2)
        ):

            correlation = combined[
                [items_2[i], items_2[j]]
            ].corr().iloc[0, 1]

            if not pd.isna(correlation):
                monotrait_2.append(
                    abs(correlation)
                )

    if not monotrait_1 or not monotrait_2:
        return np.nan

    denominator = np.sqrt(
        np.mean(monotrait_1)
        *
        np.mean(monotrait_2)
    )

    if denominator == 0:
        return np.nan

    return (
        np.mean(
            heterotrait_correlations
        )
        /
        denominator
    )


# ============================================================
# RESULTS STORAGE
# ============================================================

all_construct_results = []
all_loading_results = []

reflective_construct_scores = {}
reflective_ave = {}

formative_vif_results = []

# ============================================================
# MAIN RESULTS
# ============================================================

st.subheader(
    "📊 Measurement Model Results"
)

st.info(
    "The results are provided as researcher-support diagnostics. "
    "They should be interpreted together with theory, questionnaire "
    "design, data quality, and the overall PLS-SEM model."
)

# ============================================================
# PROCESS CONSTRUCTS
# ============================================================

for construct_name, information in constructs.items():

    items = information["items"]

    measurement_type = information["type"]

    st.divider()

    st.markdown(
        f"## {construct_name}"
    )

    st.caption(
        f"Measurement Type: {measurement_type}"
    )

    # --------------------------------------------------------
    # CHECK INDICATORS
    # --------------------------------------------------------

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

    if len(available_items) < 2:

        st.warning(
            "⚠️ At least two indicators are required "
            "for the current measurement-model diagnostics."
        )

        continue

    construct_data = clean_numeric_data(
        df[available_items]
    )

    # ========================================================
    # REFLECTIVE CONSTRUCT
    # ========================================================

    if measurement_type == "Reflective":

        st.markdown(
            "### 🔗 Indicator Reliability"
        )

        loadings = pls_style_loadings(
            construct_data
        )

        loading_rows = []

        for item in available_items:

            loading = loadings.get(
                item,
                np.nan
            )

            status = loading_status(
                loading
            )

            loading_rows.append(
                {
                    "Construct":
                        construct_name,

                    "Indicator":
                        item,

                    "Outer Loading":
                        (
                            round(
                                loading,
                                3
                            )
                            if not pd.isna(
                                loading
                            )
                            else np.nan
                        ),

                    "Status":
                        status
                }
            )

            all_loading_results.append(
                {
                    "Construct":
                        construct_name,

                    "Indicator":
                        item,

                    "Outer Loading":
                        loading,

                    "Status":
                        status,

                    "Measurement Type":
                        measurement_type
                }
            )

        loading_df = pd.DataFrame(
            loading_rows
        )

        st.dataframe(
            loading_df,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # RELIABILITY
        # ----------------------------------------------------

        alpha = cronbach_alpha(
            construct_data
        )

        cr = composite_reliability(
            loadings.values
        )

        ave = ave_value(
            loadings.values
        )

        # ----------------------------------------------------
        # CONSTRUCT SCORES
        # ----------------------------------------------------

        score = construct_score(
            construct_data
        )

        reflective_construct_scores[
            construct_name
        ] = score

        reflective_ave[
            construct_name
        ] = ave

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        st.markdown(
            "### 📐 Reliability and Convergent Validity"
        )

        c1, c2, c3 = st.columns(3)

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

        with c3:

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

        # ----------------------------------------------------
        # CONSTRUCT RESULT
        # ----------------------------------------------------

        all_construct_results.append(
            {
                "Construct":
                    construct_name,

                "Measurement Type":
                    measurement_type,

                "Cronbach's Alpha":
                    alpha,

                "Composite Reliability":
                    cr,

                "AVE":
                    ave,

                "Alpha Status":
                    reliability_status(alpha),

                "CR Status":
                    reliability_status(cr),

                "AVE Status":
                    ave_status(ave)
            }
        )

    # ========================================================
    # FORMATIVE CONSTRUCT
    # ========================================================

    else:

        st.markdown(
            "### 🧩 Formative Indicator Assessment"
        )

        st.info(
            "For formative constructs, internal consistency "
            "measures such as Cronbach's Alpha and AVE are not "
            "used as the primary assessment. Indicator "
            "collinearity is examined here. Indicator weights "
            "and their significance will be assessed later "
            "when the structural model and bootstrapping "
            "module are implemented."
        )

        vif_df = calculate_vif(
            construct_data
        )

        if not vif_df.empty:

            vif_df[
                "VIF"
            ] = vif_df[
                "VIF"
            ].replace(
                [np.inf, -np.inf],
                np.nan
            )

            vif_df[
                "Status"
            ] = vif_df[
                "VIF"
            ].apply(
                interpret_vif
            )

            vif_display = vif_df.copy()

            vif_display[
                "VIF"
            ] = vif_display[
                "VIF"
            ].round(3)

            st.dataframe(
                vif_display,
                use_container_width=True,
                hide_index=True
            )

            for _, row in vif_df.iterrows():

                formative_vif_results.append(
                    {
                        "Construct":
                            construct_name,

                        "Indicator":
                            row["Indicator"],

                        "VIF":
                            row["VIF"],

                        "Status":
                            row["Status"]
                    }
                )

        st.warning(
            "⚠️ Indicator weights and significance are not "
            "automatically interpreted at this stage. "
            "They will be evaluated through the structural "
            "model and bootstrapping procedures."
        )

# ============================================================
# CONSTRUCT SUMMARY
# ============================================================

if all_construct_results:

    st.divider()

    st.subheader(
        "📋 Reflective Construct Summary"
    )

    summary_df = pd.DataFrame(
        all_construct_results
    )

    numeric_summary_columns = [
        "Cronbach's Alpha",
        "Composite Reliability",
        "AVE"
    ]

    for column in numeric_summary_columns:

        summary_df[column] = (
            summary_df[column]
            .round(3)
        )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# FORMATIVE VIF SUMMARY
# ============================================================

if formative_vif_results:

    st.divider()

    st.subheader(
        "🧩 Formative Indicator VIF Summary"
    )

    formative_summary = pd.DataFrame(
        formative_vif_results
    )

    formative_summary[
        "VIF"
    ] = formative_summary[
        "VIF"
    ].round(3)

    st.dataframe(
        formative_summary,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# INDICATOR REVIEW
# ============================================================

if all_loading_results:

    st.divider()

    st.subheader(
        "🚦 Indicators Requiring Researcher Review"
    )

    loading_results_df = pd.DataFrame(
        all_loading_results
    )

    weak_indicators = (
        loading_results_df[
            loading_results_df[
                "Outer Loading"
            ] < 0.40
        ]
    )

    review_indicators = (
        loading_results_df[
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
    )

    if weak_indicators.empty:

        st.success(
            "✅ No indicators with outer loading below "
            "0.40 were detected."
        )

    else:

        st.error(
            f"🔴 {len(weak_indicators)} indicator(s) "
            "have outer loading below 0.40."
        )

        weak_display = weak_indicators[
            [
                "Construct",
                "Indicator",
                "Outer Loading"
            ]
        ].copy()

        weak_display[
            "Outer Loading"
        ] = weak_display[
            "Outer Loading"
        ].round(3)

        st.dataframe(
            weak_display,
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

        review_display = review_indicators[
            [
                "Construct",
                "Indicator",
                "Outer Loading"
            ]
        ].copy()

        review_display[
            "Outer Loading"
        ] = review_display[
            "Outer Loading"
        ].round(3)

        st.dataframe(
            review_display,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# DISCRIMINANT VALIDITY
# ============================================================

if len(reflective_construct_scores) >= 2:

    st.divider()

    st.subheader(
        "🔍 Discriminant Validity"
    )

    st.write(
        "Discriminant validity is examined among the "
        "reflective constructs using HTMT and the "
        "Fornell–Larcker criterion."
    )

    reflective_names = list(
        reflective_construct_scores.keys()
    )

    # --------------------------------------------------------
    # HTMT
    # --------------------------------------------------------

    st.markdown(
        "### HTMT"
    )

    htmt_rows = []

    for i in range(
        len(reflective_names)
    ):

        for j in range(
            i + 1,
            len(reflective_names)
        ):

            name_1 = reflective_names[i]
            name_2 = reflective_names[j]

            items_1 = constructs[
                name_1
            ]["items"]

            items_2 = constructs[
                name_2
            ]["items"]

            data_1 = df[
                items_1
            ]

            data_2 = df[
                items_2
            ]

            htmt = calculate_htmt(
                data_1,
                data_2
            )

            if pd.isna(htmt):

                status = "⚪ Not available"

            elif htmt < 0.85:

                status = "🟢 Good"

            elif htmt < 0.90:

                status = "🟡 Review"

            else:

                status = "🔴 High"

            htmt_rows.append(
                {
                    "Construct 1":
                        name_1,

                    "Construct 2":
                        name_2,

                    "HTMT":
                        (
                            round(
                                htmt,
                                3
                            )
                            if not pd.isna(
                                htmt
                            )
                            else np.nan
                        ),

                    "Status":
                        status
                }
            )

    if htmt_rows:

        htmt_df = pd.DataFrame(
            htmt_rows
        )

        st.dataframe(
            htmt_df,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # FORNELL-LARCKER
    # --------------------------------------------------------

    st.markdown(
        "### Fornell–Larcker Criterion"
    )

    score_data = pd.DataFrame(
        reflective_construct_scores
    )

    correlation_matrix = (
        score_data.corr()
    )

    fornell_larcker = (
        correlation_matrix.copy()
    )

    for construct_name in (
        reflective_names
    ):

        ave = reflective_ave.get(
            construct_name,
            np.nan
        )

        if not pd.isna(ave):

            fornell_larcker.loc[
                construct_name,
                construct_name
            ] = np.sqrt(
                ave
            )

    fornell_larcker = (
        fornell_larcker.round(3)
    )

    st.dataframe(
        fornell_larcker,
        use_container_width=True
    )

    st.info(
        "ℹ️ In the Fornell–Larcker matrix, the diagonal "
        "contains the square root of AVE. For adequate "
        "discriminant validity, the diagonal value should "
        "generally be greater than the construct's "
        "correlations with other constructs."
    )

# ============================================================
# RESEARCHER DECISIONS
# ============================================================

if all_loading_results:

    st.divider()

    st.subheader(
        "👨‍🏫 Researcher Decision for Reflective Indicators"
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

        if pd.isna(loading):

            needs_review = True

        else:

            needs_review = (
                loading < 0.708
            )

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
                        if not pd.isna(
                            loading
                        )
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

    if "Outer Loading" in decisions_df.columns:

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
# METHODOLOGICAL NOTES
# ============================================================

st.divider()

st.subheader(
    "📚 Interpretation Guide"
)

guide_col1, guide_col2 = st.columns(2)

with guide_col1:

    st.markdown(
        """
        **Reflective indicators**

        - Outer loading ≥ 0.708 → generally good
        - 0.40–0.707 → review carefully
        - < 0.40 → generally weak
        - Cronbach's Alpha ≥ 0.70 → generally acceptable
        - Composite Reliability ≥ 0.70 → generally acceptable
        - AVE ≥ 0.50 → generally acceptable
        """
    )

with guide_col2:

    st.markdown(
        """
        **Formative indicators**

        - Examine indicator VIF
        - Check indicator weights
        - Examine weight significance
        - Consider indicator relevance
        - Do not automatically apply Alpha/CR/AVE
        """
    )

st.info(
    "ℹ️ Important: These results are researcher-support diagnostics. "
    "Indicator removal should never be based on a numerical threshold "
    "alone. Consider theoretical relevance, content validity, "
    "construct validity, reliability, and the overall research model."
)
