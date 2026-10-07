import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="User Guide & Research Methodology",
    page_icon="📘",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("📘 User Guide & Research Methodology")

st.markdown(
    """
    Welcome to the **AI Data Analysis Agent**.

    This guide explains how to use the application, understand the
    major statistical concepts, interpret the results, and follow
    an appropriate research workflow.

    The application is designed to support researchers working with
    questionnaire and Likert-scale data, reliability analysis,
    measurement models, Higher-Order Constructs, structural models,
    PLS-SEM-style analysis, and mediation analysis.
    """
)

st.info(
    "💡 Recommended approach: Follow the research workflow from "
    "data preparation and quality checking through measurement and "
    "structural analysis before interpreting final results."
)

# ============================================================
# RESEARCH WORKFLOW
# ============================================================

st.header("🚀 Recommended Research Workflow")

st.markdown(
    """
    ### Recommended sequence

    **1. Upload Dataset**  
    ↓  
    **2. Data Quality**  
    ↓  
    **3. Descriptive Statistics**  
    ↓  
    **4. Reliability Analysis**  
    ↓  
    **5. Exploratory Data Analysis**  
    ↓  
    **6. Content Validity Review**  
    ↓  
    **7. Define PLS-SEM Model**  
    ↓  
    **8. Measurement Model**  
    ↓  
    **9. Higher-Order Construct (if applicable)**  
    ↓  
    **10. Structural Model**  
    ↓  
    **11. PLS-SEM Results**  
    ↓  
    **12. Mediation Analysis (if applicable)**  
    ↓  
    **13. Export Results**  
    ↓  
    **14. Save Project**
    """
)

st.success(
    "📌 Not every research project requires every module. "
    "For example, Higher-Order Constructs and Mediation Analysis "
    "should only be used when justified by the research framework."
)

# ============================================================
# 1. GETTING STARTED
# ============================================================

st.header("1️⃣ Getting Started")

st.subheader("📂 Uploading Your Dataset")

st.markdown(
    """
    The application supports:

    - Excel files (`.xlsx`)
    - CSV files (`.csv`)

    Your dataset should normally contain:

    - Rows = respondents/cases
    - Columns = questionnaire items or variables
    - A respondent identifier such as Participant_ID is recommended
    - Likert-scale questionnaire responses should be coded numerically

    ### Example

    | Participant_ID | Q1 | Q2 | Q3 | Q4 |
    |---|---:|---:|---:|---:|
    | P001 | 4 | 5 | 4 | 3 |
    | P002 | 3 | 4 | 4 | 5 |
    | P003 | 5 | 5 | 4 | 4 |
    """
)

st.warning(
    "⚠️ Before statistical analysis, make sure questionnaire coding, "
    "reverse-coded items, missing values, and variable names have "
    "been checked by the researcher."
)

# ============================================================
# 2. DATA QUALITY
# ============================================================

st.header("2️⃣ Data Quality")

st.markdown(
    """
    The Data Quality module helps identify potential problems before
    statistical analysis.

    Important checks include:
    """
)

quality_items = {
    "Respondent Count":
        "The number of observations/respondents in the dataset.",
    "Variable Count":
        "The number of variables/items available for analysis.",
    "Missing Values":
        "Responses that are absent or recorded as missing.",
    "Duplicate Responses":
        "Potentially repeated respondent records.",
    "Empty Rows/Columns":
        "Rows or columns containing no useful data.",
    "Data Types":
        "Whether variables are numeric or non-numeric.",
    "Out-of-Range Values":
        "Values outside the selected Likert-scale range.",
    "Constant Variables":
        "Variables where all respondents have the same value.",
    "Item Completeness":
        "A check of whether questionnaire items contain sufficient usable responses."
}

for term, definition in quality_items.items():
    st.markdown(f"**{term}:** {definition}")

st.info(
    "📌 Data Quality should normally be reviewed before proceeding "
    "to reliability, measurement, or structural analysis."
)

