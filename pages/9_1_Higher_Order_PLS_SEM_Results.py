import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Higher-Order PLS-SEM Results",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Higher-Order PLS-SEM Results")

st.write(
    "Analyze the structural relationships of the Higher-Order "
    "PLS-SEM model, including path coefficients, R², f², "
    "bootstrapping, Q², and hypothesis testing."
)

st.info(
    "This page is a research-support PLS-SEM-style implementation. "
    "It is designed to provide transparent statistical diagnostics "
    "and should not be described as an exact reproduction of SmartPLS."
)

# ============================================================
# CHECK DATA
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
        "Please complete 7_2 Higher-Order Construct first."
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

# ============================================================
# CHECK STRUCTURAL MODEL
# ============================================================

if "pls_higher_order_structural_model" not in st.session_state:

    st.warning(
        "⚠️ No Higher-Order Structural Model was found."
    )

    st.info(
        "Please complete 8_1 Higher-Order Structural Model first."
    )

    st.stop()

structural_model = st.session_state[
    "pls_higher_order_structural_model"
]

paths = structural_model.get(
    "paths",
    []
)

if not paths:

    st.error(
        "❌ No structural paths have been defined."
    )
    st.stop()

# ============================================================
# BASIC INFORMATION
# ============================================================

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Respondents",
        df.shape[0]
    )

with col2:
    st.metric(
        "Higher-Order Construct",
        hoc_name
    )

with col3:
    st.metric(
        "Dimensions",
        len(dimensions)
    )

with col4:
    st.metric(
        "Structural Paths",
        len(paths)
    )

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def numeric_dataframe(data, columns):
    return data[
        columns
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )


def standardize_series(series):
    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    std = series.std(
        ddof=0
    )

    if pd.isna(std) or std == 0:
        return series * 0

    return (
        series -
        series.mean()
    ) / std


def create_dimension_scores(data, model_dimensions):
    """
    Create mean composite scores for each dimension.
    """

    scores = {}

    for dimension_name, information in model_dimensions.items():

        items = information.get(
            "items",
            []
        )

        valid_items = [
            item
            for item in items
            if item in data.columns
        ]

        if not valid_items:
            continue

        item_data = numeric_dataframe(
            data,
            valid_items
        )

        score = item_data.mean(
            axis=1
        )

        scores[
            dimension_name
        ] = score

    return pd.DataFrame(
        scores,
        index=data.index
    )


def create_hoc_score(dimension_scores):
    """
    Create HOC score as the standardized mean of dimension scores.
    """

    if dimension_scores.empty:
        return pd.Series(
            index=dimension_scores.index,
            dtype=float
        )

    standardized = pd.DataFrame(
        index=dimension_scores.index
    )

    for column in dimension_scores.columns:

        standardized[
            column
        ] = standardize_series(
            dimension_scores[column]
        )

    return standardized.mean(
        axis=1
    )


def create_construct_scores(
    data,
    higher_order_name,
    dimensions,
    existing_constructs=None
):
    """
    Create scores for all constructs required by the
    structural model.

    Priority:
    1. Higher-Order Construct score
    2. Existing simple PLS constructs
    3. Dimension scores
    """

    scores = {}

    dimension_scores = create_dimension_scores(
        data,
        dimensions
    )

    # HOC score
    scores[
        higher_order_name
    ] = create_hoc_score(
        dimension_scores
    )

    # Existing simple constructs
    if isinstance(
        existing_constructs,
        dict
    ):

        for construct_name, information in existing_constructs.items():

            if not isinstance(
                information,
                dict
            ):
                continue

            items = information.get(
                "items",
                []
            )

            valid_items = [
                item
                for item in items
                if item in data.columns
            ]

            if not valid_items:
                continue

            item_data = numeric_dataframe(
                data,
                valid_items
            )

            scores[
                construct_name
            ] = item_data.mean(
                axis=1
            )

    # Add dimensions
    for dimension_name in dimension_scores.columns:

        scores[
            dimension_name
        ] = dimension_scores[
            dimension_name
        ]

    return pd.DataFrame(
        scores,
        index=data.index
    )


