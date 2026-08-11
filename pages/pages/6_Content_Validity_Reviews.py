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
    "Organize and record qualitative expert evaluations "
    "of questionnaire items."
)

st.info(
    "This module records expert judgments. It does not generate "
    "new questions, rewrite items, or calculate Content Validity Index (CVI)."
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

    st.info(
        "The questionnaire file is uploaded for this review session. "
        "Expert decisions can be recorded below."
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
# ITEM INFORMATION
# ==========================================
st.subheader("📝 Questionnaire Item")

item_number = st.text_input(
    "Item Number",
    placeholder="Example: SD1"
)

item_text = st.text_area(
    "Questionnaire Item",
    placeholder="Paste the questionnaire item here."
)

# ==========================================
# EXPERT DECISION
# ==========================================
st.subheader("📋 Expert Evaluation")

decision = st.selectbox(
    "Expert Decision",
    [
        "Accepted",
        "Good",
        "Revise",
        "Remove"
    ]
)

expert_comment = st.text_area(
    "Expert Comment (Optional)",
    placeholder="Enter the expert's comment if available."
)

# ==========================================
# STORE REVIEW
# ==========================================
if "content_validity_reviews" not in st.session_state:

    st.session_state.content_validity_reviews = []


if st.button("➕ Add Expert Evaluation"):

    if item_number.strip() == "":
        st.warning("⚠️ Please enter the item number.")

    elif item_text.strip() == "":
        st.warning("⚠️ Please enter the questionnaire item.")

    else:

        review = {
            "Item": item_number,
            "Item Text": item_text,
            "Expert": expert_number,
            "Expert Type": expert_type,
            "Decision": decision,
            "Comment": expert_comment
        }

        st.session_state.content_validity_reviews.append(
            review
        )

        st.success(
            "✅ Expert evaluation added successfully."
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
# SUMMARY
# ==========================================
if len(st.session_state.content_validity_reviews) > 0:

    st.subheader("📈 Review Summary")

    review_df = pd.DataFrame(
        st.session_state.content_validity_reviews
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Reviews",
            len(review_df)
        )

    with col2:
        st.metric(
            "Accepted",
            int(
                (review_df["Decision"] == "Accepted").sum()
            )
        )

    with col3:
        st.metric(
            "Good",
            int(
                (review_df["Decision"] == "Good").sum()
            )
        )

    with col4:
        st.metric(
            "Revise",
            int(
                (review_df["Decision"] == "Revise").sum()
            )
        )

    remove_count = int(
        (review_df["Decision"] == "Remove").sum()
    )

    st.write(
        f"**Remove:** {remove_count}"
    )

# ==========================================
# METHODOLOGICAL NOTE
# ==========================================
st.subheader("📌 Methodological Note")

st.write(
    "The final decision regarding questionnaire items remains "
    "with the researcher based on the qualitative judgments "
    "and recommendations provided by the academic and industrial experts."
)
