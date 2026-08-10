import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Reliability Analysis",
    page_icon="📋",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================
st.title("📋 Reliability Analysis")

st.write(
    "Calculate Cronbach's Alpha to assess the internal consistency "
    "of questionnaire items."
)

# ==========================================
# CHECK DATASET
# ==========================================
if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset on the Home page first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Home page!")

# ==========================================
# DATASET PREVIEW
# ==========================================
st.subheader("👀 Dataset Preview")

st.dataframe(
    df,
    use_container_width=True
)

# ==========================================
# CRONBACH'S ALPHA FUNCTION
# ==========================================
def cronbach_alpha(data):

    data = data.dropna()

    k = data.shape[1]

    if k < 2:
        return np.nan

    item_variances = data.var(axis=0, ddof=1)

    total_score = data.sum(axis=1)

    total_variance = total_score.var(ddof=1)

    if total_variance == 0:
        return np.nan

    alpha = (
        k / (k - 1)
    ) * (
        1 - item_variances.sum() / total_variance
    )

    return alpha


# ==========================================
# IDENTIFY CONSTRUCTS
# ==========================================
constructs = {
    "SD": [f"SD{i}" for i in range(1, 16)],
    "GI": [f"GI{i}" for i in range(1, 16)],
    "OP": [f"OP{i}" for i in range(1, 16)]
}

# ==========================================
# CHECK AVAILABLE CONSTRUCTS
# ==========================================
available_constructs = {}

for construct, items in constructs.items():

    available_items = [
        item for item in items
        if item in df.columns
    ]

    if len(available_items) >= 2:
        available_constructs[construct] = available_items


if len(available_constructs) == 0:

    st.error(
        "❌ No recognised construct items were found. "
        "Please check that your columns are named SD1–SD15, "
        "GI1–GI15, and OP1–OP15."
    )

else:

    # ==========================================
    # CONSTRUCT SELECTION
    # ==========================================
    st.subheader("🧩 Select Construct")

    selected_construct = st.selectbox(
        "Choose a construct for reliability analysis:",
        list(available_constructs.keys())
    )

    selected_items = available_constructs[
        selected_construct
    ]

    # ==========================================
    # ITEM INFORMATION
    # ==========================================
    st.subheader(
        f"📝 Items in {selected_construct}"
    )

    st.write(
        f"Number of items: **{len(selected_items)}**"
    )

    st.write(
        ", ".join(selected_items)
    )

    # ==========================================
    # CALCULATE ALPHA
    # ==========================================
    alpha = cronbach_alpha(
        df[selected_items]
    )

    # ==========================================
    # DISPLAY ALPHA
    # ==========================================
    st.subheader("📊 Cronbach's Alpha")

    if pd.isna(alpha):

        st.error(
            "Unable to calculate Cronbach's Alpha."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Cronbach's Alpha",
                f"{alpha:.3f}"
            )

        with col2:
            st.metric(
                "Number of Items",
                len(selected_items)
            )

        # ==========================================
        # INTERPRETATION
        # ==========================================

        if alpha >= 0.90:

            interpretation = (
                "Excellent internal consistency."
            )

        elif alpha >= 0.80:

            interpretation = (
                "Good internal consistency."
            )

        elif alpha >= 0.70:

            interpretation = (
                "Acceptable internal consistency."
            )

        elif alpha >= 0.60:

            interpretation = (
                "Questionable internal consistency."
            )

        else:

            interpretation = (
                "Poor internal consistency."
            )

        st.info(
            f"**Interpretation:** {interpretation}"
        )

    # ==========================================
    # ITEM-LEVEL INFORMATION
    # ==========================================
    st.subheader("📋 Item Statistics")

    item_statistics = pd.DataFrame({
        "Item": selected_items,
        "Mean": [
            round(df[item].mean(), 3)
            for item in selected_items
        ],
        "Standard Deviation": [
            round(df[item].std(), 3)
            for item in selected_items
        ]
    })

    st.dataframe(
        item_statistics,
        use_container_width=True
    )

    # ==========================================
    # ALL CONSTRUCTS SUMMARY
    # ==========================================
    st.subheader("📈 Reliability Summary")

    summary = []

    for construct, items in available_constructs.items():

        construct_alpha = cronbach_alpha(
            df[items]
        )

        summary.append({
            "Construct": construct,
            "Number of Items": len(items),
            "Cronbach's Alpha": (
                round(construct_alpha, 3)
                if not pd.isna(construct_alpha)
                else None
            )
        })

    summary_df = pd.DataFrame(summary)

    st.dataframe(
        summary_df,
        use_container_width=True
    )