def standardized_regression(
    y,
    x
):
    """
    Simple standardized regression coefficient.
    """

    data = pd.concat(
        [
            y.rename("y"),
            x.rename("x")
        ],
        axis=1
    ).dropna()

    if len(data) < 3:
        return np.nan

    y_values = standardize_series(
        data["y"]
    )

    x_values = standardize_series(
        data["x"]
    )

    denominator = np.sum(
        x_values ** 2
    )

    if denominator == 0:
        return np.nan

    beta = np.sum(
        x_values *
        y_values
    ) / denominator

    return beta


def multiple_regression(
    y,
    X
):
    """
    Multiple linear regression using numpy.
    Returns standardized path coefficients and R².
    """

    combined = pd.concat(
        [
            y.rename("target"),
            X
        ],
        axis=1
    ).dropna()

    if len(combined) < 5:
        return None

    target = combined[
        "target"
    ]

    predictors = combined[
        X.columns
    ]

    target_std = standardize_series(
        target
    )

    predictors_std = predictors.apply(
        standardize_series
    )

    matrix = predictors_std.values

    matrix = np.column_stack(
        [
            np.ones(
                len(matrix)
            ),
            matrix
        ]
    )

    try:

        coefficients = np.linalg.lstsq(
            matrix,
            target_std.values,
            rcond=None
        )[0]

    except Exception:

        return None

    predicted = (
        matrix @ coefficients
    )

    residuals = (
        target_std.values -
        predicted
    )

    ss_res = np.sum(
        residuals ** 2
    )

    ss_tot = np.sum(
        (
            target_std.values -
            np.mean(
                target_std.values
            )
        ) ** 2
    )

    if ss_tot == 0:

        r_squared = np.nan

    else:

        r_squared = (
            1 -
            ss_res /
            ss_tot
        )

    beta_values = coefficients[
        1:
    ]

    return {
        "betas": pd.Series(
            beta_values,
            index=predictors.columns
        ),
        "r2": r_squared,
        "n": len(combined)
    }


def calculate_f2(
    y,
    predictors,
    target_predictor
):
    """
    f² = (R² included - R² excluded) /
         (1 - R² included)
    """

    full_predictors = list(
        predictors
    )

    full_X = predictors[
        full_predictors
    ]

    full_model = multiple_regression(
        y,
        full_X
    )

    if full_model is None:
        return np.nan

    included_r2 = full_model[
        "r2"
    ]

    reduced_predictors = [
        predictor
        for predictor in full_predictors
        if predictor != target_predictor
    ]

    if reduced_predictors:

        reduced_model = multiple_regression(
            y,
            predictors[
                reduced_predictors
            ]
        )

        if reduced_model is None:
            return np.nan

        excluded_r2 = reduced_model[
            "r2"
        ]

    else:

        excluded_r2 = 0.0

    denominator = (
        1 -
        included_r2
    )

    if denominator == 0:
        return np.nan

    return (
        included_r2 -
        excluded_r2
    ) / denominator


def regression_pvalue(
    y,
    x
):
    """
    p-value for a simple standardized regression coefficient.
    """

    data = pd.concat(
        [
            y.rename("y"),
            x.rename("x")
        ],
        axis=1
    ).dropna()

    n = len(data)

    if n < 4:
        return np.nan

    beta = standardized_regression(
        data["y"],
        data["x"]
    )

    if pd.isna(beta):
        return np.nan

    residual = (
        standardize_series(
            data["y"]
        )
        -
        beta *
        standardize_series(
            data["x"]
        )
    )

    sse = np.sum(
        residual ** 2
    )

    x_values = standardize_series(
        data["x"]
    )

    sxx = np.sum(
        x_values ** 2
    )

    if sxx == 0:
        return np.nan

    mse = (
        sse /
        (n - 2)
    )

    se = np.sqrt(
        mse /
        sxx
    )

    if se == 0:
        return np.nan

    t_value = beta / se

    p_value = (
        2 *
        stats.t.sf(
            abs(t_value),
            df=n - 2
        )
    )

    return p_value


