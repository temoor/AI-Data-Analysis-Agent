import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Mediation Analysis",
    page_icon="🔄",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("🔄 Mediation Analysis")

st.write(
    "Assess whether a mediator explains the relationship between "
    "an independent variable (X) and dependent variable (Y)."
)

# ==========================================
# CHECK DATASET
# ==========================================
if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset on the Home page first.")
    st.stop()

df = st.session_state["df"].copy()

st.success("✅ Dataset loaded from Home page.")

# ==========================================
# BASIC INFORMATION
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.metric("Respondents", len(df))

with col2:
    st.metric("Variables", len(df.columns))


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def safe_numeric_series(series):
    return pd.to_numeric(series, errors="coerce")


def standardize_series(series):
    series = safe_numeric_series(series)
    std = series.std(ddof=1)

    if pd.isna(std) or std == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)

    return (series - series.mean()) / std


def regression_coefficient(x, y):
    """
    Simple standardized regression coefficient.
    """
    data = pd.concat(
        [
            safe_numeric_series(x).rename("x"),
            safe_numeric_series(y).rename("y")
        ],
        axis=1
    ).dropna()

    if len(data) < 3:
        return np.nan

    x_values = data["x"].values
    y_values = data["y"].values

    x_sd = np.std(x_values, ddof=1)
    y_sd = np.std(y_values, ddof=1)

    if x_sd == 0 or y_sd == 0:
        return np.nan

    return np.corrcoef(x_values, y_values)[0, 1]


def multiple_regression_coefficients(x, m, y):
    """
    Regression:
        Y = b0 + b1*X + b2*M

    Returns standardized-style coefficients using standardized variables.
    """
    data = pd.concat(
        [
            safe_numeric_series(x).rename("X"),
            safe_numeric_series(m).rename("M"),
            safe_numeric_series(y).rename("Y")
        ],
        axis=1
    ).dropna()

    if len(data) < 5:
        return np.nan, np.nan

    X_std = standardize_series(data["X"]).values
    M_std = standardize_series(data["M"]).values
    Y_std = standardize_series(data["Y"]).values

    design = np.column_stack(
        [
            np.ones(len(data)),
            X_std,
            M_std
        ]
    )

    try:
        coefficients = np.linalg.lstsq(
            design,
            Y_std,
            rcond=None
        )[0]

        b_x = coefficients[1]
        b_m = coefficients[2]

        return b_x, b_m

    except Exception:
        return np.nan, np.nan


