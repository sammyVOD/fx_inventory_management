import streamlit as st
import altair as alt
from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 
from pages.upload import upload_page

# from utils.metrics import summary_metrics
from utils.progress import step_indicator


def summary_metrics(df):
    pair_aggregates = {}
    for pair in df["unique_pairs"].unique():
        pair_aggregates[pair] = {
            "trade_count": df[df["unique_pairs"]==pair]["estimated_revenue"].count(), 
            "Revenue": df[df["unique_pairs"]==pair]["estimated_revenue"].sum(),
            "Avg Rate": df[df["unique_pairs"]==pair][st.session_state.traded_rate].mean(),
            "inventory position": df[(df["unique_pairs"]==pair) & (df["last_trade_check"]==True)]["current_inventory_state_details"].values,
        }

    return {
        "Total Trades": len(df),
        "Total Pairs": df[st.session_state.traded_pairs].nunique(),
        f"{st.session_state.recognition_cycle} periods in data": df["period"].nunique(),
        "pair_aggregates": pair_aggregates,

        "Total Traded Volume": df[st.session_state.traded_amount].sum(),
        "Total Revenue": df["estimated_revenue"].sum(),
        "Average FX Rate": df[st.session_state.traded_rate].mean(),
    }

def summary_page(go_to):

    step_indicator(current_step=2)
    st.title("📊 Revenue Summary")

    # st.write(st.session_state)

    if "output_df" not in st.session_state:
        st.session_state.output_df = evaluate_fx_recognition_logic(
            trade_df_raw = st.session_state.input_df,
            date_column = st.session_state.date_column,
            traded_pairs = st.session_state.traded_pairs,
            traded_amount = st.session_state.traded_amount,
            traded_rate = st.session_state.traded_rate,
            trade_direction = st.session_state.trade_direction,
            recognition_cycle = st.session_state.recognition_cycle,
            recognition_method = st.session_state.recognition_method
        )


    # Pull saved records from session state
    output_df = st.session_state.output_df
    temp_date_column = st.session_state.temp_date_column
    currency_pair_column = st.session_state.traded_pairs
    recognition_cycle = st.session_state.recognition_cycle,
    traded_amount = st.session_state.traded_amount
    trade_direction = st.session_state.trade_direction




    metrics = summary_metrics(output_df)
    st.write(metrics)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", metrics["Total Trades"])
    c2.metric("# Traded Pairs", metrics['Total Pairs'])

    if metrics['Total Pairs'] == 1:
        rev_sum = metrics["pair_aggregates"]["A/B"]['Revenue']
        avg_rate = metrics["pair_aggregates"]["A/B"]['Avg Rate']
        c3.metric("Total Revenue", f"{rev_sum:,.2f}")
        c4.metric("Avg FX Rate", f"{avg_rate:.4f}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back"):
            go_to("upload")

    with col2:
        if st.button("➡ View Detailed Analysis"):
            go_to("details")

    st.subheader(f"Top 20 Records - {recognition_cycle} Period by {currency_pair_column}")
    st.dataframe(output_df.drop(columns=[temp_date_column, "period"]).head(20), width= 'content')

    # Summary visualizations (optional)
    # ## by Currency pair
    st.subheader(f"{recognition_cycle} Estimated Realised Revenue")
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