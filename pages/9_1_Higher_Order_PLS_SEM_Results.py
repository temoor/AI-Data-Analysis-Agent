import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import io
from openpyxl import Workbook
from openpyxl.styles import Font


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
    "It should not be described as an exact reproduction of SmartPLS."
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
# MULTIPLE HIGHER-ORDER CONSTRUCT SUPPORT
# ============================================================

def is_valid_hoc_model(model):
    return (
        isinstance(model, dict)
        and isinstance(model.get("dimensions", {}), dict)
        and len(model.get("dimensions", {})) > 0
    )


def collect_all_hoc_models():

    models = {}

    # New multiple-HOC storage
    saved_models = st.session_state.get(
        "pls_higher_order_models"
    )

    if isinstance(saved_models, dict):

        # Format:
        # {
        #   "Variable_1": {...},
        #   "Variable_2": {...}
        # }
        for key, value in saved_models.items():

            if is_valid_hoc_model(value):

                name = value.get(
                    "name",
                    str(key)
                )

                models[name] = value

    elif isinstance(saved_models, list):

        for value in saved_models:

            if is_valid_hoc_model(value):

                name = value.get(
                    "name",
                    f"Higher-Order Construct {len(models) + 1}"
                )

                models[name] = value


    # Backward compatibility:
    # original single-HOC storage
    single_model = st.session_state.get(
        "pls_higher_order_model"
    )

    if is_valid_hoc_model(single_model):

        name = single_model.get(
            "name",
            "Higher-Order Construct"
        )

        models[name] = single_model


    return models


all_hoc_models = collect_all_hoc_models()


if not all_hoc_models:

    st.warning(
        "⚠️ No Higher-Order Construct models were found."
    )

    st.info(
        "Please complete 2 Higher Order Construct first."
    )

    st.stop()


# ============================================================
# STRUCTURAL MODEL
# ============================================================

