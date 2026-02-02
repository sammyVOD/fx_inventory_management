import streamlit as st
import altair as alt
# from inventory_engine.inventory_evaluation import recognize_revenue
from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 
from pages.upload import upload_page

# from utils.metrics import summary_metrics
from utils.progress import step_indicator


def summary_metrics(df):
    return {
        "Total Trades": len(df),
        "Total Volume": df[st.session_state.selected_amount_credited].sum(),
        "Total Revenue": df["estimated_revenue"].sum(),
        "Average FX Rate": df[st.session_state.selected_exchange_rate].mean(),
    }

def summary_page(go_to):

    step_indicator(current_step=2)
    st.title("📊 Revenue Summary")

    if "output_df" not in st.session_state:
        st.session_state.output_df = evaluate_fx_recognition_logic(
            trade_df_raw = st.session_state.input_df,
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


    # Pull saved records from session state
    output_df = st.session_state.output_df
    temp_date_column = st.session_state.temp_date_column
    currency_pair_column = st.session_state.ccy_pair_column
    selected_period = st.session_state.recognition_cycle

    metrics = summary_metrics(output_df)

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

    st.subheader(f"Top 20 Records - {selected_period} Period by {currency_pair_column}")
    st.dataframe(output_df.drop(columns=[temp_date_column, "period"]).head(20), width= 'content')

    # Summary visualizations (optional)
    # ## by Currency pair
    st.subheader(f"{selected_period} Estimated Realised Revenue")
    groupby_column = "period"
    chart = alt.Chart(output_df.groupby(groupby_column)["estimated_revenue"].sum().reset_index()).mark_bar().encode(
        x=alt.X(groupby_column, title= "Time Period"),
        y=alt.Y("estimated_revenue", title="Estimated Realised Revenue"),
        )
    st.altair_chart(chart, width='stretch')
    
    st.subheader(f"Estimated Realised Revenue by Revenue Currency")
    groupby_column = "revenue_currency"
    chart = alt.Chart(output_df.groupby(groupby_column)["estimated_revenue"].sum().reset_index()).mark_bar().encode(
        x=alt.X(groupby_column, title="Revenue Currency"),
        y=alt.Y("estimated_revenue", title="Estimated Realised Revenue"),
        )
    st.altair_chart(chart, width='stretch')

    # ## by Time Period
    st.subheader(f"Estimated Realised Revenue Over Time")
    groupby_column = temp_date_column
    chart = alt.Chart(output_df.groupby(groupby_column)["estimated_revenue"].sum().reset_index()).mark_line().encode(
        x=alt.X(groupby_column, title=None),
        y=alt.Y("estimated_revenue", title="Estimated Realised Revenue"),
        )
    st.altair_chart(chart, width='stretch')



    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("⬅ Back", key="summary_page_bottom_section_back_button"):
    #         go_to("upload")

    # with col2:
    #     if st.button("➡ View Detailed Analysis", key="summary_page_bottom_section_details_button"):
    #         go_to("details")