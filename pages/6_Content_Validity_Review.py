import streamlit as st
import pandas as pd
import re
from io import BytesIO

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
    "Upload a questionnaire and organize qualitative "
    "expert evaluations for each questionnaire item."
)

st.info(
    "This module records expert comments and the researcher's "
    "final decision. It does not calculate CVI, generate new "
    "questions, or rewrite questionnaire items."
)


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================
def extract_pdf_text(uploaded_file):

    uploaded_file.seek(0)

    pdf_bytes = uploaded_file.read()

    reader = PdfReader(BytesIO(pdf_bytes))

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# WORD TEXT EXTRACTION
# ==========================================
def extract_docx_text(uploaded_file):

    uploaded_file.seek(0)

    document = Document(uploaded_file)

    text = ""

    # Normal paragraphs
    for paragraph in document.paragraphs:

        value = paragraph.text.strip()

        if value:
            text += value + "\n"

    # Tables
    for table in document.tables:

        for row in table.rows:

            cells = []

            for cell in row.cells:

                value = cell.text.strip()

                if value:
                    cells.append(value)

            if cells:
                text += " | ".join(cells) + "\n"

    return text


# ==========================================
# EXTRACT QUESTIONNAIRE ITEMS
# ==========================================
def extract_questionnaire_items(text):

    lines = text.splitlines()

    items = []

    current_code = None
    current_statement = []

    # --------------------------------------
    # Save current item
    # --------------------------------------
    def save_current_item():

        nonlocal current_code
        nonlocal current_statement

        if current_code and current_statement:

            statement = " ".join(
                current_statement
            ).strip()

            if len(statement) > 5:

                items.append(
                    {
                        "Question Code": current_code,
                        "Question / Statement": statement
                    }
                )

        current_code = None
        current_statement = []

    # --------------------------------------
    # Process each line
    # --------------------------------------
    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # ----------------------------------
        # Remove table separators
        # ----------------------------------
        line = line.replace(" | ", " | ")

        # ----------------------------------
        # Detect code
        #
        # Examples:
        # SD1
        # SD1-1
        # A1
        # A1-1
        # EP1
        # Q1
        # ----------------------------------
        match = re.match(
            r"^([A-Za-z]{1,10}"
            r"(?:[-_]\d{1,3})?"
            r"\d{1,3})"
            r"\s*[\:\.\-\)]?\s*(.*)$",
            line
        )

        if match:

            save_current_item()

            current_code = (
                match.group(1)
                .replace(" ", "")
            )

            remaining_text = match.group(2).strip()

            if remaining_text:
                current_statement.append(
                    remaining_text
                )

            continue

        # ----------------------------------
        # Numbered questions
        #
        # Examples:
        # 1. Statement
        # 2) Statement
        # ----------------------------------
        number_match = re.match(
            r"^(\d{1,3})\s*[\.\)\-:]\s*(.+)$",
            line
        )

        if number_match:

            save_current_item()

            current_code = (
                "Q" + number_match.group(1)
            )

            current_statement.append(
                number_match.group(2).strip()
            )

            continue

        # ----------------------------------
        # Continue previous statement
        # ----------------------------------
        if current_code:

            current_statement.append(line)

    # Save final item
    save_current_item()

    # --------------------------------------
    # Remove duplicates
    # --------------------------------------
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
# UPLOAD QUESTIONNAIRE
# ==========================================
st.subheader("📄 Upload Questionnaire")

uploaded_file = st.file_uploader(
    "Upload your questionnaire",
    type=["pdf", "docx"]
)