if "pls_higher_order_structural_model" not in st.session_state:

    st.warning(
        "⚠️ No Higher-Order Structural Model was found."
    )

    st.info(
        "Please complete 1 Higher Order Structural Model first."
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
# PRIMARY HOC
# ============================================================

hoc_names = list(all_hoc_models.keys())

primary_hoc_name = hoc_names[0]

primary_hoc_model = all_hoc_models[
    primary_hoc_name
]

primary_hoc_type = primary_hoc_model.get(
    "type",
    "Reflective"
)

primary_dimensions = primary_hoc_model.get(
    "dimensions",
    {}
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def numeric_series(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def numeric_dataframe(data, columns):

    return data[
        columns
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )


def standardize_series(series):

    series = numeric_series(series)

    std = series.std(
        ddof=0
    )

    if pd.isna(std) or std == 0:

        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        series - series.mean()
    ) / std


# ============================================================
# DIMENSION SCORES
# ============================================================

def create_dimension_scores(
    data,
    dimensions
):

    scores = {}

    for dimension_name, information in dimensions.items():

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
            dimension_name
        ] = item_data.mean(
            axis=1
        )

    return pd.DataFrame(
        scores,
        index=data.index
    )


# ============================================================
# HOC SCORE
# ============================================================

def create_hoc_score(
    dimension_scores
):

    if dimension_scores.empty:

        return pd.Series(
            np.nan,
            index=df.index
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


# ============================================================
# CREATE ALL CONSTRUCT SCORES
# ============================================================

def create_all_construct_scores(
    data,
    hoc_models,
    existing_constructs
):

    scores = {}

    # --------------------------------------------------------
    # IMPORTANT:
    # Calculate EVERY Higher-Order Construct
    # --------------------------------------------------------

    for hoc_name, hoc_information in hoc_models.items():

        if not isinstance(
            hoc_information,
            dict
        ):
            continue

        dimensions = hoc_information.get(
            "dimensions",
            {}
        )

        dimension_scores = create_dimension_scores(
            data,
            dimensions
        )

        # HOC score
        if not dimension_scores.empty:

            scores[
                hoc_name
            ] = create_hoc_score(
                dimension_scores
            )

            # Also keep dimension scores available
            # if researcher uses a dimension in a path.
            for dimension_name in dimension_scores.columns:

                if dimension_name not in scores:

                    scores[
                        dimension_name
                    ] = dimension_scores[
                        dimension_name
                    ]


    # --------------------------------------------------------
    # Existing simple constructs
    # --------------------------------------------------------

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


    return pd.DataFrame(
        scores,
        index=data.index
    )


# ============================================================
# REGRESSION
# ============================================================

def multiple_regression(
    y,
    X
):

    combined = pd.concat(
        [
            numeric_series(y).rename("target"),
            X.apply(
                pd.to_numeric,
                errors="coerce"
            )
        ],
        axis=1
    )

    combined = combined.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if len(combined) < 5:

        return None

    if X.shape[1] == 0:

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

    matrix = np.column_stack(
        [
            np.ones(
                len(predictors_std)
            ),
            predictors_std.to_numpy(
                dtype=float
            )
        ]
    )

    try:

        coefficients = np.linalg.lstsq(
            matrix,
            target_std.to_numpy(
                dtype=float
            ),
            rcond=None
        )[0]

    except Exception:

        return None

    predicted = (
        matrix @ coefficients
    )

    residuals = (
        target_std.to_numpy()
        - predicted
    )

    ss_res = np.sum(
        residuals ** 2
    )

    ss_tot = np.sum(
        (
            target_std.to_numpy()
            - target_std.mean()
        ) ** 2
    )

    if ss_tot == 0:

        r_squared = np.nan

    else:

        r_squared = (
            1
            - ss_res / ss_tot
        )

    return {
        "betas": pd.Series(
            coefficients[1:],
            index=predictors.columns
        ),
        "r2": r_squared,
        "n": len(combined)
    }


# ============================================================
# P-VALUE
# ============================================================

def regression_pvalue(
    y,
    x
):

    data = pd.concat(
        [
            numeric_series(y).rename("y"),
            numeric_series(x).rename("x")
        ],
        axis=1
    ).dropna()

    n = len(data)

    if n < 4:

        return np.nan

    y_std = standardize_series(
        data["y"]
    )

    x_std = standardize_series(
        data["x"]
    )

    denominator = np.sum(
        x_std ** 2
    )

    if denominator == 0:

        return np.nan

    beta = np.sum(
        x_std * y_std
    ) / denominator

    residual = (
        y_std
        - beta * x_std
    )

    sse = np.sum(
        residual ** 2
    )

    mse = (
        sse / (n - 2)
    )

    se = np.sqrt(
        mse / denominator
    )

    if (
        se == 0
        or not np.isfinite(se)
    ):

        return np.nan

    t_value = beta / se

    return (
        2
        * stats.t.sf(
            abs(t_value),
            df=n - 2
        )
    )


# ============================================================
# F-SQUARED
# ============================================================

def calculate_f2(
    y,
    predictors,
    target_predictor
):

    full_model = multiple_regression(
        y,
        predictors
    )

    if full_model is None:

        return np.nan

    included_r2 = full_model[
        "r2"
    ]

    reduced_predictors = [
        predictor
        for predictor in predictors.columns
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
        1 - included_r2
    )

    if denominator == 0:

        return np.nan

    return (
        included_r2
        - excluded_r2
    ) / denominator


# ============================================================
# Q²
# ============================================================

def calculate_q2_style(
    target,
    predictors,
    folds=10
):

    try:

        predictor_names = list(
            predictors.columns
        )

        if not predictor_names:

            return np.nan

        combined = pd.concat(
            [
                numeric_series(
                    target
                ).rename("target"),

                predictors[
                    predictor_names
                ].apply(
                    pd.to_numeric,
                    errors="coerce"
                )
            ],
            axis=1
        )

        combined = combined.replace(
            [np.inf, -np.inf],
            np.nan
        ).dropna()

        if len(combined) < 20:

            return np.nan

        n = len(combined)

        actual = combined[
            "target"
        ].to_numpy(
            dtype=float
        )

        predicted = np.full(
            n,
            np.nan
        )

        number_of_folds = min(
            max(
                int(folds),
                2
            ),
            n
        )

        fold_indices = np.array_split(
            np.arange(n),
            number_of_folds
        )

        for test_indices in fold_indices:

            if len(test_indices) == 0:

                continue

            train_mask = np.ones(
                n,
                dtype=bool
            )

            train_mask[
                test_indices
            ] = False

            train_indices = np.where(
                train_mask
            )[0]

            if len(train_indices) < 5:

                continue

            train = combined.iloc[
                train_indices
            ]

            test = combined.iloc[
                test_indices
            ]

            train_y = train[
                "target"
            ]

            train_x = train[
                predictor_names
            ]

            test_x = test[
                predictor_names
            ]

            y_mean = float(
                train_y.mean()
            )

            y_std = float(
                train_y.std(
                    ddof=0
                )
            )

            if (
                not np.isfinite(y_std)
                or y_std <= 0
            ):

                continue

            x_mean = train_x.mean()

            x_std = train_x.std(
                ddof=0
            )

            safe_x_std = x_std.where(
                np.isfinite(x_std)
                & (x_std > 0),
                1.0
            )

            train_x_std = (
                train_x
                - x_mean
            ) / safe_x_std

            test_x_std = (
                test_x
                - x_mean
            ) / safe_x_std

            train_y_std = (
                train_y
                - y_mean
            ) / y_std

            train_matrix = np.column_stack(
                [
                    np.ones(
                        len(train_x_std)
                    ),
                    train_x_std.to_numpy(
                        dtype=float
                    )
                ]
            )

            try:

                coefficients = np.linalg.lstsq(
                    train_matrix,
                    train_y_std.to_numpy(
                        dtype=float
                    ),
                    rcond=None
                )[0]

            except Exception:

                continue

            test_matrix = np.column_stack(
                [
                    np.ones(
                        len(test_x_std)
                    ),
                    test_x_std.to_numpy(
                        dtype=float
                    )
                ]
            )

            predicted_std = (
                test_matrix
                @ coefficients
            )

            predicted_values = (
                predicted_std
                * y_std
            ) + y_mean

            if np.all(
                np.isfinite(
                    predicted_values
                )
            ):

                predicted[
                    test_indices
                ] = predicted_values

        valid = np.isfinite(
            predicted
        )

        if valid.sum() < 5:

            return np.nan

        actual_valid = actual[
            valid
        ]

        predicted_valid = predicted[
            valid
        ]

        sse = np.sum(
            (
                actual_valid
                - predicted_valid
            ) ** 2
        )

        sso = np.sum(
            (
                actual_valid
                - actual_valid.mean()
            ) ** 2
        )

        if (
            not np.isfinite(sso)
            or sso <= 0
        ):

            return np.nan

        q2 = (
            1
            - sse / sso
        )

        if not np.isfinite(q2):

            return np.nan

        return float(q2)

    except Exception:

        return np.nan


# ============================================================
# BOOTSTRAP
# ============================================================

def bootstrap_paths(
    scores,
    structural_paths,
    iterations,
    random_seed
):

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
                if path["predictor"]
                in sample.columns
            ]

            if (
                outcome not in sample.columns
                or not predictors
            ):

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

                beta = model[
                    "betas"
                ].get(
                    predictor,
                    np.nan
                )

                if (
                    key in bootstrap_results
                    and pd.notna(beta)
                ):

                    bootstrap_results[
                        key
                    ].append(
                        float(beta)
                    )

    return bootstrap_results


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
        "Higher-Order Constructs",
        len(all_hoc_models)
    )

