import streamlit as st
import pandas as pd
# from utils.functions import load_file
# from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 
from pages.upload import upload_page
from pages.summary import summary_page
from pages.output_download_page import details_page

# ---------------------------------------
# Page config
# ---------------------------------------
st.set_page_config(
    page_title="FX Revenue Recognition",
    layout="wide"
)

# ---------------------------------------
# Navigation state
# ---------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "upload"



def go_to(page):
    st.session_state.page = page
    st.rerun()

# ---------------------------------------
# Sidebar — File Upload (Global Context)
# ---------------------------------------
st.sidebar.header("Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload FX Trades File",
    type=["csv", "xlsx"]
)

# First upload
if uploaded_file and "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = uploaded_file
    st.rerun()

# Re-upload detected → warn user
if uploaded_file and "uploaded_file" in st.session_state:
    if uploaded_file != st.session_state.uploaded_file:

        st.sidebar.warning(
            "⚠️ A new file has been uploaded.\n\n"
            "This will clear the current evaluation and restart the workflow."
        )

        if st.sidebar.button("Confirm & Restart"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]

            st.session_state.uploaded_file = uploaded_file
            st.session_state.page = "upload"
            st.rerun()

# Manual reset
st.sidebar.divider()
if st.sidebar.button("Reset App"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ---------------------------------------
# Router (Progressive & Locked)
# ---------------------------------------
if st.session_state.page == "upload":
    upload_page(go_to)

elif st.session_state.page == "summary":
    if "input_df" not in st.session_state:
        go_to("upload")
    summary_page(go_to)

elif st.session_state.page == "output_download_page":
    if "output_df" not in st.session_state:
        go_to("summary")
    details_page(go_to)





# # -----------------------
# # Sidebar controls
# # -----------------------













# # A button to trigger evaluation
# st.subheader("🚀 Run FX Revenue Recognition Evaluation")
# if st.button("Start Evaluation"):

#      # -----------------------
#     # Evaluation
#     # -----------------------
#     df_output = evaluate_fx_recognition_logic(
#         trade_df_raw = df_input,
#         date_column = selected_trade_date,
#         ccy_pair_column = selected_ccy_pair,
#         buy_amount_column = selected_amount_debited,
#         buy_currency_column = selected_currency_debited,
#         sell_amount_column = selected_amount_credited,
#         sell_currency_column = selected_currency_credited,
#         exchange_rate_column = selected_exchange_rate,
#         period = selected_time_period,
#         logic_type = recognition_method
#     )

# # -----------------------
# # Summary Page
# # -----------------------

# st.subheader("📊 Revenue Summary")

# metrics = summary_metrics(df_output)

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Total Trades", f"{metrics['Total Trades']:,}")
# col2.metric("Total Volume", f"{metrics['Total Volume (Foreign)']:,.2f}")
# col3.metric(
#     "Total Revenue",
#     f"{metrics['Total Revenue']:,.2f}",
#     delta="Profit" if metrics["Total Revenue"] > 0 else "Loss"
# )
# col4.metric("Avg FX Rate", f"{metrics['Average FX Rate']:.4f}")


# # -----------------------
# # Descriptive Analysis
# # -----------------------

# st.subheader("📈 Descriptive Analysis")

# tab1, tab2 = st.tabs(["Input Stats", "Output Stats"])

# with tab1:
#     st.write("### Input File Statistics")
#     st.dataframe(df_input.describe(include="all").T)

# with tab2:
#     st.write("### Output File Statistics")
#     st.dataframe(df_output.describe(include="all").T)

# # -----------------------
# # Revenue Highlighting
# # -----------------------

# st.subheader("💰 Revenue Breakdown")

# # st.bar_chart(
# #     df_output.groupby(selected_ccy_pair)["FIFO_Revenue_LC"].sum()
# # )

# # st.line_chart(
# #     df_output.set_index(selected_trade_date)["FIFO_Revenue_LC"]
# # )

# # -----------------------
# # Output Data
# # -----------------------

# st.subheader("📤 Output File Preview")
# st.dataframe(df_output.head(), use_container_width=True)

# # -----------------------
# # Download
# # -----------------------

# csv = df_output.to_csv(index=False).encode("utf-8")

# st.download_button(
#     label="⬇️ Download Revenue Recognition Output",
#     data=csv,
#     file_name="fx_revenue_recognition_output.csv",
#     mime="text/csv"
# )