import streamlit as st
import pandas as pd

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
    "Define a higher-order construct, its dimensions, and the "
    "questionnaire indicators belonging to each dimension."
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
        "Numeric Items",
        len(numeric_columns)
    )

# ============================================================
# MODEL STRUCTURE
# ============================================================

st.divider()

st.subheader("🔍 Model Structure")

st.info(
    "This page is used when a researcher has a hierarchical "
    "measurement structure in which a higher-order construct "
    "is represented by multiple dimensions, and each dimension "
    "is measured by questionnaire indicators."
)

st.markdown(
    """
**Example**

**Environmental Factors**  
↓  
**Environmental Regulation** → EP1, EP2, EP3, EP4, EP5  
**Carbon Footprint** → EP6, EP7, EP8, EP9, EP10  
**Waste Management** → EP11, EP12, EP13, EP14, EP15
"""
)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "hoc_name_input" not in st.session_state:

    if "pls_higher_order_model" in st.session_state:

        st.session_state["hoc_name_input"] = (
            st.session_state[
                "pls_higher_order_model"
            ].get(
                "name",
                "Higher-Order Construct"
            )
        )

    else:

        st.session_state[
            "hoc_name_input"
        ] = "Higher-Order Construct"


if "hoc_type_input" not in st.session_state:

    if "pls_higher_order_model" in st.session_state:

        saved_type = (
            st.session_state[
                "pls_higher_order_model"
            ].get(
                "type",
                "Reflective"
            )
        )

        st.session_state[
            "hoc_type_input"
        ] = saved_type

    else:

        st.session_state[
            "hoc_type_input"
        ] = "Reflective"


if "hoc_number_dimensions" not in st.session_state:

    if "pls_higher_order_model" in st.session_state:

        saved_dimensions = (
            st.session_state[
                "pls_higher_order_model"
            ].get(
                "dimensions",
                {}
            )
        )

        st.session_state[
            "hoc_number_dimensions"
        ] = max(
            1,
            len(saved_dimensions)
        )

    else:

        st.session_state[
            "hoc_number_dimensions"
        ] = 3

# ============================================================
# HIGHER-ORDER CONSTRUCT SETUP
# ============================================================

st.divider()

st.subheader("🏗️ Higher-Order Construct")

hoc_name = st.text_input(
    "Higher-Order Construct Name",
    key="hoc_name_input",
    help=(
        "Enter the name of the main construct that "
        "contains multiple dimensions."
    )
)

hoc_type = st.selectbox(
    "Higher-Order Construct Measurement Type",
    [
        "Reflective",
        "Formative"
    ],
    key="hoc_type_input",
    help=(
        "Select the theoretical measurement type of "
        "the higher-order construct."
    )
)

number_of_dimensions = st.number_input(
    "Number of Dimensions",
    min_value=1,
    max_value=30,
    step=1,
    key="hoc_number_dimensions"
)

# ============================================================
# LOAD SAVED DIMENSION INFORMATION
# ============================================================

saved_dimensions = {}

if "pls_higher_order_model" in st.session_state:

    saved_dimensions = (
        st.session_state[
            "pls_higher_order_model"
        ].get(
            "dimensions",
            {}
        )
    )

# ============================================================
# DIMENSION SETUP
# ============================================================

st.divider()

st.subheader("📚 Dimension Setup")

st.write(
    "Enter a meaningful name for every dimension and select "
    "the questionnaire indicators belonging to that dimension."
)

dimensions = {}

for i in range(
    int(number_of_dimensions)
):

    st.markdown(
        f"### Dimension {i + 1}"
    )

    # --------------------------------------------------------
    # Default values
    # --------------------------------------------------------

    if i < len(saved_dimensions):

        saved_dimension_names = list(
            saved_dimensions.keys()
        )

        saved_dimension_name = (
            saved_dimension_names[i]
        )

        saved_dimension_information = (
            saved_dimensions[
                saved_dimension_name
            ]
        )

        default_dimension_name = (
            saved_dimension_name
        )

        default_dimension_type = (
            saved_dimension_information.get(
                "type",
                "Reflective"
            )
        )

        default_dimension_items = (
            saved_dimension_information.get(
                "items",
                []
            )
        )

    else:

        default_dimension_name = (
            f"Dimension {i + 1}"
        )

        default_dimension_type = (
            "Reflective"
        )

        default_dimension_items = []

    # --------------------------------------------------------
    # Persistent dimension name
    # --------------------------------------------------------

    dimension_name_key = (
        f"hoc_dimension_name_{i}"
    )

    if dimension_name_key not in st.session_state:

        st.session_state[
            dimension_name_key
        ] = default_dimension_name

    dimension_name = st.text_input(
        "Dimension Name",
        key=dimension_name_key,
        help=(
            "Enter the actual theoretical name of "
            "this dimension."
        )
    ).strip()

    # --------------------------------------------------------
    # Persistent measurement type
    # --------------------------------------------------------

    dimension_type_key = (
        f"hoc_dimension_type_{i}"
    )

    if dimension_type_key not in st.session_state:

        st.session_state[
            dimension_type_key
        ] = default_dimension_type

    dimension_type = st.selectbox(
        "Dimension Measurement Type",
        [
            "Reflective",
            "Formative"
        ],
        key=dimension_type_key
    )

    # --------------------------------------------------------
    # Persistent indicator selection
    # --------------------------------------------------------

    dimension_items_key = (
        f"hoc_dimension_items_{i}"
    )

    if dimension_items_key not in st.session_state:

        valid_saved_items = [
            item
            for item in default_dimension_items
            if item in numeric_columns
        ]

        st.session_state[
            dimension_items_key
        ] = valid_saved_items

    selected_items = st.multiselect(
        "Select Questionnaire Indicators",
        numeric_columns,
        key=dimension_items_key
    )

    # --------------------------------------------------------
    # Store current dimension
    # --------------------------------------------------------

    if dimension_name:

        dimensions[
            dimension_name
        ] = {
            "items": selected_items,
            "type": dimension_type
        }

