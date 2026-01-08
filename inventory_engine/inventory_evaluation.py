import streamlit as st
import pandas as pd
from utils.functions import get_quarter_year, get_start_of_week
from inventory_engine.fifo_engine import run_fifo_engine

def evaluate_fx_recognition_logic(trade_df_raw, date_column, ccy_pair_column:str, buy_amount_column:float, buy_currency_column:str, sell_amount_column:float, sell_currency_column:str, exchange_rate_column:float, period:str, logic_type):

# ########### ########### PERIOD EVALUATION - START ########### ########### #
    if period == "Yearly":
        trade_df_raw["period"] = pd.to_datetime(trade_df_raw[date_column], format="mixed").dt.strftime('%Y')
    elif period == "Quarterly":
        trade_df_raw["period"] = get_quarter_year(trade_df_raw[date_column])
    elif period == "Monthly":
        trade_df_raw["period"] = pd.to_datetime(trade_df_raw[date_column], format="mixed").dt.strftime('%b %Y')
    elif period == "Weekly":
        trade_df_raw["period"] = get_start_of_week(trade_df_raw[date_column], start_day = 'FRI')
    elif period == "Daily":
        trade_df_raw["period"] = pd.to_datetime(trade_df_raw[date_column], format="mixed").dt.strftime('%d %b %Y')
    else : # Default to Monthly
        trade_df_raw["period"] = pd.to_datetime(trade_df_raw[date_column], format="mixed").dt.strftime('%b %Y')

# ########### ########### PERIOD EVALUATION - END ########### ########### #

    trade_df = trade_df_raw.copy()
    model_output = pd.DataFrame({})

    temp_date_column = "temp_date"
    st.session_state['temp_date_column'] = temp_date_column

    # Sort in ascending order
    trade_df = trade_df.sort_values(by=date_column, ascending=True)
    trade_df.loc[:, temp_date_column] = pd.to_datetime(trade_df[date_column]).dt.date


    for period in trade_df["period"].unique():
        st.write(f"Working on the {logic_type} Logic evaluation for {period}")

        if logic_type == "FIFO":
            output_i = run_fifo_engine(
                trade_df = trade_df[trade_df["period"]==period],
                date_column= date_column,
                ccy_pair= ccy_pair_column,
                buy_amount= buy_amount_column,
                buy_currency= buy_currency_column,
                sell_amount= sell_amount_column,
                sell_currency= sell_currency_column,
                exchange_rate= exchange_rate_column
            )
            st.write(f"    Shape of {period} after {logic_type} computations is: {output_i.shape}")
            model_output = pd.concat([model_output, output_i], ignore_index=True)
            st.write(f"    {logic_type} Logic evaluation for {period} - COMPLETED")
        

        else:
            return st.write(f"The logic type {logic_type} is not yet implemented. Please select FIFO Logic.")
        
            break
            


    st.write(f"The Final Shape after Evaluation is => {model_output.shape}.\nSee sample view of the output")
    st.dataframe(model_output.head())

    return model_output