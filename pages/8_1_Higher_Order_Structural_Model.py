
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
    "Constructs and other constructs in the PLS-SEM model."
)

st.info(
    "This page is designed for hierarchical PLS-SEM models. "
    "The Higher-Order Construct and its dimensions are treated "
    "as a measurement hierarchy, while relationships between "
    "research constructs are specified as structural paths."
)

# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:

    st.warning(
        "⚠️ Please upload your questionnaire dataset on the Home page first."
    )

    st.stop()

df = st.session_state["df"]

# ============================================================
# CHECK HIGHER-ORDER MODEL
# ============================================================

if "pls_higher_order_model" not in st.session_state:

    st.warning(
        "⚠️ No Higher-Order Construct model has been saved yet."
    )

    st.info(
        "Please complete the Higher-Order Construct page first."
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
        "Higher-Order Construct",
        hoc_name
    )

with col3:
    st.metric(
        "Dimensions",
        len(dimensions)
    )

# ============================================================
# HIGHER-ORDER MODEL
# ============================================================

st.divider()

st.header("🏗️ Higher-Order Measurement Hierarchy")

st.write(
    "The following structure comes from the Higher-Order Construct page."
)

st.markdown(
    f"### 🟢 {hoc_name}"
)

st.caption(
    f"Higher-Order Measurement Type: {hoc_type}"
)

for dimension_name, information in dimensions.items():

    dimension_type = information.get(
        "type",
        "Reflective"
    )

    items = information.get(
        "items",
        []
    )

    st.markdown(
        f"**⬜ {dimension_name}** "
        f"({dimension_type})"
    )

    if items:

        st.write(
            "Indicators: "
            + ", ".join(items)
        )

# ============================================================
# AVAILABLE CONSTRUCTS
# ============================================================

st.divider()

st.header("🧩 Structural Constructs")

st.write(
    "Select the constructs that participate in the structural model."
)

available_constructs = []

# Existing simple PLS constructs
if "pls_constructs" in st.session_state:

    existing_constructs = st.session_state[
        "pls_constructs"
    ]

    if isinstance(
        existing_constructs,
        dict
    ):

        available_constructs.extend(
            list(
                existing_constructs.keys()
            )
        )

# Add HOC
if hoc_name not in available_constructs:

    available_constructs.append(
        hoc_name
    )

# Add dimensions if desired for structural specification
for dimension_name in dimensions.keys():

    if dimension_name not in available_constructs:

        available_constructs.append(
            dimension_name
        )

available_constructs = list(
    dict.fromkeys(
        available_constructs
    )
)

if not available_constructs:

    st.error(
        "❌ No constructs are available for structural modelling."
    )

    st.stop()

st.write(
    "**Available Constructs:**"
)

st.write(
    ", ".join(
        available_constructs
    )
)

# ============================================================
# STRUCTURAL MODEL PATHS
# ============================================================

st.divider()

st.header("🔗 Structural Path Specification")

st.write(
    "Specify the hypothesized relationship between a predictor "
    "construct and an outcome construct."
)

# ============================================================
# INITIALIZE PATH STATE
# ============================================================

if "higher_order_structural_paths" not in st.session_state:

    st.session_state[
        "higher_order_structural_paths"
    ] = []

paths = st.session_state[
    "higher_order_structural_paths"
]

# ============================================================
# ADD PATH
# ============================================================

st.subheader("➕ Add Structural Path")

col1, col2, col3 = st.columns(
    [2, 2, 1]
)

with col1:

    predictor = st.selectbox(
        "Predictor Construct",
        available_constructs,
        key="hoc_predictor"
    )

with col2:

    possible_outcomes = [
        construct
        for construct in available_constructs
        if construct != predictor
    ]

    if possible_outcomes:

        outcome = st.selectbox(
            "Outcome Construct",
            possible_outcomes,
            key="hoc_outcome"
        )

    else:

        outcome = None

with col3:

    st.write("")
    st.write("")

    add_path = st.button(
        "➕ Add Path",
        type="primary",
        key="add_hoc_path"
    )

if add_path and outcome:

    duplicate = False

    for path in paths:

        if (
            path["predictor"] == predictor
            and
            path["outcome"] == outcome
        ):

            duplicate = True

    if duplicate:

        st.warning(
            "⚠️ This structural path already exists."
        )

    else:

        hypothesis_number = len(
            paths
        ) + 1

        new_path = {
            "hypothesis":
                f"H{hypothesis_number}",
            "predictor":
                predictor,
            "outcome":
                outcome
        }

        paths.append(
            new_path
        )

        st.session_state[
            "higher_order_structural_paths"
        ] = paths

        st.success(
            f"✅ H{hypothesis_number} added: "
            f"{predictor} → {outcome}"
        )

        st.rerun()

# ============================================================
# CURRENT PATHS
# ============================================================

st.divider()

st.subheader(
    "📋 Current Structural Paths"
)

