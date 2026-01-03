import streamlit as st
from utils.functions import load_file
from utils.progress import step_indicator
from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 

def init_upload_state(df):
    defaults = {
        "selected_trade_date": df.columns[0],
        "selected_exchange_rate": df.columns[0],
        "selected_ccy_pair": df.columns[0],
        "selected_amount_debited": df.columns[0],
        "selected_amount_credited": df.columns[0],
        "selected_currency_debited": df.columns[0],
        "selected_currency_credited": df.columns[0],
        "recognition_method": df.columns[0],
        "selected_time_period": df.columns[0],
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def upload_page(go_to):

    step_indicator(1)
    st.title("Configure FX Revenue Recognition")

    if "uploaded_file" not in st.session_state:
        st.warning("Upload a file from the sidebar to continue.")
        return
        

    if "df_input" not in st.session_state:
        st.session_state.df_input = load_file(st.session_state.uploaded_file)

    df = st.session_state.df_input

    st.dataframe(df.head(), use_container_width=True)
    # st.write(["Select a Column ..."] + df.columns.tolist())

    # Pick the needed columns that should do what from the shared input file
    init_upload_state(df)
    with st.expander("🧩 Column Mapping", expanded=False):
        c1, c2 = st.columns(2)

        with c1:
            selected_trade_date = st.selectbox(
                "Identify the Date Column", ["Select a Column ..."] + df.columns.tolist(), key="trade_date_selectbox"
            )
            selected_exchange_rate = st.selectbox(
                "What Column tells us the rate of conversion used for this conversion", ["Select a Column ..."] + df.columns.difference([selected_trade_date], sort=False).tolist(), key="exchange_rate_selectbox"
            )
            selected_ccy_pair = st.selectbox(
                "What Column tells us the Currency Pair invovled in this conversion", ["Select a Column ..."] + df.columns.difference([selected_trade_date, selected_exchange_rate], sort=False).tolist(), key="ccy_pair_selectbox"
            )
            selected_amount_debited = st.selectbox(
                "What Column tells us the amount to be converted", ["Select a Column ..."] + df.columns.difference([selected_trade_date, selected_exchange_rate, selected_ccy_pair], sort=False).tolist(), key="amount_debited_selectbox"
            )

        with c2:
            selected_amount_credited = st.selectbox(
                "What Column tells us the amount to be credited to the customer", ["Select a Column ..."] + df.columns.difference([selected_trade_date, selected_exchange_rate, selected_ccy_pair, selected_amount_debited], sort=False).tolist(),key="amount_credited_selectbox"
            )
            selected_currency_debited = st.selectbox(
                "What Column tells us the currency to be converted", ["Select a Column ..."] + df.columns.difference([selected_trade_date, selected_exchange_rate, selected_ccy_pair, selected_amount_debited, selected_amount_credited], sort=False).tolist(), key="currency_debited_selectbox"
            )
            selected_currency_credited = st.selectbox(
                "What Column tells us the currency to be credited to the customer", ["Select a Column ..."] + df.columns.difference([selected_trade_date, selected_exchange_rate, selected_ccy_pair, selected_amount_debited, selected_amount_credited, selected_currency_debited], sort=False).tolist(), key="currency_credited_selectbox"
            )


    expected_column_mapping = [
        selected_trade_date,
        selected_exchange_rate,
        selected_ccy_pair,
        selected_amount_debited,
        selected_amount_credited,
        selected_currency_debited,
        selected_currency_credited
    ]
    if any([col.startswith("Select a Column") for col in expected_column_mapping]):
        st.warning("Please complete the column mapping to proceed.")
        st.stop()


    with st.expander("⚙ Recognition Method & Time Period", expanded=True):
        c3, c4 = st.columns(2)
        with c3:
            recognition_method = st.selectbox(
                "Revenue Recognition Method",
                ["FIFO", "LIFO", "Weighted Average"]
            )
        with c4:
            selected_time_period = st.selectbox(
                "Select Time Period for Recognition",
                ["Select Frequency of Revenue Recognition...", "Yearly", "Quarterly", "Monthly", "Weekly", "Daily"]
            )


    if selected_time_period.startswith("Select Frequency"):
        st.warning("Please select the time period for revenue recognition to proceed.")
        st.stop()


    if st.button("▶ Run Evaluation"):

        # -----------------------
        # Evaluation
        # -----------------------
        df_output = evaluate_fx_recognition_logic(
            trade_df_raw = df,
            date_column = selected_trade_date,
            ccy_pair_column = selected_ccy_pair,
            buy_amount_column = selected_amount_debited,
            buy_currency_column = selected_currency_debited,
            sell_amount_column = selected_amount_credited,
            sell_currency_column = selected_currency_credited,
            exchange_rate_column = selected_exchange_rate,
            period = selected_time_period,
            logic_type = recognition_method
        )
        st.session_state.df_output = df_output

        st.session_state.selected_trade_date = selected_trade_date
        st.session_state.selected_exchange_rate = selected_exchange_rate
        st.session_state.selected_ccy_pair = selected_ccy_pair
        st.session_state.selected_amount_debited = selected_amount_debited
        st.session_state.selected_amount_credited = selected_amount_credited
        st.session_state.selected_currency_debited = selected_currency_debited
        st.session_state.selected_currency_credited = selected_currency_credited
        st.session_state.recognition_method = recognition_method
        st.session_state.selected_time_period = selected_time_period

        st.session_state.column_map = {

            "selected_trade_date": st.session_state.selected_trade_date,
            "selected_exchange_rate": st.session_state.selected_exchange_rate,
            "selected_ccy_pair": st.session_state.selected_ccy_pair,
            "selected_amount_debited": st.session_state.selected_amount_debited,
            "selected_amount_credited": st.session_state.selected_amount_credited,
            "selected_currency_debited": st.session_state.selected_currency_debited,
            "selected_currency_credited": st.session_state.selected_currency_credited,
            "recognition_method": st.session_state.recognition_method,
            "selected_time_period": st.session_state.selected_time_period,

            "df_input": st.session_state.df_input,
            "df_output": st.session_state.df_output,


        }
        go_to("summary")

        # st.session_state.column_map = expected_column_mapping
        # st.session_state.method = recognition_method
        # st.session_state.df_output = df_output
        # st.session_state.df_input = df
        # st.session_state.period = selected_time_period

        # st.session_state.selected_amount_credited = selected_amount_credited
        # st.session_state.selected_exchange_rate = selected_exchange_rate

        # go_to("summary")

