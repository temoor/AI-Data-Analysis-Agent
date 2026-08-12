import streamlit as st
import pandas as pd

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
    "Record qualitative expert comments and document "
    "the researcher's final decision for each questionnaire item."
)

st.info(
    "Expert comments are recorded using their original wording. "
    "The researcher decides whether each item should be retained, "
    "revised, or removed."
)

# ==========================================
# QUESTIONNAIRE UPLOAD
# ==========================================
st.subheader("📄 Questionnaire")

uploaded_file = st.file_uploader(
    "Upload your questionnaire (Word or PDF)",
    type=["docx", "pdf"]
)

if uploaded_file is not None:
    st.success(
        f"✅ Questionnaire uploaded: {uploaded_file.name}"
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
# QUESTIONNAIRE ITEM
# ==========================================
st.subheader("📝 Questionnaire Item")

item_code = st.text_input(
    "Question Code",
    placeholder="Example: A1-1"
)

item_statement = st.text_area(
    "Question / Statement",
    placeholder="Enter or paste the questionnaire statement here.",
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
        "Example: Consider refining the wording.\n"
        "Example: Rephrase for clarity."
    ),
    height=150
)

# ==========================================
# RESEARCHER DECISION
# ==========================================
st.subheader("👨‍🏫 Researcher Decision")

researcher_decision = st.selectbox(
    "Select the final decision after evaluating the expert comment",
    [
        "Pending Review",
        "Retain",
        "Revise",
        "Remove"
    ]
)

researcher_note = st.text_area(
    "Researcher Note (Optional)",
    placeholder="Add a short note if required.",
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
if st.button("➕ Add Review"):

    if item_code.strip() == "":
        st.warning("⚠️ Please enter the question code.")

    elif item_statement.strip() == "":
        st.warning("⚠️ Please enter the question/statement.")

    elif expert_comment.strip() == "":
        st.warning("⚠️ Please enter the expert reviewer comment.")

    else:

        review = {
            "Expert": expert_number,
            "Expert Type": expert_type,
            "Question Code": item_code,
            "Question / Statement": item_statement,
            "Expert Reviewer Comment": expert_comment,
            "Researcher Decision": researcher_decision,
            "Researcher Note": researcher_note
        }

        st.session_state.content_validity_reviews.append(review)

        st.success("✅ Review added successfully.")

# ==========================================
# REVIEW TABLE
# ==========================================
st.subheader("📊 Content Validity Review Records")

if len(st.session_state.content_validity_reviews) > 0:

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
        "No questionnaire items have been reviewed yet."
    )

# ==========================================
# SUMMARY
# ==========================================
if len(st.session_state.content_validity_reviews) > 0:

    st.subheader("📈 Review Summary")

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    total_items = len(review_df)

    retain_count = int(
        (review_df["Researcher Decision"] == "Retain").sum()
    )

    revise_count = int(
        (review_df["Researcher Decision"] == "Revise").sum()
    )

    remove_count = int(
        (review_df["Researcher Decision"] == "Remove").sum()
    )

    pending_count = int(
        (review_df["Researcher Decision"] == "Pending Review").sum()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Reviews", total_items)

    with col2:
        st.metric("Retain", retain_count)

    with col3:
        st.metric("Revise", revise_count)

    with col4:
        st.metric("Remove", remove_count)

    with col5:
        st.metric("Pending", pending_count)

# ==========================================
# METHODOLOGICAL NOTE
# ==========================================
st.subheader("📌 Methodological Note")

st.write(
    "The expert's original qualitative comment is preserved. "
    "The Researcher Decision represents the researcher's judgment "
    "after considering the expert's evaluation."
)
