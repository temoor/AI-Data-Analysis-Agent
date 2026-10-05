import streamlit as st
import pandas as pd
import plotly.express as px


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
    type=["csv", "xlsx"]
)


if uploaded_file is not None:

    # ======================================
    # RESET OLD STRUCTURE INFORMATION
    # ======================================
    # This prevents an old Excel structure
    # from remaining when a new file is uploaded.

    st.session_state.pop(
        "pls_structure",
        None
    )

    st.session_state.pop(
        "excel_sheet_names",
        None
    )

    st.session_state.pop(
        "excel_structure_detected",
        None
    )


    # ======================================
    # READ CSV FILE
    # ======================================

    if uploaded_file.name.lower().endswith(".csv"):

        df = pd.read_csv(
            uploaded_file
        )

        st.session_state["df"] = df

        st.info(
            "ℹ️ CSV file detected. "
            "No Excel PLS-SEM structure sheet is available."
        )


    # ======================================
    # READ EXCEL FILE
    # ======================================

    else:

        # Read the workbook so that we can
        # access all sheets.

        excel_file = pd.ExcelFile(
            uploaded_file
        )

        sheet_names = excel_file.sheet_names

        # Save sheet names for other pages
        st.session_state[
            "excel_sheet_names"
        ] = sheet_names


        # ==================================
        # FIND QUESTIONNAIRE SHEET
        # ==================================

        questionnaire_sheet = None

        preferred_questionnaire_names = [
            "Questionnaire_Data",
            "Questionnaire Data",
            "Data",
            "Dataset",
            "Survey_Data",
            "Survey Data"
        ]

        for preferred_name in preferred_questionnaire_names:

            if preferred_name in sheet_names:

                questionnaire_sheet = preferred_name

                break


        # ==================================
        # IF NO STANDARD NAME IS FOUND
        # USE FIRST SHEET
        # ==================================

        if questionnaire_sheet is None:

            questionnaire_sheet = sheet_names[0]


        # ==================================
        # READ QUESTIONNAIRE DATA
        # ==================================

        df = pd.read_excel(
            uploaded_file,
            sheet_name=questionnaire_sheet
        )

        st.session_state[
            "df"
        ] = df


        # ==================================
        # FIND PLS-SEM STRUCTURE SHEET
        # ==================================

        structure_sheet = None

        preferred_structure_names = [
            "PLS_SEM_Structure",
            "PLS-SEM_Structure",
            "PLS SEM Structure",
            "PLS-SEM Structure",
            "SEM_Structure",
            "SEM Structure",
            "Model_Structure",
            "Model Structure"
        ]

        for preferred_name in preferred_structure_names:

            if preferred_name in sheet_names:

                structure_sheet = preferred_name

                break


        # ==================================
        # READ STRUCTURE SHEET
        # ==================================

        if structure_sheet is not None:

            structure_df = pd.read_excel(
                uploaded_file,
                sheet_name=structure_sheet
            )

            # Remove completely empty rows
            structure_df = structure_df.dropna(
                how="all"
            )

            # Remove completely empty columns
            structure_df = structure_df.dropna(
                axis=1,
                how="all"
            )

            st.session_state[
                "pls_structure"
            ] = structure_df

            st.session_state[
                "excel_structure_detected"
            ] = True

            st.success(
                "✅ PLS-SEM structure sheet detected automatically."
            )

        else:

            st.session_state[
                "excel_structure_detected"
            ] = False

            st.info(
                "ℹ️ No PLS-SEM structure sheet was found. "
                "The questionnaire data will still be available "
                "for normal analysis."
            )


    # ======================================
    # SUCCESS MESSAGE
    # ======================================

    st.success(
        "✅ File uploaded successfully!"
    )


    # ======================================
    # EXCEL SHEET INFORMATION
    # ======================================

    if uploaded_file.name.lower().endswith(
        ".xlsx"
    ):

        st.header(
            "📚 Excel Workbook Information"
        )

        st.write(
            "**Available Sheets:**"
        )

        st.write(
            sheet_names
        )

        st.write(
            f"**Questionnaire Data Sheet:** "
            f"{questionnaire_sheet}"
        )


        if structure_sheet is not None:

            st.success(
                f"✅ PLS-SEM Structure Sheet: "
                f"{structure_sheet}"
            )

        else:

            st.warning(
                "⚠️ PLS-SEM Structure Sheet: Not found"
            )


    # ======================================
    # SHOW PLS-SEM STRUCTURE
    # ======================================

    if (
        "pls_structure"
        in st.session_state
    ):

        st.header(
            "🏗️ Detected PLS-SEM Structure"
        )

        structure_df = st.session_state[
            "pls_structure"
        ]

        st.dataframe(
            structure_df,
            use_container_width=True,
            hide_index=True
        )


        # ==================================
        # STRUCTURE COLUMNS CHECK
        # ==================================

        required_structure_columns = [
            "Higher_Order_Construct",
            "Dimension",
            "Measurement_Type",
            "Indicator"
        ]

        missing_structure_columns = [
            column
            for column in required_structure_columns
            if column not in structure_df.columns
        ]


        if missing_structure_columns:

            st.warning(
                "⚠️ The PLS-SEM structure sheet was found, "
                "but some expected columns are missing:"
            )

            st.write(
                missing_structure_columns
            )

            st.info(
                "Expected columns are: "
                + ", ".join(
                    required_structure_columns
                )
            )

        else:

            st.success(
                "✅ Higher-order construct, "
                "dimension, measurement type, "
                "and indicator columns detected."
            )


    # ======================================
    # DATASET PREVIEW
    # ======================================

    st.header(
        "👀 Dataset Preview"
    )

    st.dataframe(
        df,
        use_container_width=True
    )


    # ======================================
    # DATASET INFORMATION
    # ======================================

    st.header(
        "📊 Dataset Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Rows",
            df.shape[0]
        )

    with col2:

        st.metric(
            "Columns",
            df.shape[1]
        )


    # ======================================
    # COLUMN NAMES
    # ======================================

    st.write(
        "### Column Names"
    )

    st.write(
        list(df.columns)
    )
