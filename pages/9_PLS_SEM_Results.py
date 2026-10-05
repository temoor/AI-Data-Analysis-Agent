import streamlit as st
import pandas as pd
import numpy as np
from statistics import NormalDist
from io import BytesIO

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PLS-SEM Results",
    page_icon="📈",
    layout="wide"
)

st.title("📈 PLS-SEM Results")

st.write(
    "Estimate the structural model and examine path coefficients, "
    "R², f², bootstrap significance, confidence intervals, "
    "and predictive relevance."
)

# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:

    st.warning(
        "⚠️ Please upload your questionnaire dataset "
        "on the Home page first."
    )

    st.stop()

df = st.session_state["df"].copy()

# ============================================================
# CHECK MEASUREMENT MODEL
# ============================================================

if "pls_constructs" not in st.session_state:

    st.warning(
        "⚠️ Please define and save the measurement model "
        "on the PLS-SEM Analysis page first."
    )

    st.stop()

constructs = st.session_state["pls_constructs"]

# ============================================================
# CHECK STRUCTURAL MODEL
# ============================================================

if "pls_structural_paths" not in st.session_state:

    st.warning(
        "⚠️ Please define and save the structural model "
        "on the Structural Model page first."
    )

    st.stop()

structural_paths = st.session_state[
    "pls_structural_paths"
]

if not structural_paths:

    st.warning(
        "⚠️ No structural relationships have been saved."
    )

    st.stop()

# ============================================================
# INFORMATION
# ============================================================

st.success(
    "✅ Dataset, measurement model, and structural model loaded."
)

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
        "Constructs",
        len(constructs)
    )

with col4:
    st.metric(
        "Structural Paths",
        len(structural_paths)
    )

# ============================================================
# MODEL INFORMATION
# ============================================================

st.divider()

st.subheader("🏗️ Structural Model")

paths_df = pd.DataFrame(
    structural_paths
)