# ============================================================
# 3. DESCRIPTIVE STATISTICS
# ============================================================

st.header("3️⃣ Descriptive Statistics")

st.markdown(
    """
    Descriptive statistics summarize the observed characteristics
    of the dataset.

    ### Important terms

    **Mean**  
    The arithmetic average of the observed values.

    **Median**  
    The middle value when observations are ordered.

    **Standard Deviation (SD)**  
    Indicates how dispersed observations are around the mean.

    **Minimum**  
    The smallest observed value.

    **Maximum**  
    The largest observed value.

    **Frequency**  
    The number of observations associated with a value or category.
    """
)

# ============================================================
# 4. RELIABILITY ANALYSIS
# ============================================================

st.header("4️⃣ Reliability Analysis")

st.markdown(
    """
    Reliability analysis evaluates the internal consistency of
    questionnaire items intended to measure the same construct.

    ### Cronbach's Alpha

    Cronbach's Alpha is a traditional measure of internal consistency.

    In general, higher values indicate greater internal consistency,
    but interpretation should consider the research context, number
    of indicators, and theoretical justification.

    ### Composite Reliability

    Composite Reliability (CR) is commonly reported in PLS-SEM
    measurement-model assessment.

    ### Important principle

    Reliability statistics should not be interpreted in isolation.
    Researchers should consider reliability together with indicator
    loadings, convergent validity, discriminant validity, and theory.
    """
)

# ============================================================
# 5. EXPLORATORY DATA ANALYSIS
# ============================================================

st.header("5️⃣ Exploratory Data Analysis")

st.markdown(
    """
    Exploratory Data Analysis (EDA) helps researchers understand
    patterns, distributions, relationships, and unusual observations
    before formal model interpretation.

    Common visualizations include:

    - Histograms
    - Box plots
    - Bar charts
    - Scatter plots
    - Correlation heatmaps
    - Other exploratory charts
    """
)

# ============================================================
# 6. CONTENT VALIDITY
# ============================================================

st.header("6️⃣ Content Validity Review")

st.markdown(
    """
    Content validity concerns whether questionnaire items adequately
    represent the intended construct or content domain.

    This application supports **qualitative expert review**.

    Experts may be classified, for example, as:

    - Academic experts
    - Industrial/practitioner experts

    The researcher can record the expert's original comment or decision
    and then make a researcher decision:

    - Pending Review
    - Retain
    - Revise
    - Remove

    ### Important

    The system does **not** automatically decide whether an item is
    valid and does **not** automatically rewrite questionnaire items.

    Final decisions remain with the researcher based on expert feedback,
    theory, previous literature, and research objectives.
    """
)

# ============================================================
# 7. PLS-SEM FUNDAMENTALS
# ============================================================

st.header("7️⃣ PLS-SEM Fundamentals")

st.markdown(
    """
    **PLS-SEM** stands for **Partial Least Squares Structural Equation
    Modeling**.

    It is commonly used to analyze relationships among latent
    constructs and their indicators.

    A PLS-SEM model generally contains two major parts:

    ### Measurement Model

    Examines the relationship between constructs and their indicators.

    ### Structural Model

    Examines relationships among constructs.
    """
)

# ============================================================
# 8. CONSTRUCT / DIMENSION / INDICATOR
# ============================================================

st.header("8️⃣ Construct, Dimension, and Indicator")

st.markdown(
    """
    ### Construct

    A theoretical concept that cannot usually be observed directly.

    Examples:

    - Organizational Performance
    - Environmental Performance
    - Innovation Capability

    ### Indicator

    An observed questionnaire item used to measure a construct.

    Example:

    **Construct:** Innovation Capability

    - IC1
    - IC2
    - IC3

    ### Dimension

    A subcomponent of a broader construct.

    Example:

    **Higher-Order Construct:** Environmental Performance

    → Environmental Regulation  
    → Carbon Footprint  
    → Waste Management

    Each dimension can contain its own questionnaire indicators.
    """
)

