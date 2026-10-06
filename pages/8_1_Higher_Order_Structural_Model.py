import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Higher-Order Structural Model",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Higher-Order Structural Model")

st.write(
    "Define the structural relationships between Higher-Order "
    "Constructs and other research constructs in the PLS-SEM model."
)

st.info(
    "This page is designed for hierarchical PLS-SEM models. "
    "Higher-Order Constructs and their dimensions are treated as "
    "a measurement hierarchy, while relationships between research "
    "constructs are specified as structural paths."
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
# CHECK HIGHER-ORDER MODELS
# ============================================================

higher_order_models = st.session_state.get(
    "pls_higher_order_models"
)


# ------------------------------------------------------------
# Backward compatibility with older single-HOC key
# ------------------------------------------------------------

if not isinstance(
    higher_order_models,
    dict
) or not higher_order_models:

    old_model = st.session_state.get(
        "pls_higher_order_model"
    )

    if isinstance(
        old_model,
        dict
    ):

        old_name = old_model.get(
            "name",
            "Higher-Order Construct"
        )

        higher_order_models = {
            old_name: old_model
        }

    else:

        st.warning(
            "⚠️ No Higher-Order Construct model was found."
        )

        st.info(
            "Please complete **2 Higher Order Construct** first."
        )

        st.stop()


# ============================================================
# CLEAN HOC MODELS
# ============================================================

clean_hoc_models = {}

for hoc_name, hoc_information in higher_order_models.items():

    if not isinstance(
        hoc_information,
        dict
    ):
        continue

    dimensions = hoc_information.get(
        "dimensions",
        {}
    )

    if not isinstance(
        dimensions,
        dict
    ):
        dimensions = {}

    clean_hoc_models[
        hoc_name
    ] = {
        "name":
            hoc_information.get(
                "name",
                hoc_name
            ),
        "type":
            hoc_information.get(
                "type",
                "Reflective"
            ),
        "dimensions":
            dimensions
    }


higher_order_models = clean_hoc_models


if not higher_order_models:

    st.error(
        "❌ No valid Higher-Order Constructs are available."
    )

    st.stop()


# ============================================================
# SIMPLE / ORDINARY CONSTRUCTS
# ============================================================

simple_constructs = st.session_state.get(
    "pls_constructs",
    {}
)

if not isinstance(
    simple_constructs,
    dict
):

    simple_constructs = {}


# ============================================================
# AVAILABLE STRUCTURAL CONSTRUCTS
# ============================================================
#
# IMPORTANT:
#
# Only HOCs and ordinary/simple constructs belong here.
#
# Dimensions such as V1D1, V1D2, V1D3 are deliberately NOT
# included because they are measurement components.
#
# ============================================================

available_constructs = []

# ------------------------------------------------------------
# Add all Higher-Order Constructs
# ------------------------------------------------------------

for hoc_name in higher_order_models.keys():

    if hoc_name not in available_constructs:

        available_constructs.append(
            hoc_name
        )


# ------------------------------------------------------------
# Add ordinary/simple constructs
# ------------------------------------------------------------

for construct_name in simple_constructs.keys():

    if construct_name not in available_constructs:

        available_constructs.append(
            construct_name
        )


# ------------------------------------------------------------
# Safety check
# ------------------------------------------------------------

if len(available_constructs) < 2:

    st.warning(
        "⚠️ At least two structural constructs are required "
        "to define a structural path."
    )


# ============================================================
# BASIC INFORMATION
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Respondents",
        df.shape[0]
    )

with col2:

    st.metric(
        "Higher-Order Constructs",
        len(higher_order_models)
    )

with col3:

    st.metric(
        "Structural Constructs",
        len(available_constructs)
    )


# ============================================================
# HIGHER-ORDER MEASUREMENT HIERARCHY
# ============================================================

st.divider()

st.subheader(
    "🏗️ Higher-Order Measurement Hierarchy"
)

st.write(
    "The following structures come from the Higher-Order "
    "Construct page. Dimensions remain part of the measurement "
    "hierarchy and are not treated as ordinary structural constructs."
)


for hoc_name, hoc_information in higher_order_models.items():

    hoc_type = hoc_information.get(
        "type",
        "Reflective"
    )

    dimensions = hoc_information.get(
        "dimensions",
        {}
    )

    st.markdown(
        f"### 🟢 {hoc_name}"
    )

    st.caption(
        f"Higher-Order Measurement Type: {hoc_type}"
    )

    for dimension_name, dimension_information in dimensions.items():

        dimension_type = dimension_information.get(
            "type",
            "Reflective"
        )

        items = dimension_information.get(
            "items",
            []
        )

        st.markdown(
            f"**⬜ {dimension_name} ({dimension_type})**"
        )

        if items:

            st.write(
                "Indicators: "
                + ", ".join(items)
            )

        else:

            st.warning(
                f"⚠️ No indicators found for {dimension_name}."
            )