# ==========================================
# PROCESS FILE
# ==========================================
if uploaded_file is not None:

    st.success(
        f"✅ Questionnaire uploaded: "
        f"{uploaded_file.name}"
    )

    try:

        if uploaded_file.name.lower().endswith(".pdf"):

            extracted_text = extract_pdf_text(
                uploaded_file
            )

        else:

            extracted_text = extract_docx_text(
                uploaded_file
            )

        st.session_state[
            "questionnaire_text"
        ] = extracted_text

        extracted_items = (
            extract_questionnaire_items(
                extracted_text
            )
        )

        st.session_state[
            "questionnaire_items"
        ] = extracted_items

    except Exception as error:

        st.error(
            f"❌ Unable to read the file: {error}"
        )


# ==========================================
# EXTRACTED ITEMS
# ==========================================
items = st.session_state.get(
    "questionnaire_items",
    []
)

if uploaded_file is not None:

    st.subheader(
        "📋 Extracted Questionnaire Items"
    )

    if len(items) > 0:

        st.success(
            f"✅ {len(items)} questionnaire "
            f"item(s) detected."
        )

        items_df = pd.DataFrame(items)

        st.dataframe(
            items_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "⚠️ No questionnaire items were "
            "automatically detected."
        )

        st.info(
            "If the questionnaire uses an unusual "
            "format, you can enter the item manually "
            "below."
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
# SELECT QUESTION
# ==========================================
st.subheader("📝 Questionnaire Item")

if len(items) > 0:

    item_labels = []

    for item in items:

        item_labels.append(
            item["Question Code"]
            + " — "
            + item["Question / Statement"]
        )

    selected_label = st.selectbox(
        "Select Questionnaire Item",
        item_labels
    )

    selected_index = item_labels.index(
        selected_label
    )

    selected_code = items[
        selected_index
    ]["Question Code"]

    selected_statement = items[
        selected_index
    ]["Question / Statement"]

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
st.subheader(
    "💬 Expert Reviewer Comment"
)

expert_comment = st.text_area(
    "Enter the expert's original comment",
    placeholder=(
        "Example: Clear and relevant.\n"
        "Example: Consider refining the wording.\n"
        "Example: Rephrase for clarity."
    ),
    height=150
)


# ==========================================
# RESEARCHER DECISION
# ==========================================
st.subheader(
    "👨‍🏫 Researcher Decision"
)

st.caption(
    "The researcher makes the final decision after "
    "considering the expert's qualitative comment."
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
    placeholder=(
        "Add a short explanation if required."
    ),
    height=100
)


# ==========================================
# SESSION STORAGE
# ==========================================
if "content_validity_reviews" not in st.session_state:

    st.session_state[
        "content_validity_reviews"
    ] = []


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

            "Question / Statement":
                selected_statement,

            "Expert Reviewer Comment":
                expert_comment,

            "Researcher Decision":
                researcher_decision,

            "Researcher Note":
                researcher_note
        }

        st.session_state[
            "content_validity_reviews"
        ].append(review)

        st.success(
            "✅ Expert review added successfully."
        )


# ==========================================
# REVIEW RECORDS
# ==========================================
st.subheader(
    "📊 Expert Review Records"
)

reviews = st.session_state.get(
    "content_validity_reviews",
    []
)

if len(reviews) > 0:

    review_df = pd.DataFrame(
        reviews
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
if len(reviews) > 0:

    st.subheader(
        "📈 Review Summary"
    )

    review_df = pd.DataFrame(
        reviews
    )

    total_reviews = len(review_df)

    retain_count = int(
        (
            review_df[
                "Researcher Decision"
            ] == "Retain"
        ).sum()
    )

    revise_count = int(
        (
            review_df[
                "Researcher Decision"
            ] == "Revise"
        ).sum()
    )

    remove_count = int(
        (
            review_df[
                "Researcher Decision"
            ] == "Remove"
        ).sum()
    )

    pending_count = int(
        (
            review_df[
                "Researcher Decision"
            ] == "Pending Review"
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
st.subheader(
    "📌 Methodological Note"
)

st.write(
    "The expert's original qualitative comment is "
    "preserved. The Researcher Decision represents "
    "the researcher's judgment after considering "
    "the expert's evaluation."
)
