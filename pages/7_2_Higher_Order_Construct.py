import streamlit as st
import pandas as pd
import re

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Higher-Order Construct Setup",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Higher-Order Construct Setup")

st.write(
    "Set up a higher-order construct using existing construct/dimension "
    "information where available. Manual configuration is provided only "
    "when the required theoretical structure is not already available."
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
# AVAILABLE NUMERIC ITEMS
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
    st.metric("Numeric Items", len(numeric_columns))

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_name(value):
    """Normalize a name for comparison."""
    if value is None:
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(value).lower()
    )


def find_existing_dimension_model():
    """
    Look for existing dimension/construct information already
    stored in the application session.
    """

    # --------------------------------------------------------
    # 1. Existing Higher-Order Model
    # --------------------------------------------------------

    if "pls_higher_order_model" in st.session_state:

        model = st.session_state["pls_higher_order_model"]

        if isinstance(model, dict):
            if model.get("dimensions"):
                return model

    # --------------------------------------------------------
    # 2. Existing Simple PLS Constructs
    # --------------------------------------------------------

    if "pls_constructs" in st.session_state:

        constructs = st.session_state["pls_constructs"]

        if isinstance(constructs, dict) and constructs:

            return {
                "name": "",
                "type": "Reflective",
                "dimensions": {
                    name: {
                        "items": info.get("items", []),
                        "type": info.get("type", "Reflective")
                    }
                    for name, info in constructs.items()
                    if isinstance(info, dict)
                    and info.get("items")
                }
            }

    return None


# ============================================================
# DETECT EXISTING MODEL
# ============================================================

existing_model = find_existing_dimension_model()

# ============================================================
# MODEL STRUCTURE
# ============================================================

st.divider()

st.subheader("🔍 Model Structure")

if existing_model and existing_model.get("dimensions"):

    st.success(
        "✅ Existing construct/dimension information was found "
        "in the current PLS-SEM session."
    )

    st.info(
        "The system will use the existing dimensions and indicators "
        "instead of asking you to enter them again."
    )

else:

    st.warning(
        "⚠️ No existing dimension structure was found in the current session."
    )

    st.write(
        "If your research theory already defines dimensions, you can "
        "configure them below. The software will not invent theoretical "
        "dimension names from indicator codes."
    )

# ============================================================
# EXISTING STRUCTURE
# ============================================================