if paths:

    path_table = pd.DataFrame(
        paths
    )

    path_table.columns = [
        "Hypothesis",
        "Predictor",
        "Outcome"
    ]

    st.dataframe(
        path_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No structural paths have been added yet."
    )

# ============================================================
# REMOVE PATH
# ============================================================

if paths:

    st.subheader(
        "🗑️ Remove Structural Path"
    )

    path_labels = [
        (
            f"{path['hypothesis']}: "
            f"{path['predictor']} → "
            f"{path['outcome']}"
        )
        for path in paths
    ]

    selected_path = st.selectbox(
        "Select Path to Remove",
        path_labels,
        key="remove_hoc_path"
    )

    if st.button(
        "🗑️ Remove Selected Path",
        key="remove_selected_hoc_path"
    ):

        selected_index = path_labels.index(
            selected_path
        )

        paths.pop(
            selected_index
        )

        # Renumber hypotheses
        for index, path in enumerate(
            paths
        ):

            path["hypothesis"] = (
                f"H{index + 1}"
            )

        st.session_state[
            "higher_order_structural_paths"
        ] = paths

        st.success(
            "✅ Structural path removed."
        )

        st.rerun()

# ============================================================
# CLEAR ALL
# ============================================================

if paths:

    if st.button(
        "🧹 Clear All Structural Paths",
        key="clear_hoc_paths"
    ):

        st.session_state[
            "higher_order_structural_paths"
        ] = []

        st.success(
            "✅ All structural paths cleared."
        )

        st.rerun()

# ============================================================
# QUICK MODEL BUILDER
# ============================================================

st.divider()

st.header(
    "⚡ Quick Structural Model Builder"
)

st.write(
    "Use this option when you already know the sequence "
    "of your hypothesized relationships."
)

quick_predictors = st.multiselect(
    "Select Predictor Constructs",
    available_constructs,
    key="quick_hoc_predictors"
)

quick_outcome = st.selectbox(
    "Select Common Outcome Construct",
    available_constructs,
    key="quick_hoc_outcome"
)

if st.button(
    "⚡ Build Quick Model",
    key="build_quick_hoc_model"
):

    if not quick_predictors:

        st.warning(
            "⚠️ Select at least one predictor."
        )

    else:

        added = 0

        for predictor in quick_predictors:

            if predictor == quick_outcome:
                continue

            duplicate = any(
                path["predictor"] == predictor
                and
                path["outcome"] == quick_outcome
                for path in paths
            )

            if not duplicate:

                paths.append(
                    {
                        "hypothesis":
                            f"H{len(paths) + 1}",
                        "predictor":
                            predictor,
                        "outcome":
                            quick_outcome
                    }
                )

                added += 1

        st.session_state[
            "higher_order_structural_paths"
        ] = paths

        if added:

            st.success(
                f"✅ {added} structural path(s) added."
            )

        else:

            st.info(
                "No new paths were added."
            )

        st.rerun()

# ============================================================
# SEQUENTIAL MODEL BUILDER
# ============================================================

st.divider()

st.header(
    "➡️ Sequential Model Builder"
)

st.write(
    "Build a chain such as:"
)

st.code(
    "Construct A → Construct B → Construct C"
)

sequence = st.multiselect(
    "Select Constructs in Structural Sequence",
    available_constructs,
    key="hoc_sequence"
)

if st.button(
    "➡️ Build Sequential Model",
    key="build_hoc_sequence"
):

    if len(sequence) < 2:

        st.warning(
            "⚠️ Select at least two constructs."
        )

    else:

        added = 0

        for i in range(
            len(sequence) - 1
        ):

            predictor = sequence[i]
            outcome = sequence[i + 1]

            duplicate = any(
                path["predictor"] == predictor
                and
                path["outcome"] == outcome
                for path in paths
            )

            if not duplicate:

                paths.append(
                    {
                        "hypothesis":
                            f"H{len(paths) + 1}",
                        "predictor":
                            predictor,
                        "outcome":
                            outcome
                    }
                )

                added += 1

        st.session_state[
            "higher_order_structural_paths"
        ] = paths

        st.success(
            f"✅ {added} sequential path(s) added."
        )

        st.rerun()

# ============================================================
# MODEL DIAGRAM
# ============================================================

st.divider()

st.header(
    "📊 Structural Model Diagram"
)