def bootstrap_mediation(
    x,
    m,
    y,
    n_bootstrap=1000,
    random_seed=42
):
    """
    Bootstrap mediation estimates.

    Returns:
        a
        b
        c
        c_prime
        indirect
        bootstrap arrays
    """

    data = pd.concat(
        [
            safe_numeric_series(x).rename("X"),
            safe_numeric_series(m).rename("M"),
            safe_numeric_series(y).rename("Y")
        ],
        axis=1
    ).dropna()

    if len(data) < 10:
        raise ValueError(
            "Not enough complete observations for mediation analysis."
        )

    x_values = data["X"].values
    m_values = data["M"].values
    y_values = data["Y"].values

    # --------------------------------------
    # Original estimates
    # --------------------------------------

    a = regression_coefficient(
        data["X"],
        data["M"]
    )

    b, _ = multiple_regression_coefficients(
        data["X"],
        data["M"],
        data["Y"]
    )

    # b is M -> Y controlling X
    _, b_m = multiple_regression_coefficients(
        data["X"],
        data["M"],
        data["Y"]
    )

    b = b_m

    c = regression_coefficient(
        data["X"],
        data["Y"]
    )

    c_prime, _ = multiple_regression_coefficients(
        data["X"],
        data["M"],
        data["Y"]
    )

    indirect = a * b

    # --------------------------------------
    # Bootstrap
    # --------------------------------------

    rng = np.random.default_rng(random_seed)

    boot_a = []
    boot_b = []
    boot_c = []
    boot_c_prime = []
    boot_indirect = []

    n = len(data)

    for _ in range(n_bootstrap):

        indices = rng.integers(
            0,
            n,
            size=n
        )

        bx = x_values[indices]
        bm = m_values[indices]
        by = y_values[indices]

        # a: X -> M
        boot_a_value = regression_coefficient(
            pd.Series(bx),
            pd.Series(bm)
        )

        # b: M -> Y | X
        bx_b = pd.Series(bx)
        bm_b = pd.Series(bm)
        by_b = pd.Series(by)

        boot_b_x, boot_b_m = multiple_regression_coefficients(
            bx_b,
            bm_b,
            by_b
        )

        # c: X -> Y
        boot_c_value = regression_coefficient(
            bx_b,
            by_b
        )

        # c': X -> Y | M
        boot_c_prime_x, _ = multiple_regression_coefficients(
            bx_b,
            bm_b,
            by_b
        )

        if (
            not pd.isna(boot_a_value)
            and not pd.isna(boot_b_m)
        ):
            boot_indirect_value = (
                boot_a_value * boot_b_m
            )
        else:
            boot_indirect_value = np.nan

        boot_a.append(boot_a_value)
        boot_b.append(boot_b_m)
        boot_c.append(boot_c_value)
        boot_c_prime.append(boot_c_prime_x)
        boot_indirect.append(boot_indirect_value)

    boot_a = np.array(boot_a, dtype=float)
    boot_b = np.array(boot_b, dtype=float)
    boot_c = np.array(boot_c, dtype=float)
    boot_c_prime = np.array(boot_c_prime, dtype=float)
    boot_indirect = np.array(boot_indirect, dtype=float)

    boot_a = boot_a[~np.isnan(boot_a)]
    boot_b = boot_b[~np.isnan(boot_b)]
    boot_c = boot_c[~np.isnan(boot_c)]
    boot_c_prime = boot_c_prime[~np.isnan(boot_c_prime)]
    boot_indirect = boot_indirect[
        ~np.isnan(boot_indirect)
    ]

    return {
        "a": a,
        "b": b,
        "c": c,
        "c_prime": c_prime,
        "indirect": indirect,
        "boot_a": boot_a,
        "boot_b": boot_b,
        "boot_c": boot_c,
        "boot_c_prime": boot_c_prime,
        "boot_indirect": boot_indirect,
        "n": len(data)
    }


def bootstrap_statistics(
    coefficient,
    bootstrap_values
):
    """
    Bootstrap SE, t and approximate two-sided p-value.
    """

    if (
        bootstrap_values is None
        or len(bootstrap_values) < 2
        or pd.isna(coefficient)
    ):
        return np.nan, np.nan, np.nan

    se = np.std(
        bootstrap_values,
        ddof=1
    )

    if se == 0 or pd.isna(se):
        return se, np.nan, np.nan

    t_value = coefficient / se

    # Normal approximation for two-sided p-value
    p_value = 2 * (
        1 - 0.5 * (
            1 + np.math.erf(
                abs(t_value) / np.sqrt(2)
            )
        )
    )

    return se, t_value, p_value


def percentile_ci(values, confidence_level):
    alpha = 1 - confidence_level

    lower = np.percentile(
        values,
        100 * alpha / 2
    )

    upper = np.percentile(
        values,
        100 * (1 - alpha / 2)
    )

    return lower, upper


def mediation_decision(
    indirect,
    indirect_lower,
    indirect_upper,
    direct,
    direct_p
):
    """
    Research-oriented mediation classification.

    Main criterion:
    bootstrap CI of indirect effect must exclude zero.
    """

    indirect_significant = (
        indirect_lower > 0
        or indirect_upper < 0
    )

    if not indirect_significant:
        return (
            "No Mediation",
            "The bootstrap confidence interval for the "
            "indirect effect includes zero."
        )

    if pd.isna(direct_p):
        return (
            "Mediation Supported",
            "The bootstrap confidence interval for the "
            "indirect effect excludes zero."
        )

    if direct_p < 0.05:
        return (
            "Partial Mediation",
            "The indirect effect is significant and the "
            "direct effect remains statistically significant."
        )

    return (
        "Full Mediation",
        "The indirect effect is significant while the "
        "direct effect is not statistically significant."
    )


# ==========================================
# PREPARE CONSTRUCT SCORES
# ==========================================
construct_scores = {}

