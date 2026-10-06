import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

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
    "Evaluate the measurement quality of a Higher-Order Construct "
    "through its dimensions and questionnaire indicators."
)

st.info(
    "This page uses the Higher-Order Construct model saved on the "
    "previous page. The researcher remains responsible for the "
    "theoretical specification of reflective and formative constructs."
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
        "⚠️ No Higher-Order Construct model has been saved yet."
    )

    st.info(
        "Please define and save your model on "
        "7_2 Higher-Order Construct first."
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
        "❌ The Higher-Order Construct contains no dimensions."
    )

    st.stop()

# ============================================================
# BASIC DATA INFORMATION
# ============================================================

numeric_columns = df.select_dtypes(
    include=["number"]
).columns.tolist()

st.divider()

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
    total_indicators = sum(
        len(info.get("items", []))
        for info in dimensions.values()
    )

    st.metric(
        "Indicators",
        total_indicators
    )

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def numeric_series(data, column):
    return pd.to_numeric(
        data[column],
        errors="coerce"
    )


def cronbach_alpha(data):
    """
    Cronbach's alpha.
    """

    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    data = data.dropna(
        axis=0,
        how="any"
    )

    k = data.shape[1]

    if k < 2:
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

    if total_variance == 0:
        return np.nan

    alpha = (
        k / (k - 1)
    ) * (
        1 -
        item_variances.sum() /
        total_variance
    )

    return alpha


def iterative_mode_a_loadings(data):
    """
    PLS-style Mode A loading diagnostic.

    This is a research-support implementation and is not
    presented as an exact SmartPLS algorithm.
    """

    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    data = data.dropna(
        axis=0,
        how="any"
    )

    if data.shape[1] < 2:
        return pd.Series(
            1.0,
            index=data.columns
        )

    standardized = (
        data - data.mean()
    ) / data.std(
        ddof=0
    )

    weights = pd.Series(
        1.0,
        index=data.columns
    )

    weights = weights / np.sqrt(
        np.sum(weights ** 2)
    )

    for _ in range(100):

        composite = (
            standardized *
            weights
        ).sum(
            axis=1
        )

        new_loadings = standardized.apply(
            lambda column:
            column.corr(
                composite
            )
        )

        new_loadings = new_loadings.fillna(
            0
        )

        new_weights = (
            new_loadings.abs()
        )

        if new_weights.sum() == 0:
            break

        new_weights = (
            new_weights /
            np.sqrt(
                np.sum(
                    new_weights ** 2
                )
            )
        )

        if np.max(
            np.abs(
                new_weights.values -
                weights.values
            )
        ) < 0.000001:

            weights = new_weights
            break

        weights = new_weights

    composite = (
        standardized *
        weights
    ).sum(
        axis=1
    )

    loadings = standardized.apply(
        lambda column:
        column.corr(
            composite
        )
    )

    return loadings.fillna(0)


def composite_reliability(loadings):
    """
    Composite Reliability using standardized loadings.
    """

    loadings = pd.Series(
        loadings
    ).dropna()

    if len(loadings) == 0:
        return np.nan

    numerator = (
        loadings.sum()
    ) ** 2

    denominator = (
        numerator +
        np.sum(
            1 -
            loadings ** 2
        )
    )

    if denominator == 0:
        return np.nan

    return numerator / denominator


def average_variance_extracted(loadings):
    """
    AVE = mean squared standardized loadings.
    """

    loadings = pd.Series(
        loadings
    ).dropna()

    if len(loadings) == 0:
        return np.nan

    return np.mean(
        loadings ** 2
    )