# ============================================================
# STRUCTURAL CONSTRUCTS
# ============================================================

st.divider()

st.subheader(
    "🔗 Structural Model Constructs"
)

st.write(
    "Only research constructs that can participate in "
    "hypothesized structural relationships are listed here."
)

st.success(
    "Available Structural Constructs: "
    + ", ".join(available_constructs)
)


# ============================================================
# CURRENT PATH STORAGE
# ============================================================

if (
    "pls_higher_order_structural_paths"
    not in st.session_state
):

    st.session_state[
        "pls_higher_order_structural_paths"
    ] = []


paths = st.session_state[
    "pls_higher_order_structural_paths"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def path_exists(
    paths_list,
    predictor,
    outcome
):
    """
    Check whether a predictor → outcome path already exists.
    """

    for path in paths_list:

        if (
            path.get("predictor")
            == predictor
            and
            path.get("outcome")
            == outcome
        ):

            return True

    return False


def next_hypothesis_number(
    paths_list
):
    """
    Return H1, H2, H3...
    """

    return f"H{len(paths_list) + 1}"


def remove_path_by_index(
    paths_list,
    index
):
    """
    Remove one structural path.
    """

    if (
        index >= 0
        and
        index < len(paths_list)
    ):

        return (
            paths_list[:index]
            +
            paths_list[index + 1:]
        )

    return paths_list


def create_path_table(
    paths_list
):

    rows = []

    for path in paths_list:

        rows.append(
            {
                "Hypothesis":
                    path.get(
                        "hypothesis",
                        ""
                    ),

                "Predictor":
                    path.get(
                        "predictor",
                        ""
                    ),

                "Outcome":
                    path.get(
                        "outcome",
                        ""
                    )
            }
        )

    return pd.DataFrame(rows)


def make_structural_figure(
    constructs,
    paths_list
):
    """
    Create a simple structural model diagram.
    """

    fig = go.Figure()

    if not constructs:

        return fig

    n = len(constructs)

    if n == 1:

        x_positions = [0.5]

    else:

        x_positions = [
            0.08
            +
            (
                0.84
                *
                i
                /
                (n - 1)
            )
            for i in range(n)
        ]

    y_position = 0.55

    position_map = {
        construct:
            (
                x_positions[i],
                y_position
            )
        for i, construct in enumerate(
            constructs
        )
    }

    # --------------------------------------------------------
    # Draw structural arrows
    # --------------------------------------------------------

    for path in paths_list:

        predictor = path.get(
            "predictor"
        )

        outcome = path.get(
            "outcome"
        )

        if (
            predictor not in position_map
            or
            outcome not in position_map
        ):

            continue

        predictor_x, predictor_y = position_map[
            predictor
        ]

        outcome_x, outcome_y = position_map[
            outcome
        ]

        fig.add_annotation(
            x=outcome_x,
            y=outcome_y,
            ax=predictor_x,
            ay=predictor_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2,
            text=""
        )

    # --------------------------------------------------------
    # Node labels
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=x_positions,
            y=[
                y_position
                for _ in constructs
            ],
            mode="markers+text",
            marker=dict(
                size=70,
                symbol="circle",
                line=dict(
                    width=2
                )
            ),
            text=[
                f"<b>{construct}</b>"
                for construct in constructs
            ],
            textposition="middle center",
            hoverinfo="text",
            hovertext=[
                f"Construct: {construct}"
                for construct in constructs
            ],
            showlegend=False
        )
    )

    fig.update_layout(
        title={
            "text":
                "Higher-Order Structural Model",
            "x": 0.5
        },
        height=500,
        margin=dict(
            l=40,
            r=40,
            t=80,
            b=40
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

    return fig


# ============================================================
# STRUCTURAL PATH SPECIFICATION
# ============================================================

st.divider()

st.subheader(
    "🔗 Structural Path Specification"
)

st.write(
    "Specify the hypothesized relationship between a "
    "predictor construct and an outcome construct."
)


# ------------------------------------------------------------
# Add path
# ------------------------------------------------------------

st.markdown(
    "### ➕ Add Structural Path"
)

if len(available_constructs) >= 2:

    col1, col2, col3 = st.columns(
        [1, 1, 0.35]
    )

    with col1:

        predictor_construct = st.selectbox(
            "Predictor Construct",
            available_constructs,
            key="hoc_structural_predictor"
        )

    with col2:

        outcome_construct = st.selectbox(
            "Outcome Construct",
            available_constructs,
            key="hoc_structural_outcome"
        )

    with col3:

        st.write("")
        st.write("")

        add_path_clicked = st.button(
            "➕ Add Path",
            type="primary",
            key="hoc_add_path"
        )

    if add_path_clicked:

        if predictor_construct == outcome_construct:

            st.error(
                "❌ A construct cannot be used as both "
                "predictor and outcome in the same path."
            )

        elif path_exists(
            paths,
            predictor_construct,
            outcome_construct
        ):

            st.warning(
                "⚠️ This structural path already exists."
            )

        else:

            hypothesis = next_hypothesis_number(
                paths
            )

            new_path = {
                "hypothesis":
                    hypothesis,

                "predictor":
                    predictor_construct,

                "outcome":
                    outcome_construct
            }

            paths = paths + [
                new_path
            ]

            st.session_state[
                "pls_higher_order_structural_paths"
            ] = paths

            st.success(
                f"✅ {hypothesis} added: "
                f"{predictor_construct} → "
                f"{outcome_construct}"
            )

            st.rerun()

else:

    st.warning(
        "⚠️ At least two constructs are required."
    )


# ============================================================
# CURRENT STRUCTURAL PATHS
# ============================================================

st.divider()

st.subheader(
    "📋 Current Structural Paths"
)

if paths:

    path_table = create_path_table(
        paths
    )

    st.dataframe(
        path_table,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # Remove path
    # --------------------------------------------------------

    st.markdown(
        "### 🗑️ Remove Structural Path"
    )

    path_labels = []

    for i, path in enumerate(paths):

        path_labels.append(
            (
                i,
                f"{path.get('hypothesis', f'H{i+1}')}: "
                f"{path.get('predictor', '')} → "
                f"{path.get('outcome', '')}"
            )
        )

    selected_path_label = st.selectbox(
        "Select path to remove",
        path_labels,
        format_func=lambda x: x[1],
        key="hoc_remove_path_selection"
    )

    if st.button(
        "🗑️ Remove Selected Path",
        key="hoc_remove_path"
    ):

        remove_index = selected_path_label[0]

        paths = remove_path_by_index(
            paths,
            remove_index
        )

        # ----------------------------------------------------
        # Renumber hypotheses
        # ----------------------------------------------------

        for i, path in enumerate(paths):

            path["hypothesis"] = f"H{i + 1}"

        st.session_state[
            "pls_higher_order_structural_paths"
        ] = paths

        st.success(
            "✅ Structural path removed."
        )

        st.rerun()

else:

    st.info(
        "No structural paths have been added yet."
    )


# ============================================================
# QUICK MODEL BUILDER
# ============================================================

st.divider()

st.subheader(
    "⚡ Quick Structural Model Builder"
)

st.write(
    "Use this option to create several structural paths "
    "quickly. The system will use the constructs currently "
    "available in the structural model."
)

if len(available_constructs) >= 2:

    quick_predictor = st.selectbox(
        "Quick Builder Predictor",
        available_constructs,
        key="quick_hoc_predictor"
    )

    quick_outcomes = st.multiselect(
        "Quick Builder Outcomes",
        [
            construct
            for construct in available_constructs
            if construct != quick_predictor
        ],
        key="quick_hoc_outcomes"
    )

    if st.button(
        "⚡ Add Quick Structural Paths",
        key="quick_add_hoc_paths"
    ):

        if not quick_outcomes:

            st.warning(
                "⚠️ Please select at least one outcome construct."
            )

        else:

            updated_paths = paths.copy()

            added_count = 0

            for outcome in quick_outcomes:

                if not path_exists(
                    updated_paths,
                    quick_predictor,
                    outcome
                ):

                    updated_paths.append(
                        {
                            "hypothesis":
                                f"H{len(updated_paths) + 1}",

                            "predictor":
                                quick_predictor,

                            "outcome":
                                outcome
                        }
                    )

                    added_count += 1

            # Renumber
            for i, path in enumerate(
                updated_paths
            ):

                path["hypothesis"] = f"H{i + 1}"

            st.session_state[
                "pls_higher_order_structural_paths"
            ] = updated_paths

            st.success(
                f"✅ {added_count} structural path(s) added."
            )

            st.rerun()


# ============================================================
# SEQUENTIAL MODEL BUILDER
# ============================================================

st.divider()

st.subheader(
    "➡️ Sequential Structural Model Builder"
)

st.write(
    "Create a sequential chain such as "
    "Variable_1 → Variable_2 → Variable_3."
)

if len(available_constructs) >= 2:

    sequential_order = st.multiselect(
        "Select constructs in theoretical sequence",
        available_constructs,
        key="hoc_sequential_order"
    )

    if st.button(
        "➡️ Build Sequential Model",
        key="build_hoc_sequential"
    ):

        if len(sequential_order) < 2:

            st.warning(
                "⚠️ Select at least two constructs."
            )

        else:

            updated_paths = paths.copy()

            added_count = 0

            for i in range(
                len(sequential_order) - 1
            ):

                predictor = sequential_order[i]
                outcome = sequential_order[i + 1]

                if not path_exists(
                    updated_paths,
                    predictor,
                    outcome
                ):

                    updated_paths.append(
                        {
                            "hypothesis":
                                f"H{len(updated_paths) + 1}",

                            "predictor":
                                predictor,

                            "outcome":
                                outcome
                        }
                    )

                    added_count += 1

            for i, path in enumerate(
                updated_paths
            ):

                path["hypothesis"] = f"H{i + 1}"

            st.session_state[
                "pls_higher_order_structural_paths"
            ] = updated_paths

            st.success(
                f"✅ Sequential model created with "
                f"{added_count} new path(s)."
            )

            st.rerun()


# ============================================================
# STRUCTURAL MODEL DIAGRAM
# ============================================================

st.divider()

st.subheader(
    "📊 Structural Model Diagram"
)

if paths:

    structural_figure = make_structural_figure(
        available_constructs,
        paths
    )

    st.plotly_chart(
        structural_figure,
        use_container_width=True
    )

else:

    st.info(
        "Add at least one structural path to display the diagram."
    )


# ============================================================
# ENDOGENOUS / EXOGENOUS SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📊 Structural Model Summary"
)

if paths:

    endogenous = []

    exogenous = []

    for construct in available_constructs:

        is_outcome = any(
            path.get("outcome")
            == construct
            for path in paths
        )

        is_predictor = any(
            path.get("predictor")
            == construct
            for path in paths
        )

        if is_outcome:

            endogenous.append(
                construct
            )

        elif is_predictor:

            exogenous.append(
                construct
            )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Structural Paths",
            len(paths)
        )

    with col2:

        st.metric(
            "Endogenous Constructs",
            len(endogenous)
        )

    with col3:

        st.metric(
            "Exogenous Constructs",
            len(exogenous)
        )

    st.write(
        "**Endogenous Constructs:** "
        + (
            ", ".join(endogenous)
            if endogenous
            else "None"
        )
    )

    st.write(
        "**Exogenous Constructs:** "
        + (
            ", ".join(exogenous)
            if exogenous
            else "None"
        )
    )


# ============================================================
# RESEARCHER CONFIRMATION
# ============================================================

st.divider()

st.subheader(
    "🧑‍🔬 Researcher Confirmation"
)

st.write(
    "Structural paths are theory-driven hypotheses. "
    "The software does not determine which constructs should "
    "predict which other constructs."
)

if paths:

    confirm_structural_model = st.checkbox(
        "I confirm that the structural paths represent "
        "the theoretically hypothesized relationships "
        "in my research model.",
        key="confirm_hoc_structural_model"
    )

else:

    confirm_structural_model = False

    st.info(
        "Add at least one structural path before confirming the model."
    )


# ============================================================
# SAVE STRUCTURAL MODEL
# ============================================================

if st.button(
    "💾 Save Higher-Order Structural Model",
    type="primary",
    disabled=(
        not paths
        or not confirm_structural_model
    ),
    key="save_hoc_structural_model"
):

    structural_model = {
        "higher_order_models":
            higher_order_models,

        "paths":
            paths,

        "constructs":
            available_constructs,

        "confirmed":
            True
    }

    # --------------------------------------------------------
    # Main structural model key
    # --------------------------------------------------------

    st.session_state[
        "pls_higher_order_structural_model"
    ] = structural_model

    # --------------------------------------------------------
    # Explicit path key
    # --------------------------------------------------------

    st.session_state[
        "pls_higher_order_structural_paths"
    ] = paths

    st.success(
        "✅ Higher-Order Structural Model saved successfully."
    )

    st.rerun()


# ============================================================
# SAVED STRUCTURAL MODEL
# ============================================================

saved_structural_model = st.session_state.get(
    "pls_higher_order_structural_model"
)

if isinstance(
    saved_structural_model,
    dict
):

    saved_paths = saved_structural_model.get(
        "paths",
        []
    )

    if saved_paths:

        st.divider()

        st.subheader(
            "💾 Saved Higher-Order Structural Model"
        )

        st.success(
            "✅ Structural model is currently saved."
        )

        saved_table = create_path_table(
            saved_paths
        )

        st.dataframe(
            saved_table,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"**Number of Structural Paths:** "
            f"{len(saved_paths)}"
        )

        st.write(
            "**Structural Constructs:** "
            +
            ", ".join(
                saved_structural_model.get(
                    "constructs",
                    available_constructs
                )
            )
        )


# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.info(
    "📌 Methodological note: The Higher-Order Construct → "
    "Dimension → Indicator relationships represent a measurement "
    "hierarchy and are not automatically treated as structural "
    "hypotheses. Structural paths are specified separately based "
    "on the researcher's theoretical framework. This application "
    "provides research-support PLS-SEM-style functionality and "
    "should not be described as an exact reproduction of SmartPLS."
)
