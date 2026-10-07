import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from openpyxl import Workbook


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Mediation Analysis",
    page_icon="🔄",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================
st.title("🔄 Mediation Analysis")

st.write(
    "Assess whether a mediator explains the relationship "
    "between an independent variable (X) and dependent "
    "variable (Y)."
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

st.success(
    "✅ Dataset loaded from Home page."
)


# =========================================================
# BASIC DATA INFORMATION
# =========================================================
col1, col2 = st.columns(2)

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


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def clean_numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce"
    )


def standardize(series):
    series = clean_numeric(series)

    mean = series.mean()
    std = series.std(ddof=1)

    if pd.isna(std) or std == 0:
        return pd.Series(
            np.zeros(len(series)),
            index=series.index
        )

    return (series - mean) / std


def mean_score(data, items):
    """
    Create a composite score by averaging indicators.
    """
    valid_items = [
        item for item in items
        if item in data.columns
    ]

    if not valid_items:
        return None

    numeric_data = data[valid_items].apply(
        pd.to_numeric,
        errors="coerce"
    )

    return numeric_data.mean(
        axis=1,
        skipna=True
    )


def regression_coefficients(y, predictors):
    """
    OLS regression using standardized variables.

    Returns:
        coefficients including intercept
        standard error
        residuals
    """

    y = np.asarray(y, dtype=float)

    X = np.asarray(
        predictors,
        dtype=float
    )

    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Add intercept
    X_design = np.column_stack(
        [
            np.ones(X.shape[0]),
            X
        ]
    )

    beta = np.linalg.lstsq(
        X_design,
        y,
        rcond=None
    )[0]

    predictions = X_design @ beta

    residuals = y - predictions

    n = X_design.shape[0]
    p = X_design.shape[1]

    df_residual = max(
        n - p,
        1
    )

    residual_variance = (
        np.sum(residuals ** 2)
        / df_residual
    )

    try:

        covariance = (
            residual_variance
            * np.linalg.inv(
                X_design.T @ X_design
            )
        )

        standard_errors = np.sqrt(
            np.maximum(
                np.diag(covariance),
                0
            )
        )

    except np.linalg.LinAlgError:

        standard_errors = np.full(
            len(beta),
            np.nan
        )

    return (
        beta,
        standard_errors,
        residuals
    )


def prepare_construct_scores(data):
    """
    Prepare scores for simple constructs and
    higher-order constructs.
    """

    scores = {}

    # -----------------------------------------------------
    # SIMPLE CONSTRUCTS
    # -----------------------------------------------------
    if "pls_constructs" in st.session_state:

        simple_constructs = (
            st.session_state[
                "pls_constructs"
            ]
        )

        if isinstance(
            simple_constructs,
            dict
        ):

            for construct, info in (
                simple_constructs.items()
            ):

                items = []

                if isinstance(
                    info,
                    dict
                ):

                    items = info.get(
                        "items",
                        []
                    )

                elif isinstance(
                    info,
                    list
                ):

                    items = info

                valid_items = [
                    item
                    for item in items
                    if item in data.columns
                ]

                if len(valid_items) >= 1:

                    score = mean_score(
                        data,
                        valid_items
                    )

                    if score is not None:
                        scores[
                            str(construct)
                        ] = score

    # -----------------------------------------------------
    # HIGHER-ORDER CONSTRUCTS
    # -----------------------------------------------------
    hoc_models = None

    if "pls_higher_order_models" in st.session_state:

        hoc_models = st.session_state[
            "pls_higher_order_models"
        ]

    elif "pls_higher_order_model" in st.session_state:

        hoc_models = {
            "Higher-Order Construct":
                st.session_state[
                    "pls_higher_order_model"
                ]
        }

    if hoc_models:

        if isinstance(
            hoc_models,
            dict
        ):

            for hoc_name, hoc_info in (
                hoc_models.items()
            ):

                dimension_scores = []

                # -------------------------------------------------
                # FORMAT A:
                # {"dimensions": {...}}
                # -------------------------------------------------
                dimensions = {}

                if isinstance(
                    hoc_info,
                    dict
                ):

                    dimensions = hoc_info.get(
                        "dimensions",
                        {}
                    )

                    # -------------------------------------------------
                    # FORMAT B:
                    # direct dimension dictionary
                    # -------------------------------------------------
                    if not dimensions:

                        possible_dimensions = {}

                        for key, value in (
                            hoc_info.items()
                        ):

                            if key in [
                                "name",
                                "construct",
                                "type",
                                "measurement_type",
                                "higher_order_construct"
                            ]:
                                continue

                            if isinstance(
                                value,
                                dict
                            ):

                                possible_dimensions[
                                    key
                                ] = value

                        dimensions = (
                            possible_dimensions
                        )

                # -------------------------------------------------
                # PROCESS DIMENSIONS
                # -------------------------------------------------
                if isinstance(
                    dimensions,
                    dict
                ):

                    for dimension_name, dim_info in (
                        dimensions.items()
                    ):

                        items = []

                        measurement_type = (
                            "Reflective"
                        )

                        if isinstance(
                            dim_info,
                            dict
                        ):

                            items = dim_info.get(
                                "items",
                                dim_info.get(
                                    "indicators",
                                    []
                                )
                            )

                            measurement_type = (
                                dim_info.get(
                                    "type",
                                    dim_info.get(
                                        "measurement_type",
                                        "Reflective"
                                    )
                                )
                            )

                        elif isinstance(
                            dim_info,
                            list
                        ):

                            items = dim_info

                        valid_items = [
                            item
                            for item in items
                            if item in data.columns
                        ]

                        if (
                            len(valid_items) >= 1
                        ):

                            dimension_score = (
                                mean_score(
                                    data,
                                    valid_items
                                )
                            )

                            if dimension_score is not None:

                                dimension_scores.append(
                                    dimension_score
                                )

                # -------------------------------------------------
                # HOC SCORE
                # -------------------------------------------------
                if dimension_scores:

                    hoc_score = pd.concat(
                        dimension_scores,
                        axis=1
                    ).mean(
                        axis=1,
                        skipna=True
                    )

                    scores[
                        str(hoc_name)
                    ] = hoc_score

    return scores


