import pandas as pd
import numpy as np
from utils.functions import get_quarter_year, get_start_of_week, get_unique_pairs


def run_fifo_engine(trade_df, date_column, traded_pairs, traded_amount, traded_rate, trade_direction):
    model_ouput = pd.DataFrame({})

    trade_df = get_unique_pairs(
        df = trade_df,
        currencypair = traded_pairs
    )



    for unique_pair in trade_df["unique_pairs"].unique(): #  Loop through all currency pairs in the table
        # Pick a currency Pair
        df_ = trade_df[trade_df["unique_pairs"] == unique_pair]

        df_ = df_.sort_values(by=date_column, ascending=True)

        # Convert Columns to numpy to make it easier to interact with
        fx_type_numpy = df_[trade_direction].to_numpy()
        trade_amount_numpy = df_[traded_amount].to_numpy()
        exchange_rate_numpy = df_[traded_rate].to_numpy() 


        a = df_[df_["unique_pairs"] == unique_pair]
        # display(a.head())
        b = a.groupby(traded_pairs)[traded_rate].mean().reset_index()
        first_pair = b[traded_pairs].values[0]

        first_rate_used = b[b[traded_pairs] == first_pair][traded_rate].values[0]
        # print(first_pair, first_rate_used)
        base_currency = (
            np.where(
                first_rate_used > 1
                ,first_pair.split("-")[1]
                ,first_pair.split("-")[0]
            )
        )


        revenue_currency = (
            np.where(
                unique_pair == f"{base_currency}/{base_currency}"
                , base_currency
                , str(unique_pair).replace(str(base_currency), "").replace("/", "").strip()
            )
        )
        print(f"base_currency {base_currency}, revenue_currency {revenue_currency}")
        # df_["FX Type"] = (
        #     np.where(
        #         df_[traded_pairs].str[:3] == base_currency
        #         ,"Buy", "Sell"
        #     )
        # )

        # fx_type_numpy = df_["FX Type"].to_numpy()


        inventory_list_recent_state = []
        inventory_of_shorts__fx_sales = []
        inventory_of_longs____fx_buys = []
        shorts____fx_sales = 0
        longs______fx_buys = 0
        last_buy_rate = 0

        current_inventory_state_details = ''
        shorts_detail = ''
        longs_detail = ''

        number_of_records = len(df_)

        traded_amount = np.empty(number_of_records, dtype= np.result_type(float))
        inventory_amount = np.empty(number_of_records, dtype= np.result_type(float))
        inventory_state = np.empty(number_of_records, dtype= np.result_type(dict))
        ccy_inventory_state_after_txn_list = np.empty(number_of_records, dtype= np.result_type(dict))
        # cumm_inventory_stage_after_trade = np.empty(number_of_records, dtype= np.result_type(list))
        # amount_in_long_or_short = np.empty(number_of_records, dtype= np.result_type(list))


        computed_revenue_lc = np.empty(number_of_records, dtype= np.result_type(float)) # Initialize an dict to hold the records of the Computed Revenue in Local Currency
        revenue_calc_formula = np.empty(number_of_records, dtype= np.result_type(str)) # Initialize an str to hold the implemented revenue formula
        current_inventory_state = np.empty(number_of_records, dtype= np.result_type(str)) # Initialize an str to hold the final state positions of shorts and longs
        current_inventory_state_details = np.empty(number_of_records, dtype= np.result_type(str)) # Initialize an str to hold the details of all the rates of shorts and longs
        last_state_identifier = np.empty(number_of_records, dtype=bool)

        WAR = np.empty(number_of_records, dtype= np.result_type(float))
        unrealized_revenue_with_WAR_formula = np.empty(number_of_records, dtype= np.result_type(str))


        # print(f"    --Running for the {unique_pair} pair")
        # MAIN CALCULATIONS
        for row_index in range(number_of_records):
            revenue_calc_formula[row_index] = ''
            computed_revenue_lc[row_index] = 0.0
            current_inventory_state[row_index] = ''

            # if exchange_rate_numpy[row_index] == 0:
            #     rate_inverse_for_comparism = 0
            if exchange_rate_numpy[row_index] > 1:
                rate_inverse_for_comparism = exchange_rate_numpy[row_index]
            else:
                rate_inverse_for_comparism = 1/exchange_rate_numpy[row_index]

            if fx_type_numpy[row_index] == "Buy":
                inventory_amount[row_index] = inventory_amount[row_index - 1] + trade_amount_numpy[row_index] # Update Inventory with this amount (addition to inventory)

                trade_info = {
                    "row_id": row_index,
                    "base_amount": trade_amount_numpy[row_index],
                    "rates": rate_inverse_for_comparism,
                    "trade_type" : "Buy"
                }
                traded_amount[row_index] = trade_amount_numpy[row_index]
                inventory_of_longs____fx_buys += [trade_info]
                longs______fx_buys += trade_amount_numpy[row_index]

                