# ------------------------------------------
# SIMPLE CONSTRUCTS
# ------------------------------------------
if "pls_constructs" in st.session_state:

    simple_constructs = st.session_state["pls_constructs"]

    if isinstance(simple_constructs, dict):

        for construct_name, info in simple_constructs.items():

            if not isinstance(info, dict):
                continue

            items = info.get("items", [])

            valid_items = [
                item
                for item in items
                if item in df.columns
            ]

            if len(valid_items) >= 2:

                construct_scores[construct_name] = (
                    df[valid_items]
                    .apply(pd.to_numeric, errors="coerce")
                    .mean(axis=1)
                )


# ------------------------------------------
# HIGHER-ORDER CONSTRUCTS
# ------------------------------------------
hoc_models = {}

if "pls_higher_order_models" in st.session_state:

    hoc_models = st.session_state[
        "pls_higher_order_models"
    ]

elif "pls_higher_order_model" in st.session_state:

    single_model = st.session_state[
        "pls_higher_order_model"
    ]

    if isinstance(single_model, dict):
        hoc_models = {
            single_model.get(
                "name",
                "Higher-Order Construct"
            ): single_model
        }


if isinstance(hoc_models, dict):

    for hoc_name, hoc_info in hoc_models.items():

        if not isinstance(hoc_info, dict):
            continue

        dimensions = hoc_info.get(
            "dimensions",
            {}
        )

        dimension_scores = []

        if isinstance(dimensions, dict):

            for dimension_name, dimension_info in dimensions.items():

                if not isinstance(dimension_info, dict):
                    continue

                items = dimension_info.get(
                    "items",
                    []
                )

                valid_items = [
                    item
                    for item in items
                    if item in df.columns
                ]

                if len(valid_items) >= 1:

                    dim_score = (
                        df[valid_items]
                        .apply(
                            pd.to_numeric,
                            errors="coerce"
                        )
                        .mean(axis=1)
                    )

                    dimension_scores.append(
                        dim_score
                    )

        # HOC score = mean of dimension scores
        if len(dimension_scores) >= 1:

            hoc_score = pd.concat(
                dimension_scores,
                axis=1
            ).mean(axis=1)

            construct_scores[hoc_name] = hoc_score


# ==========================================
# VALIDATE CONSTRUCT SCORES
# ==========================================
if len(construct_scores) < 3:

    st.error(
        "❌ At least three construct scores are required "
        "for mediation analysis."
    )

    st.info(
        "Please define at least three constructs or "
        "higher-order constructs first."
    )

    st.stop()


st.success(
    f"✅ {len(construct_scores)} construct scores prepared successfully."
)

with st.expander("📋 Available Construct Scores"):

    score_summary = pd.DataFrame(
        [
            {
                "Construct": name,
                "Valid Scores": int(
                    series.notna().sum()
                ),
                "Mean": round(
                    series.mean(),
                    3
                ),
                "SD": round(
                    series.std(),
                    3
                )
            }
            for name, series in construct_scores.items()
        ]
    )

    st.dataframe(
        score_summary,
        use_container_width=True
    )


# ==========================================
# DEFINE MEDIATION MODEL
# ==========================================
st.subheader("1️⃣ Define Mediation Model")

st.write(
    "Select the independent variable (X), mediator (M), "
    "and dependent variable (Y)."
)

construct_names = list(
    construct_scores.keys()
)

col1, col2, col3 = st.columns(3)

with col1:

    x_var = st.selectbox(
        "Independent Variable (X)",
        construct_names,
        index=0,
        key="mediation_x"
    )

with col2:

    mediator_options = [
        c for c in construct_names
        if c != x_var
    ]

    m_var = st.selectbox(
        "Mediator (M)",
        mediator_options,
        index=0,
        key="mediation_m"
    )

with col3:

    y_options = [
        c for c in construct_names
        if c not in [x_var, m_var]
    ]

    y_var = st.selectbox(
        "Dependent Variable (Y)",
        y_options,
        index=0,
        key="mediation_y"
    )


st.markdown("### 🔗 Mediation Model")

st.write(
    f"**{x_var} (X) → {m_var} (M) → {y_var} (Y)**"
)

st.write("**Direct relationship:**")

st.write(
    f"**{x_var} (X) → {y_var} (Y)**"
)


# ==========================================
# BOOTSTRAP SETTINGS
# ==========================================
st.subheader("⚙️ Bootstrap Settings")

col1, col2 = st.columns(2)

