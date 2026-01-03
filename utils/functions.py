import pandas as pd
import numpy as np
import ast
from collections import Counter


def standardize_currency_pair(pair):
    """Sorts currency pair strings alphabetically."""
    # Handle cases with or without a hyphen
    currencies = pair.replace('-', ' ').strip().split()
    
    # Sort the list alphabetically and join back with a hyphen
    return '/'.join(sorted(currencies))


# Create a function to safely evaluate and handle the numpy type
def safe_literal_eval_numpy_inclusive(s):
    # Check for NaN first (if applicable)
    if isinstance(s, float):
        return s
    
    # Remove the problematic 'np.float64()' part from the string
    s = str(s).replace('np.float64(', '').replace(')', '')
    
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        # Fallback for any remaining malformed strings
        return s


def get_fx_type_and_unique_pairs(df, exchangerte, currencypair, rate_inversion):
    df_copy = df.copy()
    df_copy.loc[:,"FX Type"] = np.where(df_copy.loc[:, exchangerte] >1, "Buy", "Sell")
    df_copy.loc[:,"unique_pairs"] = df_copy.loc[:, currencypair].apply(standardize_currency_pair)
    return df_copy

def disambiguate_column_names(df):
    counts = Counter()
    new_header = []

    curr_header = df.columns

    for col in curr_header:
        counts[col] += 1
        if counts[col] > 1:
            new_header.append(f'{col}_{counts[col]}')
        else:
            new_header.append(col)

    df.columns = new_header

    return df   

def remove_empty_cells(df):
    # Identify and remove empty rows
    df["non_empty_cells"] = df.map(lambda x: len(str(x))>0).sum(axis=1)
    df = df[df["non_empty_cells"] > 0]
    
	# Identify and remove empty columns
    # df.columns = [str(i) for i in df.columns] 
    def count_non_empty_col(column):
        return column.apply(lambda x: len(str(x))>0).sum()
    col_check = df.apply(count_non_empty_col)
    cols_with_values = col_check[col_check > 0].index

    df = df[cols_with_values].drop(["non_empty_cells"], axis="columns")
    

    # Exclude Rows without enough data  (up to one-third of the valid columns)
    len_of_valid_columns = df.shape[1]
    df["non_empty_cells"] = df.iloc[:,:].replace({"":np.nan}).count(axis=1) 
    df = df[df["non_empty_cells"] > len_of_valid_columns/3]
    df = df.drop(["non_empty_cells"], axis="columns")

    return df

def replace_comma(str_text):
    return str_text.replace(',','').replace(')', '').replace('(', '-')

def safe_convert_to_datetime(val, year):
    try:
        return pd.to_datetime(val)
    except:
        try:
            return pd.to_datetime(f"{val} {year}")
        except:
            return pd.NaT
    
def safe_convert_to_float(val):
    val = val.replace(',','')

    try:
        return pd.to_numeric(val)
    except:
        if "%" in val:
            return float(val.replace('%', ''))/100
        else:
            return np.nan

def convert_datatype_in_base_file(df, numeric_col, date_col):
    for col in numeric_col:
        df[col] = df[col].astype(str).apply(replace_comma).replace('nan','')
        df[col] = pd.to_numeric(df[col])

    for col in date_col:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed').dt.date

    df = df[df["date"].notna()]   
    return df

def get_quarter_year(input_date):
    """
    Converts a date object to a 'YYYY QX' string format.
    """
    # 1. Ensure input is datetime
    series = pd.to_datetime(input_date)
    
    # 2. Extract year and quarter using .dt accessor (Vectorized)
    years = series.dt.year.astype(str)
    quarters = series.dt.quarter.astype(str)
    
    # 3. Concatenate the strings
    return "Q" + quarters + " " + years


def get_start_of_week(series, start_day='Mon'):
    """
    Returns the start of the week for a given Series of dates.
    
    Parameters:
    - series: Pandas Series (datetime objects)
    - start_day: String ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    """
    # 1. Map days to their integer index (Monday=0, Sunday=6)
    day_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
    target_day_index = day_map.get(start_day.upper(), 4)
    
    # 2. Ensure series is datetime and normalize (remove time)
    series = pd.to_datetime(series).dt.normalize()
    
    # 3. Vectorized Math: 
    # (Current day index - Target day index) % 7 gives days since the last start_day
    days_to_subtract = (series.dt.weekday - target_day_index) % 7
    
    # 4. Subtract the delta using vectorized Timedelta series
    return (series - pd.to_timedelta(days_to_subtract, unit='D')).dt.date

def load_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)