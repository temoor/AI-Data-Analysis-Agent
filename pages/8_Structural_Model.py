import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Structural Model",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Structural Model")

st.write(
    "Build and examine the structural model by defining "
    "relationships between constructs."
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
# CHECK CONSTRUCTS
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
        "⚠️ No constructs have been saved."
    )
    st.stop()

st.success(
    "✅ Dataset and measurement model loaded."
)

# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("📋 Model Information")

col1, col2, col3 = st.columns(3)

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

# ============================================================
# CONSTRUCT LIST
# ============================================================

construct_names = list(
    constructs.keys()
)

st.subheader(
    "🏗️ Available Constructs"
)

construct_info_rows = []

for name, information in constructs.items():

    construct_info_rows.append(
        {
            "Construct":
                name,

            "Measurement Type":
                information["type"],

            "Indicators":
                ", ".join(
                    information["items"]
                ),

            "Number of Indicators":
                len(
                    information["items"]
                )
        }
    )

construct_info_df = pd.DataFrame(
    construct_info_rows
)

st.dataframe(
    construct_info_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# SESSION STATE FOR PATHS
# ============================================================

if "structural_paths" not in st.session_state:
    st.session_state["structural_paths"] = []

if "hypothesis_counter" not in st.session_state:
    st.session_state["hypothesis_counter"] = 0

# ============================================================
# ADD PATH MANUALLY
# ============================================================

st.divider()

st.subheader(
    "➕ Add Structural Relationship"
)

st.write(
    "Select a predictor construct and an outcome construct. "
    "The website will automatically assign a hypothesis number."
)

col1, col2 = st.columns(2)

with col1:

    predictor = st.selectbox(
        "Predictor / Exogenous Construct",
        construct_names,
        key="manual_predictor"
    )

with col2:

    possible_outcomes = [
        name
        for name in construct_names
        if name != predictor
    ]

    if possible_outcomes:

        outcome = st.selectbox(
            "Outcome / Endogenous Construct",
            possible_outcomes,
            key="manual_outcome"
        )

    else:

        outcome = None

if st.button(
    "➕ Add Path",
    type="primary"
):

    if outcome is None:

        st.error(
            "❌ At least two different constructs "
            "are required."
        )

    elif predictor == outcome:

        st.error(
            "❌ A construct cannot be connected "
            "to itself."
        )

    else:

        existing_paths = [
            (
                path["Predictor"],
                path["Outcome"]
            )
            for path in st.session_state[
                "structural_paths"
            ]
        ]

        if (
            predictor,
            outcome
        ) in existing_paths:

            st.warning(
                "⚠️ This relationship has already been added."
            )

        else:

            st.session_state[
                "hypothesis_counter"
            ] += 1

            hypothesis = (
                f"H"
                f"{st.session_state['hypothesis_counter']}"
            )

            st.session_state[
                "structural_paths"
            ].append(
                {
                    "Hypothesis":
                        hypothesis,

                    "Predictor":
                        predictor,

                    "Outcome":
                        outcome
                }
            )

            st.success(
                f"✅ {hypothesis}: "
                f"{predictor} → {outcome} added."
            )

# ============================================================
# QUICK MODEL BUILDER
# ============================================================

st.divider()

st.subheader(
    "⚡ Quick Model Builder"
)

st.write(
    "Use this option when you want to create several "
    "relationships at once."
)

quick_col1, quick_col2 = st.columns(2)

with quick_col1:

    quick_predictors = st.multiselect(
        "Select Predictor Constructs",
        construct_names,
        key="quick_predictors"
    )

with quick_col2:

    quick_outcome_options = [
        name
        for name in construct_names
    ]

    quick_outcome = st.selectbox(
        "Select Common Outcome Construct",
        quick_outcome_options,
        key="quick_outcome"
    )

if st.button(
    "⚡ Add Selected Predictors → Outcome"
):

    if not quick_predictors:

        st.warning(
            "⚠️ Please select at least one predictor."
        )

    else:

        added_count = 0

        for predictor in quick_predictors:

            if predictor == quick_outcome:
                continue

            existing_paths = [
                (
                    path["Predictor"],
                    path["Outcome"]
                )
                for path in st.session_state[
                    "structural_paths"
                ]
            ]

            if (
                predictor,
                quick_outcome
            ) not in existing_paths:

                st.session_state[
                    "hypothesis_counter"
                ] += 1

                hypothesis = (
                    f"H"
                    f"{st.session_state['hypothesis_counter']}"
                )

                st.session_state[
                    "structural_paths"
                ].append(
                    {
                        "Hypothesis":
                            hypothesis,

                        "Predictor":
                            predictor,

                        "Outcome":
                            quick_outcome
                    }
                )

                added_count += 1

        if added_count > 0:

            st.success(
                f"✅ {added_count} structural "
                "relationship(s) added."
            )

        else:

            st.warning(
                "⚠️ No new relationships were added."
            )

# ============================================================
# SEQUENTIAL MODEL
# ============================================================

st.divider()

st.subheader(
    "🔗 Sequential Model Builder"
)

st.write(
    "Select constructs in order to create a simple "
    "chain model. For example: A → B → C."
)

sequence = st.multiselect(
    "Select Constructs in Model Order",
    construct_names,
    key="sequence_constructs"
)

if st.button(
    "🔗 Create Sequential Paths"
):

    if len(sequence) < 2:

        st.warning(
            "⚠️ Select at least two constructs."
        )

    else:

        added_count = 0

        for i in range(
            len(sequence) - 1
        ):

            predictor = sequence[i]
            outcome = sequence[i + 1]

            existing_paths = [
                (
                    path["Predictor"],
                    path["Outcome"]
                )
                for path in st.session_state[
                    "structural_paths"
                ]
            ]

            if (
                predictor,
                outcome
            ) not in existing_paths:

                st.session_state[
                    "hypothesis_counter"
                ] += 1

                hypothesis = (
                    f"H"
                    f"{st.session_state['hypothesis_counter']}"
                )

                st.session_state[
                    "structural_paths"
                ].append(
                    {
                        "Hypothesis":
                            hypothesis,

                        "Predictor":
                            predictor,

                        "Outcome":
                            outcome
                    }
                )

                added_count += 1

        if added_count > 0:

            st.success(
                f"✅ {added_count} sequential "
                "path(s) created."
            )

        else:

            st.warning(
                "⚠️ These paths already exist."
            )

# ============================================================
# CURRENT STRUCTURAL MODEL
# ============================================================

st.divider()

st.subheader(
    "📊 Current Structural Model"
)

paths = st.session_state[
    "structural_paths"
]

if not paths:

    st.info(
        "ℹ️ No structural relationships have been "
        "defined yet."
    )

else:

    paths_df = pd.DataFrame(
        paths
    )

    st.dataframe(
        paths_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# REMOVE PATH
# ============================================================

if paths:

    st.subheader(
        "🗑️ Remove Structural Relationship"
    )

    path_labels = []

    for path in paths:

        label = (
            f"{path['Hypothesis']}: "
            f"{path['Predictor']} → "
            f"{path['Outcome']}"
        )

        path_labels.append(
            label
        )

    selected_path = st.selectbox(
        "Select relationship to remove",
        path_labels,
        key="remove_path_selection"
    )

    if st.button(
        "🗑️ Remove Selected Path"
    ):

        selected_index = (
            path_labels.index(
                selected_path
            )
        )

        removed = st.session_state[
            "structural_paths"
        ].pop(
            selected_index
        )

        st.success(
            f"✅ Removed {removed['Hypothesis']}: "
            f"{removed['Predictor']} → "
            f"{removed['Outcome']}"
        )

        st.rerun()

# ============================================================
# CLEAR MODEL
# ============================================================

if paths:

    if st.button(
        "🧹 Clear All Structural Paths"
    ):

        st.session_state[
            "structural_paths"
        ] = []

        st.session_state[
            "hypothesis_counter"
        ] = 0

        st.success(
            "✅ All structural paths have been cleared."
        )

        st.rerun()

# ============================================================
# SAVE STRUCTURAL MODEL
# ============================================================

st.divider()

if st.button(
    "💾 Save Structural Model",
    type="primary"
):

    if not st.session_state[
        "structural_paths"
    ]:

        st.error(
            "❌ Please add at least one structural "
            "relationship before saving."
        )

    else:

        st.session_state[
            "pls_structural_paths"
        ] = (
            st.session_state[
                "structural_paths"
            ].copy()
        )

        st.success(
            "✅ Structural model saved successfully."
        )

# ============================================================
# SAVED STRUCTURAL MODEL
# ============================================================

if "pls_structural_paths" in st.session_state:

    st.divider()

    st.subheader(
        "📌 Saved Structural Model"
    )

    saved_paths_df = pd.DataFrame(
        st.session_state[
            "pls_structural_paths"
        ]
    )

    st.dataframe(
        saved_paths_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# STRUCTURAL MODEL SUMMARY
# ============================================================

if "pls_structural_paths" in st.session_state:

    saved_paths = st.session_state[
        "pls_structural_paths"
    ]

    st.divider()

    st.subheader(
        "📈 Structural Model Summary"
    )

    endogenous_constructs = list(
        dict.fromkeys(
            path["Outcome"]
            for path in saved_paths
        )
    )

    exogenous_constructs = [
        name
        for name in construct_names
        if name not in endogenous_constructs
    ]

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Structural Paths",
            len(saved_paths)
        )

    with c2:

        st.metric(
            "Endogenous Constructs",
            len(endogenous_constructs)
        )

    with c3:

        st.metric(
            "Exogenous Constructs",
            len(exogenous_constructs)
        )

# ============================================================
# RESEARCHER GUIDANCE
# ============================================================

st.divider()

st.subheader(
    "📚 Structural Model Guidance"
)

st.info(
    "ℹ️ The Structural Model page is designed as a "
    "general-purpose model builder. The researcher "
    "defines relationships based on the theoretical "
    "framework and hypotheses of the study. The software "
    "does not automatically decide which constructs "
    "should be connected."
)

st.warning(
    "⚠️ Creating a path does not mean that the hypothesis "
    "is supported. Hypothesis support is determined only "
    "after estimating the structural model and evaluating "
    "the path coefficient, standard error, t-value, "
    "p-value, confidence interval, and related criteria."
)