# ============================================================
# SAVE HIGHER-ORDER MODEL
# ============================================================

st.divider()

if st.button(
    "💾 Save Higher-Order Construct Model",
    type="primary"
):

    valid_dimensions = {}

    for dimension_name, information in (
        dimensions.items()
    ):

        clean_name = dimension_name.strip()

        if clean_name and information["items"]:

            valid_dimensions[
                clean_name
            ] = {
                "items": information["items"],
                "type": information["type"]
            }

    # --------------------------------------------------------
    # VALIDATION: HOC NAME
    # --------------------------------------------------------

    if not hoc_name.strip():

        st.error(
            "❌ Please enter a Higher-Order Construct name."
        )

    # --------------------------------------------------------
    # VALIDATION: DIMENSIONS
    # --------------------------------------------------------

    elif not valid_dimensions:

        st.error(
            "❌ Please define at least one dimension "
            "with questionnaire indicators."
        )

    # --------------------------------------------------------
    # VALIDATION: DUPLICATE DIMENSION NAMES
    # --------------------------------------------------------

    elif len(valid_dimensions) != len(
        [
            name
            for name in dimensions.keys()
            if name.strip()
        ]
    ):

        st.error(
            "❌ Each dimension must have a unique name."
        )

    else:

        # ----------------------------------------------------
        # CHECK DUPLICATE INDICATORS
        # ----------------------------------------------------

        duplicate_items = []

        used_items = {}

        for dimension_name, information in (
            valid_dimensions.items()
        ):

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

                    used_items[item] = (
                        dimension_name
                    )

        if duplicate_items:

            st.error(
                "❌ The same questionnaire indicator "
                "has been assigned to more than one dimension."
            )

            for (
                item,
                first_dimension,
                second_dimension
            ) in duplicate_items:

                st.write(
                    f"• **{item}** is assigned to "
                    f"**{first_dimension}** and "
                    f"**{second_dimension}**."
                )

        else:

            # ------------------------------------------------
            # SAVE MODEL
            # ------------------------------------------------

            higher_order_model = {

                "name":
                    hoc_name.strip(),

                "type":
                    hoc_type,

                "dimensions":
                    valid_dimensions
            }

            st.session_state[
                "pls_higher_order_model"
            ] = higher_order_model

            # ------------------------------------------------
            # Synchronize persistent inputs
            # ------------------------------------------------

            st.session_state[
                "hoc_name_input"
            ] = hoc_name.strip()

            st.session_state[
                "hoc_type_input"
            ] = hoc_type

            st.success(
                "✅ Higher-Order Construct model "
                "saved successfully."
            )

# ============================================================
# SHOW SAVED MODEL
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

    for (
        dimension_name,
        information
    ) in saved_model[
        "dimensions"
    ].items():

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
                    len(
                        information["items"]
                    ),

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

# ============================================================
# MODEL STRUCTURE DISPLAY
# ============================================================

if "pls_higher_order_model" in st.session_state:

    st.divider()

    st.subheader(
        "🌳 Model Structure"
    )

    saved_model = st.session_state[
        "pls_higher_order_model"
    ]

    st.markdown(
        f"### **{saved_model['name']}**"
    )

    st.markdown(
        f"Measurement Type: "
        f"**{saved_model['type']}**"
    )

    for (
        dimension_name,
        information
    ) in saved_model[
        "dimensions"
    ].items():

        st.markdown(
            f"**↳ {dimension_name}** "
            f"({information['type']})"
        )

        for item in information["items"]:

            st.write(
                f"　↳ {item}"
            )

# ============================================================
# DIMENSION INDICATOR INFORMATION
# ============================================================

if "pls_higher_order_model" in st.session_state:

    st.divider()

    st.subheader(
        "📈 Dimension Indicator Information"
    )

    saved_model = st.session_state[
        "pls_higher_order_model"
    ]

    indicator_rows = []

    for (
        dimension_name,
        information
    ) in saved_model[
        "dimensions"
    ].items():

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

# ============================================================
# MODEL STATUS
# ============================================================

if "pls_higher_order_model" in st.session_state:

    st.divider()

    st.subheader(
        "🔎 Higher-Order Model Status"
    )

    saved_model = st.session_state[
        "pls_higher_order_model"
    ]

    st.success(
        f"✅ Higher-Order Construct: "
        f"{saved_model['name']}"
    )

    st.success(
        f"✅ Dimensions defined: "
        f"{len(saved_model['dimensions'])}"
    )

    for (
        dimension_name,
        information
    ) in saved_model[
        "dimensions"
    ].items():

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
    "This page defines the hierarchical measurement structure "
    "for a higher-order construct. Selecting Reflective or "
    "Formative measurement type is a researcher/theory-driven "
    "decision. The software does not automatically determine "
    "the correct measurement specification."
)

st.warning(
    "⚠️ Saving a higher-order model on this page does not "
    "automatically establish statistical validity. The "
    "higher-order measurement model must be evaluated using "
    "appropriate PLS-SEM procedures before research conclusions "
    "are made."
)
