import streamlit as st
import pandas as pd
import pickle
import zipfile
import io
from datetime import datetime


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Project Manager",
    page_icon="📁",
    layout="wide"
)

st.title("📁 Project Manager")
st.write("Save your complete AI Data Analysis project and reopen it later.")


# ---------------------------------------------------------
# SESSION STATE KEYS TO SAVE
# ---------------------------------------------------------
SESSION_KEYS = [
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


# ---------------------------------------------------------
# CREATE PROJECT PACKAGE
# ---------------------------------------------------------
def create_project_package(project_name):
    """Create a downloadable .aida project package."""

    project_data = {}

    # Save dataframe
    if "df" in st.session_state:
        project_data["df"] = st.session_state["df"]

    # Save structure information
    if "pls_structure" in st.session_state:
        project_data["pls_structure"] = st.session_state["pls_structure"]

    if "excel_structure_detected" in st.session_state:
        project_data["excel_structure_detected"] = st.session_state[
            "excel_structure_detected"
        ]

    # Save analysis/session information
    for key in SESSION_KEYS:
        if key in st.session_state:
            project_data[key] = st.session_state[key]

    metadata = {
        "project_name": project_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "application": "AI Data Analysis Agent",
        "project_format": "AIDA Project",
    }

    complete_project = {
        "metadata": metadata,
        "project_data": project_data,
    }

    # Create ZIP-based project file
    package_buffer = io.BytesIO()

    with zipfile.ZipFile(
        package_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as project_zip:

        project_zip.writestr(
            "project.pkl",
            pickle.dumps(complete_project)
        )

        project_zip.writestr(
            "project_info.txt",
            (
                f"Project Name: {project_name}\n"
                f"Created: {metadata['created_at']}\n"
                f"Application: AI Data Analysis Agent\n"
                f"Format: AIDA Project\n"
            )
        )

    package_buffer.seek(0)

    return package_buffer.getvalue()


# ---------------------------------------------------------
# OPEN PROJECT PACKAGE
# ---------------------------------------------------------
def open_project_package(uploaded_file):
    """Open and restore an AIDA project."""

    uploaded_bytes = uploaded_file.read()

    package_buffer = io.BytesIO(uploaded_bytes)

    with zipfile.ZipFile(package_buffer, "r") as project_zip:

        if "project.pkl" not in project_zip.namelist():
            raise ValueError(
                "This file is not a valid AIDA project."
            )

        project_bytes = project_zip.read("project.pkl")

    project = pickle.loads(project_bytes)

    metadata = project.get("metadata", {})
    project_data = project.get("project_data", {})

    # Clear old project data
    keys_to_clear = [
        "df",
        "pls_structure",
        "excel_structure_detected",
    ] + SESSION_KEYS

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Restore project
    for key, value in project_data.items():
        st.session_state[key] = value

    return metadata


# ---------------------------------------------------------
# CURRENT PROJECT STATUS
# ---------------------------------------------------------
st.header("📊 Current Project")

if "df" in st.session_state:

    df = st.session_state["df"]

    col1, col2, col3, col4 = st.columns(4)

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
        if "pls_constructs" in st.session_state:
            st.metric(
                "Simple Constructs",
                len(st.session_state["pls_constructs"])
            )
        else:
            st.metric(
                "Simple Constructs",
                0
            )

    with col4:
        if "pls_higher_order_models" in st.session_state:
            st.metric(
                "Higher-Order Constructs",
                len(st.session_state["pls_higher_order_models"])
            )
        elif "pls_higher_order_model" in st.session_state:
            st.metric(
                "Higher-Order Constructs",
                1
            )
        else:
            st.metric(
                "Higher-Order Constructs",
                0
            )

else:

    st.info(
        "No dataset is currently loaded. "
        "Please upload your dataset from the Home page first."
    )


# ---------------------------------------------------------
# SAVE PROJECT
# ---------------------------------------------------------
st.divider()

st.header("💾 Save Project")

project_name = st.text_input(
    "Project Name",
    value="My_AI_Data_Analysis_Project",
    help="Enter a name for your research project."
)

if st.button(
    "💾 Prepare Project for Download",
    type="primary",
    use_container_width=True
):

    if "df" not in st.session_state:

        st.warning(
            "Please upload a dataset before saving the project."
        )

    else:

        try:

            project_bytes = create_project_package(
                project_name
            )

            safe_name = (
                project_name
                .strip()
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )

            if not safe_name:
                safe_name = "AI_Data_Analysis_Project"

            file_name = safe_name + ".aida"

            st.success(
                "Project package created successfully."
            )

            st.download_button(
                label="⬇️ Download Project File",
                data=project_bytes,
                file_name=file_name,
                mime="application/octet-stream",
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Could not create the project file: {e}"
            )


# ---------------------------------------------------------
# OPEN PROJECT
# ---------------------------------------------------------
st.divider()

st.header("📂 Open Project")

st.write(
    "Upload a previously saved `.aida` project file."
)

uploaded_project = st.file_uploader(
    "Choose AIDA Project File",
    type=["aida"],
    key="aida_project_uploader"
)

if uploaded_project is not None:

    if st.button(
        "📂 Open Project",
        type="primary",
        use_container_width=True
    ):

        try:

            metadata = open_project_package(
                uploaded_project
            )

            st.success(
                "Project opened successfully!"
            )

            project_name_loaded = metadata.get(
                "project_name",
                "Unknown Project"
            )

            created_at = metadata.get(
                "created_at",
                "Unknown"
            )

            st.info(
                f"**Project:** {project_name_loaded}\n\n"
                f"**Created:** {created_at}"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not open this project file: {e}"
            )


# ---------------------------------------------------------
# SAVED PROJECT INFORMATION
# ---------------------------------------------------------
st.divider()

st.header("📋 Project Information")

if "df" in st.session_state:

    df = st.session_state["df"]

    information = {
        "Dataset Loaded": "Yes",
        "Respondents": df.shape[0],
        "Variables": df.shape[1],
        "Simple PLS-SEM Model": (
            "Yes"
            if "pls_constructs" in st.session_state
            else "No"
        ),
        "Simple Structural Model": (
            "Yes"
            if "pls_structural_paths" in st.session_state
            else "No"
        ),
        "Higher-Order Model": (
            "Yes"
            if (
                "pls_higher_order_models" in st.session_state
                or "pls_higher_order_model" in st.session_state
            )
            else "No"
        ),
        "Higher-Order Structural Model": (
            "Yes"
            if "pls_higher_order_structural_paths"
            in st.session_state
            else "No"
        ),
        "Mediation Analysis": (
            "Yes"
            if "mediation_results" in st.session_state
            else "No"
        ),
    }

    info_df = pd.DataFrame(
        list(information.items()),
        columns=["Project Component", "Status"]
    )

    st.dataframe(
        info_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Project information will appear here after a dataset is loaded."
    )


# ---------------------------------------------------------
# PRIVACY / SECURITY NOTE
# ---------------------------------------------------------
st.divider()

st.caption(
    "🔐 Project files are created locally in your browser through "
    "the Streamlit download process. Only open AIDA project files "
    "that you trust."
)