# current_inventory_state[row_index] = []
                break_outer_buy_loop = False
                while (round(shorts____fx_sales, 8) > 0) & (len(inventory_of_longs____fx_buys) > 0):
                    # print(f"row_index: {row_index}; current buy inventory: {inventory_of_longs____fx_buys} ... existing sell inventory {inventory_of_shorts__fx_sales}")
                    
                    for buy_inventory_id in range(len(inventory_of_longs____fx_buys)):
                        # print(f"dfadsf - Buy {inventory_of_longs____fx_buys[buy_inventory_id]["base_amount"]}")
                        buy_records = inventory_of_longs____fx_buys[buy_inventory_id]
                        amount_bought_i = buy_records["base_amount"]
                        rates_bought_i = buy_records["rates"]
                        # print(f"longs______fx_buys {longs______fx_buys}, sales_inven_len {len(inventory_of_shorts__fx_sales)} details as inventory_of_shorts__fx_sales: {inventory_of_shorts__fx_sales} ")

                        if len(inventory_of_shorts__fx_sales) == 0:
                            # print("Hi")
                            break_outer_buy_loop = True
                            break

                        # if round(longs______fx_buys, 8) > 0:
                        break_inner_buy_loop = False
                        while (round(longs______fx_buys, 8) >0) & (len(inventory_of_shorts__fx_sales) > 0):
                            # for sell_inventory_id in range(len(inventory_of_shorts__fx_sales)): 
                            sell_records = inventory_of_shorts__fx_sales[0]
                            amount_sold_i = sell_records["base_amount"]
                            rates_sold_i = sell_records["rates"]

                            # REV Cal
                            if amount_bought_i >= amount_sold_i:
                                # print(f"here...amount_bought {amount_bought_i}")
                                revenue_calc_formula[row_index] += f"{amount_sold_i:.2f} bought at {rates_bought_i:.4f} but sold at {rates_sold_i:.4f} \n"
                                computed_revenue_lc[row_index] += (amount_sold_i * rates_sold_i) - (amount_sold_i * rates_bought_i)
                                # print(f"row_index: {row_index}; rev_cal {revenue_calc_formula[row_index]}")
                                # print(f"row_index: {row_index}; computed_rev {computed_revenue_lc[row_index]}")


                                # amount_sold_i -= amount_bought_i # No need for this as I will pop the element from list in next line
                                inventory_of_shorts__fx_sales.pop(0)
                                inventory_of_longs____fx_buys[buy_inventory_id]["base_amount"] -= amount_sold_i
                                
                                longs______fx_buys -= amount_sold_i
                                # print(f"before: {shorts____fx_sales}")
                                shorts____fx_sales -= amount_sold_i
                                # print(f"after: {shorts____fx_sales}")

                                
                                amount_bought_i -= amount_sold_i

                                # shorts_detail += f"{round(shorts____fx_sales, 8):,.4f} @ {rates_sold_i:,.8f}; " if round(shorts____fx_sales, 8) > 0 else ""
                                # longs_detail  += f"{round(longs______fx_buys, 8):,.4f} @ {rates_bought_i:,.8f}; " if round(longs______fx_buys, 8) > 0 else ""


                            
                            else:
                                # print(f"here 2...Buy")

                                if len(inventory_of_longs____fx_buys) == 0:
                                    break_inner_buy_loop = True
                                    break
                                
                                # print(f"inventory_of_longs____fx_buys {inventory_of_longs____fx_buys}")
                                revenue_calc_formula[row_index] += f"{amount_bought_i:.2f} bought at {rates_bought_i:.4f} but sold at {rates_sold_i:.4f} \n"
                                computed_revenue_lc[row_index] += (amount_bought_i * rates_sold_i) - (amount_bought_i * rates_bought_i)
                                # print(f"row_index: {row_index}; rev_cal {revenue_calc_formula[row_index]}")
                                # print(f"row_index: {row_index}; computed_rev {computed_revenue_lc[row_index]}")

                                amount_sold_i -= amount_bought_i
                                inventory_of_shorts__fx_sales[0]["base_amount"] -= amount_bought_i
                                inventory_of_longs____fx_buys.pop(buy_inventory_id)

                                longs______fx_buys -= amount_bought_i
                                # print(f"before: {shorts____fx_sales}....")
                                shorts____fx_sales -= amount_bought_i
                                # print(f"after: {shorts____fx_sales}")

                                
                                amount_bought_i -= amount_bought_i


                            if break_inner_buy_loop == True:
                                break



                            # print(f"After first evaluation, longs______fx_buys {longs______fx_buys}; shorts____fx_sales {shorts____fx_sales}, sales_inv {inventory_of_shorts__fx_sales}, buy inv {inventory_of_longs____fx_buys}")

                    if break_outer_buy_loop == True:
                        break
                # print(f"revenue_calc_formula:- {revenue_calc_formula[row_index]} computed_revenue_lc:- {computed_revenue_lc[row_index]}")

                current_inventory_state[row_index] = f"Short: {round(shorts____fx_sales, 8):,.2f} \n Long: {round(longs______fx_buys, 8):,.2f}"
                # current_inventory_state[row_index] = f"Short: {round(shorts____fx_sales, 8)} => ({shorts_detail}) \n Long: {round(longs______fx_buys, 8)} => ({longs_detail})"

                # for sell_trades in inventory_of_shorts__fx_sales:
                #     shorts_detail = f"{sell_trades["base_amount"]:,.4f} to be sold @ {sell_trades["rates"]:,.8f} \n"
                # for buy_trades in inventory_of_longs____fx_buys:
                #     longs_detail = f"{buy_trades["base_amount"]:,.4f} bought @ {buy_trades["rates"]:,.8f} \n"

                # current_inventory_state_details[row_index] = f"Sell Position: {shorts_detail} \n Buy Position: {longs_detail}"



                    



            elif fx_type_numpy[row_index] == "Sell":
                inventory_amount[row_index] = inventory_amount[row_index - 1] - trade_amount_numpy[row_index] # Update Inventory with this amount (addition to inventory)

                
                trade_info = {
                    "row_id": row_index,
                    "base_amount": trade_amount_numpy[row_index],
                    "rates": rate_inverse_for_comparism, # exchange_rate_numpy[row_index] if exchange_rate_numpy[row_index] > 1  else (1/exchange_rate_numpy[row_index]),
                    "trade_type": "Sell"
                }

                inventory_of_shorts__fx_sales += [trade_info]
                shorts____fx_sales += trade_amount_numpy[row_index]
                traded_amount[row_index] = trade_amount_numpy[row_index]

                break_outer_sell_loop = False
                while (round(longs______fx_buys, 8) > 0) & (len(inventory_of_shorts__fx_sales) > 0):# & (len(inventory_of_longs____fx_buys)) > 0:
                    # print(f"row_index: {row_index}; current Sell inventory: {inventory_of_shorts__fx_sales}... existing buy inventory {inventory_of_longs____fx_buys}")
                    
                    for sell_inventory_id in range(len(inventory_of_shorts__fx_sales)):
                        # print(f"dfadsf - Sell {inventory_of_shorts__fx_sales[sell_inventory_id]["base_amount"]}")
                        sell_records = inventory_of_shorts__fx_sales[sell_inventory_id]
                        amount_sold_i = sell_records["base_amount"]
                        rates_sold_i = sell_records["rates"]
                        # print(f"shorts____fx_sales {shorts____fx_sales}, buy_inven_len {len(inventory_of_longs____fx_buys)} details as inventory_of_longs____fx_buys: {inventory_of_longs____fx_buys} ")
                        
                        if len(inventory_of_longs____fx_buys) == 0:
                            # print("Hi")
                            break_outer_sell_loop = True
                            break

                        break_inner_sell_loop = False
                        while (round(shorts____fx_sales, 8) > 0) & (len(inventory_of_longs____fx_buys) > 0):
                            buy_records = inventory_of_longs____fx_buys[0]
                            amount_bought_i = buy_records["base_amount"]
                            rates_bought_i = buy_records["rates"]

                            # REV Cal
                            if amount_sold_i >= amount_bought_i:
                                # print(f"here...amount_sold {amount_sold_i}")
                                revenue_calc_formula[row_index] += f"{amount_bought_i:.2f} sold at {rates_sold_i:.2f} but bought at {rates_bought_i:.2f} \n"
                                # print(revenue_calc_formula[row_index] )
                                computed_revenue_lc[row_index] += (amount_bought_i * rates_sold_i) - (amount_bought_i * rates_bought_i)
                                # print(f"row_index: {row_index}; rev_cal {revenue_calc_formula[row_index]}")
                                # print(f"row_index: {row_index}; computed_rev {computed_revenue_lc[row_index]}")


                                # amount_bought_i -= amount_sold_i # No need for this as I will pop the element from list in next line
                                inventory_of_longs____fx_buys.pop(0)
                                inventory_of_shorts__fx_sales[sell_inventory_id]["base_amount"] -= amount_bought_i
                                
                                shorts____fx_sales -= amount_bought_i
                                # print(f"before: {longs______fx_buys}")
                                longs______fx_buys -= amount_bought_i
                                # print(f"after: {longs______fx_buys}")

                                amount_sold_i -= amount_bought_i

                                # shorts_detail += f"{round(shorts____fx_sales, 8):,.4f} @ {rates_sold_i:,.8f}; " if round(shorts____fx_sales, 8) > 0 else ""
                                # longs_detail  += f"{round(longs______fx_buys, 8):,.4f} @ {rates_bought_i:,.8f}; " if round(longs______fx_buys, 8) > 0 else ""
                            else:
                                # print(f"here 2...Sell")

                                if len(inventory_of_shorts__fx_sales) == 0:
                                    break_inner_sell_loop = True
                                    break

                                revenue_calc_formula[row_index] += f"{amount_sold_i:.2f} sold at {rates_sold_i:.2f} but bought at {rates_bought_i:.2f} \n"
                                computed_revenue_lc[row_index] += (amount_sold_i * rates_sold_i) - (amount_sold_i * rates_bought_i)
                                # print(f"row_index: {row_index}; rev_cal {revenue_calc_formula[row_index]}")
                                # print(f"row_index: {row_index}; computed_rev {computed_revenue_lc[row_index]}")
                                
                                amount_bought_i -= amount_sold_i
                                inventory_of_longs____fx_buys[0]["base_amount"] -= amount_sold_i
                                inventory_of_shorts__fx_sales.pop(sell_inventory_id)

                                shorts____fx_sales -= amount_sold_i
                                longs______fx_buys -= amount_sold_i



                                amount_sold_i -= amount_sold_i

                        # shorts_detail += f"{round(shorts____fx_sales, 8):,.4f} to be sold @ {rates_sold_i:,.8f}; " if round(shorts____fx_sales, 8) > 0 else ""
                        # longs_detail  += f"{round(longs______fx_buys, 8):,.4f} bought @ {rates_bought_i:,.8f}; " if round(longs______fx_buys, 8) > 0 else ""

                                # print(f"shorts_detail = {shorts_detail}")

                            # print(f"After first evaluation, shorts____fx_sales {shorts____fx_sales}; longs______fx_buys {longs______fx_buys}, buy_inv {inventory_of_longs____fx_buys}, sell inv {inventory_of_shorts__fx_sales}")
                           
                            if break_inner_sell_loop == True:
                                break

                    if break_outer_sell_loop == True:
                        break
                # print(f"revenue_calc_formula:- {revenue_calc_formula[row_index]} computed_revenue_lc:- {computed_revenue_lc[row_index]}")

                current_inventory_state[row_index] = f"Short: {round(shorts____fx_sales, 8):,.2f} \n Long: {round(longs______fx_buys, 8):,.2f}"
                # current_inventory_state_details[row_index] = f"Short: {shorts_detail} \n Long: {longs_detail}"


            # print(f"sell inv : {inventory_of_shorts__fx_sales}")
            # print(f"buy inv : {inventory_of_longs____fx_buys}")