# ============================================================
# 9. REFLECTIVE VS FORMATIVE
# ============================================================

st.header("9️⃣ Reflective vs Formative Measurement")

with st.expander("🔵 Reflective Measurement", expanded=True):
    st.markdown(
        """
        In a reflective specification, the construct is viewed as
        influencing or reflecting in its observed indicators.

        Example:

        **Construct → Q1, Q2, Q3**

        Indicators are expected to share common variance.

        Common assessment includes:

        - Outer loadings
        - Cronbach's Alpha
        - Composite Reliability
        - AVE
        - Discriminant validity
        """
    )

with st.expander("🟠 Formative Measurement"):
    st.markdown(
        """
        In a formative specification, indicators contribute to or
        form the construct.

        Example:

        **Q1 + Q2 + Q3 → Construct**

        Indicators do not necessarily need to be highly correlated.

        Important diagnostic considerations can include:

        - Collinearity/VIF
        - Indicator relevance
        - Theoretical justification
        """
    )

st.warning(
    "⚠️ Reflective or formative specification should be determined "
    "from theory and the conceptual meaning of the construct, not "
    "simply from statistical results."
)

# ============================================================
# 10. MEASUREMENT MODEL
# ============================================================

st.header("🔟 Measurement Model")

measurement_terms = {
    "Outer Loading":
        "Indicates the strength of the relationship between a reflective indicator and its construct.",
    "Cronbach's Alpha":
        "A measure of internal consistency.",
    "Composite Reliability (CR)":
        "A reliability measure commonly used in PLS-SEM.",
    "Average Variance Extracted (AVE)":
        "A measure of the average amount of variance captured by a construct's indicators.",
    "HTMT":
        "Heterotrait-Monotrait ratio, commonly used as a discriminant-validity assessment.",
    "Fornell–Larcker Criterion":
        "A traditional approach for assessing discriminant validity.",
    "VIF":
        "Variance Inflation Factor, commonly used to assess collinearity."
}

for term, definition in measurement_terms.items():
    st.markdown(f"**{term}:** {definition}")

st.info(
    "📌 Measurement-model decisions should be made using multiple "
    "criteria and theoretical justification rather than relying on "
    "one statistic alone."
)

# ============================================================
# 11. HIGHER-ORDER CONSTRUCTS
# ============================================================

st.header("1️⃣1️⃣ Higher-Order Constructs")

st.markdown(
    """
    A Higher-Order Construct (HOC) represents a broader theoretical
    concept that is composed of multiple dimensions.

    ### Model structure

    **Higher-Order Construct**  
    ↓  
    **Dimensions**  
    ↓  
    **Indicators**

    Example:

    **Environmental Performance**

    ├── Environmental Regulation  
    │   ├── ER1  
    │   ├── ER2  
    │   └── ER3  
    │
    ├── Carbon Footprint  
    │   ├── CF1  
    │   ├── CF2  
    │   └── CF3  
    │
    └── Waste Management  
        ├── WM1  
        ├── WM2  
        └── WM3
    """
)

st.warning(
    "⚠️ A Higher-Order Construct should be theoretically justified. "
    "The software can organize the hierarchy, but the researcher "
    "must establish that the dimensions legitimately represent the "
    "broader construct."
)

# ============================================================
# 12. STRUCTURAL MODEL
# ============================================================

st.header("1️⃣2️⃣ Structural Model")

structural_terms = {
    "Exogenous Construct":
        "A construct that acts as a predictor and has no incoming structural path in the specified model.",
    "Endogenous Construct":
        "A construct that is predicted by one or more other constructs.",
    "Path Coefficient (β)":
        "Represents the estimated direction and strength of a structural relationship.",
    "Hypothesis":
        "A theoretically proposed relationship that can be tested using the structural model.",
    "R²":
        "Represents the proportion of variance in an endogenous construct explained by its predictors.",
    "f²":
        "An effect-size diagnostic describing the contribution of a predictor to an endogenous construct."
}

