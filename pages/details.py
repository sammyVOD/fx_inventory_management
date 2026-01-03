import streamlit as st
from utils.progress import step_indicator

def details_page(go_to):

    step_indicator(current_step=3)
    st.title("📈 Detailed Analysis")

    df = st.session_state.df_output

    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe().T)

    st.subheader("Revenue Over Time")
    st.line_chart(
        df.set_index("trade_date")["recognized_revenue"]
    )

    st.subheader("Revenue by Currency")
    st.bar_chart(
        df.groupby("currency_pair")["recognized_revenue"].sum()
    )

    if st.button("⬅ Back to Summary"):
        go_to("summary")
