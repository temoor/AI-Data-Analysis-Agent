import streamlit as st
import pandas as pd
import pickle
import io
import zipfile
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Project Manager",
    page_icon="💾",
    layout="wide"
)

st.title("💾 Project Manager")

st.write(
    "Save your complete research project and restore it later. "
    "A project package can contain the dataset, model specifications, "
    "structural paths, researcher decisions, and analysis settings."
)

st.info(
    "📌 The project file is intended for research continuity. "
    "Keep a backup of your project file in a secure location."
)


# ============================================================
# PROJECT VERSION
# ============================================================

PROJECT_VERSION = "1.0"


# ============================================================
# HELPER: SAFE SERIALIZATION
# ============================================================

def collect_project_state():

    project = {
        "project_version": PROJECT_VERSION,
        "saved_at": datetime.now().isoformat(),
        "session_state": {}
    }

    # --------------------------------------------------------
    # Keys that contain research/model information
    # --------------------------------------------------------

    allowed_keys = [
        "pls_constructs",
        "pls_structural_paths",
        "pls_higher_order_model",
        "pls_higher_order_models",
        "pls_higher_order_structural_model",
        "pls_higher_order_structural_paths",
        "measurement_model_decisions",
        "higher_order_measurement_decisions",
        "content_validity_results",
        "content_validity_decisions",
        "data_quality_results",
        "reliability_results",
        "eda_results",
        "mediation_results",
    ]

    for key in allowed_keys:

        if key in st.session_state:

            try:

                project["session_state"][key] = (
                    st.session_state[key]
                )

            except Exception:

                pass

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    if "df" in st.session_state:

        try:

            project["dataset"] = st.session_state[
                "df"
            ].copy()

        except Exception:

            project["dataset"] = None

    else:

        project["dataset"] = None

    # --------------------------------------------------------
    # PLS structure from Excel
    # --------------------------------------------------------

    if "pls_structure" in st.session_state:

        try:

            structure = st.session_state[
                "pls_structure"
            ]

            if isinstance(
                structure,
                pd.DataFrame
            ):

                project["pls_structure"] = structure.copy()

            else:

                project["pls_structure"] = structure

        except Exception:

            project["pls_structure"] = None

    else:

        project["pls_structure"] = None

    # --------------------------------------------------------
    # Excel structure detection flag
    # --------------------------------------------------------

    project[
        "excel_structure_detected"
    ] = st.session_state.get(
        "excel_structure_detected",
        False
    )

    return project


# ============================================================
# HELPER: CREATE PROJECT FILE
# ============================================================

def create_project_file(project):

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as archive:

        # ----------------------------------------------------
        # Project metadata and session state
        # ----------------------------------------------------

        project_without_dataset = project.copy()

        dataset = project_without_dataset.pop(
            "dataset",
            None
        )

        structure = project_without_dataset.pop(
            "pls_structure",
            None
        )

        session_bytes = pickle.dumps(
            project_without_dataset
        )

        archive.writestr(
            "project.pkl",
            session_bytes
        )

        # ----------------------------------------------------
        # Dataset
        # ----------------------------------------------------

        if isinstance(
            dataset,
            pd.DataFrame
        ):

            dataset_buffer = io.BytesIO()

            dataset.to_pickle(
                dataset_buffer
            )

            archive.writestr(
                "dataset.pkl",
                dataset_buffer.getvalue()
            )

        # ----------------------------------------------------
        # Structure
        # ----------------------------------------------------

        if isinstance(
            structure,
            pd.DataFrame
        ):

            structure_buffer = io.BytesIO()

            structure.to_pickle(
                structure_buffer
            )

            archive.writestr(
                "pls_structure.pkl",
                structure_buffer.getvalue()
            )

        elif structure is not None:

            structure_bytes = pickle.dumps(
                structure
            )

            archive.writestr(
                "pls_structure_raw.pkl",
                structure_bytes
            )

        # ----------------------------------------------------
        # Readable project information
        # ----------------------------------------------------

        dataset_rows = (
            len(dataset)
            if isinstance(
                dataset,
                pd.DataFrame
            )
            else 0
        )

        dataset_columns = (
            len(dataset.columns)
            if isinstance(
                dataset,
                pd.DataFrame
            )
            else 0
        )

        information = f"""
AI DATA ANALYSIS AGENT
PROJECT PACKAGE

Project Version: {PROJECT_VERSION}
Saved At: {project.get("saved_at", "")}

Dataset Rows: {dataset_rows}
Dataset Columns: {dataset_columns}

Files contained:
- project.pkl
- dataset.pkl (if dataset exists)
- PLS-SEM structure information (if available)

This project package is intended for research continuity.
"""

        archive.writestr(
            "PROJECT_INFO.txt",
            information.strip()
        )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# HELPER: LOAD PROJECT