for term, definition in structural_terms.items():
    st.markdown(f"**{term}:** {definition}")

# ============================================================
# 13. BOOTSTRAPPING
# ============================================================

st.header("1️⃣3️⃣ Bootstrapping")

st.markdown(
    """
    Bootstrapping is a resampling procedure used to estimate the
    sampling uncertainty of model parameters.

    The application uses bootstrap resampling for research-support
    estimation of:

    - Path coefficients
    - Standard errors
    - t-values
    - p-values
    - Confidence intervals

    ### Bootstrap Samples

    A larger number of bootstrap samples can generally provide a more
    stable approximation of the sampling distribution, subject to
    computational resources and the research design.

    ### Confidence Interval

    A confidence interval provides a range of plausible values for
    the estimated effect.
    """
)

# ============================================================
# 14. Q2
# ============================================================

st.header("1️⃣4️⃣ Q² — Predictive Relevance")

st.markdown(
    """
    Q² is used as a predictive-relevance-style diagnostic.

    A positive Q² value can indicate predictive relevance under the
    corresponding cross-validation approach.

    ### Important methodological note

    The Q² implementation in this application is a
    **cross-validated predictive-relevance-style diagnostic**.

    It should **not be described as an exact reproduction of
    SmartPLS blindfolding**.
    """
)

# ============================================================
# 15. MEDIATION
# ============================================================

st.header("1️⃣5️⃣ Mediation Analysis")

st.markdown(
    """
    Mediation analysis examines whether the relationship between an
    independent variable and an outcome operates through a mediator.

    ### Basic model

    **X → M → Y**

    Where:

    - **X** = Predictor / independent variable
    - **M** = Mediator
    - **Y** = Outcome / dependent variable
    """
)

mediation_terms = {
    "Path a":
        "The relationship from X to the mediator M.",
    "Path b":
        "The relationship from M to Y while accounting for X.",
    "Total Effect (c)":
        "The overall relationship between X and Y before accounting for the mediator.",
    "Direct Effect (c′)":
        "The relationship between X and Y after accounting for the mediator.",
    "Indirect Effect (a × b)":
        "The estimated effect of X on Y transmitted through M."
}

for term, definition in mediation_terms.items():
    st.markdown(f"**{term}:** {definition}")

st.subheader("Mediation Interpretation")

st.markdown(
    """
    The application uses the bootstrap confidence interval for the
    indirect effect as an important basis for mediation assessment.

    **Confidence interval excludes zero:**  
    Evidence of an indirect effect.

    **Confidence interval includes zero:**  
    Evidence for the indirect effect is not established under the
    specified analysis.

    The application may classify results as:

    - Full Mediation
    - Partial Mediation
    - No Mediation

    Interpretation should always consider the direct effect,
    indirect effect, total effect, theoretical framework, and
    statistical uncertainty.
    """
)

# ============================================================
# 16. PROJECT MANAGER
# ============================================================

st.header("1️⃣6️⃣ Project Manager")

st.markdown(
    """
    The Project Manager allows the researcher to save and reopen
    project information.

    ### Save Project

    A project can be prepared as an `.aida` project package.

    Depending on the current project state, this can preserve:

    - Dataset
    - PLS-SEM structure
    - Higher-Order Construct structure
    - Structural model
    - Measurement-model decisions
    - Content-validity information
    - Data-quality information
    - Mediation information
    - Other supported analysis state
    """
)

st.warning(
    "🔐 Security note: Project files use a Python-based project "
    "serialization format. Only open `.aida` project files from "
    "trusted sources."
)

st.info(
    "💡 Keep a backup copy of important project files and original "
    "datasets outside the application."
)