def calculate_q2_style(
    data,
    target,
    predictors,
    folds=10
):
    """
    Cross-validated Q²-style diagnostic.

    This is a research-support predictive relevance
    implementation and not an exact SmartPLS blindfolding
    algorithm.
    """

    combined = pd.concat(
        [
            target.rename("target"),
            predictors
        ],
        axis=1
    ).dropna()

    if len(combined) < 20:
        return np.nan

    actual = combined[
        "target"
    ].values

    predicted = np.zeros(
        len(combined)
    )

    fold_indices = np.array_split(
        np.arange(
            len(combined)
        ),
        min(
            folds,
            len(combined)
        )
    )

    for test_indices in fold_indices:

        train_indices = np.array(
            [
                i
                for i in range(
                    len(combined)
                )
                if i not in set(
                    test_indices
                )
            ]
        )

        if len(train_indices) < 5:
            continue

        train_y = combined.iloc[
            train_indices
        ]["target"]

        train_X = combined.iloc[
            train_indices
        ][predictors.columns]

        test_X = combined.iloc[
            test_indices
        ][predictors.columns]

        model = multiple_regression(
            train_y,
            train_X
        )

        if model is None:
            continue

        train_mean = train_y.mean()
        train_std = train_y.std(
            ddof=0
        )

        if train_std == 0:
            continue

        test_X_std = (
            test_X -
            train_X.mean()
        ) / train_X.std(
            ddof=0
        )

        test_X_std = test_X_std.replace(
            [np.inf, -np.inf],
            np.nan
        ).fillna(0)

        matrix = np.column_stack(
            [
                np.ones(
                    len(test_X_std)
                ),
                test_X_std.values
            ]
        )

        coefficients = np.concatenate(
            [
                [0],
                model["betas"].values
            ]
        )

        predicted_values = (
            matrix @ coefficients
        )

        predicted_values = (
            predicted_values *
            train_std
        ) + train_mean

        predicted[
            test_indices
        ] = predicted_values

    sse = np.sum(
        (
            actual -
            predicted
        ) ** 2
    )

    sso = np.sum(
        (
            actual -
            np.mean(actual)
        ) ** 2
    )

    if sso == 0:
        return np.nan

    return (
        1 -
        sse /
        sso
    )


def bootstrap_paths(
    scores,
    structural_paths,
    iterations,
    random_seed
):
    """
    Bootstrap structural path coefficients.
    """

    rng = np.random.default_rng(
        random_seed
    )

    bootstrap_results = {
        (
            path["predictor"],
            path["outcome"]
        ): []
        for path in structural_paths
    }

    n = len(scores)

    for _ in range(
        iterations
    ):

        indices = rng.integers(
            0,
            n,
            size=n
        )

        sample = scores.iloc[
            indices
        ].reset_index(
            drop=True
        )

        # Find each endogenous outcome
        outcomes = list(
            dict.fromkeys(
                path["outcome"]
                for path in structural_paths
            )
        )

        for outcome in outcomes:

            relevant_paths = [
                path
                for path in structural_paths
                if path["outcome"] == outcome
            ]

            predictors = [
                path["predictor"]
                for path in relevant_paths
                if path["predictor"] in sample.columns
            ]

            if outcome not in sample.columns:
                continue

            if not predictors:
                continue

            model = multiple_regression(
                sample[outcome],
                sample[predictors]
            )

            if model is None:
                continue

            for predictor in predictors:

                key = (
                    predictor,
                    outcome
                )

                if key in bootstrap_results:

                    beta = model[
                        "betas"
                    ].get(
                        predictor,
                        np.nan
                    )

                    if pd.notna(beta):

                        bootstrap_results[
                            key
                        ].append(
                            beta
                        )

    return bootstrap_results


# ============================================================
# CREATE CONSTRUCT SCORES
# ============================================================

st.divider()

st.header(
    "📐 Construct Score Preparation"
)

existing_constructs = st.session_state.get(
    "pls_constructs",
    {}
)

construct_scores = create_construct_scores(
    df,
    hoc_name,
    dimensions,
    existing_constructs
)

# Keep only constructs actually needed by paths
required_constructs = set()

for path in paths:

    required_constructs.add(
        path["predictor"]
    )

    required_constructs.add(
        path["outcome"]
    )

missing_constructs = [
    construct
    for construct in required_constructs
    if construct not in construct_scores.columns
]

if missing_constructs:

    st.error(
        "❌ The following structural constructs could not "
        "be calculated from the current model:"
    )

    for construct in missing_constructs:

        st.write(
            f"• {construct}"
        )

    st.stop()