with col3:

    st.metric(
        "Total Dimensions",
        sum(
            len(
                model.get(
                    "dimensions",
                    {}
                )
            )
            for model in all_hoc_models.values()
        )
    )

with col4:

    st.metric(
        "Structural Paths",
        len(paths)
    )


# ============================================================
# HOC OVERVIEW
# ============================================================

st.divider()

st.header(
    "🏗️ Higher-Order Construct Overview"
)

hoc_overview_rows = []

for name, model in all_hoc_models.items():

    dims = model.get(
        "dimensions",
        {}
    )

    indicator_count = 0

    for information in dims.values():

        if isinstance(
            information,
            dict
        ):

            indicator_count += len(
                information.get(
                    "items",
                    []
                )
            )

    hoc_overview_rows.append(
        {
            "Higher-Order Construct":
                name,
            "Measurement Type":
                model.get(
                    "type",
                    "Reflective"
                ),
            "Dimensions":
                len(dims),
            "Indicators":
                indicator_count
        }
    )

st.dataframe(
    pd.DataFrame(
        hoc_overview_rows
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CONSTRUCT SCORE PREPARATION
# ============================================================

st.divider()

st.header(
    "📐 Construct Score Preparation"
)

existing_constructs = st.session_state.get(
    "pls_constructs",
    {}
)

construct_scores = create_all_construct_scores(
    df,
    all_hoc_models,
    existing_constructs
)

# ------------------------------------------------------------
# Required constructs from structural paths
# ------------------------------------------------------------

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
        "❌ The following structural constructs could not be calculated:"
    )

    for construct in missing_constructs:

        st.write(
            f"• {construct}"
        )

    st.info(
        "The Higher-Order Construct page must save all HOCs "
        "used in the structural model before results can be calculated."
    )

    st.stop()


st.success(
    "✅ Construct scores prepared successfully."
)

st.write(
    "The system calculated scores for all Higher-Order Constructs "
    "and any simple constructs required by the structural model."
)

st.dataframe(
    construct_scores[
        list(required_constructs)
    ].head(
        10
    ).round(
        3
    ),
    use_container_width=True
)


# ============================================================
# PATH COEFFICIENTS
# ============================================================

st.divider()

st.header(
    "🔗 Path Coefficients"
)

paths_by_outcome = {}

for path in paths:

    outcome = path[
        "outcome"
    ]

    paths_by_outcome.setdefault(
        outcome,
        []
    ).append(
        path
    )


path_results = []

r_squared_results = {}

f_squared_results = []


for outcome, outcome_paths in paths_by_outcome.items():

    predictors = [
        path["predictor"]
        for path in outcome_paths
        if path["predictor"]
        in construct_scores.columns
    ]

    if (
        outcome not in construct_scores.columns
        or not predictors
    ):

        continue

    model = multiple_regression(
        construct_scores[outcome],
        construct_scores[predictors]
    )

    if model is None:

        continue

    r_squared_results[
        outcome
    ] = model[
        "r2"
    ]

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

        if pd.isna(beta):

            direction = "Not available"

        elif abs(beta) >= 0.30:

            direction = "Moderate/Strong"

        elif abs(beta) >= 0.10:

            direction = "Small/Moderate"

        else:

            direction = "Weak"

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
                    model["n"],

                "Direction":
                    direction
            }
        )


