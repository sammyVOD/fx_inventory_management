import streamlit as st
from pathlib import Path
from utils.progress import step_indicator



def render(go_to):
    step_indicator(1)

    st.title("ℹ️ How This FX Revenue Tool Works")

    st.markdown("""
    ### Why this step matters

    We understand that FX transaction data can arrive in **different structures**
    depending on:
    - Your trading system/Business Model
    - Internal reporting standards
    - Even your Bank / counterparty

    Instead of forcing a single rigid format, this tool supports **multiple known schemas**. See supported input formats below
    """)

    st.markdown("---")

    st.subheader("✅ Supported Input Formats")
    st.caption("Sample files are provided for testing and demonstration purposes.")

    base_img = Path("assets/screenshots")
    base_sample = Path("assets/sample_files")


    formats = {
        "Format A — Trade-Level": {
            "desc": """
            - One row per FX trade  
            - Explicit buy/sell direction  
            - Trade date, rate, notional
            """,
            "image": base_img / "Screenshot_1.png",
            "sample": base_sample / "format_1.csv"
        },
        "Format B — Ledger-Style": {
            "desc": """
            - One row per posting  
            - Signed amounts  
            - Currency pair inferred
            """,
            "image": base_img / "Screenshot_2.png",
            "sample": base_sample / "format_2.csv"
        },
        # "Format C — Settlement-Based": {
        #     "desc": """
        #     - Cash-flow focused  
        #     - Separate legs per currency  
        #     - Requires normalization
        #     """,
        #     "image": base_img / "Screenshot_1.png",
        #     "sample": base_sample / "format_3.csv"
        # }
    }


    # -----------------------------
    # Display formats
    # -----------------------------
    for name, info in formats.items():
        with st.expander(name, expanded=False):

            st.markdown(info["desc"])

            # Screenshot
            if info["image"].exists():
                st.image(
                    str(info["image"]),
                    caption=f"Example layout for {name}",
                    width='stretch'
                )
            else:
                st.warning("Screenshot not available.")

            # Sample download
            if info["sample"].exists():
                with open(info["sample"], "rb") as f:
                    st.download_button(
                        label="⬇ Download Sample File",
                        data=f,
                        file_name=info["sample"].name,
                        mime="text/csv"
                    )
            else:
                st.warning("Sample file not available.")

    st.markdown("---")

    # -----------------------------
    # Schema Selection
    # -----------------------------
    st.subheader("📌 Select Your Input Format")

    schema = st.radio(
        "Choose the format that best matches your file:",
        options=list(formats.keys()),
        key="input_schema_choice"
    )

    st.info(
        "Your selection determines how your data is standardized before revenue recognition."
    )

    # st.session_state.input_schema = schema
    # -----------------------------
    # Continue Button
    # -----------------------------
    if st.button("➡️ Continue to Upload"):
        st.session_state.input_schema = schema
        st.session_state.page = "upload"
        st.rerun()

        go_to("upload")
