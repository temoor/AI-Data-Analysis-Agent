import streamlit as st
import pandas as pd
import re
from io import BytesIO

# PDF and Word readers
from pypdf import PdfReader
from docx import Document


# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Content Validity Review",
    page_icon="📝",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================
st.title("📝 Questionnaire Content Validity Review")

st.write(
    "Upload a questionnaire and record qualitative expert "
    "evaluations for each questionnaire item."
)

st.info(
    "This module supports qualitative content validity review. "
    "It does not calculate CVI, generate new questions, or "
    "automatically decide whether an item should be retained."
)


# ==========================================
# FUNCTIONS
# ==========================================

def extract_pdf_text(uploaded_file):
    """Extract text from a PDF file."""

    pdf_bytes = uploaded_file.read()
    reader = PdfReader(BytesIO(pdf_bytes))

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(uploaded_file):
    """Extract text from a Word document."""

    doc = Document(uploaded_file)

    text = ""

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text.strip() + "\n"

    # Also read tables
    for table in doc.tables:
        for row in table.rows:
            row_text = []

            for cell in row.cells:
                if cell.text.strip():
                    row_text.append(cell.text.strip())

            if row_text:
                text += " | ".join(row_text) + "\n"

    return text


def extract_questionnaire_items(text):
    """
    Try to identify questionnaire items from extracted text.

    Examples that can be detected:
    SD1: Statement
    SD1 - Statement
    SD1. Statement
    Q1: Statement
    Q1. Statement
    1. Statement
    """

    lines = text.splitlines()

    items = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Pattern for codes such as SD1, SD2, EP1, A1, Q1
        code_match = re.match(
            r"^([A-Za-z]{1,10}\s*[-_]?\s*\d{1,3})"
            r"\s*[\:\.\-\)]?\s*(.+)$",
            line
        )

        if code_match:

            code = code_match.group(1).replace(" ", "")
            statement = code_match.group(2).strip()

            if len(statement) > 5:
                items.append(
                    {
                        "Question Code": code,
                        "Question / Statement": statement
                    }
                )

            continue

        # Pattern for numbered questions such as:
        # 1. Statement
        # 2) Statement
        number_match = re.match(
            r"^(\d{1,3})\s*[\.\)\-:]\s*(.+)$",
            line
        )

        if number_match:

            code = "Q" + number_match.group(1)
            statement = number_match.group(2).strip()

            if len(statement) > 5:
                items.append(
                    {
                        "Question Code": code,
                        "Question / Statement": statement
                    }
                )

    # Remove duplicates
    unique_items = []

    seen = set()

    for item in items:

        key = (
            item["Question Code"],
            item["Question / Statement"]
        )

        if key not in seen:

            seen.add(key)
            unique_items.append(item)

    return unique_items


# ==========================================
# QUESTIONNAIRE UPLOAD
# ==========================================
st.subheader("📄 Upload Questionnaire")

uploaded_file = st.file_uploader(
    "Upload your questionnaire",
    type=["pdf", "docx"],
    help="Upload a PDF or Microsoft Word questionnaire."
)


# ==========================================
# PROCESS QUESTIONNAIRE
# ==========================================
if uploaded_file is not None:

    st.success(
        f"✅ Questionnaire uploaded: {uploaded_file.name}"
    )

    try:

        # Read PDF
        if uploaded_file.name.lower().endswith(".pdf"):

            extracted_text = extract_pdf_text(uploaded_file)

        # Read Word
        else:

            extracted_text = extract_docx_text(uploaded_file)

        # Store extracted text
        st.session_state["questionnaire_text"] = extracted_text

        # Extract items
        extracted_items = extract_questionnaire_items(
            extracted_text
        )

        st.session_state["questionnaire_items"] = extracted_items

    except Exception as e:

        st.error(
            f"❌ Could not read the questionnaire: {e}"
        )


# ==========================================
# SHOW EXTRACTED ITEMS
# ==========================================
if "questionnaire_items" in st.session_state:

    items = st.session_state["questionnaire_items"]

    st.subheader("📋 Extracted Questionnaire Items")

    if len(items) > 0:

        st.success(
            f"✅ {len(items)} questionnaire item(s) detected."
        )

        items_df = pd.DataFrame(items)

        st.dataframe(
            items_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "⚠️ No questionnaire items were automatically detected."
        )

        st.info(
            "The document may use a format that the automatic "
            "item detector does not recognize. You can still "
            "review items manually below."
        )


# ==========================================
# EXPERT INFORMATION
# ==========================================
st.subheader("👤 Expert Information")

col1, col2 = st.columns(2)

with col1:

    expert_number = st.selectbox(
        "Expert",
        [
            "Expert 1",
            "Expert 2",
            "Expert 3",
            "Expert 4",
            "Expert 5"
        ]
    )

