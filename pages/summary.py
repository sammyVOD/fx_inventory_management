import streamlit as st
# from inventory_engine.inventory_evaluation import recognize_revenue
from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 
from pages.upload import upload_page

# from utils.metrics import summary_metrics
from utils.progress import step_indicator


def summary_metrics(df):
    return {
        "Total Trades": len(df),
        "Total Volume": df[st.session_state.selected_amount_credited].sum(),
        "Total Revenue": df["FIFO_Revenue_LC"].sum(),
        "Average FX Rate": df[st.session_state.selected_exchange_rate].mean(),
    }

def summary_page(go_to):

    step_indicator(current_step=2)
    st.title("📊 Revenue Summary")

    # df_out = evaluate_fx_recognition_logic(
    #     st.session_state.df_input,
    #     st.session_state.method,
    #     st.session_state.column_map
    # )

    # st.session_state.df_output = df_out

    if "df_output" not in st.session_state:
        st.session_state.df_output = evaluate_fx_recognition_logic(
            trade_df_raw = st.session_state.df_input,
            date_column = st.session_state.selected_trade_date,
            ccy_pair_column = st.session_state.selected_ccy_pair,
            buy_amount_column = st.session_state.selected_amount_debited,
            buy_currency_column = st.session_state.selected_currency_debited,
            sell_amount_column = st.session_state.selected_amount_credited,
            sell_currency_column = st.session_state.selected_currency_credited,
            exchange_rate_column = st.session_state.selected_exchange_rate,
            period = st.session_state.selected_time_period,
            logic_type = st.session_state.recognition_method
        )


    df_out = st.session_state.df_output

    metrics = summary_metrics(df_out)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", metrics["Total Trades"])
    c2.metric("Total Volume", f"{metrics['Total Volume']:,.2f}")
    c3.metric("Total Revenue", f"{metrics['Total Revenue']:,.2f}")
    c4.metric("Avg FX Rate", f"{metrics['Average FX Rate']:.4f}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back"):
            go_to("upload")

    with col2:
        if st.button("➡ View Detailed Analysis"):
            go_to("details")