# ******************** # ******************** # ******************** # ******************** # *** ******************** # ***************** # ******************** #
        # DETAIlL THE PENDING INVENTORY AFTER THE EXECUTION OF THIS TRADE 
            # Set Default details if we have ran out of a position
            longs_detail = '-'
            shorts_detail = '-'
            for sell_trades in inventory_of_shorts__fx_sales:
                # print(f"row {row_index}; sell inv : {inventory_of_shorts__fx_sales}")
                shorts_detail = f"... to be sold @ ..."
                # shorts_detail = f"{sell_trades["base_amount"]:,.4f} to be sold @ {sell_trades["rates"]:,.8f}" 
            for buy_trades in inventory_of_longs____fx_buys:
                # print(f"row {row_index}; buy inv : {inventory_of_longs____fx_buys}")
                longs_detail = f"... bought @ ..."
                # longs_detail = f"{buy_trades["base_amount"]:,.4f} bought @ {buy_trades["rates"]:,.8f}"

            current_inventory_state_details[row_index] = f"Sell Position: \n{shorts_detail} \n Buy Position: \n{longs_detail}"
            # print(f"Checks: {current_inventory_state_details[row_index]}")



# ******************** # ******************** # ******************** # ******************** # *** ******************** # ***************** # ******************** #
# START
            # IDENTIFY THE LAST TRADE OF THE CURRENCY PAIR PER DAY and evaluate the Weighted Average Rate (WAR)

            if row_index == number_of_records - 1:
                last_state_identifier[row_index] = True # to identify last trade for the day on each currency pair
                unrealized_revenue_with_WAR_formula[row_index] = ''

                # WAR Calculations
                total_in_base_currency = 0
                total_in_revenue_currency = 0


                if len(inventory_of_shorts__fx_sales) == 0: # Hence we are in a long position
                    for each_long_position in inventory_of_longs____fx_buys:
                        amount_to_cover = each_long_position["base_amount"]
                        bought_at = each_long_position["rates"]
                        # # print(f"Unrealized....BUY")

                        total_in_base_currency += amount_to_cover
                        total_in_revenue_currency += (amount_to_cover * bought_at)
                        WAR[row_index] = total_in_revenue_currency/total_in_base_currency

                    unrealized_revenue_with_WAR_formula[row_index] = f"{longs______fx_buys:.2f} bought at a weighted average rate of {WAR[row_index]:.4f} \n"



                else : # len(inventory_of_longs____fx_buys) == 0: # => Hence we are in a Short position
                    for each_short_position in inventory_of_shorts__fx_sales:
                        amount_to_cover = each_short_position["base_amount"]
                        sold_at = each_short_position["rates"]
                        # # print(f"Unrealized....SELL")

                        total_in_base_currency += amount_to_cover
                        total_in_revenue_currency += (amount_to_cover * sold_at)
                        WAR[row_index] = total_in_revenue_currency/total_in_base_currency

                    unrealized_revenue_with_WAR_formula[row_index] = f"{shorts____fx_sales:.2f} sold at a weighted average rate of {WAR[row_index]:.4f} \n"


            else:
                last_state_identifier[row_index] = False # to identify last trade for the day on each currency pair
                WAR[row_index] = None
                unrealized_revenue_with_WAR_formula[row_index] = None



# ******************** # ******************** # ******************** # ******************** # *** ******************** # ***************** # ******************** #
# ROLL UP 
        df_["traded_currency"] = base_currency
        df_["traded_amount"] = traded_amount
        df_["revenue_currency"] = revenue_currency
        df_["inventory_balance"] = inventory_amount
        df_["revenue_calculation_formula"] = revenue_calc_formula
        df_["estimated_revenue"] = np.round(computed_revenue_lc, 8)

        df_["current_inventory_state"] = current_inventory_state
        df_["last_trade_check"] = last_state_identifier
        df_["current_inventory_state_details"] = current_inventory_state_details
        

        df_["WAR of Open Position"] = WAR
        df_["unrealized_revenue_with_WAR_formula"] = unrealized_revenue_with_WAR_formula 
    
        model_ouput = pd.concat([model_ouput, df_], ignore_index= True)

    return model_ouput