with col1:

    n_bootstrap = st.selectbox(
        "Number of Bootstrap Samples",
        [1000, 2000, 5000],
        index=0
    )

with col2:

    confidence_level_percent = st.selectbox(
        "Confidence Level",
        [90, 95, 99],
        index=1
    )

confidence_level = (
    confidence_level_percent / 100
)


# ==========================================
# RUN ANALYSIS
# ==========================================
run_analysis = st.button(
    "▶️ Run Mediation Analysis",
    type="primary",
    use_container_width=True
)


if run_analysis:

    with st.spinner(
        "Running mediation analysis and bootstrap procedure..."
    ):

        try:

            results = bootstrap_mediation(
                construct_scores[x_var],
                construct_scores[m_var],
                construct_scores[y_var],
                n_bootstrap=n_bootstrap
            )

        except Exception as e:

            st.error(
                f"❌ Mediation analysis could not be completed: {e}"
            )

            st.stop()

        # ----------------------------------
        # EXTRACT RESULTS
        # ----------------------------------
        a = results["a"]
        b = results["b"]
        c = results["c"]
        c_prime = results["c_prime"]
        indirect = results["indirect"]

        boot_a = results["boot_a"]
        boot_b = results["boot_b"]
        boot_c = results["boot_c"]
        boot_c_prime = results["boot_c_prime"]
        boot_indirect = results["boot_indirect"]

        # ----------------------------------
        # BOOTSTRAP STATISTICS
        # ----------------------------------
        a_se, a_t, a_p = bootstrap_statistics(
            a,
            boot_a
        )

        b_se, b_t, b_p = bootstrap_statistics(
            b,
            boot_b
        )

        c_se, c_t, c_p = bootstrap_statistics(
            c,
            boot_c
        )

        c_prime_se, c_prime_t, c_prime_p = (
            bootstrap_statistics(
                c_prime,
                boot_c_prime
            )
        )

        indirect_se, indirect_t, indirect_p = (
            bootstrap_statistics(
                indirect,
                boot_indirect
            )
        )

        # ----------------------------------
        # CONFIDENCE INTERVALS
        # ----------------------------------
        a_lower, a_upper = percentile_ci(
            boot_a,
            confidence_level
        )

        b_lower, b_upper = percentile_ci(
            boot_b,
            confidence_level
        )

        c_lower, c_upper = percentile_ci(
            boot_c,
            confidence_level
        )

        c_prime_lower, c_prime_upper = (
            percentile_ci(
                boot_c_prime,
                confidence_level
            )
        )

        indirect_lower, indirect_upper = (
            percentile_ci(
                boot_indirect,
                confidence_level
            )
        )

        # ----------------------------------
        # MEDIATION DECISION
        # ----------------------------------
        decision, decision_reason = mediation_decision(
            indirect,
            indirect_lower,
            indirect_upper,
            c_prime,
            c_prime_p
        )

        # ==================================
        # RESULTS
        # ==================================
        st.subheader("2️⃣ Mediation Results")

        results_table = pd.DataFrame(
            [
                {
                    "Effect": "Path a: X → M",
                    "Coefficient (β)": a,
                    "Bootstrap SE": a_se,
                    "t": a_t,
                    "p": a_p
                },
                {
                    "Effect": "Path b: M → Y | X",
                    "Coefficient (β)": b,
                    "Bootstrap SE": b_se,
                    "t": b_t,
                    "p": b_p
                },
                {
                    "Effect": "Total Effect c: X → Y",
                    "Coefficient (β)": c,
                    "Bootstrap SE": c_se,
                    "t": c_t,
                    "p": c_p
                },
                {
                    "Effect": "Direct Effect c': X → Y | M",
                    "Coefficient (β)": c_prime,
                    "Bootstrap SE": c_prime_se,
                    "t": c_prime_t,
                    "p": c_prime_p
                },
                {
                    "Effect": "Indirect Effect a × b",
                    "Coefficient (β)": indirect,
                    "Bootstrap SE": indirect_se,
                    "t": indirect_t,
                    "p": indirect_p
                }
            ]
        )

        display_results = results_table.copy()

        for column in [
            "Coefficient (β)",
            "Bootstrap SE",
            "t",
            "p"
        ]:

            display_results[column] = (
                display_results[column]
                .apply(
                    lambda value:
                    round(value, 4)
                    if pd.notna(value)
                    else None
                )
            )

        st.dataframe(
            display_results,
            use_container_width=True,
            hide_index=True
        )


        # ==================================
        # INDIRECT EFFECT
        # ==================================
        st.subheader("🔄 Indirect Effect")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Indirect Effect (a × b)",
                f"{indirect:.4f}"
            )

        with col2:

            st.metric(
                f"{confidence_level_percent}% CI Lower",
                f"{indirect_lower:.4f}"
            )

        with col3:

            st.metric(
                f"{confidence_level_percent}% CI Upper",
                f"{indirect_upper:.4f}"
            )

        if (
            indirect_lower <= 0
            <= indirect_upper
        ):

            st.warning(
                "⚠️ The bootstrap confidence interval "
                "includes zero. The indirect effect is "
                "not statistically significant."
            )

        else:

            st.success(
                "✅ The bootstrap confidence interval "
                "excludes zero. The indirect effect "
                "is statistically significant."
            )


        # ==================================
        # MEDIATION DECISION
        # ==================================
        st.subheader("🎯 Mediation Decision")

        if decision == "No Mediation":

            st.info(
                f"**{decision}**"
            )

        elif decision == "Partial Mediation":

            st.success(
                f"**{decision}**"
            )

        elif decision == "Full Mediation":

            st.success(
                f"**{decision}**"
            )

        else:

            st.success(
                f"**{decision}**"
            )

        st.write(
            decision_reason
        )


        # ==================================
        # EFFECT SUMMARY
        # ==================================
        st.subheader("📊 Effect Summary")

        effect_summary = pd.DataFrame(
            [
                {
                    "Effect": "Total Effect (c)",
                    "Estimate": c,
                    "CI Lower": c_lower,
                    "CI Upper": c_upper,
                    "p-value": c_p
                },
                {
                    "Effect": "Direct Effect (c')",
                    "Estimate": c_prime,
                    "CI Lower": c_prime_lower,
                    "CI Upper": c_prime_upper,
                    "p-value": c_prime_p
                },
                {
                    "Effect": "Indirect Effect (a × b)",
                    "Estimate": indirect,
                    "CI Lower": indirect_lower,
                    "CI Upper": indirect_upper,
                    "p-value": indirect_p
                }
            ]
        )

        effect_summary_display = effect_summary.copy()

        for column in [
            "Estimate",
            "CI Lower",
            "CI Upper",
            "p-value"
        ]:

            effect_summary_display[column] = (
                effect_summary_display[column]
                .apply(
                    lambda value:
                    round(value, 4)
                    if pd.notna(value)
                    else None
                )
            )

        st.dataframe(
            effect_summary_display,
            use_container_width=True,
            hide_index=True
        )


        # ==================================
        # MEDIATION MODEL DIAGRAM
        # ==================================
        st.subheader("📈 Mediation Model Diagram")

        fig = go.Figure()

        # Nodes
        fig.add_trace(
            go.Scatter(
                x=[0, 5, 10],
                y=[1, 1, 1],
                mode="markers+text",
                marker=dict(
                    size=55
                ),
                text=[
                    x_var,
                    m_var,
                    y_var
                ],
                textposition="bottom center",
                hoverinfo="text",
                showlegend=False
            )
        )

        # Path a
        fig.add_annotation(
            x=2.5,
            y=1.25,
            text=f"a = {a:.3f}",
            showarrow=False
        )

        fig.add_annotation(
            x=2.5,
            y=1,
            ax=0,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            arrowhead=2
        )

        # Path b
        fig.add_annotation(
            x=7.5,
            y=1.25,
            text=f"b = {b:.3f}",
            showarrow=False
        )

        fig.add_annotation(
            x=7.5,
            y=1,
            ax=5,
            ay=1,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            arrowhead=2
        )

        # Direct effect
        fig.add_annotation(
            x=5,
            y=0.25,
            text=f"c' = {c_prime:.3f}",
            showarrow=False
        )

        fig.add_annotation(
            x=7,
            y=0.25,
            ax=3,
            ay=0.25,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            arrowhead=2
        )

        fig.update_layout(
            height=450,
            xaxis=dict(
                visible=False,
                range=[-1, 11]
            ),
            yaxis=dict(
                visible=False,
                range=[0, 2]
            ),
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


        # ==================================
        # RESEARCH INTERPRETATION
        # ==================================
        st.subheader("📝 Research Interpretation")

        st.write(
            f"The mediation model evaluates whether "
            f"**{m_var}** mediates the relationship between "
            f"**{x_var}** and **{y_var}**."
        )

        st.write(
            f"The estimated indirect effect is "
            f"**{indirect:.4f}**."
        )

        st.write(
            f"The bootstrap {confidence_level_percent}% "
            f"confidence interval is "
            f"**[{indirect_lower:.4f}, "
            f"{indirect_upper:.4f}]**."
        )

        st.write(
            f"Therefore, the mediation assessment indicates: "
            f"**{decision}.**"
        )


        # ==================================
        # SAVE RESULTS TO SESSION STATE
        # ==================================
        mediation_results = {
            "X": x_var,
            "Mediator": m_var,
            "Y": y_var,
            "Sample Size": results["n"],
            "Bootstrap Samples": n_bootstrap,
            "Confidence Level": confidence_level_percent,
            "Path a": a,
            "Path a SE": a_se,
            "Path a t": a_t,
            "Path a p": a_p,
            "Path b": b,
            "Path b SE": b_se,
            "Path b t": b_t,
            "Path b p": b_p,
            "Total Effect c": c,
            "Total Effect SE": c_se,
            "Total Effect t": c_t,
            "Total Effect p": c_p,
            "Direct Effect c_prime": c_prime,
            "Direct Effect SE": c_prime_se,
            "Direct Effect t": c_prime_t,
            "Direct Effect p": c_prime_p,
            "Indirect Effect": indirect,
            "Indirect Effect SE": indirect_se,
            "Indirect Effect t": indirect_t,
            "Indirect Effect p": indirect_p,
            "Indirect CI Lower": indirect_lower,
            "Indirect CI Upper": indirect_upper,
            "Decision": decision
        }

        st.session_state[
            "mediation_results"
        ] = mediation_results


        # ==================================
        # EXPORT
        # ==================================
        st.subheader("📥 Export Mediation Results")

        export_df = pd.DataFrame(
            [
                {
                    "X": x_var,
                    "Mediator": m_var,
                    "Y": y_var,
                    "Effect": row["Effect"],
                    "Coefficient": row["Coefficient (β)"],
                    "Bootstrap SE": row["Bootstrap SE"],
                    "t": row["t"],
                    "p": row["p"]
                }
                for _, row in results_table.iterrows()
            ]
        )

        effect_export = effect_summary.copy()

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            export_df.to_excel(
                writer,
                sheet_name="Mediation Results",
                index=False
            )

            effect_export.to_excel(
                writer,
                sheet_name="Effect Summary",
                index=False
            )

            pd.DataFrame(
                {
                    "Item": [
                        "Independent Variable",
                        "Mediator",
                        "Dependent Variable",
                        "Sample Size",
                        "Bootstrap Samples",
                        "Confidence Level",
                        "Mediation Decision"
                    ],
                    "Value": [
                        x_var,
                        m_var,
                        y_var,
                        results["n"],
                        n_bootstrap,
                        f"{confidence_level_percent}%",
                        decision
                    ]
                }
            ).to_excel(
                writer,
                sheet_name="Model Information",
                index=False
            )

        output.seek(0)

        st.download_button(
            label="⬇️ Download Mediation Results (Excel)",
            data=output.getvalue(),
            file_name="Mediation_Analysis_Results.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )


        # ==================================
        # METHODOLOGICAL NOTE
        # ==================================
        with st.expander("ℹ️ Methodological Note"):

            st.write(
                "The mediation procedure estimates the total effect, "
                "direct effect, and indirect effect using composite "
                "construct scores. The indirect effect is evaluated "
                "using bootstrap resampling and a percentile confidence "
                "interval. The bootstrap confidence interval of the "
                "indirect effect is the primary criterion for assessing "
                "mediation."
            )

            st.write(
                "The Path a and Path b standard errors, t-values, and "
                "p-values are based on the bootstrap distributions. "
                "This implementation is intended as a research-support "
                "PLS-SEM-style analysis and should be interpreted "
                "alongside the measurement model, structural model, "
                "research design, and theoretical framework."
            )