path_results_df = pd.DataFrame(
    path_results
)


if path_results_df.empty:

    st.error(
        "❌ No structural path results could be calculated."
    )

    st.stop()


path_results_display = (
    path_results_df.copy()
)

path_results_display[
    "Path Coefficient (β)"
] = path_results_display[
    "Path Coefficient (β)"
].round(
    4
)

path_results_display[
    "p-value"
] = path_results_display[
    "p-value"
].round(
    6
)

st.dataframe(
    path_results_display,
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
                )
                if pd.notna(r2)
                else np.nan,

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
        if path["predictor"]
        in construct_scores.columns
    ]

    if (
        outcome not in construct_scores.columns
        or not predictors
    ):

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
    ].round(
        4
    )

    st.dataframe(
        f2_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# BOOTSTRAPPING
# ============================================================

st.divider()

st.header(
    "🔄 Bootstrapping"
)

st.write(
    "Bootstrapping estimates the stability and sampling "
    "uncertainty of structural path coefficients."
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

        st.session_state[
            "higher_order_bootstrap_results"
        ] = bootstrap_paths(
            construct_scores,
            paths,
            int(bootstrap_iterations),
            int(random_seed)
        )

    st.success(
        f"✅ Bootstrapping completed using "
        f"{bootstrap_iterations:,} samples."
    )


# ============================================================
# BOOTSTRAP RESULTS
# ============================================================

bootstrap_df = pd.DataFrame()


if (
    "higher_order_bootstrap_results"
    in st.session_state
):

    st.divider()

    st.header(
        "📊 Bootstrap Path Results"
    )

    bootstrap_results = st.session_state[
        "higher_order_bootstrap_results"
    ]

    bootstrap_rows = []

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
                    beta
                    / bootstrap_sd
                )

                p_value = (
                    2
                    * stats.norm.sf(
                        abs(t_value)
                    )
                )

            else:

                t_value = np.nan
                p_value = np.nan

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
                    row["Hypothesis"],

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

    numeric_columns = [
        "Original β",
        "Bootstrap Mean",
        "Bootstrap SD",
        "t-value",
        "p-value",
        "2.5% CI",
        "97.5% CI"
    ]

    bootstrap_df[
        numeric_columns
    ] = bootstrap_df[
        numeric_columns
    ].round(
        4
    )

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

st.caption(
    "Q² is calculated independently of bootstrapping. "
    "You do not need to run bootstrapping first."
)

q2_rows = []


for outcome, outcome_paths in paths_by_outcome.items():

    predictors = [
        path["predictor"]
        for path in outcome_paths
        if path["predictor"]
        in construct_scores.columns
    ]

    if (
        not predictors
        or outcome not in construct_scores.columns
    ):

        continue

    q2 = calculate_q2_style(
        construct_scores[outcome],
        construct_scores[predictors],
        folds=10
    )

    if pd.isna(q2):

        interpretation = "Not available"

    elif q2 > 0:

        interpretation = (
            "Predictive relevance indicated"
        )

    else:

        interpretation = (
            "Predictive relevance not indicated"
        )

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
    ].round(
        4
    )

    st.dataframe(
        q2_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "⚠️ Q² could not be calculated for the current model."
    )