# =========================================================
# PREPARE CONSTRUCT SCORES
# =========================================================
with st.spinner(
    "Preparing construct scores..."
):

    construct_scores = (
        prepare_construct_scores(df)
    )


# =========================================================
# FALLBACK:
# TRY CURRENT HIGHER-ORDER MODELS IN COMMON FORMAT
# =========================================================
if not construct_scores:

    st.error(
        "❌ No simple or higher-order constructs "
        "could be prepared."
    )

    st.info(
        "Please define your constructs or higher-order "
        "constructs before performing mediation analysis."
    )

    st.stop()


st.success(
    f"✅ {len(construct_scores)} construct scores "
    "prepared successfully."
)


# =========================================================
# CONSTRUCT SCORE SUMMARY
# =========================================================
with st.expander(
    "📋 Available Construct Scores"
):

    score_summary = []

    for name, score in (
        construct_scores.items()
    ):

        score_summary.append({

            "Construct":
                name,

            "Valid Responses":
                int(
                    score.notna().sum()
                ),

            "Mean":
                round(
                    score.mean(),
                    3
                ),

            "Standard Deviation":
                round(
                    score.std(),
                    3
                )

        })

    st.dataframe(
        pd.DataFrame(score_summary),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# MEDIATION MODEL
# =========================================================
st.divider()

st.header(
    "1️⃣ Define Mediation Model"
)

st.write(
    "Select the independent variable (X), mediator (M), "
    "and dependent variable (Y)."
)

construct_names = list(
    construct_scores.keys()
)


if len(construct_names) < 3:

    st.warning(
        "⚠️ At least three constructs are required "
        "for mediation analysis: X, M, and Y."
    )

    st.stop()


col1, col2, col3 = st.columns(3)


with col1:

    x_construct = st.selectbox(
        "Independent Variable (X)",
        construct_names,
        key="mediation_x"
    )


with col2:

    mediator_options = [
        name
        for name in construct_names
        if name != x_construct
    ]

    mediator_construct = st.selectbox(
        "Mediator (M)",
        mediator_options,
        key="mediation_m"
    )


with col3:

    y_options = [
        name
        for name in construct_names
        if name not in [
            x_construct,
            mediator_construct
        ]
    ]

    y_construct = st.selectbox(
        "Dependent Variable (Y)",
        y_options,
        key="mediation_y"
    )


# =========================================================
# MODEL DIAGRAM
# =========================================================
st.subheader(
    "🔗 Mediation Model"
)

st.markdown(
    f"""
    **{x_construct} (X)** → **{mediator_construct} (M)**
    → **{y_construct} (Y)**

    Direct relationship:

    **{x_construct} (X)** → **{y_construct} (Y)**
    """
)


# =========================================================
# BOOTSTRAP SETTINGS
# =========================================================
st.subheader(
    "⚙️ Bootstrap Settings"
)

bootstrap_iterations = st.selectbox(
    "Number of Bootstrap Samples",
    [500, 1000, 2000, 5000],
    index=1
)

confidence_level = st.selectbox(
    "Confidence Level",
    [90, 95, 99],
    index=1
)


# =========================================================
# RUN MEDIATION
# =========================================================
run_mediation = st.button(
    "▶️ Run Mediation Analysis",
    type="primary",
    use_container_width=True
)


if run_mediation:

    # -----------------------------------------------------
    # PREPARE DATA
    # -----------------------------------------------------
    analysis_data = pd.DataFrame({

        "X":
            construct_scores[
                x_construct
            ],

        "M":
            construct_scores[
                mediator_construct
            ],

        "Y":
            construct_scores[
                y_construct
            ]

    }).dropna()

    # -----------------------------------------------------
    # CHECK SAMPLE
    # -----------------------------------------------------
    if len(analysis_data) < 10:

        st.error(
            "❌ Too few complete observations for "
            "mediation analysis."
        )

        st.stop()


    # -----------------------------------------------------
    # STANDARDIZE VARIABLES
    # -----------------------------------------------------
    X = standardize(
        analysis_data["X"]
    ).values

    M = standardize(
        analysis_data["M"]
    ).values

    Y = standardize(
        analysis_data["Y"]
    ).values


    # =====================================================
    # PATH a: X → M
    # =====================================================
    beta_a, se_a, residual_a = (
        regression_coefficients(
            M,
            X
        )
    )

    a = beta_a[1]


    # =====================================================
    # PATH c: X → Y
    # TOTAL EFFECT
    # =====================================================
    beta_c, se_c, residual_c = (
        regression_coefficients(
            Y,
            X
        )
    )

    c = beta_c[1]


    # =====================================================
    # PATH b AND c':
    # M → Y CONTROLLING X
    # X → Y CONTROLLING M
    # =====================================================
    beta_bc, se_bc, residual_bc = (
        regression_coefficients(
            Y,
            np.column_stack(
                [
                    X,
                    M
                ]
            )
        )
    )

    c_prime = beta_bc[1]

    b = beta_bc[2]


    # =====================================================
    # INDIRECT EFFECT
    # =====================================================
    indirect = a * b


    # =====================================================
    # EFFECT SIZE
    # =====================================================
    total_effect = c

    direct_effect = c_prime


    # =====================================================
    # BOOTSTRAPPING
    # =====================================================
    rng = np.random.default_rng(
        42
    )

    bootstrap_indirect = []

    bootstrap_direct = []

    bootstrap_total = []

    bootstrap_a = []

    bootstrap_b = []

    n = len(
        analysis_data
    )


    progress = st.progress(
        0
    )

    status_text = st.empty()


    for iteration in range(
        bootstrap_iterations
    ):

        indices = rng.integers(
            0,
            n,
            size=n
        )

        xb = X[
            indices
        ]

        mb = M[
            indices
        ]

        yb = Y[
            indices
        ]

        try:

            beta_a_boot, _, _ = (
                regression_coefficients(
                    mb,
                    xb
                )
            )

            beta_bc_boot, _, _ = (
                regression_coefficients(
                    yb,
                    np.column_stack(
                        [
                            xb,
                            mb
                        ]
                    )
                )
            )

            beta_c_boot, _, _ = (
                regression_coefficients(
                    yb,
                    xb
                )
            )

            a_boot = (
                beta_a_boot[1]
            )

            b_boot = (
                beta_bc_boot[2]
            )

            c_prime_boot = (
                beta_bc_boot[1]
            )

            c_boot = (
                beta_c_boot[1]
            )

            indirect_boot = (
                a_boot * b_boot
            )

            bootstrap_a.append(
                a_boot
            )

            bootstrap_b.append(
                b_boot
            )

            bootstrap_indirect.append(
                indirect_boot
            )

            bootstrap_direct.append(
                c_prime_boot
            )

            bootstrap_total.append(
                c_boot
            )

        except Exception:
            continue


        if (
            iteration % max(
                1,
                bootstrap_iterations // 100
            )
            == 0
        ):

            progress.progress(
                min(
                    (iteration + 1)
                    / bootstrap_iterations,
                    1.0
                )
            )

            status_text.text(
                f"Bootstrap progress: "
                f"{iteration + 1:,} / "
                f"{bootstrap_iterations:,}"
            )


    progress.progress(
        1.0
    )

    status_text.text(
        "Bootstrap completed."
    )


    bootstrap_indirect = np.asarray(
        bootstrap_indirect
    )

    bootstrap_direct = np.asarray(
        bootstrap_direct
    )

    bootstrap_total = np.asarray(
        bootstrap_total
    )


    # =====================================================
    # CONFIDENCE INTERVAL
    # =====================================================
    alpha_level = (
        1
        -
        confidence_level / 100
    )

    lower_percentile = (
        alpha_level / 2
    ) * 100

    upper_percentile = (
        1
        -
        alpha_level / 2
    ) * 100


    indirect_lower = np.percentile(
        bootstrap_indirect,
        lower_percentile
    )

    indirect_upper = np.percentile(
        bootstrap_indirect,
        upper_percentile
    )


    direct_lower = np.percentile(
        bootstrap_direct,
        lower_percentile
    )

    direct_upper = np.percentile(
        bootstrap_direct,
        upper_percentile
    )


    total_lower = np.percentile(
        bootstrap_total,
        lower_percentile
    )

    total_upper = np.percentile(
        bootstrap_total,
        upper_percentile
    )


    # =====================================================
    # BOOTSTRAP STANDARD ERRORS
    # =====================================================
    indirect_se = np.std(
        bootstrap_indirect,
        ddof=1
    )

    direct_se = np.std(
        bootstrap_direct,
        ddof=1
    )

    total_se = np.std(
        bootstrap_total,
        ddof=1
    )


    # =====================================================
    # APPROXIMATE T VALUES
    # =====================================================
    indirect_t = (
        indirect / indirect_se
        if indirect_se > 0
        else np.nan
    )

    direct_t = (
        direct_effect / direct_se
        if direct_se > 0
        else np.nan
    )

    total_t = (
        total_effect / total_se
        if total_se > 0
        else np.nan
    )


    # =====================================================
    # NORMAL-APPROXIMATION P VALUES
    # =====================================================
    from scipy.stats import norm

    indirect_p = (
        2
        * (
            1
            -
            norm.cdf(
                abs(indirect_t)
            )
        )
        if not pd.isna(indirect_t)
        else np.nan
    )

    direct_p = (
        2
        * (
            1
            -
            norm.cdf(
                abs(direct_t)
            )
        )
        if not pd.isna(direct_t)
        else np.nan
    )

    total_p = (
        2
        * (
            1
            -
            norm.cdf(
                abs(total_t)
            )
        )
        if not pd.isna(total_t)
        else np.nan
    )


    # =====================================================
    # MEDIATION DECISION
    # =====================================================
    indirect_significant = (
        indirect_lower > 0
        or indirect_upper < 0
    )

    direct_significant = (
        direct_lower > 0
        or direct_upper < 0
    )


    if indirect_significant:

        if direct_significant:

            mediation_decision = (
                "Partial Mediation"
            )

            mediation_explanation = (
                "The indirect effect is significant and "
                "the direct effect remains significant."
            )

        else:

            mediation_decision = (
                "Full Mediation"
            )

            mediation_explanation = (
                "The indirect effect is significant while "
                "the direct effect is not significant."
            )

    else:

        mediation_decision = (
            "No Mediation"
        )

        mediation_explanation = (
            "The bootstrap confidence interval for the "
            "indirect effect includes zero."
        )


    # =====================================================
    # SAVE RESULTS
    # =====================================================
    mediation_results = {

        "Independent Variable":
            x_construct,

        "Mediator":
            mediator_construct,

        "Dependent Variable":
            y_construct,

        "Sample Size":
            len(analysis_data),

        "Bootstrap Samples":
            bootstrap_iterations,

        "Confidence Level":
            confidence_level,

        "Path a":
            a,

        "Path b":
            b,

        "Total Effect c":
            c,

        "Direct Effect c'":
            c_prime,

        "Indirect Effect a*b":
            indirect,

        "Indirect CI Lower":
            indirect_lower,

        "Indirect CI Upper":
            indirect_upper,

        "Indirect SE":
            indirect_se,

        "Indirect t":
            indirect_t,

        "Indirect p":
            indirect_p,

        "Direct CI Lower":
            direct_lower,

        "Direct CI Upper":
            direct_upper,

        "Direct SE":
            direct_se,

        "Direct t":
            direct_t,

        "Direct p":
            direct_p,

        "Total CI Lower":
            total_lower,

        "Total CI Upper":
            total_upper,

        "Total SE":
            total_se,

        "Total t":
            total_t,

        "Total p":
            total_p,

        "Mediation Decision":
            mediation_decision

    }


    st.session_state[
        "mediation_results"
    ] = mediation_results


    # =====================================================
    # RESULTS
    # =====================================================
    st.divider()

    st.header(
        "2️⃣ Mediation Results"
    )


    # -----------------------------------------------------
    # MAIN EFFECTS
    # -----------------------------------------------------
    results_table = pd.DataFrame({

        "Effect": [
            "Path a: X → M",
            "Path b: M → Y | X",
            "Total Effect c: X → Y",
            "Direct Effect c': X → Y | M",
            "Indirect Effect a × b"
        ],

        "Coefficient (β)": [
            a,
            b,
            c,
            c_prime,
            indirect
        ],

        "Bootstrap SE": [
            np.nan,
            np.nan,
            total_se,
            direct_se,
            indirect_se
        ],

        "t": [
            np.nan,
            np.nan,
            total_t,
            direct_t,
            indirect_t
        ],

        "p": [
            np.nan,
            np.nan,
            total_p,
            direct_p,
            indirect_p
        ]

    })


    results_table[
        "Coefficient (β)"
    ] = results_table[
        "Coefficient (β)"
    ].round(4)

    results_table[
        "Bootstrap SE"
    ] = results_table[
        "Bootstrap SE"
    ].round(4)

    results_table[
        "t"
    ] = results_table[
        "t"
    ].round(4)

    results_table[
        "p"
    ] = results_table[
        "p"
    ].round(4)


    st.dataframe(
        results_table,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # INDIRECT EFFECT
    # =====================================================
    st.subheader(
        "🔄 Indirect Effect"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Indirect Effect (a × b)",
            f"{indirect:.4f}"
        )


    with col2:

        st.metric(
            f"{confidence_level}% CI Lower",
            f"{indirect_lower:.4f}"
        )


    with col3:

        st.metric(
            f"{confidence_level}% CI Upper",
            f"{indirect_upper:.4f}"
        )


    if indirect_significant:

        st.success(
            "✅ The bootstrap confidence interval "
            "does not include zero. The indirect effect "
            "is statistically significant."
        )

    else:

        st.warning(
            "⚠️ The bootstrap confidence interval "
            "includes zero. The indirect effect is "
            "not statistically significant."
        )


    # =====================================================
    # MEDIATION DECISION
    # =====================================================
    st.subheader(
        "🎯 Mediation Decision"
    )


    if mediation_decision == "Partial Mediation":

        st.success(
            f"✅ **{mediation_decision}**"
        )

    elif mediation_decision == "Full Mediation":

        st.success(
            f"✅ **{mediation_decision}**"
        )

    else:

        st.info(
            f"ℹ️ **{mediation_decision}**"
        )


    st.write(
        mediation_explanation
    )


    # =====================================================
    # EFFECT SUMMARY
    # =====================================================
    st.subheader(
        "📊 Effect Summary"
    )


    effect_summary = pd.DataFrame({

        "Effect": [
            "Total Effect (c)",
            "Direct Effect (c')",
            "Indirect Effect (a × b)"
        ],

        "Estimate": [
            c,
            c_prime,
            indirect
        ],

        "CI Lower": [
            total_lower,
            direct_lower,
            indirect_lower
        ],

        "CI Upper": [
            total_upper,
            direct_upper,
            indirect_upper
        ],

        "p-value": [
            total_p,
            direct_p,
            indirect_p
        ]

    })


    st.dataframe(
        effect_summary.round(4),
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # MEDIATION DIAGRAM
    # =====================================================
    st.subheader(
        "📈 Mediation Model Diagram"
    )


    fig = go.Figure()


    # Nodes
    fig.add_trace(
        go.Scatter(
            x=[0, 1, 2],
            y=[0, 0, 0],
            mode="markers+text",
            marker=dict(
                size=55
            ),
            text=[
                x_construct,
                mediator_construct,
                y_construct
            ],
            textposition="bottom center",
            hoverinfo="skip"
        )
    )


    # Path a
    fig.add_annotation(
        x=0.5,
        y=0.18,
        ax=0,
        ay=0.18,
        axref="x",
        ayref="y",
        xref="x",
        yref="y",
        text=f"a = {a:.3f}",
        showarrow=True,
        arrowhead=2
    )


    # Path b
    fig.add_annotation(
        x=1.5,
        y=0.18,
        ax=1,
        ay=0.18,
        axref="x",
        ayref="y",
        xref="x",
        yref="y",
        text=f"b = {b:.3f}",
        showarrow=True,
        arrowhead=2
    )


    # Direct effect
    fig.add_annotation(
        x=1,
        y=-0.35,
        ax=0,
        ay=-0.35,
        axref="x",
        ayref="y",
        xref="x",
        yref="y",
        text=f"c' = {c_prime:.3f}",
        showarrow=True,
        arrowhead=2
    )


    fig.update_xaxes(
        visible=False,
        range=[-0.5, 2.5]
    )

    fig.update_yaxes(
        visible=False,
        range=[-0.7, 0.5]
    )

    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # =====================================================
    # MODEL INTERPRETATION
    # =====================================================
    st.subheader(
        "📝 Research Interpretation"
    )


    st.write(
        f"""
        The mediation model evaluates whether **{mediator_construct}**
        mediates the relationship between **{x_construct}** and
        **{y_construct}**.

        The estimated indirect effect is **{indirect:.4f}**.

        The bootstrap {confidence_level}% confidence interval is
        **[{indirect_lower:.4f}, {indirect_upper:.4f}]**.

        Therefore, the mediation assessment indicates:
        **{mediation_decision}**.
        """
    )


    # =====================================================
    # EXCEL EXPORT
    # =====================================================
    st.divider()

    st.subheader(
        "📥 Export Mediation Results"
    )


    output = BytesIO()

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Mediation Results"


    export_rows = [
        [
            "Variable",
            "Value"
        ],

        [
            "Independent Variable",
            x_construct
        ],

        [
            "Mediator",
            mediator_construct
        ],

        [
            "Dependent Variable",
            y_construct
        ],

        [
            "Sample Size",
            len(analysis_data)
        ],

        [
            "Bootstrap Samples",
            bootstrap_iterations
        ],

        [
            "Confidence Level",
            confidence_level
        ],

        [
            "Path a",
            a
        ],

        [
            "Path b",
            b
        ],

        [
            "Total Effect c",
            c
        ],

        [
            "Direct Effect c'",
            c_prime
        ],

        [
            "Indirect Effect a*b",
            indirect
        ],

        [
            "Indirect CI Lower",
            indirect_lower
        ],

        [
            "Indirect CI Upper",
            indirect_upper
        ],

        [
            "Indirect SE",
            indirect_se
        ],

        [
            "Indirect t",
            indirect_t
        ],

        [
            "Indirect p",
            indirect_p
        ],

        [
            "Mediation Decision",
            mediation_decision
        ]
    ]


    for row in export_rows:

        worksheet.append(
            row
        )


    # -----------------------------------------------------
    # EFFECT SUMMARY SHEET
    # -----------------------------------------------------
    worksheet2 = workbook.create_sheet(
        "Effect Summary"
    )


    for row in [
        list(effect_summary.columns)
    ] + effect_summary.values.tolist():

        worksheet2.append(
            row
        )


    workbook.save(
        output
    )

    output.seek(0)


    st.download_button(
        label="⬇️ Download Mediation Results (Excel)",
        data=output,
        file_name="Mediation_Analysis_Results.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
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
        This mediation module estimates the relationships using
        standardized composite construct scores.

        The indirect effect is calculated as:

        **Indirect Effect = a × b**

        where:

        • a = X → M

        • b = M → Y while controlling for X

        • c = total effect of X → Y

        • c' = direct effect of X → Y while controlling for M

        Bootstrap confidence intervals are used for the indirect
        effect because the sampling distribution of an indirect
        effect is generally not assumed to be normal.

        The mediation classification is based primarily on whether
        the bootstrap confidence interval for the indirect effect
        excludes zero and whether the direct effect remains
        statistically significant.

        This is a research-support implementation of mediation
        analysis using composite scores. It should not be described
        as an exact replication of proprietary SmartPLS software.
        """
    )
