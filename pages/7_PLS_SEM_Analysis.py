import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PLS-SEM Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 PLS-SEM Analysis")
st.write(
    "Set up and examine the measurement model for your questionnaire."
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

st.success("✅ Dataset loaded from Home page.")

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
        "Numeric Variables",
        len(df.select_dtypes(include="number").columns)
    )

# ============================================================
# AVAILABLE ITEMS
# ============================================================

numeric_columns = (
    df.select_dtypes(include="number")
    .columns
    .tolist()
)

if not numeric_columns:
    st.error(
        "❌ No numeric questionnaire items were detected."
    )
    st.stop()

st.subheader("📝 Available Questionnaire Items")

st.write(
    "Numeric variables available for measurement-model analysis:"
)

st.dataframe(
    pd.DataFrame(
        {"Questionnaire Item": numeric_columns}
    ),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# CONSTRUCT SETUP
# ============================================================

st.divider()

st.subheader("🏗️ Construct Setup")

st.write(
    "Define the constructs and select the questionnaire items "
    "belonging to each construct."
)

# Number of constructs

number_of_constructs = st.number_input(
    "Number of Constructs",
    min_value=1,
    max_value=30,
    value=3,
    step=1
)

constructs = {}

for i in range(int(number_of_constructs)):

    st.markdown(
        f"### Construct {i + 1}"
    )

    col1, col2 = st.columns([1, 2])

    with col1:

        construct_name = st.text_input(
            "Construct Name",
            value=f"Construct {i + 1}",
            key=f"construct_name_{i}"
        )

    with col2:

        selected_items = st.multiselect(
            "Select Questionnaire Items",
            numeric_columns,
            key=f"construct_items_{i}"
        )

    measurement_type = st.selectbox(
        "Measurement Type",
        [
            "Reflective",
            "Formative"
        ],
        key=f"measurement_type_{i}"
    )

    constructs[construct_name] = {
        "items": selected_items,
        "type": measurement_type
    }

# ============================================================
# SAVE MODEL
# ============================================================

st.divider()

if st.button(
    "💾 Save Measurement Model",
    type="primary"
):

    valid_constructs = {}

    for name, information in constructs.items():

        if information["items"]:

            valid_constructs[name] = information

    if not valid_constructs:

        st.error(
            "❌ Please select at least one item for a construct."
        )

    else:

        st.session_state[
            "pls_constructs"
        ] = valid_constructs

        st.success(
            "✅ Measurement model setup saved."
        )


# ============================================================
# SHOW SAVED MODEL
# ============================================================

if "pls_constructs" in st.session_state:

    st.divider()

    st.subheader(
        "📊 Current Measurement Model"
    )

    saved_constructs = (
        st.session_state["pls_constructs"]
    )

    model_rows = []

    for name, information in saved_constructs.items():

        model_rows.append(
            {
                "Construct": name,
                "Measurement Type": information["type"],
                "Number of Indicators": len(
                    information["items"]
                ),
                "Indicators": ", ".join(
                    information["items"]
                )
            }
        )

    model_df = pd.DataFrame(
        model_rows
    )

    st.dataframe(
        model_df,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# DESCRIPTIVE INDICATOR INFORMATION
# ============================================================

if "pls_constructs" in st.session_state:

    st.divider()

    st.subheader(
        "📈 Indicator Information"
    )

    selected_all_items = []

    for information in (
        st.session_state[
            "pls_constructs"
        ].values()
    ):

        selected_all_items.extend(
            information["items"]
        )

    selected_all_items = list(
        dict.fromkeys(
            selected_all_items
        )
    )

    if selected_all_items:

        indicator_rows = []

        for item in selected_all_items:

            series = pd.to_numeric(
                df[item],
                errors="coerce"
            )

            indicator_rows.append(
                {
                    "Indicator": item,
                    "Valid Responses": int(
                        series.notna().sum()
                    ),
                    "Missing": int(
                        series.isna().sum()
                    ),
                    "Mean": round(
                        series.mean(),
                        3
                    ),
                    "Standard Deviation": round(
                        series.std(),
                        3
                    ),
                    "Minimum": series.min(),
                    "Maximum": series.max()
                }
            )

        indicator_df = pd.DataFrame(
            indicator_rows
        )

        st.dataframe(
            indicator_df,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# MEASUREMENT MODEL STATUS
# ============================================================

if "pls_constructs" in st.session_state:

    st.divider()

    st.subheader(
        "🔎 Measurement Model Status"
    )

    for name, information in (
        st.session_state[
            "pls_constructs"
        ].items()
    ):

        number_items = len(
            information["items"]
        )

        if number_items >= 3:

            st.success(
                f"✅ {name}: "
                f"{number_items} indicators selected."
            )

        elif number_items == 2:

            st.warning(
                f"⚠️ {name}: only 2 indicators selected. "
                "Review the construct specification."
            )

        elif number_items == 1:

            st.warning(
                f"⚠️ {name}: only 1 indicator selected. "
                "Review the construct specification."
            )

        else:

            st.error(
                f"❌ {name}: no indicators selected."
            )

# ============================================================
# NOTE
# ============================================================

st.divider()

st.info(
    "ℹ️ This is the measurement-model setup stage. "
    "The researcher specifies the constructs, indicators, "
    "and measurement type before reliability and validity "
    "statistics are calculated."
)