st.caption(
    "Q² here is a cross-validated predictive-relevance-style "
    "diagnostic. It is not claimed to reproduce SmartPLS "
    "blindfolding exactly."
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

    p_value = row[
        "p-value"
    ]

    if pd.isna(p_value):

        decision = "Not available"

    elif p_value < 0.05:

        decision = "Supported"

    else:

        decision = "Not Supported"

    hypothesis_rows.append(
        {
            "Hypothesis":
                row["Hypothesis"],

            "Relationship":
                f"{row['Predictor']} → {row['Outcome']}",

            "β":
                row["Path Coefficient (β)"],

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
    hypothesis_df.round(
        4
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# GRAPHICAL STRUCTURAL RESULTS
# ============================================================

st.divider()

st.header(
    "📊 Graphical Structural Results"
)

st.info(
    "The diagram is a SmartPLS-inspired research visualization. "
    "It is not claimed to be an exact SmartPLS graphical reproduction."
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


node_positions = {}

number_nodes = len(
    structural_constructs
)


if number_nodes == 1:

    x_positions = [0.5]

else:

    x_positions = [
        0.10
        + (
            0.80
            * i
            / (number_nodes - 1)
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

    if (
        predictor not in node_positions
        or outcome not in node_positions
    ):

        continue

    x1, y1 = node_positions[
        predictor
    ]

    x2, y2 = node_positions[
        outcome
    ]

    if pd.notna(beta):

        label = (
            f"{row['Hypothesis']}<br>"
            f"β = {beta:.3f}"
        )

    else:

        label = (
            f"{row['Hypothesis']}<br>"
            "β = NA"
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


node_text = []

for construct in structural_constructs:

    if construct in all_hoc_models:

        node_text.append(
            f"<b>{construct}</b><br>"
            "Higher-Order"
        )

    elif any(
        construct in model.get(
            "dimensions",
            {}
        )
        for model in all_hoc_models.values()
        if isinstance(model, dict)
    ):

        node_text.append(
            f"<b>{construct}</b><br>"
            "Dimension"
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
                if c in all_hoc_models
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
        "x":
            0.5
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
            ]
            == "Supported"
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

    st.metric(
        "Endogenous Constructs",
        len(r_squared_results)
    )


# ============================================================
# EXCEL EXPORT
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

        output = io.BytesIO()

        workbook = Workbook()

        workbook.remove(
            workbook.active
        )


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        ws_summary = workbook.create_sheet(
            "Summary"
        )

        summary_rows = [
            [
                "Higher-Order Constructs",
                len(all_hoc_models)
            ],
            [
                "Respondents",
                df.shape[0]
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
        # HOC INFORMATION
        # ----------------------------------------------------

        ws_hoc = workbook.create_sheet(
            "Higher-Order Constructs"
        )

        ws_hoc.append(
            [
                "Higher-Order Construct",
                "Measurement Type",
                "Dimensions"
            ]
        )

        for name, model in all_hoc_models.items():

            ws_hoc.append(
                [
                    name,
                    model.get(
                        "type",
                        "Reflective"
                    ),
                    len(
                        model.get(
                            "dimensions",
                            {}
                        )
                    )
                ]
            )


        # ----------------------------------------------------
        # PATH RESULTS
        # ----------------------------------------------------

        ws_paths = workbook.create_sheet(
            "Path Results"
        )

        ws_paths.append(
            list(
                path_results_df.columns
            )
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
        # HYPOTHESES
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
        # BOOTSTRAPPING
        # ----------------------------------------------------

        if not bootstrap_df.empty:

            ws_boot = workbook.create_sheet(
                "Bootstrapping"
            )

            ws_boot.append(
                list(
                    bootstrap_df.columns
                )
            )

            for row in bootstrap_df.itertuples(
                index=False,
                name=None
            ):

                ws_boot.append(
                    list(row)
                )


        # ----------------------------------------------------
        # HOC DIMENSIONS
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


        for hoc_name_export, model in all_hoc_models.items():

            export_dimensions = model.get(
                "dimensions",
                {}
            )

            for dimension_name, information in export_dimensions.items():

                ws_dimensions.append(
                    [
                        hoc_name_export,
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
        # FORMATTING
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

                        max_length = max(
                            max_length,
                            len(
                                str(
                                    cell.value
                                )
                            )
                        )

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
            label=(
                "⬇️ Download Higher-Order "
                "PLS-SEM Results"
            ),
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
