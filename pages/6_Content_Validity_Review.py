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
    "Record and organize qualitative expert evaluations "
    "of questionnaire items."
)

st.info(
    "This module records the original qualitative comments "
    "provided by experts. It does not generate new questions, "
    "rewrite questionnaire items, or calculate CVI."
)

# ==========================================
# QUESTIONNAIRE UPLOAD
# ==========================================
st.subheader("📄 Upload Questionnaire")

uploaded_file = st.file_uploader(
    "Upload your questionnaire",
    type=["docx", "pdf"]
)

if uploaded_file is not None:

    st.success(
        f"✅ Questionnaire uploaded: {uploaded_file.name}"
    )

# ==========================================
# EXPERT INFORMATION
# ==========================================
st.subheader("👥 Expert Information")

col1, col2 = st.columns(2)

with col1:

    expert_number = st.selectbox(
        "Select Expert",
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

item_number = st.text_input(
    "Item Number",
    placeholder="Example: A1-1"
)

item_text = st.text_area(
    "Questionnaire Item",
    placeholder="Enter or paste the questionnaire item here."
)

# ==========================================
# EXPERT EVALUATION
# ==========================================
st.subheader("💬 Expert Evaluation")

st.write(
    "Enter the expert's evaluation using the original wording. "
    "Experts may use any wording they prefer."
)

expert_comment = st.text_area(
    "Original Expert Comment",
    placeholder=(
        "Example: Clear and relevant.\n"
        "Example: Consider refining the wording.\n"
        "Example: Rephrase for clarity.\n"
        "Example: No change needed."
    ),
    height=150
)

# ==========================================
# RESEARCHER REVIEW CATEGORY
# ==========================================
st.subheader("📋 Researcher Review Category")

st.caption(
    "This category is a standardized research record. "
    "It does not replace the expert's original comment."
)

researcher_category = st.selectbox(
    "Select category",
    [
        "Accepted",
        "Good",
        "Revise",
        "Remove",
        "Pending Researcher Decision"
    ]
)

# ==========================================
# RESEARCHER FINAL DECISION
# ==========================================
st.subheader("👤 Researcher Final Decision")

researcher_decision = st.selectbox(
    "Final decision",
    [
        "Retain",
        "Revise",
        "Remove",
        "Pending"
    ]
)

researcher_comment = st.text_area(
    "Researcher Note (Optional)",
    placeholder=(
        "Enter your final decision or note about the item."
    )
)

# ==========================================
# STORE REVIEWS
# ==========================================
if "content_validity_reviews" not in st.session_state:

    st.session_state.content_validity_reviews = []


if st.button("➕ Add Expert Evaluation"):

    if item_number.strip() == "":
        st.warning("⚠️ Please enter the item number.")

    elif item_text.strip() == "":
        st.warning("⚠️ Please enter the questionnaire item.")

    elif expert_comment.strip() == "":
        st.warning("⚠️ Please enter the expert's original evaluation.")

    else:

        review = {
            "Item": item_number,
            "Item Text": item_text,
            "Expert": expert_number,
            "Expert Type": expert_type,
            "Original Expert Comment": expert_comment,
            "Review Category": researcher_category,
            "Researcher Decision": researcher_decision,
            "Researcher Note": researcher_comment
        }

        st.session_state.content_validity_reviews.append(
            review
        )

        st.success(
            "✅ Expert evaluation recorded successfully."
        )

# ==========================================
# REVIEW RECORDS
# ==========================================
st.subheader("📊 Expert Review Records")

if len(st.session_state.content_validity_reviews) > 0:

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    st.dataframe(
        review_df,
        use_container_width=True
    )

else:

    st.info(
        "No expert evaluations have been recorded yet."
    )

# ==========================================
# REVIEW SUMMARY
# ==========================================
if len(st.session_state.content_validity_reviews) > 0:

    st.subheader("📈 Review Summary")

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    total_reviews = len(review_df)

    accepted_count = int(
        (review_df["Review Category"] == "Accepted").sum()
    )

    good_count = int(
        (review_df["Review Category"] == "Good").sum()
    )

    revise_count = int(
        (review_df["Review Category"] == "Revise").sum()
    )

    remove_count = int(
        (review_df["Review Category"] == "Remove").sum()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Reviews",
            total_reviews
        )

    with col2:
        st.metric(
            "Accepted",
            accepted_count
        )

    with col3:
        st.metric(
            "Good",
            good_count
        )

    with col4:
        st.metric(
            "Revise",
            revise_count
        )

    with col5:
        st.metric(
            "Remove",
            remove_count
        )

# ==========================================
# METHODOLOGICAL NOTE
# ==========================================
st.subheader("📌 Methodological Note")

st.write(
    "The original wording of expert comments is retained. "
    "The standardized review category is used only to organize "
    "the qualitative evaluation. The final decision remains "
    "with the researcher."
)
