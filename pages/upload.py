import streamlit as st
import pandas as pd
import numpy as np
from utils.functions import load_file, init_upload_state
# from utils.progress import step_indicator
from inventory_engine.inventory_evaluation import evaluate_fx_recognition_logic 

def upload_page(go_to):

    # step_indicator(1)
    st.title("Configure FX Revenue Recognition")

    if "uploaded_file" not in st.session_state:
        st.warning("Upload a file from the sidebar to continue.")
        return
        

    if "input_df" not in st.session_state:
        st.session_state.original_input_df = load_file(st.session_state.uploaded_file)

    original_input_df = st.session_state.original_input_df
    selected_input_schema = st.session_state.input_schema
    input_df = st.session_state.original_input_df.copy()
    st.session_state.input_df = input_df

    st.dataframe(input_df.head(), width='stretch')
    # st.write(["Select a Column ..."] + df.columns.tolist())

    # Initialize states across all columns that will play a part
    init_upload_state(input_df)

    # Pick the needed columns that should do what from the shared input file
    with st.expander("🧩 Column Mapping", expanded=False):
        selected_columns = []

        if "Format A" in selected_input_schema:
            # ROW 1
            c1, c2 = st.columns(2)
            with c1:
                selected_trade_direction = st.selectbox(
                    "Identify the Trade Direction Column", ["Select a Column ..."] + input_df.columns.tolist(), key="trade_direction_selectbox"
                )
                selected_columns.append(selected_trade_direction)
            with c2:
                selected_trade_amount = st.selectbox(
                    "Identify the Trade Amount Column", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="trade_amount_selectbox"
                )
                selected_columns.append(selected_trade_amount)            
            
            # ROW 2
            c1, c2 = st.columns(2)
            with c1:
                selected_trade_date = st.selectbox(
                    "Identify the Date Column", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="trade_date_selectbox"
                )
                selected_columns.append(selected_trade_date)
            with c2:
                selected_trade_rate = st.selectbox(
                    "Identify Trade Rate Column", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="trade_rate_selectbox"
                )
                selected_columns.append(selected_trade_rate)

            expected_column_mapping = [
                selected_trade_direction,
                selected_trade_amount,
                selected_trade_date,
                selected_trade_rate
            ]

        elif "Format B" in selected_input_schema:
            # ROW 1
            c1, c2 = st.columns(2)
            with c1:
                selected_trade_date = st.selectbox(
                    "Identify the Date Column", ["Select a Column ..."] + input_df.columns.tolist(), key="trade_date_selectbox"
                )
                selected_columns.append(selected_trade_date)
            # with c2:
            #     selected_trade_rate = st.selectbox(
            #         "Identify Trade Rate Column", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="trade_rate_selectbox"
            #     )
            #     selected_columns.append(selected_trade_rate)
            
            # ROW 2
            c1, c2 = st.columns(2)
            with c1:
                selected_currency_debited = st.selectbox(
                    "Identify Currency To Convert From", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="currency_debited_selectbox"
                )
                selected_columns.append(selected_currency_debited)
            with c2:
                selected_amount_debited = st.selectbox(
                    "Identify Amount Before FX Conversion", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="amount_debited_selectbox"
                )
                selected_columns.append(selected_amount_debited)

            # ROW 3
            c1, c2 = st.columns(2)
            with c1:
                selected_currency_credited = st.selectbox(
                    "Identify Currency To Convert To", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(), key="currency_credited_selectbox"
                )
                selected_columns.append(selected_currency_credited)
            with c2:
                selected_amount_credited = st.selectbox(
                    "Identify Amount After FX Conversion", ["Select a Column ..."] + input_df.columns.difference(selected_columns, sort=False).tolist(),key="amount_credited_selectbox"
                )
                selected_columns.append(selected_amount_credited)


            expected_column_mapping = [
                selected_trade_date,
                # selected_trade_rate,
                selected_currency_debited,
                selected_amount_debited,
                selected_currency_credited,
                selected_amount_credited,
            ]


    if any([col.startswith("Select a Column") for col in expected_column_mapping]):
        st.warning("Please complete the column mapping to proceed.")
        st.stop()


    # Extra Computations
    if "Format B" in selected_input_schema:
        selected_trade_rate = "trade_rate_temp_column"
        input_df[selected_trade_rate] = input_df[selected_amount_debited] / input_df[selected_amount_credited]
    
        selected_trade_direction = "trade_direction_temp_column"
        input_df[selected_trade_direction] = (
            np.where(
                input_df[selected_trade_rate] < 1
                ,"Buy"
                ,"Sell"
            )
        )

        selected_trade_amount = "trade_amount_temp_column"
        input_df[selected_trade_amount] = (
            np.where(
                input_df[selected_amount_debited] < input_df[selected_amount_credited]
                , input_df[selected_amount_debited]
                , input_df[selected_amount_credited]
            )
        )

        traded_pairs_temp_column = "traded_pairs_temp_column"      
        input_df[traded_pairs_temp_column] = input_df[selected_currency_debited].str.strip() + "-" +  input_df[selected_currency_credited].str.strip()

        # Convert required columns to appropriate data types
        input_df[selected_amount_debited] = pd.to_numeric(input_df[selected_amount_debited], errors='coerce')
        input_df[selected_amount_credited] = pd.to_numeric(input_df[selected_amount_credited], errors='coerce')
    else:
        traded_pairs_temp_column = "traded_pairs_temp_column"
        input_df[traded_pairs_temp_column] = "A-B"

    # ensure the date column is datetime indeed
    input_df[selected_trade_date] = pd.to_datetime(input_df[selected_trade_date], errors='coerce')
    input_df[selected_trade_amount] = pd.to_numeric(input_df[selected_trade_amount], errors='coerce')
    input_df[selected_trade_rate] = pd.to_numeric(input_df[selected_trade_rate], errors='coerce')
    input_df[selected_trade_direction] = input_df[selected_trade_direction].str.strip()
    # input_df[traded_pairs_temp_column]
    
    with st.expander("⚙ Recognition Method & Time Period", expanded=True):
        c3, c4 = st.columns(2)
        with c3:
            recognition_method = st.selectbox(
                "Revenue Recognition Method",
                ["Select Revenue Recognition Method...", "FIFO", "LIFO", "Weighted Average"]
            )

            if recognition_method not in ['FIFO', 'Select Revenue Recognition Method...']:
                st.warning(f"The logic type {recognition_method} is not yet implemented. Please select FIFO Logic.")
                st.stop()

        with c4:
            recognition_cycle = st.selectbox(
                "Select Time Period for Recognition",
                ["Select Cycle of Revenue Recognition...", "Yearly", "Quarterly", "Monthly", "Weekly", "Daily"]
            )


    if recognition_method.startswith("Select Revenue"):
        st.warning("Please select the desired methodology to use for this revenue recognition process.")
        st.stop()
    elif recognition_cycle.startswith("Select Cycle"):
        st.warning("Please select the time period for revenue recognition to proceed.")
        st.stop()


    if "evaluation_done" not in st.session_state:
        st.session_state.evaluation_done = False

    start_eval = st.button("▶ Run Evaluation")
    if start_eval:

        # -----------------------
        # Evaluation
        # -----------------------
        st.write(f"⏳Running the {recognition_method} model")
        output_df = evaluate_fx_recognition_logic(
            trade_df_raw = input_df,
            date_column = selected_trade_date,
            traded_pairs = traded_pairs_temp_column,
            traded_amount = selected_trade_amount,
            traded_rate = selected_trade_rate,
            trade_direction = selected_trade_direction,
            period = recognition_cycle,
            logic_type = recognition_method
        )
        st.session_state.output_df = output_df

        st.session_state.date_column = selected_trade_date
        st.session_state.traded_pairs = traded_pairs_temp_column
        st.session_state.traded_amount = selected_trade_amount
        st.session_state.traded_rate = selected_trade_rate
        st.session_state.trade_direction = selected_trade_direction
        st.session_state.recognition_method = recognition_method
        st.session_state.recognition_cycle = recognition_cycle

        st.session_state.column_map = {

            "selected_trade_date": st.session_state.selected_trade_date,
            "selected_trade_pairs": st.session_state.traded_pairs,
            "selected_trade_amount": st.session_state.traded_amount,
            "selected_trade_rate": st.session_state.traded_rate,
            "selected_trade_direction": st.session_state.trade_direction,
            "recognition_method": st.session_state.recognition_method,
            "recognition_cycle": st.session_state.recognition_cycle,

            "input_df": st.session_state.input_df,
            "output_df": st.session_state.output_df,
            "original_input_df": st.session_state.original_input_df

        }

        st.session_state.evaluation_done = True

        # Show proceed section AFTER evaluation
        if st.session_state.evaluation_done:
            st.success("Evaluation Complete! Proceed to a Summary Report")

    if st.session_state.evaluation_done and st.button("PROCEED"):
        st.session_state.page = "output_summary"
        st.rerun()
        go_to("output_summary")