st.success(
    "✅ Construct scores prepared successfully."
)

score_preview = construct_scores[
    list(required_constructs)
].head(10)

st.dataframe(
    score_preview.round(3),
    use_container_width=True
)

# ============================================================
# STRUCTURAL PATH RESULTS
# ============================================================

st.divider()

st.header(
    "🔗 Path Coefficients"
)

# Group paths by outcome
paths_by_outcome = {}

for path in paths:

    outcome = path[
        "outcome"
    ]

    if outcome not in paths_by_outcome:

        paths_by_outcome[
            outcome
        ] = []

    paths_by_outcome[
        outcome
    ].append(
        path
    )

path_results = []

r_squared_results = {}

f_squared_results = []

for outcome, outcome_paths in paths_by_outcome.items():

    predictors = [
        path["predictor"]
        for path in outcome_paths
    ]

    predictors = [
        predictor
        for predictor in predictors
        if predictor in construct_scores.columns
    ]

    if outcome not in construct_scores.columns:
        continue

    model = multiple_regression(
        construct_scores[outcome],
        construct_scores[
            predictors
        ]
    )

    if model is None:
        continue

    r2 = model[
        "r2"
    ]

    r_squared_results[
        outcome
    ] = r2

    for path in outcome_paths:

        predictor = path[
            "predictor"
        ]

        beta = model[
            "betas"
        ].get(
            predictor,
            np.nan
        )

        p_value = regression_pvalue(
            construct_scores[outcome],
            construct_scores[predictor]
        )

        n = model[
            "n"
        ]

        if pd.notna(beta):

            if abs(beta) >= 0.30:
                effect_direction = "Moderate/Strong"

            elif abs(beta) >= 0.10:
                effect_direction = "Small/Moderate"

            else:
                effect_direction = "Weak"

        else:

            effect_direction = "Not available"

        path_results.append(
            {
                "Hypothesis":
                    path["hypothesis"],
                "Predictor":
                    predictor,
                "Outcome":
                    outcome,
                "Path Coefficient (β)":
                    beta,
                "p-value":
                    p_value,
                "N":
                    n,
                "Direction":
                    effect_direction
            }
        )

# ============================================================
# DISPLAY PATH RESULTS
# ============================================================

path_results_df = pd.DataFrame(
    path_results
)

if path_results_df.empty:

    st.error(
        "❌ No structural path results could be calculated."
    )

    st.stop()

path_results_df[
    "Path Coefficient (β)"
] = path_results_df[
    "Path Coefficient (β)"
].round(4)

path_results_df[
    "p-value"
] = path_results_df[
    "p-value"
].round(6)