st.dataframe(
    paths_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# PREPARE CONSTRUCT SCORES
# ============================================================

st.divider()

st.subheader("📊 Construct Scores")

st.write(
    "Construct scores are calculated from the indicators "
    "defined in the measurement model. Indicators are "
    "standardized before forming composite construct scores."
)

construct_scores = pd.DataFrame(
    index=df.index
)

score_warnings = []

for construct_name, information in constructs.items():

    items = information["items"]

    valid_items = [
        item
        for item in items
        if item in df.columns
    ]

    if not valid_items:

        score_warnings.append(
            f"{construct_name}: no valid indicators found."
        )

        continue

    item_data = df[
        valid_items
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Standardize indicators
    standardized_items = pd.DataFrame(
        index=item_data.index
    )

    for item in valid_items:

        mean_value = item_data[item].mean()
        std_value = item_data[item].std()

        if (
            pd.isna(std_value)
            or std_value == 0
        ):

            standardized_items[item] = (
                item_data[item] - mean_value
            )

        else:

            standardized_items[item] = (
                item_data[item] - mean_value
            ) / std_value

    construct_scores[
        construct_name
    ] = standardized_items.mean(
        axis=1
    )

for warning in score_warnings:

    st.warning(
        f"⚠️ {warning}"
    )

if construct_scores.empty:

    st.error(
        "❌ Construct scores could not be calculated."
    )

    st.stop()

score_preview = construct_scores.describe().T

score_preview = score_preview[
    [
        "count",
        "mean",
        "std",
        "min",
        "max"
    ]
]

score_preview.columns = [
    "Valid Responses",
    "Mean",
    "Standard Deviation",
    "Minimum",
    "Maximum"
]

score_preview = score_preview.round(3)

st.dataframe(
    score_preview,
    use_container_width=True
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def standardize_series(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    mean_value = series.mean()
    std_value = series.std()

    if (
        pd.isna(std_value)
        or std_value == 0
    ):

        return pd.Series(
            np.zeros(
                len(series)
            ),
            index=series.index
        )

    return (
        series - mean_value
    ) / std_value


def calculate_regression(
    data,
    outcome,
    predictors
):

    columns = [
        outcome
    ] + predictors

    model_data = data[
        columns
    ].dropna()

    if (
        model_data.empty
        or len(model_data) <= len(predictors)
    ):

        return {
            "r2": np.nan,
            "coefficients": {}
        }

    y = model_data[
        outcome
    ].to_numpy(
        dtype=float
    )

    x = model_data[
        predictors
    ].to_numpy(
        dtype=float
    )

    x = np.column_stack(
        [
            np.ones(
                len(x)
            ),
            x
        ]
    )

    try:

        beta = np.linalg.lstsq(
            x,
            y,
            rcond=None
        )[0]

    except Exception:

        return {
            "r2": np.nan,
            "coefficients": {}
        }

    y_pred = x @ beta

    ss_total = np.sum(
        (
            y
            - np.mean(y)
        ) ** 2
    )

    ss_error = np.sum(
        (
            y
            - y_pred
        ) ** 2
    )

    if ss_total == 0:

        r2 = np.nan

    else:

        r2 = 1 - (
            ss_error
            / ss_total
        )

    coefficients = {}

    for index, predictor in enumerate(
        predictors,
        start=1
    ):

        coefficients[
            predictor
        ] = beta[index]

    return {
        "r2": r2,
        "coefficients": coefficients
    }


def normal_two_sided_p_value(
    statistic
):

    if pd.isna(statistic):

        return np.nan

    value = abs(
        float(statistic)
    )

    return 2 * (
        1
        - NormalDist().cdf(value)
    )


# ============================================================
# BUILD ENDOGENOUS PREDICTOR STRUCTURE
# ============================================================

construct_names = list(
    constructs.keys()
)

endogenous_predictors = {
    construct: []
    for construct in construct_names
}

for path in structural_paths:

    predictor = path[
        "Predictor"
    ]

    outcome = path[
        "Outcome"
    ]

    if outcome in endogenous_predictors:

        if predictor not in endogenous_predictors[
            outcome
        ]:

            endogenous_predictors[
                outcome
            ].append(
                predictor
            )

# ============================================================
# PATH COEFFICIENTS AND R²
# ============================================================

st.divider()

st.subheader(
    "🔗 Path Coefficients"
)

path_results = []

r2_results = []

for outcome, predictors in endogenous_predictors.items():

    if not predictors:
        continue

    regression_result = calculate_regression(
        construct_scores,
        outcome,
        predictors
    )

    r2_value = regression_result[
        "r2"
    ]

    r2_results.append(
        {
            "Construct": outcome,
            "R²": r2_value
        }
    )

    for predictor in predictors:

        coefficient = regression_result[
            "coefficients"
        ].get(
            predictor,
            np.nan
        )

        matching_paths = [
            path
            for path in structural_paths
            if (
                path["Predictor"]
                == predictor
                and
                path["Outcome"]
                == outcome
            )
        ]

        if matching_paths:

            hypothesis = matching_paths[
                0
            ]["Hypothesis"]

        else:

            hypothesis = ""

        path_results.append(
            {
                "Hypothesis":
                    hypothesis,

                "Predictor":
                    predictor,

                "Outcome":
                    outcome,

                "Path Coefficient (β)":
                    coefficient,

                "R² of Outcome":
                    r2_value
            }
        )

path_results_df = pd.DataFrame(
    path_results
)

if not path_results_df.empty:

    path_results_df[
        "Path Coefficient (β)"
    ] = path_results_df[
        "Path Coefficient (β)"
    ].round(4)

    path_results_df[
        "R² of Outcome"
    ] = path_results_df[
        "R² of Outcome"
    ].round(4)

    st.dataframe(
        path_results_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# R²
# ============================================================

st.subheader(
    "📐 R² — Coefficient of Determination"
)

r2_df = pd.DataFrame(
    r2_results
)

if not r2_df.empty:

    r2_df["R²"] = r2_df[
        "R²"
    ].round(4)

    r2_df["Interpretation"] = r2_df[
        "R²"
    ].apply(
        lambda value:
        "Not available"
        if pd.isna(value)
        else (
            "Weak"
            if value < 0.25
            else
            "Moderate"
            if value < 0.50
            else
            "Substantial"
        )
    )

    st.dataframe(
        r2_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# EFFECT SIZE f²
# ============================================================

st.divider()

st.subheader(
    "📏 Effect Size f²"
)

st.write(
    "f² evaluates how much an individual predictor contributes "
    "to the R² of an endogenous construct."
)

f2_results = []

for outcome, predictors in endogenous_predictors.items():

    if not predictors:
        continue

    full_model = calculate_regression(
        construct_scores,
        outcome,
        predictors
    )

    r2_included = full_model[
        "r2"
    ]

    for predictor in predictors:

        remaining_predictors = [
            p
            for p in predictors
            if p != predictor
        ]

        if remaining_predictors:

            reduced_model = calculate_regression(
                construct_scores,
                outcome,
                remaining_predictors
            )

            r2_excluded = reduced_model[
                "r2"
            ]

        else:

            r2_excluded = 0.0

        if (
            pd.isna(r2_included)
            or
            pd.isna(r2_excluded)
            or
            1 - r2_included == 0
        ):

            f2_value = np.nan

        else:

            f2_value = (
                r2_included
                - r2_excluded
            ) / (
                1 - r2_included
            )

        matching_paths = [
            path
            for path in structural_paths
            if (
                path["Predictor"]
                == predictor
                and
                path["Outcome"]
                == outcome
            )
        ]

        hypothesis = (
            matching_paths[0]["Hypothesis"]
            if matching_paths
            else ""
        )

        f2_results.append(
            {
                "Hypothesis":
                    hypothesis,

                "Predictor":
                    predictor,

                "Outcome":
                    outcome,

                "f²":
                    f2_value
            }
        )

f2_df = pd.DataFrame(
    f2_results
)

if not f2_df.empty:

    f2_df["f²"] = f2_df[
        "f²"
    ].round(4)

    f2_df["Interpretation"] = f2_df[
        "f²"
    ].apply(
        lambda value:
        "Not available"
        if pd.isna(value)
        else (
            "Small"
            if value < 0.15
            else
            "Medium"
            if value < 0.35
            else
            "Large"
        )
    )

    st.dataframe(
        f2_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# BOOTSTRAPPING SETTINGS
# ============================================================

st.divider()

st.subheader(
    "🔄 Bootstrapping"
)

st.write(
    "Bootstrap resampling is used to estimate the sampling "
    "distribution of structural path coefficients."
)

bootstrap_col1, bootstrap_col2 = st.columns(2)

with bootstrap_col1:

    bootstrap_iterations = st.number_input(
        "Number of Bootstrap Samples",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )

with bootstrap_col2:

    confidence_level = st.selectbox(
        "Confidence Level",
        [
            "90%",
            "95%",
            "99%"
        ],
        index=1
    )

if confidence_level == "90%":

    lower_percentile = 5
    upper_percentile = 95

elif confidence_level == "99%":

    lower_percentile = 0.5
    upper_percentile = 99.5

else:

    lower_percentile = 2.5
    upper_percentile = 97.5

# ============================================================
# RUN BOOTSTRAP
# ============================================================

if st.button(
    "🚀 Run PLS-SEM Bootstrap Analysis",
    type="primary"
):

    progress_bar = st.progress(
        0
    )

    status_text = st.empty()

    bootstrap_coefficients = {
        (
            path["Predictor"],
            path["Outcome"]
        ): []
        for path in structural_paths
    }

    rng = np.random.default_rng(
        42
    )

    n = len(
        construct_scores
    )

    for iteration in range(
        int(bootstrap_iterations)
    ):

        sample_indices = rng.integers(
            0,
            n,
            size=n
        )

        bootstrap_sample = (
            construct_scores.iloc[
                sample_indices
            ].reset_index(
                drop=True
            )
        )

        for outcome, predictors in (
            endogenous_predictors.items()
        ):

            if not predictors:
                continue

            result = calculate_regression(
                bootstrap_sample,
                outcome,
                predictors
            )

            for predictor in predictors:

                coefficient = result[
                    "coefficients"
                ].get(
                    predictor,
                    np.nan
                )

                bootstrap_coefficients[
                    (
                        predictor,
                        outcome
                    )
                ].append(
                    coefficient
                )

        if (
            iteration % 10 == 0
            or
            iteration
            == int(
                bootstrap_iterations
            ) - 1
        ):

            progress = (
                (
                    iteration + 1
                )
                /
                int(
                    bootstrap_iterations
                )
            )

            progress_bar.progress(
                progress
            )

            status_text.write(
                f"Bootstrap sample "
                f"{iteration + 1:,} "
                f"of "
                f"{int(bootstrap_iterations):,}"
            )

    progress_bar.empty()
    status_text.empty()

    # ========================================================
    # BOOTSTRAP RESULTS
    # ========================================================

    bootstrap_results = []

    for path in structural_paths:

        predictor = path[
            "Predictor"
        ]

        outcome = path[
            "Outcome"
        ]

        hypothesis = path[
            "Hypothesis"
        ]

        original_rows = path_results_df[
            (
                path_results_df[
                    "Predictor"
                ]
                == predictor
            )
            &
            (
                path_results_df[
                    "Outcome"
                ]
                == outcome
            )
        ]

        if original_rows.empty:

            continue

        original_beta = original_rows[
            "Path Coefficient (β)"
        ].iloc[0]

        values = np.array(
            bootstrap_coefficients[
                (
                    predictor,
                    outcome
                )
            ],
            dtype=float
        )

        values = values[
            np.isfinite(values)
        ]

        if len(values) < 10:

            standard_error = np.nan
            t_value = np.nan
            p_value = np.nan
            lower_ci = np.nan
            upper_ci = np.nan

        else:

            standard_error = np.std(
                values,
                ddof=1
            )

            if (
                pd.isna(
                    standard_error
                )
                or
                standard_error == 0
            ):

                t_value = np.nan
                p_value = np.nan

            else:

                t_value = (
                    original_beta
                    /
                    standard_error
                )

                p_value = (
                    normal_two_sided_p_value(
                        t_value
                    )
                )

            lower_ci = np.percentile(
                values,
                lower_percentile
            )

            upper_ci = np.percentile(
                values,
                upper_percentile
            )

        if (
            pd.notna(p_value)
            and
            p_value < 0.05
        ):

            hypothesis_decision = (
                "Supported at 5% level"
            )

        else:

            hypothesis_decision = (
                "Not supported at 5% level"
            )

        bootstrap_results.append(
            {
                "Hypothesis":
                    hypothesis,

                "Predictor":
                    predictor,

                "Outcome":
                    outcome,

                "Path Coefficient (β)":
                    original_beta,

                "Bootstrap SE":
                    standard_error,

                "t-value":
                    t_value,

                "p-value":
                    p_value,

                f"{confidence_level} CI Lower":
                    lower_ci,

                f"{confidence_level} CI Upper":
                    upper_ci,

                "Decision":
                    hypothesis_decision
            }
        )

    bootstrap_results_df = pd.DataFrame(
        bootstrap_results
    )

    numeric_columns = [
        "Path Coefficient (β)",
        "Bootstrap SE",
        "t-value",
        "p-value",
        f"{confidence_level} CI Lower",
        f"{confidence_level} CI Upper"
    ]

    for column in numeric_columns:

        if column in bootstrap_results_df.columns:

            bootstrap_results_df[
                column
            ] = bootstrap_results_df[
                column
            ].round(4)

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    st.session_state[
        "pls_bootstrap_results"
    ] = bootstrap_results_df

    st.success(
        "✅ Bootstrap analysis completed successfully."
    )

# ============================================================
# SHOW BOOTSTRAP RESULTS
# ============================================================

if "pls_bootstrap_results" in st.session_state:

    st.divider()

    st.subheader(
        "📊 Bootstrap Path Results"
    )

    bootstrap_results_df = st.session_state[
        "pls_bootstrap_results"
    ]

    st.dataframe(
        bootstrap_results_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# Q²-STYLE PREDICTIVE RELEVANCE
# ============================================================

st.divider()

st.subheader(
    "🔮 Predictive Relevance"
)

st.write(
    "The following Q²-style cross-validated predictive "
    "relevance diagnostic uses 10-fold prediction. "
    "It is provided as a research-support diagnostic and "
    "should not be interpreted as identical to SmartPLS "
    "blindfolding."
)

q2_results = []

number_of_folds = 10

for outcome, predictors in endogenous_predictors.items():

    if not predictors:
        continue

    outcome_data = construct_scores[
        [
            outcome
        ] + predictors
    ].dropna()

    if len(outcome_data) < number_of_folds:

        q2_value = np.nan

    else:

        shuffled_indices = np.arange(
            len(outcome_data)
        )

        rng = np.random.default_rng(
            42
        )

        rng.shuffle(
            shuffled_indices
        )

        fold_indices = np.array_split(
            shuffled_indices,
            number_of_folds
        )

        sse = 0.0

        sst = 0.0

        actual_values = outcome_data[
            outcome
        ].to_numpy(
            dtype=float
        )

        mean_actual = np.mean(
            actual_values
        )

        sst = np.sum(
            (
                actual_values
                - mean_actual
            ) ** 2
        )

        for fold in fold_indices:

            train_indices = np.setdiff1d(
                shuffled_indices,
                fold
            )

            test_indices = fold

            train_data = outcome_data.iloc[
                train_indices
            ]

            test_data = outcome_data.iloc[
                test_indices
            ]

            if len(train_data) <= len(
                predictors
            ):

                continue

            x_train = train_data[
                predictors
            ].to_numpy(
                dtype=float
            )

            y_train = train_data[
                outcome
            ].to_numpy(
                dtype=float
            )

            x_train = np.column_stack(
                [
                    np.ones(
                        len(x_train)
                    ),
                    x_train
                ]
            )

            try:

                beta = np.linalg.lstsq(
                    x_train,
                    y_train,
                    rcond=None
                )[0]

            except Exception:

                continue

            x_test = test_data[
                predictors
            ].to_numpy(
                dtype=float
            )

            x_test = np.column_stack(
                [
                    np.ones(
                        len(x_test)
                    ),
                    x_test
                ]
            )

            y_test = test_data[
                outcome
            ].to_numpy(
                dtype=float
            )

            predictions = (
                x_test @ beta
            )

            sse += np.sum(
                (
                    y_test
                    - predictions
                ) ** 2
            )

        if sst == 0:

            q2_value = np.nan

        else:

            q2_value = 1 - (
                sse / sst
            )

    if pd.isna(q2_value):

        interpretation = "Not available"

    elif q2_value > 0:

        interpretation = (
            "Predictive relevance indicated"
        )

    else:

        interpretation = (
            "No predictive relevance indicated"
        )

    q2_results.append(
        {
            "Endogenous Construct":
                outcome,

            "Q²-style":
                q2_value,

            "Interpretation":
                interpretation
        }
    )

q2_df = pd.DataFrame(
    q2_results
)

if not q2_df.empty:

    q2_df[
        "Q²-style"
    ] = q2_df[
        "Q²-style"
    ].round(4)

    st.dataframe(
        q2_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# FINAL HYPOTHESIS SUMMARY
# ============================================================

if "pls_bootstrap_results" in st.session_state:

    st.divider()

    st.subheader(
        "🧪 Hypothesis Testing Summary"
    )

    hypothesis_df = st.session_state[
        "pls_bootstrap_results"
    ].copy()

    display_columns = [
        "Hypothesis",
        "Predictor",
        "Outcome",
        "Path Coefficient (β)",
        "t-value",
        "p-value",
        "Decision"
    ]

    display_columns = [
        column
        for column in display_columns
        if column in hypothesis_df.columns
    ]

    st.dataframe(
        hypothesis_df[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# DOWNLOAD RESULTS
# ============================================================

if "pls_bootstrap_results" in st.session_state:

    st.divider()

    st.subheader(
        "📥 Download Results"
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        path_results_df.to_excel(
            writer,
            sheet_name="Path_Coefficients",
            index=False
        )

        r2_df.to_excel(
            writer,
            sheet_name="R_Squared",
            index=False
        )

        f2_df.to_excel(
            writer,
            sheet_name="Effect_Size_f2",
            index=False
        )

        st.session_state[
            "pls_bootstrap_results"
        ].to_excel(
            writer,
            sheet_name="Bootstrap",
            index=False
        )

        q2_df.to_excel(
            writer,
            sheet_name="Predictive_Relevance",
            index=False
        )

        paths_df.to_excel(
            writer,
            sheet_name="Structural_Model",
            index=False
        )

        score_preview.to_excel(
            writer,
            sheet_name="Construct_Scores"
        )

    output.seek(0)

    st.download_button(
        label="📥 Download PLS-SEM Results Excel",
        data=output,
        file_name="PLS_SEM_Results.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.subheader(
    "📚 Methodological Note"
)

st.info(
    "This page provides a research-support implementation "
    "of PLS-SEM-style structural estimation using composite "
    "construct scores, regression-based path estimation, "
    "bootstrap resampling, effect-size analysis, and "
    "cross-validated predictive relevance. It should not "
    "be described as an exact reproduction of the proprietary "
    "SmartPLS PLS algorithm. Final research conclusions "
    "should be evaluated together with the theoretical model, "
    "measurement model, data quality, sample characteristics, "
    "and established PLS-SEM methodological guidance."
)

st.warning(
    "⚠️ Statistical significance does not by itself establish "
    "causality or theoretical support. The researcher must "
    "interpret the results in relation to the hypotheses and "
    "theory of the study."
)
