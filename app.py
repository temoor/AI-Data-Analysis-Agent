import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
from io import BytesIO


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="🏠",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================
st.title("🤖 AI Data Analysis Agent")

st.markdown("""
Welcome to the **AI Data Analysis Agent**.

Upload an Excel (.xlsx) or CSV (.csv) file to analyse your data.
""")


# ==========================================
# FILE UPLOAD
# ==========================================
uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV",
    type=["csv", "xlsx"],
    key="main_dataset_uploader"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_signature = hashlib.sha256(file_bytes).hexdigest()
    previous_signature = st.session_state.get("dataset_signature")

    # Only parse/reset when a genuinely different file is uploaded.
    # This prevents ordinary reruns from repeatedly clearing the
    # detected workbook structure.
    if file_signature != previous_signature:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(BytesIO(file_bytes))
                sheet_names = []
                questionnaire_sheet = None
                structure_sheet = None
                st.session_state.pop("pls_structure", None)
                st.session_state["excel_sheet_names"] = []
                st.session_state["excel_structure_detected"] = False
            else:
                excel_file = pd.ExcelFile(BytesIO(file_bytes))
                sheet_names = excel_file.sheet_names

                preferred_questionnaire_names = [
                    "Questionnaire_Data", "Questionnaire Data",
                    "Data", "Dataset", "Survey_Data", "Survey Data"
                ]
                questionnaire_sheet = next(
                    (name for name in preferred_questionnaire_names
                     if name in sheet_names),
                    sheet_names[0] if sheet_names else None
                )
                if questionnaire_sheet is None:
                    st.error("The uploaded Excel workbook contains no worksheets.")
                    st.stop()

                df = pd.read_excel(
                    BytesIO(file_bytes),
                    sheet_name=questionnaire_sheet
                )

                preferred_structure_names = [
                    "PLS_SEM_Structure", "PLS-SEM_Structure",
                    "PLS SEM Structure", "PLS-SEM Structure",
                    "SEM_Structure", "SEM Structure",
                    "Model_Structure", "Model Structure"
                ]
                structure_sheet = next(
                    (name for name in preferred_structure_names
                     if name in sheet_names),
                    None
                )

                if structure_sheet is not None:
                    structure_df = pd.read_excel(
                        BytesIO(file_bytes),
                        sheet_name=structure_sheet
                    ).dropna(how="all").dropna(axis=1, how="all")

                    # Standardise common spreadsheet header variants so
                    # all analysis pages receive the same schema.
                    structure_aliases = {
                        "higherorderconstruct": "Higher_Order_Construct",
                        "higherorderconstructname": "Higher_Order_Construct",
                        "higherorder": "Higher_Order_Construct",
                        "hoc": "Higher_Order_Construct",
                        "construct": "Higher_Order_Construct",
                        "dimension": "Dimension",
                        "dimensionname": "Dimension",
                        "measurementtype": "Measurement_Type",
                        "measurement": "Measurement_Type",
                        "type": "Measurement_Type",
                        "indicator": "Indicator",
                        "item": "Indicator",
                        "questionnaireitem": "Indicator",
                    }
                    structure_rename = {}
                    for column in structure_df.columns:
                        normalised = "".join(
                            char.lower() for char in str(column).strip()
                            if char.isalnum()
                        )
                        if normalised in structure_aliases:
                            structure_rename[column] = structure_aliases[normalised]
                    structure_df = structure_df.rename(columns=structure_rename)

                    st.session_state["pls_structure"] = structure_df
                    st.session_state["excel_structure_detected"] = True
                else:
                    st.session_state.pop("pls_structure", None)
                    st.session_state["excel_structure_detected"] = False

                st.session_state["excel_sheet_names"] = sheet_names

            # A different dataset invalidates models/results linked to
            # the previous dataset. Clear them to avoid analysing stale items.
            dataset_dependent_keys = [
                "pls_constructs", "pls_structural_paths",
                "pls_higher_order_model", "pls_higher_order_models",
                "pls_higher_order_structural_model",
                "pls_higher_order_structural_paths",
                "measurement_model_decisions",
                "higher_order_measurement_decisions",
                "content_validity_results", "content_validity_decisions",
                "data_quality_results", "reliability_results",
                "eda_results", "mediation_results"
            ]
            for key in dataset_dependent_keys:
                st.session_state.pop(key, None)

            st.session_state["df"] = df
            st.session_state["dataset_signature"] = file_signature
            st.session_state["dataset_file_name"] = uploaded_file.name
            st.session_state["dataset_questionnaire_sheet"] = questionnaire_sheet
            st.session_state["dataset_structure_sheet"] = structure_sheet

        except Exception as exc:
            st.error(f"Could not read the uploaded dataset: {exc}")
            st.stop()

    # Always read the active dataset from session state.
    df = st.session_state["df"]
    st.success(
        f"✅ Dataset active: **{st.session_state.get('dataset_file_name', uploaded_file.name)}**. "
        "You can move between analysis pages without uploading it again."
    )

    if uploaded_file.name.lower().endswith(".xlsx"):
        st.header("📚 Excel Workbook Information")
        st.write("**Available Sheets:**")
        st.write(st.session_state.get("excel_sheet_names", []))
        st.write(
            "**Questionnaire Data Sheet:** "
            f"{st.session_state.get('dataset_questionnaire_sheet')}"
        )
        structure_sheet = st.session_state.get("dataset_structure_sheet")
        if structure_sheet:
            st.success(f"✅ PLS-SEM Structure Sheet: {structure_sheet}")
        else:
            st.info(
                "No dedicated PLS-SEM structure sheet was found. "
                "You can define and save your model in the PLS-SEM pages."
            )

    if "pls_structure" in st.session_state:
        st.header("🏗️ Detected PLS-SEM Structure")
        st.dataframe(
            st.session_state["pls_structure"],
            use_container_width=True,
            hide_index=True
        )

    st.header("👀 Dataset Preview")
    st.dataframe(df, use_container_width=True)

    st.header("📊 Dataset Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])

    st.write("### Column Names")
    st.write(list(df.columns))

elif "df" in st.session_state:
    # Keep the already loaded dataset visible after navigation/reruns.
    df = st.session_state["df"]
    st.success(
        f"✅ Existing dataset is still active: "
        f"**{st.session_state.get('dataset_file_name', 'Uploaded dataset')}** "
        f"({df.shape[0]} respondents, {df.shape[1]} variables)."
    )
    st.info(
        "You do not need to upload the same file again when moving between "
        "analysis pages. Upload a different file only to start a new analysis."
    )
    with st.expander("👀 View active dataset"):
        st.dataframe(df.head(20), use_container_width=True)
else:
    st.info(
        "Upload your Excel or CSV dataset once. The dataset will remain "
        "available to the other analysis pages during this active app session."
    )