def calculate_vif(data):
    """
    VIF calculated from regressions among indicators.
    """

    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    ).dropna()

    if data.shape[1] < 2:
        return pd.Series(
            1.0,
            index=data.columns
        )

    results = {}

    for target in data.columns:

        predictors = [
            col
            for col in data.columns
            if col != target
        ]

        if not predictors:
            results[target] = 1.0
            continue

        y = data[target].values
        X = data[predictors].values

        X = np.column_stack(
            [
                np.ones(
                    len(X)
                ),
                X
            ]
        )

        try:

            beta = np.linalg.lstsq(
                X,
                y,
                rcond=None
            )[0]

            predicted = X @ beta

            ss_res = np.sum(
                (y - predicted) ** 2
            )

            ss_tot = np.sum(
                (y - np.mean(y)) ** 2
            )

            if ss_tot == 0:
                r_squared = 0

            else:
                r_squared = (
                    1 -
                    ss_res /
                    ss_tot
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

        results[target] = vif

    return pd.Series(results)


def construct_score(data):
    """
    Standardized mean composite score.
    """

    data = data.apply(
        pd.to_numeric,
        errors="coerce"
    )

    return data.mean(
        axis=1
    )


def correlation_matrix(data):
    return data.corr()


def calculate_htmt(scores_dict):
    """
    HTMT-style diagnostic between dimensions.

    Uses indicator correlations between dimensions
    relative to within-dimension correlations.
    """

    results = {}

    names = list(
        scores_dict.keys()
    )

    for first, second in combinations(
        names,
        2
    ):

        first_data = scores_dict[first]
        second_data = scores_dict[second]

        first_items = list(
            first_data.columns
        )

        second_items = list(
            second_data.columns
        )

        heterotrait = []

        for item_a in first_items:

            for item_b in second_items:

                corr = first_data[
                    item_a
                ].corr(
                    second_data[
                        item_b
                    ]
                )

                if pd.notna(corr):
                    heterotrait.append(
                        abs(corr)
                    )

        monotrait_first = []

        for a, b in combinations(
            first_items,
            2
        ):

            corr = first_data[
                a
            ].corr(
                first_data[
                    b
                ]
            )

            if pd.notna(corr):
                monotrait_first.append(
                    abs(corr)
                )

        monotrait_second = []

        for a, b in combinations(
            second_items,
            2
        ):

            corr = second_data[
                a
            ].corr(
                second_data[
                    b
                ]
            )

            if pd.notna(corr):
                monotrait_second.append(
                    abs(corr)
                )

        if (
            not heterotrait
            or not monotrait_first
            or not monotrait_second
        ):

            value = np.nan

        else:

            numerator = np.mean(
                heterotrait
            )

            denominator = np.sqrt(
                np.mean(
                    monotrait_first
                )
                *
                np.mean(
                    monotrait_second
                )
            )

            if denominator == 0:
                value = np.nan
            else:
                value = (
                    numerator /
                    denominator
                )

        results[
            f"{first} ↔ {second}"
        ] = value

    return pd.Series(results)


# ============================================================
# MODEL OVERVIEW
# ============================================================

st.divider()

st.subheader(
    "🏗️ Higher-Order Model Overview"
)

overview_rows = []

for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    overview_rows.append(
        {
            "Higher-Order Construct":
                hoc_name,
            "HOC Type":
                hoc_type,
            "Dimension":
                dimension_name,
            "Dimension Type":
                information.get(
                    "type",
                    "Reflective"
                ),
            "Indicators":
                len(items),
            "Indicator List":
                ", ".join(items)
        }
    )

overview_df = pd.DataFrame(
    overview_rows
)

st.dataframe(
    overview_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# INDICATOR VALIDATION
# ============================================================

st.divider()

st.subheader(
    "🔎 Indicator Validation"
)

missing_items = []

for dimension_name, information in dimensions.items():

    for item in information.get(
        "items",
        []
    ):

        if item not in df.columns:
            missing_items.append(
                (
                    dimension_name,
                    item
                )
            )

if missing_items:

    st.error(
        "❌ Some indicators in the Higher-Order model "
        "are not present in the uploaded dataset."
    )

    missing_table = pd.DataFrame(
        [
            {
                "Dimension": dimension,
                "Missing Indicator": item
            }
            for dimension, item in missing_items
        ]
    )

    st.dataframe(
        missing_table,
        use_container_width=True,
        hide_index=True
    )

    st.stop()

else:

    st.success(
        "✅ All Higher-Order model indicators "
        "are present in the dataset."
    )

# ============================================================
# INDICATOR DESCRIPTIVE STATISTICS
# ============================================================

st.divider()

st.subheader(
    "📊 Indicator Descriptive Statistics"
)

indicator_rows = []

for dimension_name, information in dimensions.items():

    for item in information.get(
        "items",
        []
    ):

        series = numeric_series(
            df,
            item
        )

        indicator_rows.append(
            {
                "Dimension":
                    dimension_name,
                "Indicator":
                    item,
                "Valid":
                    int(
                        series.notna().sum()
                    ),
                "Missing":
                    int(
                        series.isna().sum()
                    ),
                "Mean":
                    round(
                        series.mean(),
                        3
                    ),
                "Std. Deviation":
                    round(
                        series.std(),
                        3
                    ),
                "Minimum":
                    round(
                        series.min(),
                        3
                    ),
                "Maximum":
                    round(
                        series.max(),
                        3
                    )
            }
        )

indicator_stats = pd.DataFrame(
    indicator_rows
)

st.dataframe(
    indicator_stats,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# DIMENSION MEASUREMENT RESULTS
# ============================================================

st.divider()

st.header(
    "📐 Dimension-Level Measurement Model"
)

st.write(
    "The following diagnostics evaluate each dimension "
    "using its assigned questionnaire indicators."
)

measurement_results = []

dimension_loadings = {}

dimension_scores = {}

dimension_raw_data = {}

for dimension_name, information in dimensions.items():

    items = information.get(
        "items",
        []
    )

    measurement_type = information.get(
        "type",
        "Reflective"
    )

    data = df[
        items
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )

    dimension_raw_data[
        dimension_name
    ] = data

    # --------------------------------------------------------
    # REFLECTIVE
    # --------------------------------------------------------

    if measurement_type == "Reflective":

        loadings = iterative_mode_a_loadings(
            data
        )

        dimension_loadings[
            dimension_name
        ] = loadings

        alpha = cronbach_alpha(
            data
        )

        cr = composite_reliability(
            loadings
        )

        ave = average_variance_extracted(
            loadings
        )

        score = construct_score(
            data
        )

        dimension_scores[
            dimension_name
        ] = score

        min_loading = (
            loadings.min()
            if len(loadings)
            else np.nan
        )

        max_loading = (
            loadings.max()
            if len(loadings)
            else np.nan
        )

        measurement_results.append(
            {
                "Dimension":
                    dimension_name,
                "Type":
                    "Reflective",
                "Indicators":
                    len(items),
                "Min Loading":
                    round(
                        min_loading,
                        3
                    ),
                "Max Loading":
                    round(
                        max_loading,
                        3
                    ),
                "Cronbach Alpha":
                    round(
                        alpha,
                        3
                    )
                    if pd.notna(alpha)
                    else np.nan,
                "Composite Reliability":
                    round(
                        cr,
                        3
                    )
                    if pd.notna(cr)
                    else np.nan,
                "AVE":
                    round(
                        ave,
                        3
                    )
                    if pd.notna(ave)
                    else np.nan
            }
        )

    # --------------------------------------------------------
    # FORMATIVE
    # --------------------------------------------------------

    else:

        vif = calculate_vif(
            data
        )

        score = construct_score(
            data
        )

        dimension_scores[
            dimension_name
        ] = score

        min_vif = (
            vif.min()
            if len(vif)
            else np.nan
        )

        max_vif = (
            vif.max()
            if len(vif)
            else np.nan
        )

        measurement_results.append(
            {
                "Dimension":
                    dimension_name,
                "Type":
                    "Formative",
                "Indicators":
                    len(items),
                "Min Loading":
                    np.nan,
                "Max Loading":
                    np.nan,
                "Cronbach Alpha":
                    np.nan,
                "Composite Reliability":
                    np.nan,
                "AVE":
                    np.nan,
                "Min VIF":
                    round(
                        min_vif,
                        3
                    )
                    if pd.notna(min_vif)
                    else np.nan,
                "Max VIF":
                    round(
                        max_vif,
                        3
                    )
                    if pd.notna(max_vif)
                    else np.nan
            }
        )

measurement_df = pd.DataFrame(
    measurement_results
)

st.dataframe(
    measurement_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# LOADING DETAILS
# ============================================================

st.divider()

st.subheader(
    "📌 Indicator Loading Details"
)

loading_rows = []

for dimension_name, loadings in dimension_loadings.items():

    for indicator, loading in loadings.items():

        if loading >= 0.708:
            status = "Good"

        elif loading >= 0.40:
            status = "Review"

        else:
            status = "Low"

        loading_rows.append(
            {
                "Dimension":
                    dimension_name,
                "Indicator":
                    indicator,
                "Loading":
                    round(
                        loading,
                        3
                    ),
                "Status":
                    status
            }
        )

if loading_rows:

    loading_df = pd.DataFrame(
        loading_rows
    )

    st.dataframe(
        loading_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Loading values around 0.708 or above are commonly "
        "associated with approximately 50% explained indicator variance. "
        "Lower values should be evaluated in the context of theory, "
        "content validity, reliability, and the overall measurement model."
    )

# ============================================================
# FORMATIVE VIF
# ============================================================

formative_dimensions = [
    name
    for name, information in dimensions.items()
    if information.get(
        "type",
        "Reflective"
    ) == "Formative"
]

if formative_dimensions:

    st.divider()

    st.subheader(
        "📊 Formative Indicator Collinearity"
    )

    formative_vif_rows = []

    for dimension_name in formative_dimensions:

        data = dimension_raw_data[
            dimension_name
        ]

        vif = calculate_vif(
            data
        )

        for indicator, value in vif.items():

            if pd.isna(value):
                status = "Not available"

            elif value < 3:
                status = "Good"

            elif value < 5:
                status = "Review"

            else:
                status = "High"

            formative_vif_rows.append(
                {
                    "Dimension":
                        dimension_name,
                    "Indicator":
                        indicator,
                    "VIF":
                        round(
                            value,
                            3
                        )
                        if np.isfinite(value)
                        else np.inf,
                    "Status":
                        status
                }
            )

    st.dataframe(
        pd.DataFrame(
            formative_vif_rows
        ),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# HTMT BETWEEN DIMENSIONS
# ============================================================

st.divider()

st.subheader(
    "🔗 HTMT Between Dimensions"
)

reflective_dimensions = [
    name
    for name, information in dimensions.items()
    if information.get(
        "type",
        "Reflective"
    ) == "Reflective"
]

if len(reflective_dimensions) >= 2:

    reflective_scores_data = {
        name:
        dimension_raw_data[name]
        for name in reflective_dimensions
    }

    htmt = calculate_htmt(
        reflective_scores_data
    )

    if not htmt.empty:

        htmt_rows = []

        for pair, value in htmt.items():

            if pd.isna(value):
                status = "Not available"

            elif value < 0.85:
                status = "Good"

            elif value < 0.90:
                status = "Review"

            else:
                status = "Potential discriminant validity concern"

            htmt_rows.append(
                {
                    "Dimension Pair":
                        pair,
                    "HTMT":
                        round(
                            value,
                            3
                        )
                        if pd.notna(value)
                        else np.nan,
                    "Status":
                        status
                }
            )

        st.dataframe(
            pd.DataFrame(
                htmt_rows
            ),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "HTMT is a discriminant-validity diagnostic. "
            "Thresholds should be interpreted according to the "
            "research context and methodological literature."
        )

else:

    st.info(
        "HTMT requires at least two reflective dimensions."
    )

# ============================================================
# FORNELL-LARCKER
# ============================================================

st.divider()

st.subheader(
    "📋 Fornell–Larcker Criterion"
)

if len(reflective_dimensions) >= 2:

    reflective_score_table = pd.DataFrame(
        {
            name:
            dimension_scores[name]
            for name in reflective_dimensions
        }
    )

    correlations = reflective_score_table.corr()

    ave_values = {}

    for dimension_name in reflective_dimensions:

        loadings = dimension_loadings.get(
            dimension_name
        )

        if loadings is not None:

            ave_values[
                dimension_name
            ] = average_variance_extracted(
                loadings
            )

    fornell_larcker = correlations.copy()

    for dimension_name in reflective_dimensions:

        ave = ave_values.get(
            dimension_name,
            np.nan
        )

        if pd.notna(ave):

            fornell_larcker.loc[
                dimension_name,
                dimension_name
            ] = np.sqrt(
                ave
            )

    st.dataframe(
        fornell_larcker.round(3),
        use_container_width=True
    )

    st.caption(
        "Diagonal values represent the square root of AVE; "
        "off-diagonal values represent correlations among dimensions."
    )

else:

    st.info(
        "Fornell–Larcker evaluation requires at least "
        "two reflective dimensions."
    )

# ============================================================
# HIGHER-ORDER COMPOSITE SCORE
# ============================================================

st.divider()

st.header(
    "🏗️ Higher-Order Construct Score"
)

st.write(
    "Dimension scores are combined to create a standardized "
    "research-support score for the Higher-Order Construct."
)

dimension_score_table = pd.DataFrame(
    dimension_scores
)

if not dimension_score_table.empty:

    standardized_dimensions = (
        dimension_score_table -
        dimension_score_table.mean()
    ) / dimension_score_table.std(
        ddof=0
    )

    hoc_score = standardized_dimensions.mean(
        axis=1
    )

    st.session_state[
        "pls_higher_order_score"
    ] = hoc_score

    st.metric(
        "Mean HOC Score",
        round(
            hoc_score.mean(),
            3
        )
    )

    st.metric(
        "HOC Score SD",
        round(
            hoc_score.std(),
            3
        )
    )

    score_preview = pd.DataFrame(
        {
            "Dimension":
                standardized_dimensions.columns,
            "Mean Standardized Score":
                standardized_dimensions.mean().values
        }
    )

    st.dataframe(
        score_preview.round(3),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# GRAPHICAL MEASUREMENT MODEL
# ============================================================

st.divider()

st.header(
    "📊 Graphical Measurement Model"
)

st.info(
    "This visualization is a SmartPLS-inspired research figure. "
    "It represents the measurement hierarchy and is not claimed "
    "to be an exact SmartPLS graphical reproduction."
)

# ------------------------------------------------------------
# Build graphical coordinates
# ------------------------------------------------------------

dimension_names = list(
    dimensions.keys()
)

fig = go.Figure()

hoc_x = 0.5
hoc_y = 1.0

dimension_y = 0.60
indicator_y = 0.20

if len(dimension_names) == 1:

    dimension_x = [0.5]

else:

    dimension_x = [
        0.12 +
        (
            0.76 *
            i /
            (len(dimension_names) - 1)
        )
        for i in range(
            len(dimension_names)
        )
    ]

indicator_positions = {}

for i, dimension_name in enumerate(
    dimension_names
):

    items = dimensions[
        dimension_name
    ].get(
        "items",
        []
    )

    dx = dimension_x[i]

    if len(items) == 1:

        positions = [dx]

    else:

        spread = min(
            0.22,
            0.06 * len(items)
        )

        start = dx - spread / 2
        end = dx + spread / 2

        positions = [
            start +
            (
                (end - start) *
                j /
                (len(items) - 1)
            )
            for j in range(
                len(items)
            )
        ]

    for item, position in zip(
        items,
        positions
    ):

        indicator_positions[
            item
        ] = position

# ------------------------------------------------------------
# HOC -> Dimension arrows
# ------------------------------------------------------------

for i, dimension_name in enumerate(
    dimension_names
):

    fig.add_annotation(
        x=dimension_x[i],
        y=dimension_y + 0.05,
        ax=hoc_x,
        ay=hoc_y - 0.05,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        text=""
    )

# ------------------------------------------------------------
# Dimension -> Indicator arrows
# ------------------------------------------------------------

for i, dimension_name in enumerate(
    dimension_names
):

    dx = dimension_x[i]

    for item in dimensions[
        dimension_name
    ].get(
        "items",
        []
    ):

        fig.add_annotation(
            x=indicator_positions[item],
            y=indicator_y + 0.04,
            ax=dx,
            ay=dimension_y - 0.05,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.2,
            text=""
        )

# ------------------------------------------------------------
# HOC
# ------------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=[hoc_x],
        y=[hoc_y],
        mode="markers+text",
        marker=dict(
            size=75,
            symbol="circle",
            line=dict(
                width=2
            )
        ),
        text=[
            f"<b>{hoc_name}</b><br>{hoc_type}"
        ],
        textposition="middle center",
        showlegend=False,
        hoverinfo="text"
    )
)

# ------------------------------------------------------------
# Dimensions
# ------------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=dimension_x,
        y=[
            dimension_y
            for _ in dimension_names
        ],
        mode="markers+text",
        marker=dict(
            size=60,
            symbol="square",
            line=dict(
                width=2
            )
        ),
        text=[
            f"<b>{name}</b>"
            for name in dimension_names
        ],
        textposition="middle center",
        showlegend=False,
        hoverinfo="text"
    )
)

# ------------------------------------------------------------
# Indicators
# ------------------------------------------------------------

all_items = []
all_x = []

for dimension_name in dimension_names:

    for item in dimensions[
        dimension_name
    ].get(
        "items",
        []
    ):

        all_items.append(
            item
        )

        all_x.append(
            indicator_positions[item]
        )

fig.add_trace(
    go.Scatter(
        x=all_x,
        y=[
            indicator_y
            for _ in all_items
        ],
        mode="markers+text",
        marker=dict(
            size=38,
            symbol="circle",
            line=dict(
                width=1.5
            )
        ),
        text=[
            f"<b>{item}</b>"
            for item in all_items
        ],
        textposition="bottom center",
        showlegend=False,
        hoverinfo="text"
    )
)

fig.update_layout(
    height=max(
        600,
        500 +
        len(all_items) * 8
    ),
    margin=dict(
        l=40,
        r=40,
        t=70,
        b=50
    ),
    title={
        "text":
            "Higher-Order Measurement Model",
        "x": 0.5
    },
    xaxis=dict(
        visible=False,
        range=[0, 1]
    ),
    yaxis=dict(
        visible=False,
        range=[0, 1.12]
    ),
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# MEASUREMENT MODEL STATUS
# ============================================================

st.divider()

st.header(
    "🔎 Measurement Model Status"
)

status_messages = []

for _, row in measurement_df.iterrows():

    dimension_name = row[
        "Dimension"
    ]

    measurement_type = row[
        "Type"
    ]

    if measurement_type == "Reflective":

        alpha = row[
            "Cronbach Alpha"
        ]

        cr = row[
            "Composite Reliability"
        ]

        ave = row[
            "AVE"
        ]

        if (
            pd.notna(alpha)
            and pd.notna(cr)
            and pd.notna(ave)
        ):

            if (
                alpha >= 0.70
                and cr >= 0.70
                and ave >= 0.50
            ):

                status_messages.append(
                    (
                        dimension_name,
                        "Pass",
                        "Reliability and convergent validity indicators "
                        "are within commonly used guideline ranges."
                    )
                )

            else:

                status_messages.append(
                    (
                        dimension_name,
                        "Review",
                        "One or more reliability/convergent validity "
                        "statistics require researcher review."
                    )
                )

    else:

        status_messages.append(
            (
                dimension_name,
                "Review",
                "Formative dimension should be evaluated primarily "
                "using collinearity and substantive/theoretical relevance."
            )
        )

for dimension_name, status, message in status_messages:

    if status == "Pass":

        st.success(
            f"✅ **{dimension_name}** — {message}"
        )

    else:

        st.warning(
            f"⚠️ **{dimension_name}** — {message}"
        )

# ============================================================
# RESEARCHER DECISION
# ============================================================

st.divider()

st.header(
    "🧑‍🔬 Researcher Measurement Decision"
)

st.write(
    "Statistical indicators support researcher judgment; "
    "they do not automatically determine whether an indicator "
    "should be retained or removed."
)

decision_options = [
    "Pending Review",
    "Accept Measurement Model",
    "Review Indicators",
    "Revise Measurement Model"
]

current_decision = st.session_state.get(
    "higher_order_measurement_decision",
    "Pending Review"
)

decision = st.selectbox(
    "Researcher Decision",
    decision_options,
    index=decision_options.index(
        current_decision
    )
)

researcher_notes = st.text_area(
    "Researcher Notes",
    value=st.session_state.get(
        "higher_order_measurement_notes",
        ""
    ),
    placeholder=(
        "Enter methodological notes, theoretical justification, "
        "indicator decisions, or reasons for retaining/reviewing items."
    )
)

if st.button(
    "💾 Save Measurement Model Decision",
    type="primary"
):

    st.session_state[
        "higher_order_measurement_decision"
    ] = decision

    st.session_state[
        "higher_order_measurement_notes"
    ] = researcher_notes

    st.success(
        "✅ Measurement model decision saved."
    )

# ============================================================
# FINAL SUMMARY
# ============================================================

st.divider()

st.header(
    "📋 Higher-Order Measurement Model Summary"
)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:

    st.write(
        f"**Higher-Order Construct:** {hoc_name}"
    )

    st.write(
        f"**HOC Measurement Type:** {hoc_type}"
    )

    st.write(
        f"**Number of Dimensions:** {len(dimensions)}"
    )

    st.write(
        f"**Total Indicators:** {total_indicators}"
    )

with summary_col2:

    st.write(
        f"**Researcher Decision:** "
        f"{st.session_state.get(
            'higher_order_measurement_decision',
            'Pending Review'
        )}"
    )

    st.write(
        "**Next Step:** Higher-Order Structural Model"
    )

# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.info(
    "📌 Methodological note: This page provides a "
    "research-support PLS-SEM-style measurement assessment. "
    "The calculations are designed to support academic analysis "
    "but should not be described as an exact reproduction of "
    "SmartPLS. Measurement specification and final indicator "
    "decisions remain the responsibility of the researcher."
)
