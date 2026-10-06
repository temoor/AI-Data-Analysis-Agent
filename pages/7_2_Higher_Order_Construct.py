import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Higher-Order Construct",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Higher-Order Construct")
st.write(
    "Define and confirm a hierarchical PLS-SEM measurement structure "
    "in which a Higher-Order Construct (HOC) contains multiple dimensions, "
    "and each dimension is measured by questionnaire indicators."
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
# NUMERIC QUESTIONNAIRE ITEMS
# ============================================================

numeric_columns = df.select_dtypes(
    include=["number"]
).columns.tolist()

if not numeric_columns:
    st.error(
        "❌ No numeric questionnaire indicators were detected."
    )
    st.stop()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    """Convert a value to clean text."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_name(value):
    """Normalize names for comparison."""
    return re.sub(
        r"[^a-z0-9]+",
        "",
        clean_text(value).lower()
    )


def clean_structure_dataframe(structure_df):
    """
    Clean the PLS-SEM structure sheet.
    Expected columns:
    Higher_Order_Construct
    Dimension
    Measurement_Type
    Indicator
    """

    if structure_df is None or structure_df.empty:
        return None

    structure_df = structure_df.copy()

    # Clean column names
    structure_df.columns = [
        clean_text(col)
        for col in structure_df.columns
    ]

    # Allow common alternative column names
    rename_map = {}

    for col in structure_df.columns:
        normalized = normalize_name(col)

        if normalized in [
            "higherorderconstruct",
            "higherorder",
            "hoc",
            "higherorderconstructname"
        ]:
            rename_map[col] = "Higher_Order_Construct"

        elif normalized in [
            "dimension",
            "dimensionname"
        ]:
            rename_map[col] = "Dimension"

        elif normalized in [
            "measurementtype",
            "type",
            "measurement"
        ]:
            rename_map[col] = "Measurement_Type"

        elif normalized in [
            "indicator",
            "item",
            "question",
            "questioncode",
            "indicatoritem"
        ]:
            rename_map[col] = "Indicator"

    structure_df = structure_df.rename(
        columns=rename_map
    )

    required_columns = [
        "Higher_Order_Construct",
        "Dimension",
        "Measurement_Type",
        "Indicator"
    ]

    missing = [
        col
        for col in required_columns
        if col not in structure_df.columns
    ]

    if missing:
        return None

    structure_df = structure_df[
        required_columns
    ].copy()

    for col in required_columns:
        structure_df[col] = structure_df[col].apply(
            clean_text
        )

    structure_df = structure_df[
        (
            structure_df["Higher_Order_Construct"] != ""
        )
        & (
            structure_df["Dimension"] != ""
        )
        & (
            structure_df["Indicator"] != ""
        )
    ]

    if structure_df.empty:
        return None

    structure_df["Measurement_Type"] = (
        structure_df["Measurement_Type"]
        .replace("", "Reflective")
    )

    structure_df["Measurement_Type"] = (
        structure_df["Measurement_Type"]
        .apply(
            lambda x:
            "Formative"
            if normalize_name(x) == "formative"
            else "Reflective"
        )
    )

    return structure_df


def structure_from_excel():
    """
    Read the structure detected by app.py.
    """

    structure_df = st.session_state.get(
        "pls_structure"
    )

    return clean_structure_dataframe(
        structure_df
    )


def structure_from_existing_constructs():
    """
    Convert the existing simple PLS-SEM construct
    structure into dimensions.

    Existing structure:
        Construct -> Indicators

    Converted structure:
        Higher-Order Construct
             -> Construct/Dimension
                  -> Indicators
    """

    constructs = st.session_state.get(
        "pls_constructs"
    )

    if not isinstance(constructs, dict):
        return None

    if not constructs:
        return None

    rows = []

    for construct_name, information in constructs.items():

        if not isinstance(information, dict):
            continue

        items = information.get(
            "items",
            []
        )

        measurement_type = information.get(
            "type",
            "Reflective"
        )

        if not items:
            continue

        for item in items:

            rows.append(
                {
                    "Higher_Order_Construct":
                        "Higher-Order Construct",
                    "Dimension":
                        construct_name,
                    "Measurement_Type":
                        measurement_type,
                    "Indicator":
                        item
                }
            )

    if not rows:
        return None

    return pd.DataFrame(rows)


def build_model_from_structure(structure_df):
    """
    Convert structure dataframe into:
    HOC -> Dimensions -> Indicators
    """

    model = {}

    for _, row in structure_df.iterrows():

        hoc = clean_text(
            row["Higher_Order_Construct"]
        )

        dimension = clean_text(
            row["Dimension"]
        )

        measurement_type = clean_text(
            row["Measurement_Type"]
        )

        indicator = clean_text(
            row["Indicator"]
        )

        if not hoc or not dimension or not indicator:
            continue

        if hoc not in model:
            model[hoc] = {
                "dimensions": {},
                "hoc_type": "Reflective"
            }

        if dimension not in model[hoc]["dimensions"]:

            model[hoc]["dimensions"][dimension] = {
                "items": [],
                "type": measurement_type
            }

        if indicator not in model[hoc]["dimensions"][dimension]["items"]:

            model[hoc]["dimensions"][dimension]["items"].append(
                indicator
            )

    return model


def validate_structure(model):
    """
    Validate the hierarchical model.
    """

    errors = []
    warnings = []

    if not model:
        errors.append(
            "No higher-order construct structure was found."
        )
        return errors, warnings

    all_items = []

    for hoc_name, hoc_information in model.items():

        dimensions = hoc_information.get(
            "dimensions",
            {}
        )

        if not dimensions:
            errors.append(
                f"'{hoc_name}' has no dimensions."
            )
            continue

        if len(dimensions) < 2:
            warnings.append(
                f"'{hoc_name}' currently has only one dimension. "
                "A higher-order construct normally requires multiple dimensions."
            )

        for dimension_name, dimension_information in dimensions.items():

            items = dimension_information.get(
                "items",
                []
            )

            if not items:
                errors.append(
                    f"Dimension '{dimension_name}' has no indicators."
                )

            for item in items:

                if item not in df.columns:
                    errors.append(
                        f"Indicator '{item}' is not present in the uploaded dataset."
                    )

                all_items.append(
                    (
                        item,
                        dimension_name
                    )
                )

    # Duplicate indicator check
    indicator_locations = {}

    for item, dimension_name in all_items:

        if item not in indicator_locations:
            indicator_locations[item] = []

        indicator_locations[item].append(
            dimension_name
        )

    for item, locations in indicator_locations.items():

        unique_locations = list(
            dict.fromkeys(locations)
        )

        if len(unique_locations) > 1:
            errors.append(
                f"Indicator '{item}' is assigned to multiple dimensions: "
                + ", ".join(unique_locations)
            )

    return errors, warnings


def make_hoc_figure(
    hoc_name,
    hoc_type,
    dimensions
):
    """
    Create a SmartPLS-inspired hierarchical
    measurement model figure.

    HOC
      ↓
    Dimensions
      ↓
    Indicators
    """

    fig = go.Figure()

    dimension_names = list(
        dimensions.keys()
    )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    hoc_x = 0.5
    hoc_y = 1.0

    dimension_y = 0.62
    indicator_y = 0.20

    # Spread dimensions horizontally
    if len(dimension_names) == 1:
        dimension_positions = [0.5]
    else:
        dimension_positions = [
            0.12 + (
                0.76 * i / (len(dimension_names) - 1)
            )
            for i in range(
                len(dimension_names)
            )
        ]

    # --------------------------------------------------------
    # Indicator positions
    # --------------------------------------------------------

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

        dim_x = dimension_positions[i]

        if len(items) == 1:

            positions = [dim_x]

        else:

            spread = min(
                0.22,
                0.06 * len(items)
            )

            start = dim_x - spread / 2
            end = dim_x + spread / 2

            positions = [
                start + (
                    (end - start) * j /
                    (len(items) - 1)
                )
                for j in range(
                    len(items)
                )
            ]

        for item, x_position in zip(
            items,
            positions
        ):

            indicator_positions[
                item
            ] = x_position

    # --------------------------------------------------------
    # Edges: HOC -> Dimensions
    # --------------------------------------------------------

    for i, dimension_name in enumerate(
        dimension_names
    ):

        dim_x = dimension_positions[i]

        fig.add_annotation(
            x=dim_x,
            y=dimension_y + 0.055,
            ax=hoc_x,
            ay=hoc_y - 0.055,
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

    # --------------------------------------------------------
    # Edges: Dimensions -> Indicators
    # --------------------------------------------------------

    for i, dimension_name in enumerate(
        dimension_names
    ):

        dim_x = dimension_positions[i]

        items = dimensions[
            dimension_name
        ].get(
            "items",
            []
        )

        for item in items:

            item_x = indicator_positions[
                item
            ]

            fig.add_annotation(
                x=item_x,
                y=indicator_y + 0.045,
                ax=dim_x,
                ay=dimension_y - 0.055,
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

    # --------------------------------------------------------
    # HOC node
    # --------------------------------------------------------

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
                f"<b>{hoc_name}</b><br>"
                f"{hoc_type}"
            ],
            textposition="middle center",
            hoverinfo="text",
            hovertext=[
                f"Higher-Order Construct: {hoc_name}<br>"
                f"Measurement Type: {hoc_type}"
            ],
            showlegend=False
        )
    )

    # --------------------------------------------------------
    # Dimension nodes
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=dimension_positions,
            y=[
                dimension_y
                for _ in dimension_names
            ],
            mode="markers+text",
            marker=dict(
                size=58,
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
            hoverinfo="text",
            hovertext=[
                (
                    f"Dimension: {name}<br>"
                    f"Measurement Type: "
                    f"{dimensions[name].get('type', 'Reflective')}"
                )
                for name in dimension_names
            ],
            showlegend=False
        )
    )

    # --------------------------------------------------------
    # Indicator nodes
    # --------------------------------------------------------

    all_indicator_names = []
    all_indicator_x = []

    for dimension_name in dimension_names:

        for item in dimensions[
            dimension_name
        ].get(
            "items",
            []
        ):

            all_indicator_names.append(
                item
            )

            all_indicator_x.append(
                indicator_positions[item]
            )

    fig.add_trace(
        go.Scatter(
            x=all_indicator_x,
            y=[
                indicator_y
                for _ in all_indicator_names
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
                for item in all_indicator_names
            ],
            textposition="bottom center",
            hoverinfo="text",
            hovertext=[
                f"Indicator: {item}"
                for item in all_indicator_names
            ],
            showlegend=False
        )
    )

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    figure_height = max(
        600,
        480 + (
            len(all_indicator_names) * 8
        )
    )

    fig.update_layout(
        title={
            "text":
                "SmartPLS-Inspired Higher-Order Measurement Model",
            "x": 0.5
        },
        height=figure_height,
        margin=dict(
            l=40,
            r=40,
            t=90,
            b=40
        ),
        xaxis=dict(
            visible=False,
            range=[0, 1]
        ),
        yaxis=dict(
            visible=False,
            range=[0, 1.12]
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest"
    )

    return fig


# ============================================================
# DATASET INFORMATION
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
        "Variables",
        df.shape[1]
    )

with col3:
    st.metric(
        "Numeric Items",
        len(numeric_columns)
    )

# ============================================================
# DETECT MODEL STRUCTURE
# ============================================================

st.divider()

st.subheader("🔍 Model Structure Detection")

excel_structure = structure_from_excel()

existing_construct_structure = (
    structure_from_existing_constructs()
)

detected_source = None
detected_structure = None

if excel_structure is not None:

    detected_structure = excel_structure
    detected_source = "Excel PLS-SEM Structure"

elif existing_construct_structure is not None:

    detected_structure = existing_construct_structure
    detected_source = "Existing PLS-SEM Constructs"

# ============================================================
# AUTOMATIC DETECTION
# ============================================================

if detected_structure is not None:

    detected_model = build_model_from_structure(
        detected_structure
    )

    if detected_model:

        st.success(
            f"✅ A model structure was detected from: "
            f"**{detected_source}**"
        )

        st.info(
            "The software has detected a possible hierarchical "
            "measurement structure. Please review and confirm it "
            "before using it for PLS-SEM analysis."
        )

        # ----------------------------------------------------
        # HOC SELECTION
        # ----------------------------------------------------

        hoc_names = list(
            detected_model.keys()
        )

        selected_hoc = st.selectbox(
            "Select Higher-Order Construct to Review",
            hoc_names,
            key="detected_hoc_selection"
        )

        selected_information = detected_model[
            selected_hoc
        ]

        dimensions = selected_information[
            "dimensions"
        ]

        # ----------------------------------------------------
        # HOC TYPE
        # ----------------------------------------------------

        existing_saved_model = st.session_state.get(
            "pls_higher_order_model"
        )

        default_hoc_type = "Reflective"

        if (
            isinstance(
                existing_saved_model,
                dict
            )
            and existing_saved_model.get("name")
            == selected_hoc
        ):

            default_hoc_type = existing_saved_model.get(
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
                if default_hoc_type == "Reflective"
                else 1
            ),
            key="detected_hoc_type"
        )

        # ----------------------------------------------------
        # DETECTED TABLE
        # ----------------------------------------------------

        st.subheader(
            "📚 Detected Dimensions and Indicators"
        )

        detected_rows = []

        for dimension_name, information in dimensions.items():

            for item in information.get(
                "items",
                []
            ):

                detected_rows.append(
                    {
                        "Higher-Order Construct":
                            selected_hoc,
                        "Dimension":
                            dimension_name,
                        "Measurement Type":
                            information.get(
                                "type",
                                "Reflective"
                            ),
                        "Indicator":
                            item,
                        "Indicator Exists":
                            "Yes"
                            if item in df.columns
                            else "No"
                    }
                )

        detected_table = pd.DataFrame(
            detected_rows
        )

        st.dataframe(
            detected_table,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # VALIDATE DETECTED MODEL
        # ----------------------------------------------------

        validation_model = {
            selected_hoc: {
                "dimensions": dimensions
            }
        }

        errors, warnings = validate_structure(
            validation_model
        )

        if errors:

            st.error(
                "❌ Please correct the following issues:"
            )

            for error in errors:
                st.write(
                    f"• {error}"
                )

        if warnings:

            st.warning(
                "⚠️ Please review:"
            )

            for warning in warnings:
                st.write(
                    f"• {warning}"
                )

        # ----------------------------------------------------
        # RESEARCHER CONFIRMATION
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "✅ Researcher Confirmation"
        )

        st.write(
            "Higher-order constructs are theory-driven. "
            "The software can detect the structure from your "
            "Excel model sheet, but the researcher must confirm "
            "that the dimensions and indicators are theoretically correct."
        )

        confirm_model = st.checkbox(
            "I confirm that the detected Higher-Order Construct, "
            "dimensions, indicators, and measurement specification "
            "are theoretically correct.",
            key="confirm_detected_hoc"
        )

        if st.button(
            "💾 Save Confirmed Higher-Order Model",
            type="primary",
            disabled=(
                not confirm_model
                or bool(errors)
            ),
            key="save_detected_hoc"
        ):

            higher_order_model = {
                "name": selected_hoc,
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
# MANUAL FALLBACK
# ============================================================

else:

    st.warning(
        "⚠️ No Excel PLS-SEM dimension structure was detected. "
        "Manual higher-order model setup is available."
    )

    st.info(
        "If your research theory defines dimensions, enter them "
        "manually below. The software will not invent theoretical "
        "dimensions from indicator names."
    )

    # --------------------------------------------------------
    # HOC NAME
    # --------------------------------------------------------

    hoc_name = st.text_input(
        "Higher-Order Construct Name",
        placeholder="Example: Environmental Factors",
        key="manual_hoc_name"
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
        key="manual_hoc_type"
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
        key="manual_hoc_number_dimensions"
    )

    st.divider()

    dimensions = {}

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    for i in range(
        int(number_of_dimensions)
    ):

        st.markdown(
            f"### Dimension {i + 1}"
        )

        dimension_name = st.text_input(
            "Dimension Name",
            placeholder=(
                f"Example: Dimension {i + 1}"
            ),
            key=f"manual_dimension_name_{i}"
        )

        dimension_type = st.selectbox(
            "Dimension Measurement Type",
            [
                "Reflective",
                "Formative"
            ],
            key=f"manual_dimension_type_{i}"
        )

        selected_items = st.multiselect(
            "Select Questionnaire Indicators",
            numeric_columns,
            key=f"manual_dimension_items_{i}"
        )

        if dimension_name.strip():

            dimensions[
                dimension_name.strip()
            ] = {
                "items": selected_items,
                "type": dimension_type
            }

    # --------------------------------------------------------
    # SAVE MANUAL MODEL
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "💾 Save Higher-Order Construct Model",
        type="primary",
        key="save_manual_hoc"
    ):

        if not hoc_name.strip():

            st.error(
                "❌ Please enter a Higher-Order Construct name."
            )
            st.stop()

        if not dimensions:

            st.error(
                "❌ Please define at least one dimension."
            )
            st.stop()

        empty_dimensions = []

        for dimension_name, information in dimensions.items():

            if not information.get("items"):

                empty_dimensions.append(
                    dimension_name
                )

        if empty_dimensions:

            st.error(
                "❌ The following dimensions have no indicators:"
            )

            for dimension_name in empty_dimensions:

                st.write(
                    f"• {dimension_name}"
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
# DISPLAY SAVED MODEL
# ============================================================

if "pls_higher_order_model" in st.session_state:

    saved_model = st.session_state[
        "pls_higher_order_model"
    ]

    st.divider()

    st.subheader(
        "🌳 Confirmed Higher-Order Model"
    )

    st.success(
        f"✅ Higher-Order Construct: "
        f"**{saved_model['name']}**"
    )

    st.write(
        f"Measurement Type: "
        f"**{saved_model['type']}**"
    )

    # --------------------------------------------------------
    # MODEL TABLE
    # --------------------------------------------------------

    model_rows = []

    for dimension_name, information in saved_model[
        "dimensions"
    ].items():

        for item in information.get(
            "items",
            []
        ):

            model_rows.append(
                {
                    "Higher-Order Construct":
                        saved_model["name"],
                    "Dimension":
                        dimension_name,
                    "Measurement Type":
                        information.get(
                            "type",
                            "Reflective"
                        ),
                    "Indicator":
                        item
                }
            )

    if model_rows:

        st.dataframe(
            pd.DataFrame(model_rows),
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # MODEL TREE
    # ========================================================

    st.divider()

    st.subheader(
        "🌳 Hierarchical Model Structure"
    )

    st.markdown(
        f"### 🟢 {saved_model['name']}"
    )

    st.caption(
        f"Higher-Order Measurement Type: "
        f"{saved_model['type']}"
    )

    for dimension_name, information in saved_model[
        "dimensions"
    ].items():

        st.markdown(
            f"**⬜ {dimension_name}** "
            f"({information.get('type', 'Reflective')})"
        )

        for item in information.get(
            "items",
            []
        ):

            st.markdown(
                f"&nbsp;&nbsp;&nbsp;&nbsp;↳ 🔵 {item}",
                unsafe_allow_html=True
            )

    # ========================================================
    # GRAPHICAL HIGHER-ORDER MODEL
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Graphical Higher-Order Measurement Model"
    )

    st.info(
        "This is a SmartPLS-inspired visualization of the "
        "hierarchical measurement structure. It shows the "
        "Higher-Order Construct → Dimensions → Indicators."
    )

    figure = make_hoc_figure(
        saved_model["name"],
        saved_model["type"],
        saved_model["dimensions"]
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    # ========================================================
    # INDICATOR INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "📈 Dimension Indicator Information"
    )

    indicator_rows = []

    for dimension_name, information in saved_model[
        "dimensions"
    ].items():

        for item in information.get(
            "items",
            []
        ):

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
                        int(series.notna().sum()),
                    "Missing":
                        int(series.isna().sum()),
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

    if indicator_rows:

        st.dataframe(
            pd.DataFrame(indicator_rows),
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

    validation_model = {
        saved_model["name"]: {
            "dimensions":
                saved_model["dimensions"]
        }
    }

    errors, warnings = validate_structure(
        validation_model
    )

    if errors:

        st.error(
            "❌ Model requires attention."
        )

        for error in errors:

            st.write(
                f"• {error}"
            )

    else:

        st.success(
            f"✅ Higher-Order Construct: "
            f"{saved_model['name']}"
        )

        st.success(
            f"✅ Number of Dimensions: "
            f"{len(saved_model['dimensions'])}"
        )

        total_indicators = sum(
            len(
                information.get(
                    "items",
                    []
                )
            )
            for information in saved_model[
                "dimensions"
            ].values()
        )

        st.success(
            f"✅ Total Indicators: "
            f"{total_indicators}"
        )

    if warnings:

        st.warning(
            "⚠️ Researcher Review"
        )

        for warning in warnings:

            st.write(
                f"• {warning}"
            )

    # ========================================================
    # METHODOLOGICAL NOTE
    # ========================================================

    st.divider()

    st.info(
        "📌 Methodological note: A higher-order construct is "
        "a theory-driven hierarchical measurement structure. "
        "The software does not determine whether the HOC or "
        "its dimensions should be reflective or formative. "
        "These measurement specifications must be justified "
        "by the researcher's theoretical framework and research design. "
        "Statistical assessment is performed in the subsequent "
        "Higher-Order Measurement Model page."
    )