st.dataframe(
    path_results_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# R-SQUARED
# ============================================================

st.divider()

st.header(
    "📈 R² — Coefficient of Determination"
)

r2_rows = []

for outcome, r2 in r_squared_results.items():

    if pd.isna(r2):

        interpretation = "Not available"

    elif r2 >= 0.75:

        interpretation = "Substantial"

    elif r2 >= 0.50:

        interpretation = "Moderate"

    elif r2 >= 0.25:

        interpretation = "Weak to moderate"

    else:

        interpretation = "Weak"

    r2_rows.append(
        {
            "Endogenous Construct":
                outcome,
            "R²":
                round(
                    r2,
                    4
                ),
            "Interpretation":
                interpretation
        }
    )

r2_df = pd.DataFrame(
    r2_rows
)

st.dataframe(
    r2_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "R² represents the proportion of variance in an endogenous "
    "construct explained by its predictor constructs."
)

# ============================================================
# F-SQUARED
# ============================================================

st.divider()

st.header(
    "📊 f² — Effect Size"
)

for outcome, outcome_paths in paths_by_outcome.items():

    predictors = [
        path["predictor"]
        for path in outcome_paths
    ]

    predictors = [
        predictor
        for predictor in predictors
        if predictor in construct_scores.columns
    ]

    if outcome not in construct_scores.columns:
        continue

    for path in outcome_paths:

        predictor = path[
            "predictor"
        ]

        if predictor not in predictors:
            continue

        f2 = calculate_f2(
            construct_scores[outcome],
            construct_scores[predictors],
            predictor
        )

        if pd.isna(f2):

            interpretation = "Not available"

        elif f2 >= 0.35:

            interpretation = "Large"

        elif f2 >= 0.15:

            interpretation = "Medium"

        elif f2 >= 0.02:

            interpretation = "Small"

        else:

            interpretation = "Negligible"

        f_squared_results.append(
            {
                "Hypothesis":
                    path["hypothesis"],
                "Predictor":
                    predictor,
                "Outcome":
                    outcome,
                "f²":
                    f2,
                "Effect Size":
                    interpretation
            }
        )

f2_df = pd.DataFrame(
    f_squared_results
)

if not f2_df.empty:

    f2_df[
        "f²"
    ] = f2_df[
        "f²"
    ].round(4)

    st.dataframe(
        f2_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# BOOTSTRAPPING SETTINGS
# ============================================================

st.divider()

st.header(
    "🔄 Bootstrapping"
)

st.write(
    "Bootstrapping estimates the stability and sampling "
    "uncertainty of the structural path coefficients."
)

col1, col2 = st.columns(2)

with col1:

    bootstrap_iterations = st.number_input(
        "Bootstrap Samples",
        min_value=500,
        max_value=10000,
        value=1000,
        step=500,
        key="hoc_bootstrap_iterations"
    )

with col2:

    random_seed = st.number_input(
        "Random Seed",
        min_value=1,
        max_value=999999,
        value=42,
        step=1,
        key="hoc_bootstrap_seed"
    )

run_bootstrap = st.button(
    "🔄 Run Bootstrapping",
    type="primary",
    key="run_hoc_bootstrap"
)

if run_bootstrap:

    with st.spinner(
        "Running bootstrap analysis..."
    ):

        bootstrap_results = bootstrap_paths(
            construct_scores,
            paths,
            int(
                bootstrap_iterations
            ),
            int(
                random_seed
            )
        )

    st.session_state[
        "higher_order_bootstrap_results"
    ] = bootstrap_results

    st.success(
        f"✅ Bootstrapping completed using "
        f"{bootstrap_iterations:,} samples."
    )

# ============================================================
# BOOTSTRAP RESULTS
# ============================================================

if "higher_order_bootstrap_results" in st.session_state:

    st.divider()

    st.header(
        "📊 Bootstrap Path Results"
    )

    bootstrap_results = st.session_state[
        "higher_order_bootstrap_results"
    ]

    bootstrap_rows = []

    for _, path_row in path_results_df.iterrows():

        predictor = path_row[
            "Predictor"
        ]

        outcome = path_row[
            "Outcome"
        ]

        beta = path_row[
            "Path Coefficient (β)"
        ]

        key = (
            predictor,
            outcome
        )

        values = np.array(
            bootstrap_results.get(
                key,
                []
            )
        )

        if len(values) >= 10:

            bootstrap_mean = np.mean(
                values
            )

            bootstrap_sd = np.std(
                values,
                ddof=1
            )

            if bootstrap_sd > 0:

                t_value = (
                    beta /
                    bootstrap_sd
                )

            else:

                t_value = np.nan

            p_value = (
                2 *
                stats.norm.sf(
                    abs(t_value)
                )
                if pd.notna(t_value)
                else np.nan
            )

            lower_ci = np.percentile(
                values,
                2.5
            )

            upper_ci = np.percentile(
                values,
                97.5
            )

        else:

            bootstrap_mean = np.nan
            bootstrap_sd = np.nan
            t_value = np.nan
            p_value = np.nan
            lower_ci = np.nan
            upper_ci = np.nan

        bootstrap_rows.append(
            {
                "Hypothesis":
                    path_row["Hypothesis"],
                "Predictor":
                    predictor,
                "Outcome":
                    outcome,
                "Original β":
                    beta,
                "Bootstrap Mean":
                    bootstrap_mean,
                "Bootstrap SD":
                    bootstrap_sd,
                "t-value":
                    t_value,
                "p-value":
                    p_value,
                "2.5% CI":
                    lower_ci,
                "97.5% CI":
                    upper_ci
            }
        )

    bootstrap_df = pd.DataFrame(
        bootstrap_rows
    )

    numeric_bootstrap_columns = [
        "Original β",
        "Bootstrap Mean",
        "Bootstrap SD",
        "t-value",
        "p-value",
        "2.5% CI",
        "97.5% CI"
    ]

    bootstrap_df[
        numeric_bootstrap_columns
    ] = bootstrap_df[
        numeric_bootstrap_columns
    ].round(4)

    st.dataframe(
        bootstrap_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# Q²
# ============================================================

st.divider()

st.header(
    "🔮 Q² — Predictive Relevance"
)

q2_rows = []

for outcome, outcome_paths in paths_by_outcome.items():

    predictors = [
        path["predictor"]
        for path in outcome_paths
    ]

    predictors = [
        predictor
        for predictor in predictors
        if predictor in construct_scores.columns
    ]

    if not predictors:
        continue

    q2 = calculate_q2_style(
        construct_scores[outcome],
        construct_scores[
            predictors
        ],
        folds=10
    )

    if pd.isna(q2):

        interpretation = "Not available"

    elif q2 > 0:

        interpretation = "Predictive relevance indicated"

    else:

        interpretation = "Predictive relevance not indicated"

    q2_rows.append(
        {
            "Endogenous Construct":
                outcome,
            "Q²":
                q2,
            "Interpretation":
                interpretation
        }
    )

q2_df = pd.DataFrame(
    q2_rows
)

if not q2_df.empty:

    q2_df[
        "Q²"
    ] = q2_df[
        "Q²"
    ].round(4)

    st.dataframe(
        q2_df,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Q² here is a cross-validated predictive-relevance-style "
    "diagnostic. It is not claimed to reproduce SmartPLS blindfolding exactly."
)

# ============================================================
# HYPOTHESIS TESTING
# ============================================================

st.divider()

st.header(
    "🧪 Hypothesis Testing"
)

hypothesis_rows = []

for _, row in path_results_df.iterrows():

    hypothesis = row[
        "Hypothesis"
    ]

    predictor = row[
        "Predictor"
    ]

    outcome = row[
        "Outcome"
    ]

    beta = row[
        "Path Coefficient (β)"
    ]

    p_value = row[
        "p-value"
    ]

    if pd.isna(
        p_value
    ):

        decision = "Not available"

    elif p_value < 0.05:

        decision = "Supported"

    else:

        decision = "Not Supported"

    hypothesis_rows.append(
        {
            "Hypothesis":
                hypothesis,
            "Relationship":
                f"{predictor} → {outcome}",
            "β":
                beta,
            "p-value":
                p_value,
            "Decision":
                decision
        }
    )

hypothesis_df = pd.DataFrame(
    hypothesis_rows
)

st.dataframe(
    hypothesis_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# GRAPHICAL RESULTS
# ============================================================

st.divider()

st.header(
    "📊 Graphical Structural Results"
)

st.info(
    "The diagram below is a SmartPLS-inspired results visualization. "
    "Path coefficients are displayed on the structural relationships."
)

structural_constructs = []

for path in paths:

    if path["predictor"] not in structural_constructs:

        structural_constructs.append(
            path["predictor"]
        )

    if path["outcome"] not in structural_constructs:

        structural_constructs.append(
            path["outcome"]
        )

# ------------------------------------------------------------
# Position constructs
# ------------------------------------------------------------

node_positions = {}

number_nodes = len(
    structural_constructs
)

if number_nodes == 1:

    x_positions = [0.5]

else:

    x_positions = [
        0.10 +
        (
            0.80 *
            i /
            (number_nodes - 1)
        )
        for i in range(
            number_nodes
        )
    ]

for construct, x in zip(
    structural_constructs,
    x_positions
):

    node_positions[
        construct
    ] = (
        x,
        0.55
    )

result_fig = go.Figure()

# ------------------------------------------------------------
# Arrows and coefficients
# ------------------------------------------------------------

for _, row in path_results_df.iterrows():

    predictor = row[
        "Predictor"
    ]

    outcome = row[
        "Outcome"
    ]

    beta = row[
        "Path Coefficient (β)"
    ]

    x1, y1 = node_positions[
        predictor
    ]

    x2, y2 = node_positions[
        outcome
    ]

    label = (
        f"{row['Hypothesis']}<br>"
        f"β = {beta:.3f}"
        if pd.notna(beta)
        else
        f"{row['Hypothesis']}<br>β = NA"
    )

    result_fig.add_annotation(
        x=x2,
        y=y2,
        ax=x1,
        ay=y1,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        text=label
    )

# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------

node_text = []

for construct in structural_constructs:

    if construct == hoc_name:

        node_text.append(
            f"<b>{construct}</b><br>"
            f"Higher-Order"
        )

    elif construct in dimensions:

        node_text.append(
            f"<b>{construct}</b><br>"
            f"Dimension"
        )

    else:

        r2_text = ""

        if construct in r_squared_results:

            r2_text = (
                f"<br>R² = "
                f"{r_squared_results[construct]:.3f}"
            )

        node_text.append(
            f"<b>{construct}</b>"
            f"{r2_text}"
        )

result_fig.add_trace(
    go.Scatter(
        x=[
            node_positions[c][0]
            for c in structural_constructs
        ],
        y=[
            node_positions[c][1]
            for c in structural_constructs
        ],
        mode="markers+text",
        marker=dict(
            size=[
                80
                if c == hoc_name
                else 65
                for c in structural_constructs
            ],
            symbol="circle",
            line=dict(
                width=2
            )
        ),
        text=node_text,
        textposition="middle center",
        hoverinfo="text",
        showlegend=False
    )
)

result_fig.update_layout(
    title={
        "text":
            "Higher-Order PLS-SEM Structural Results",
        "x": 0.5
    },
    height=650,
    margin=dict(
        l=50,
        r=50,
        t=90,
        b=50
    ),
    xaxis=dict(
        visible=False,
        range=[0, 1]
    ),
    yaxis=dict(
        visible=False,
        range=[0, 1]
    ),
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    result_fig,
    use_container_width=True
)

# ============================================================
# RESULTS DASHBOARD
# ============================================================

st.divider()

st.header(
    "📌 Results Dashboard"
)

dashboard_col1, dashboard_col2, dashboard_col3, dashboard_col4 = st.columns(4)

with dashboard_col1:

    supported_count = int(
        (
            hypothesis_df[
                "Decision"
            ] == "Supported"
        ).sum()
    )

    st.metric(
        "Supported Hypotheses",
        supported_count
    )

with dashboard_col2:

    st.metric(
        "Structural Paths",
        len(paths)
    )

with dashboard_col3:

    mean_beta = path_results_df[
        "Path Coefficient (β)"
    ].mean()

    st.metric(
        "Mean β",
        round(
            mean_beta,
            3
        )
    )

with dashboard_col4:

    endogenous_count = len(
        r_squared_results
    )

    st.metric(
        "Endogenous Constructs",
        endogenous_count
    )

# ============================================================
# EXPORT TO EXCEL
# ============================================================

st.divider()

st.header(
    "📥 Export Results"
)

st.write(
    "Export the Higher-Order PLS-SEM results to an Excel workbook."
)

if st.button(
    "📥 Prepare Excel Results",
    key="prepare_hoc_excel"
):

    try:

        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font

        output = io.BytesIO()

        workbook = Workbook()

        # ----------------------------------------------------
        # Remove default sheet
        # ----------------------------------------------------

        default_sheet = workbook.active

        workbook.remove(
            default_sheet
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        ws_summary = workbook.create_sheet(
            "Summary"
        )

        summary_rows = [
            [
                "Higher-Order Construct",
                hoc_name
            ],
            [
                "HOC Measurement Type",
                hoc_type
            ],
            [
                "Respondents",
                df.shape[0]
            ],
            [
                "Dimensions",
                len(dimensions)
            ],
            [
                "Structural Paths",
                len(paths)
            ]
        ]

        for row in summary_rows:

            ws_summary.append(
                row
            )

        # ----------------------------------------------------
        # Path Results
        # ----------------------------------------------------

        ws_paths = workbook.create_sheet(
            "Path Results"
        )

        for row in [
            list(
                path_results_df.columns
            )
        ]:

            ws_paths.append(
                row
            )

        for row in path_results_df.itertuples(
            index=False,
            name=None
        ):

            ws_paths.append(
                list(row)
            )

        # ----------------------------------------------------
        # R2
        # ----------------------------------------------------

        ws_r2 = workbook.create_sheet(
            "R2"
        )

        ws_r2.append(
            list(
                r2_df.columns
            )
        )

        for row in r2_df.itertuples(
            index=False,
            name=None
        ):

            ws_r2.append(
                list(row)
            )

        # ----------------------------------------------------
        # F2
        # ----------------------------------------------------

        if not f2_df.empty:

            ws_f2 = workbook.create_sheet(
                "F2"
            )

            ws_f2.append(
                list(
                    f2_df.columns
                )
            )

            for row in f2_df.itertuples(
                index=False,
                name=None
            ):

                ws_f2.append(
                    list(row)
                )

        # ----------------------------------------------------
        # Q2
        # ----------------------------------------------------

        if not q2_df.empty:

            ws_q2 = workbook.create_sheet(
                "Q2"
            )

            ws_q2.append(
                list(
                    q2_df.columns
                )
            )

            for row in q2_df.itertuples(
                index=False,
                name=None
            ):

                ws_q2.append(
                    list(row)
                )

        # ----------------------------------------------------
        # Hypotheses
        # ----------------------------------------------------

        ws_hyp = workbook.create_sheet(
            "Hypotheses"
        )

        ws_hyp.append(
            list(
                hypothesis_df.columns
            )
        )

        for row in hypothesis_df.itertuples(
            index=False,
            name=None
        ):

            ws_hyp.append(
                list(row)
            )

        # ----------------------------------------------------
        # Bootstrap
        # ----------------------------------------------------

        if "higher_order_bootstrap_results" in st.session_state:

            bootstrap_export = []

            for _, row in bootstrap_df.iterrows():

                bootstrap_export.append(
                    row.to_dict()
                )

            if bootstrap_export:

                ws_boot = workbook.create_sheet(
                    "Bootstrapping"
                )

                export_df = pd.DataFrame(
                    bootstrap_export
                )

                ws_boot.append(
                    list(
                        export_df.columns
                    )
                )

                for row in export_df.itertuples(
                    index=False,
                    name=None
                ):

                    ws_boot.append(
                        list(row)
                    )

        # ----------------------------------------------------
        # Dimension Structure
        # ----------------------------------------------------

        ws_dimensions = workbook.create_sheet(
            "HOC Dimensions"
        )

        ws_dimensions.append(
            [
                "Higher-Order Construct",
                "Dimension",
                "Measurement Type",
                "Indicators"
            ]
        )

        for dimension_name, information in dimensions.items():

            ws_dimensions.append(
                [
                    hoc_name,
                    dimension_name,
                    information.get(
                        "type",
                        "Reflective"
                    ),
                    ", ".join(
                        information.get(
                            "items",
                            []
                        )
                    )
                ]
            )

        # ----------------------------------------------------
        # Formatting
        # ----------------------------------------------------

        for worksheet in workbook.worksheets:

            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True
                )

            for column in worksheet.columns:

                max_length = 0

                column_letter = (
                    column[0].column_letter
                )

                for cell in column:

                    try:

                        cell_length = len(
                            str(
                                cell.value
                            )
                        )

                        if cell_length > max_length:

                            max_length = cell_length

                    except Exception:

                        pass

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max_length + 2,
                    45
                )

        workbook.save(
            output
        )

        output.seek(
            0
        )

        st.download_button(
            label="⬇️ Download Higher-Order PLS-SEM Results",
            data=output,
            file_name=(
                "Higher_Order_PLS_SEM_Results.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key="download_hoc_results"
        )

        st.success(
            "✅ Excel results workbook prepared successfully."
        )

    except Exception as error:

        st.error(
            "❌ Could not prepare the Excel workbook."
        )

        st.exception(
            error
        )

# ============================================================
# FINAL METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.info(
    "📌 Methodological note: This Higher-Order PLS-SEM Results "
    "page provides a transparent research-support implementation "
    "using composite construct scores, regression-based structural "
    "relationships, bootstrap resampling, effect-size diagnostics, "
    "and cross-validation-style predictive relevance. It should "
    "not be presented as an exact reproduction of SmartPLS. "
    "For a thesis or publication, the researcher should report "
    "the implementation approach transparently and justify the "
    "Higher-Order Construct specification theoretically."
)