# ============================================================

def load_project_file(uploaded_file):

    project = None
    dataset = None
    structure = None

    try:

        file_bytes = uploaded_file.getvalue()

        with zipfile.ZipFile(
            io.BytesIO(file_bytes),
            mode="r"
        ) as archive:

            files = archive.namelist()

            # ------------------------------------------------
            # Check project file
            # ------------------------------------------------

            if "project.pkl" not in files:

                raise ValueError(
                    "This file does not contain a valid "
                    "AI Data Analysis Agent project."
                )

            project = pickle.loads(
                archive.read(
                    "project.pkl"
                )
            )

            # ------------------------------------------------
            # Dataset
            # ------------------------------------------------

            if "dataset.pkl" in files:

                dataset = pd.read_pickle(
                    io.BytesIO(
                        archive.read(
                            "dataset.pkl"
                        )
                    )
                )

            # ------------------------------------------------
            # Structure
            # ------------------------------------------------

            if "pls_structure.pkl" in files:

                structure = pd.read_pickle(
                    io.BytesIO(
                        archive.read(
                            "pls_structure.pkl"
                        )
                    )

            elif "pls_structure_raw.pkl" in files:

                structure = pickle.loads(
                    archive.read(
                        "pls_structure_raw.pkl"
                    )
                )

        return (
            project,
            dataset,
            structure
        )

    except Exception as error:

        raise ValueError(
            f"Could not open project: {error}"
        )


# ============================================================
# CURRENT PROJECT STATUS
# ============================================================

st.divider()

st.header(
    "📊 Current Project"
)

current_df = st.session_state.get(
    "df"
)

current_hocs = st.session_state.get(
    "pls_higher_order_models",
    {}
)

current_constructs = st.session_state.get(
    "pls_constructs",
    {}
)

current_paths = st.session_state.get(
    "pls_structural_paths",
    []
)

current_hoc_paths = st.session_state.get(
    "pls_higher_order_structural_paths",
    []
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    if isinstance(
        current_df,
        pd.DataFrame
    ):

        st.metric(
            "Dataset Rows",
            current_df.shape[0]
        )

    else:

        st.metric(
            "Dataset Rows",
            0
        )

with col2:

    if isinstance(
        current_df,
        pd.DataFrame
    ):

        st.metric(
            "Dataset Variables",
            current_df.shape[1]
        )

    else:

        st.metric(
            "Dataset Variables",
            0
        )

with col3:

    st.metric(
        "Simple Constructs",
        len(current_constructs)
        if isinstance(
            current_constructs,
            dict
        )
        else 0
    )

with col4:

    st.metric(
        "Higher-Order Constructs",
        len(current_hocs)
        if isinstance(
            current_hocs,
            dict
        )
        else 0
    )


# ============================================================
# SAVE PROJECT
# ============================================================

st.divider()

st.header(
    "💾 Save Project"
)

project_name = st.text_input(
    "Project Name",
    value="My_Research_Project",
    help=(
        "Give your research project a meaningful name. "
        "The project file will be downloaded to your computer."
    )
)

if st.button(
    "💾 Save Project",
    type="primary",
    key="save_project"
):

    if not project_name.strip():

        st.error(
            "❌ Please enter a project name."
        )

    elif "df" not in st.session_state:

        st.error(
            "❌ No dataset is currently loaded."
        )

    else:

        project = collect_project_state()

        project_bytes = create_project_file(
            project
        )

        safe_name = (
            project_name.strip()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        if not safe_name.lower().endswith(
            ".aida"
        ):

            safe_name += ".aida"

        st.download_button(
            label="⬇️ Download Project File",
            data=project_bytes,
            file_name=safe_name,
            mime="application/octet-stream",
            key="download_project_file"
        )

        st.success(
            "✅ Project package prepared successfully."
        )

        st.write(
            "Download the project file and keep it safely. "
            "You can upload this file later to restore your work."
        )


# ============================================================
# OPEN PROJECT
# ============================================================

st.divider()

st.header(
    "📂 Open Previous Project"
)

st.write(
    "Upload a previously saved `.aida` project file."
)

uploaded_project = st.file_uploader(
    "Choose Project File",
    type=["aida"],
    key="project_upload"
)


if uploaded_project is not None:

    if st.button(
        "📂 Open Project",
        type="primary",
        key="open_project"
    ):

        try:

            project, dataset, structure = (
                load_project_file(
                    uploaded_project
                )
            )

            # ------------------------------------------------
            # Restore session state
            # ------------------------------------------------

            saved_state = project.get(
                "session_state",
                {}
            )

            if isinstance(
                saved_state,
                dict
            ):

                for key, value in saved_state.items():

                    st.session_state[
                        key
                    ] = value

            # ------------------------------------------------
            # Restore dataset
            # ------------------------------------------------

            if isinstance(
                dataset,
                pd.DataFrame
            ):

                st.session_state[
                    "df"
                ] = dataset.copy()

            # ------------------------------------------------
            # Restore structure
            # ------------------------------------------------

            if structure is not None:

                if isinstance(
                    structure,
                    pd.DataFrame
                ):

                    st.session_state[
                        "pls_structure"
                    ] = structure.copy()

                else:

                    st.session_state[
                        "pls_structure"
                    ] = structure

            # ------------------------------------------------
            # Restore structure flag
            # ------------------------------------------------

            st.session_state[
                "excel_structure_detected"
            ] = project.get(
                "excel_structure_detected",
                False
            )

            # ------------------------------------------------
            # Project metadata
            # ------------------------------------------------

            st.session_state[
                "current_project_name"
            ] = uploaded_project.name

            st.session_state[
                "current_project_saved_at"
            ] = project.get(
                "saved_at",
                ""
            )

            st.success(
                "✅ Project opened successfully."
            )

            if isinstance(
                dataset,
                pd.DataFrame
            ):

                st.write(
                    f"**Dataset:** "
                    f"{dataset.shape[0]} respondents × "
                    f"{dataset.shape[1]} variables"
                )

            if isinstance(
                saved_state.get(
                    "pls_higher_order_models"
                ),
                dict
            ):

                st.write(
                    f"**Higher-Order Constructs restored:** "
                    f"{len(saved_state['pls_higher_order_models'])}"
                )

            if isinstance(
                saved_state.get(
                    "pls_higher_order_structural_paths"
                ),
                list
            ):

                st.write(
                    f"**Higher-Order Structural Paths restored:** "
                    f"{len(saved_state['pls_higher_order_structural_paths'])}"
                )

            st.info(
                "🔄 The project information is now restored "
                "in the current session. You can continue analysis "
                "from the relevant page."
            )

        except Exception as error:

            st.error(
                "❌ Could not open this project file."
            )

            st.exception(
                error
            )


# ============================================================
# CURRENT SAVED PROJECT INFORMATION
# ============================================================

if (
    "current_project_name"
    in st.session_state
):

    st.divider()

    st.subheader(
        "📌 Current Project Information"
    )

    st.write(
        f"**Project File:** "
        f"{st.session_state['current_project_name']}"
    )

    saved_at = st.session_state.get(
        "current_project_saved_at",
        ""
    )

    if saved_at:

        st.write(
            f"**Saved At:** {saved_at}"
        )


# ============================================================
# WHAT IS SAVED?
# ============================================================

st.divider()

st.header(
    "📦 What Is Saved in the Project?"
)

saved_items = [
    "Dataset",
    "Excel PLS-SEM structure",
    "Simple PLS-SEM constructs",
    "Simple structural paths",
    "Higher-Order Constructs",
    "Higher-Order Structural Model",
    "Higher-Order Structural Paths",
    "Measurement/analysis decisions when stored in session state",
    "Mediation results when available"
]

for item in saved_items:

    st.write(
        f"✅ {item}"
    )


# ============================================================
# IMPORTANT NOTE
# ============================================================

st.divider()

st.info(
    "🔐 Privacy note: The project package contains your dataset "
    "and research-model information. Treat it like your original "
    "research data and store it securely. Do not upload confidential "
    "or personally identifiable research data to an unsecured location."
)


# ============================================================
# METHOD NOTE
# ============================================================

st.divider()

st.caption(
    "AI Data Analysis Agent — Project Manager. "
    "Project packages are designed to preserve research work "
    "between sessions and are not a substitute for institutional "
    "data-management or backup procedures."
)