with col2:

    expert_type = st.selectbox(
        "Expert Type",
        [
            "Academic",
            "Industrial"
        ]
    )


# ==========================================
# SELECT QUESTIONNAIRE ITEM
# ==========================================
st.subheader("📝 Questionnaire Item")

items = st.session_state.get(
    "questionnaire_items",
    []
)

if len(items) > 0:

    item_labels = []

    for item in items:

        label = (
            item["Question Code"]
            + " — "
            + item["Question / Statement"]
        )

        item_labels.append(label)

    selected_item = st.selectbox(
        "Select Questionnaire Item",
        item_labels
    )

    selected_index = item_labels.index(
        selected_item
    )

    selected_code = items[selected_index][
        "Question Code"
    ]

    selected_statement = items[selected_index][
        "Question / Statement"
    ]

    st.text_input(
        "Question Code",
        value=selected_code,
        disabled=True
    )

    st.text_area(
        "Question / Statement",
        value=selected_statement,
        height=120,
        disabled=True
    )

else:

    st.warning(
        "No extracted items available. Enter the item manually."
    )

    selected_code = st.text_input(
        "Question Code",
        placeholder="Example: EP1"
    )

    selected_statement = st.text_area(
        "Question / Statement",
        placeholder="Enter or paste the questionnaire statement.",
        height=120
    )


# ==========================================
# EXPERT COMMENT
# ==========================================
st.subheader("💬 Expert Reviewer Comment")

expert_comment = st.text_area(
    "Enter the expert's original comment",
    placeholder=(
        "Example: Clear and relevant.\n"
        "Example: The wording could be improved.\n"
        "Example: Appropriate for the intended respondents."
    ),
    height=150
)


# ==========================================
# RESEARCHER DECISION
# ==========================================
st.subheader("👨‍🏫 Researcher Decision")

st.caption(
    "The researcher makes the final decision after considering "
    "the expert's qualitative comment."
)

researcher_decision = st.selectbox(
    "Select Decision",
    [
        "Pending Review",
        "Retain",
        "Revise",
        "Remove"
    ]
)


researcher_note = st.text_area(
    "Researcher Note (Optional)",
    placeholder="Add a short explanation if needed.",
    height=100
)


# ==========================================
# SESSION STORAGE
# ==========================================
if "content_validity_reviews" not in st.session_state:

    st.session_state.content_validity_reviews = []


# ==========================================
# ADD REVIEW
# ==========================================
if st.button(
    "➕ Add Expert Review",
    type="primary"
):

    if not selected_code.strip():

        st.warning(
            "⚠️ Please provide a question code."
        )

    elif not selected_statement.strip():

        st.warning(
            "⚠️ Please provide the questionnaire statement."
        )

    elif not expert_comment.strip():

        st.warning(
            "⚠️ Please enter the expert's comment."
        )

    else:

        review = {
            "Expert": expert_number,
            "Expert Type": expert_type,
            "Question Code": selected_code,
            "Question / Statement": selected_statement,
            "Expert Reviewer Comment": expert_comment,
            "Researcher Decision": researcher_decision,
            "Researcher Note": researcher_note
        }

        st.session_state.content_validity_reviews.append(
            review
        )

        st.success(
            "✅ Expert review added successfully."
        )


# ==========================================
# REVIEW RECORDS
# ==========================================
st.subheader("📊 Expert Review Records")

if len(
    st.session_state.content_validity_reviews
) > 0:

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    st.dataframe(
        review_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No expert reviews have been recorded yet."
    )


# ==========================================
# SUMMARY
# ==========================================
if len(
    st.session_state.content_validity_reviews
) > 0:

    st.subheader("📈 Review Summary")

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    total_reviews = len(review_df)

    retain_count = int(
        (
            review_df["Researcher Decision"]
            == "Retain"
        ).sum()
    )

    revise_count = int(
        (
            review_df["Researcher Decision"]
            == "Revise"
        ).sum()
    )

    remove_count = int(
        (
            review_df["Researcher Decision"]
            == "Remove"
        ).sum()
    )

    pending_count = int(
        (
            review_df["Researcher Decision"]
            == "Pending Review"
        ).sum()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Reviews",
            total_reviews
        )

    with col2:
        st.metric(
            "Retain",
            retain_count
        )

    with col3:
        st.metric(
            "Revise",
            revise_count
        )

    with col4:
        st.metric(
            "Remove",
            remove_count
        )

    with col5:
        st.metric(
            "Pending",
            pending_count
        )


# ==========================================
# METHODOLOGICAL NOTE
# ==========================================
st.subheader("📌 Methodological Note")

st.write(
    "This module is designed to document qualitative expert "
    "judgment. Expert comments are preserved in their original "
    "form, while the researcher records the final decision "
    "for each questionnaire item."
)