if paths:

    # --------------------------------------------------------
    # Determine constructs used in structural paths
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    node_positions = {}

    number_of_nodes = len(
        structural_constructs
    )

    if number_of_nodes == 1:

        x_positions = [0.5]

    else:

        x_positions = [
            0.10 +
            (
                0.80 *
                i /
                (number_of_nodes - 1)
            )
            for i in range(
                number_of_nodes
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

    fig = go.Figure()

    # --------------------------------------------------------
    # Draw paths first
    # --------------------------------------------------------

    for path in paths:

        predictor = path[
            "predictor"
        ]

        outcome = path[
            "outcome"
        ]

        x1, y1 = node_positions[
            predictor
        ]

        x2, y2 = node_positions[
            outcome
        ]

        fig.add_annotation(
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
            text=path[
                "hypothesis"
            ]
        )

    # --------------------------------------------------------
    # Node labels
    # --------------------------------------------------------

    node_text = []

    for construct in structural_constructs:

        if construct == hoc_name:

            node_text.append(
                f"<b>{construct}</b><br>"
                f"Higher-Order Construct"
            )

        elif construct in dimensions:

            node_text.append(
                f"<b>{construct}</b><br>"
                f"Dimension"
            )

        else:

            node_text.append(
                f"<b>{construct}</b><br>"
                f"Construct"
            )

    node_sizes = []

    for construct in structural_constructs:

        if construct == hoc_name:

            node_sizes.append(
                80
            )

        else:

            node_sizes.append(
                65
            )

    fig.add_trace(
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
                size=node_sizes,
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

    fig.update_layout(
        title={
            "text":
                "Higher-Order Structural Model",
            "x": 0.5
        },
        height=600,
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
        fig,
        use_container_width=True
    )

else:

    st.info(
        "Add at least one structural path to display the model diagram."
    )

# ============================================================
# STRUCTURAL MODEL SUMMARY
# ============================================================

st.divider()

st.header(
    "📋 Structural Model Summary"
)

if paths:

    endogenous = list(
        dict.fromkeys(
            path["outcome"]
            for path in paths
        )
    )

    exogenous = [
        construct
        for construct in structural_constructs
        if construct not in endogenous
    ]

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            "Structural Paths",
            len(paths)
        )

    with summary_col2:

        st.metric(
            "Endogenous Constructs",
            len(endogenous)
        )

    with summary_col3:

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

else:

    st.info(
        "No structural paths have been defined."
    )

# ============================================================
# HIGHER-ORDER CONSTRUCT RELATIONSHIP NOTE
# ============================================================

st.divider()

st.header(
    "📌 Higher-Order Construct Interpretation"
)

st.info(
    f"The Higher-Order Construct **{hoc_name}** contains "
    f"{len(dimensions)} dimension(s). The relationships between "
    "the HOC and its dimensions belong to the measurement model. "
    "The structural model should contain theoretical relationships "
    "between research constructs."
)

st.warning(
    "⚠️ Do not interpret HOC → Dimension relationships as ordinary "
    "hypotheses unless your theoretical model specifically requires "
    "such a structural interpretation. In hierarchical PLS-SEM, "
    "these relationships are generally part of the higher-order "
    "measurement specification."
)

# ============================================================
# RESEARCHER CONFIRMATION
# ============================================================

st.divider()

st.header(
    "🧑‍🔬 Researcher Confirmation"
)

confirm_structure = st.checkbox(
    "I confirm that the structural paths and hypotheses "
    "represent my theoretical research model.",
    key="confirm_higher_order_structural_model"
)

researcher_notes = st.text_area(
    "Researcher Notes",
    placeholder=(
        "Enter theoretical justification, hypothesis notes, "
        "or other methodological comments."
    ),
    key="higher_order_structural_notes"
)

# ============================================================
# SAVE STRUCTURAL MODEL
# ============================================================

if st.button(
    "💾 Save Higher-Order Structural Model",
    type="primary",
    disabled=not confirm_structure,
    key="save_higher_order_structural_model"
):

    if not paths:

        st.error(
            "❌ Please define at least one structural path."
        )

    else:

        structural_model = {
            "higher_order_construct":
                hoc_name,
            "higher_order_type":
                hoc_type,
            "dimensions":
                dimensions,
            "paths":
                paths,
            "researcher_notes":
                researcher_notes
        }

        st.session_state[
            "pls_higher_order_structural_model"
        ] = structural_model

        # Also save a compatible path structure
        st.session_state[
            "pls_higher_order_structural_paths"
        ] = paths

        st.success(
            "✅ Higher-Order Structural Model saved successfully."
        )

# ============================================================
# SAVED MODEL STATUS
# ============================================================

if "pls_higher_order_structural_model" in st.session_state:

    saved_structural_model = st.session_state[
        "pls_higher_order_structural_model"
    ]

    st.divider()

    st.subheader(
        "✅ Saved Higher-Order Structural Model"
    )

    st.write(
        f"**Higher-Order Construct:** "
        f"{saved_structural_model['higher_order_construct']}"
    )

    st.write(
        f"**Structural Paths:** "
        f"{len(saved_structural_model['paths'])}"
    )

    saved_path_table = pd.DataFrame(
        saved_structural_model[
            "paths"
        ]
    )

    st.dataframe(
        saved_path_table,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.info(
    "📌 Methodological note: This page provides a "
    "research-support structural-model builder. Path coefficients, "
    "R², f², bootstrapping, Q², and hypothesis testing should be "
    "calculated on the subsequent PLS-SEM Results page. The software "
    "should not be described as an exact SmartPLS replacement."
)