# ============================================================
# 17. EXPORTING RESULTS
# ============================================================

st.header("1️⃣7️⃣ Exporting Results")

st.markdown(
    """
    Several analysis pages provide Excel export functionality.

    Exported results can help researchers:

    - Review statistical outputs
    - Prepare thesis tables
    - Document analysis
    - Preserve research results
    - Conduct additional checking

    ### Important

    Exported results should be reviewed by the researcher before being
    inserted into a thesis, dissertation, journal article, or report.
    """
)

# ============================================================
# 18. RESEARCHER RESPONSIBILITY
# ============================================================

st.header("1️⃣8️⃣ Researcher Responsibility")

st.markdown(
    """
    The application is a **research-support tool**.

    The researcher remains responsible for:

    - Selecting appropriate constructs
    - Defining indicators
    - Choosing reflective/formative specifications
    - Establishing theoretical relationships
    - Defining hypotheses
    - Checking data quality
    - Evaluating measurement validity
    - Interpreting structural relationships
    - Reporting methods transparently
    - Justifying methodological decisions
    """
)

st.error(
    "⚠️ Statistical software output should not replace theoretical "
    "reasoning, methodological judgment, or researcher responsibility."
)

# ============================================================
# 19. SMARTPLS METHODOLOGICAL NOTE
# ============================================================

st.header("1️⃣9️⃣ Important Methodological Note")

st.markdown(
    """
    The PLS-SEM and Higher-Order PLS-SEM modules in this application
    provide a **research-support PLS-SEM-style implementation**.

    They use transparent computational procedures including:

    - Composite construct scores
    - Regression-based structural relationships
    - Bootstrap resampling
    - Effect-size diagnostics
    - Cross-validation-style predictive relevance

    These implementations should **not be described as exact
    reproductions of SmartPLS**.

    Researchers should report the actual analytical implementation
    used by this application and provide appropriate methodological
    justification in academic work.
    """
)

# ============================================================
# 20. QUICK GLOSSARY
# ============================================================

st.header("2️⃣0️⃣ Quick Research Glossary")

glossary = {
    "AVE": "Average Variance Extracted.",
    "β": "Path coefficient.",
    "CR": "Composite Reliability.",
    "CVI": "Content Validity Index.",
    "EDA": "Exploratory Data Analysis.",
    "f²": "Effect-size diagnostic.",
    "HOC": "Higher-Order Construct.",
    "HTMT": "Heterotrait-Monotrait ratio.",
    "PLS-SEM": "Partial Least Squares Structural Equation Modeling.",
    "Q²": "Predictive-relevance-style diagnostic.",
    "R²": "Coefficient of determination.",
    "VIF": "Variance Inflation Factor."
}

for term, definition in glossary.items():
    st.markdown(f"**{term}:** {definition}")

# ============================================================
# FINAL RESEARCH CHECKLIST
# ============================================================

st.header("✅ Final Research Checklist")

checklist = [
    "Dataset uploaded and checked",
    "Missing values reviewed",
    "Duplicate records reviewed",
    "Likert-scale coding verified",
    "Descriptive statistics reviewed",
    "Questionnaire reliability assessed",
    "Content validity reviewed by experts where applicable",
    "Constructs theoretically defined",
    "Indicators assigned correctly",
    "Reflective/formative specification justified",
    "Measurement model evaluated",
    "Higher-Order Construct justified where applicable",
    "Structural paths theoretically justified",
    "Hypotheses specified",
    "R² and effect sizes reviewed",
    "Bootstrapping results reviewed",
    "Q² reviewed where applicable",
    "Mediation tested where theoretically applicable",
    "Results exported and checked",
    "Project saved and backed up"
]

for item in checklist:
    st.checkbox(item, key=f"check_{item}")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "AI Data Analysis Agent — User Guide & Research Methodology"
)

st.caption(
    "Designed to support researchers in transparent, structured "
    "data analysis and methodological review."
)