if existing_model and existing_model.get("dimensions"):

    st.divider()

    st.subheader("📚 Existing Dimensions Detected")

    detected_rows = []

    for dimension_name, information in (
        existing_model["dimensions"].items()
    ):

        detected_rows.append(
            {
                "Dimension": dimension_name,
                "Measurement Type": information.get(
                    "type",
                    "Reflective"
                ),
                "Indicators": ", ".join(
                    information.get("items", [])
                ),
                "Number of Indicators": len(
                    information.get("items", [])
                )
            }
        )

    detected_df = pd.DataFrame(detected_rows)

    st.dataframe(
        detected_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # HOC NAME
    # --------------------------------------------------------

    st.subheader("🏗️ Higher-Order Construct")

    saved_hoc_name = existing_model.get("name", "")

    if not saved_hoc_name:

        saved_hoc_name = st.text_input(
            "Higher-Order Construct Name",
            value="Environmental Factors",
            key="hoc_new_name"
        )

    else:

        st.text_input(
            "Higher-Order Construct Name",
            value=saved_hoc_name,
            disabled=True,
            key="hoc_detected_name"
        )

    # --------------------------------------------------------
    # HOC TYPE
    # --------------------------------------------------------

    existing_hoc_type = existing_model.get(
        "type",
        "Reflective"
    )

    hoc_type = st.selectbox(
        "Higher-Order Construct Measurement Type",
        [
            "Reflective",
            "Formative"
        ],
        index=(
            0
            if existing_hoc_type == "Reflective"
            else 1
        ),
        key="hoc_detected_type"
    )

    # --------------------------------------------------------
    # CONFIRM DETECTED MODEL
    # --------------------------------------------------------

    st.divider()

    st.subheader("✅ Researcher Confirmation")

    st.write(
        "Please confirm that the detected dimensions and indicators "
        "represent your theoretical higher-order construct."
    )

    confirm_model = st.checkbox(
        "I confirm that these dimensions and indicators are theoretically correct.",
        key="confirm_detected_hoc"
    )

    if st.button(
        "💾 Save Detected Higher-Order Model",
        type="primary",
        disabled=not confirm_model
    ):

        final_name = (
            saved_hoc_name.strip()
            if saved_hoc_name
            else "Higher-Order Construct"
        )

        higher_order_model = {
            "name": final_name,
            "type": hoc_type,
            "dimensions": existing_model["dimensions"]
        }

        st.session_state[
            "pls_higher_order_model"
        ] = higher_order_model

        st.success(
            "✅ Higher-Order Construct model saved successfully."
        )

        st.rerun()

# ============================================================
# MANUAL FALLBACK
# ============================================================

else:

    st.divider()

    st.subheader("🛠️ Manual Higher-Order Model Setup")

    st.info(
        "Manual setup is required because the current session does not "
        "contain dimension information."
    )

    # --------------------------------------------------------
    # HOC NAME
    # --------------------------------------------------------

    hoc_name = st.text_input(
        "Higher-Order Construct Name",
        value="",
        placeholder="Example: Environmental Factors",
        key="hoc_manual_name"
    )

    # --------------------------------------------------------
    # HOC TYPE
    # --------------------------------------------------------

    hoc_type = st.selectbox(
        "Higher-Order Construct Measurement Type",
        [
            "Reflective",
            "Formative"
        ],
        key="hoc_manual_type"
    )

    # --------------------------------------------------------
    # NUMBER OF DIMENSIONS
    # --------------------------------------------------------

    number_of_dimensions = st.number_input(
        "Number of Dimensions",
        min_value=1,
        max_value=30,
        value=3,
        step=1,
        key="hoc_manual_number_dimensions"
    )

    st.divider()

    st.subheader("📚 Dimension Setup")

    st.write(
        "Enter the dimension names and select the indicators belonging "
        "to each dimension."
    )

    dimensions = {}

    for i in range(int(number_of_dimensions)):

        st.markdown(
            f"### Dimension {i + 1}"
        )

        dimension_name = st.text_input(
            "Dimension Name",
            placeholder=f"Example: Dimension {i + 1}",
            key=f"hoc_manual_dimension_name_{i}"
        )

        dimension_type = st.selectbox(
            "Dimension Measurement Type",
            [
                "Reflective",
                "Formative"
            ],
            key=f"hoc_manual_dimension_type_{i}"
        )

        selected_items = st.multiselect(
            "Select Questionnaire Indicators",
            numeric_columns,
            key=f"hoc_manual_dimension_items_{i}"
        )

        if dimension_name.strip():

            dimensions[
                dimension_name.strip()
            ] = {
                "items": selected_items,
                "type": dimension_type
            }

    # ========================================================
    # SAVE MANUAL MODEL
    # ========================================================

    st.divider()

    if st.button(
        "💾 Save Higher-Order Construct Model",
        type="primary",
        key="save_manual_hoc"
    ):

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not hoc_name.strip():

            st.error(
                "❌ Please enter a Higher-Order Construct name."
            )

            st.stop()

        if not dimensions:

            st.error(
                "❌ Please enter at least one dimension name."
            )

            st.stop()

        # ----------------------------------------------------
        # EMPTY DIMENSIONS
        # ----------------------------------------------------

        empty_dimensions = []

        for dimension_name, information in dimensions.items():

            if not information["items"]:

                empty_dimensions.append(
                    dimension_name
                )

        if empty_dimensions:

            st.error(
                "❌ The following dimensions have no indicators:"
            )

            for dimension in empty_dimensions:

                st.write(
                    f"• {dimension}"
                )

            st.stop()

        # ----------------------------------------------------
        # DUPLICATE INDICATORS
        # ----------------------------------------------------

        used_items = {}
        duplicate_items = []

        for dimension_name, information in dimensions.items():

            for item in information["items"]:

                if item in used_items:

                    duplicate_items.append(
                        (
                            item,
                            used_items[item],
                            dimension_name
                        )
                    )

                else:

                    used_items[item] = dimension_name

        if duplicate_items:

            st.error(
                "❌ The same questionnaire indicator has been "
                "assigned to more than one dimension."
            )

            for (
                item,
                first_dimension,
                second_dimension
            ) in duplicate_items:

                st.write(
                    f"• **{item}** → "
                    f"{first_dimension} and "
                    f"{second_dimension}"
                )

            st.stop()

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        higher_order_model = {
            "name": hoc_name.strip(),
            "type": hoc_type,
            "dimensions": dimensions
        }

        st.session_state[
            "pls_higher_order_model"
        ] = higher_order_model

        st.success(
            "✅ Higher-Order Construct model saved successfully."
        )

        st.rerun()

# ============================================================
# DISPLAY SAVED HIGHER-ORDER MODEL
# ============================================================

if "pls_higher_order_model" in st.session_state:

    st.divider()

    st.subheader(
        "📊 Current Higher-Order Construct Model"
    )

    saved_model = st.session_state[
        "pls_higher_order_model"
    ]

    st.markdown(
        f"### {saved_model['name']}"
    )

    st.write(
        f"**Higher-Order Measurement Type:** "
        f"{saved_model['type']}"
    )

    model_rows = []

    for dimension_name, information in (
        saved_model["dimensions"].items()
    ):

        model_rows.append(
            {
                "Higher-Order Construct":
                    saved_model["name"],

                "HOC Type":
                    saved_model["type"],

                "Dimension":
                    dimension_name,

                "Dimension Type":
                    information["type"],

                "Number of Indicators":
                    len(information["items"]),

                "Indicators":
                    ", ".join(
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

    # ========================================================
    # MODEL TREE
    # ========================================================

    st.divider()

    st.subheader(
        "🌳 Model Structure"
    )

    st.markdown(
        f"### {saved_model['name']}"
    )

    st.markdown(
        f"Measurement Type: **{saved_model['type']}**"
    )

    for dimension_name, information in (
        saved_model["dimensions"].items()
    ):

        st.markdown(
            f"**↳ {dimension_name}** "
            f"({information['type']})"
        )

        for item in information["items"]:

            st.write(
                f"　↳ {item}"
            )

    # ========================================================
    # INDICATOR INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "📈 Dimension Indicator Information"
    )

    indicator_rows = []

    for dimension_name, information in (
        saved_model["dimensions"].items()
    ):

        for item in information["items"]:

            if item not in df.columns:
                continue

            series = pd.to_numeric(
                df[item],
                errors="coerce"
            )

            indicator_rows.append(
                {
                    "Dimension":
                        dimension_name,

                    "Indicator":
                        item,

                    "Valid Responses":
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

                    "Standard Deviation":
                        round(
                            series.std(),
                            3
                        ),

                    "Minimum":
                        series.min(),

                    "Maximum":
                        series.max()
                }
            )

    if indicator_rows:

        indicator_df = pd.DataFrame(
            indicator_rows
        )

        st.dataframe(
            indicator_df,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # MODEL STATUS
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 Higher-Order Model Status"
    )

    st.success(
        f"✅ Higher-Order Construct: "
        f"{saved_model['name']}"
    )

    st.success(
        f"✅ Dimensions defined: "
        f"{len(saved_model['dimensions'])}"
    )

    for dimension_name, information in (
        saved_model["dimensions"].items()
    ):

        item_count = len(
            information["items"]
        )

        if item_count >= 3:

            st.success(
                f"✅ {dimension_name}: "
                f"{item_count} indicators."
            )

        elif item_count == 2:

            st.warning(
                f"⚠️ {dimension_name}: only 2 indicators. "
                "Review the specification."
            )

        elif item_count == 1:

            st.warning(
                f"⚠️ {dimension_name}: only 1 indicator. "
                "Review the specification."
            )

        else:

            st.error(
                f"❌ {dimension_name}: no indicators."
            )

# ============================================================
# METHODOLOGICAL NOTE
# ============================================================

st.divider()

st.subheader(
    "📚 Methodological Note"
)

st.info(
    "A higher-order construct is a theory-driven hierarchical "
    "measurement structure. The software can reuse an existing "
    "construct/dimension specification, but it should not invent "
    "theoretical dimensions merely from indicator names."
)

st.warning(
    "⚠️ Saving the higher-order structure does not by itself "
    "establish reliability, validity, or statistical significance. "
    "The higher-order measurement model must be evaluated using "
    "appropriate PLS-SEM procedures."
)
