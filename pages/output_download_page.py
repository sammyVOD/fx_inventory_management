import streamlit as st
import io
import pandas as pd
from utils.progress import step_indicator

def details_page(go_to):

    step_indicator(current_step=3)
    st.title("📈 Detailed Analysis")

    # Pull saved records from session state
    output_df = st.session_state.output_df
    temp_date_column = st.session_state.temp_date_column
    currency_pair_column = st.session_state.ccy_pair_column


    output_df = output_df.drop(columns=[temp_date_column, currency_pair_column, "period"])
    st.write(output_df.head(20))


    if st.button("⬅ Back to Summary"):
        go_to("summary")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        output_df.to_excel(writer, index=False, sheet_name="Results")

    st.download_button(
        label="⬇️ Download Excel",
        data=buffer.getvalue(),
        file_name="fx_inventory_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
