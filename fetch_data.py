import streamlit as st
import pandas as pd
import pymysql
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ----------------------------------
# Cached Google Sheets client
# ----------------------------------
@st.cache_resource(ttl=1800)
def get_gspread_client(secret_key: str):
    secret_info = st.secrets[secret_key]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    return gspread.authorize(creds)

# ----------------------------------
# Fetch ACKG Sheet with selected columns
# ----------------------------------
@st.cache_data(ttl=1800)
def fetch_data_ackg(selected_columns):
    client = get_gspread_client("sheets")
    spreadsheet = client.open("[Pivot Traits] REKAP HASIL AC ECOSYSTEM MODEL-2021 update")
    sheet = spreadsheet.sheet1

    # Fetch raw values and slice from row 4 (index 3)
    all_values = sheet.get_all_values()
    headers = all_values[3]
    data_rows = all_values[4:]
    
    df = pd.DataFrame(data_rows, columns=headers)
    return df[selected_columns]

# ----------------------------------
# Fetch Credentials Sheet
# ----------------------------------
@st.cache_data(ttl=1800)
def fetch_data_creds():
    client = get_gspread_client("sheets")
    spreadsheet = client.open("ACKG - Dashboard Credentials")

    sheet1 = spreadsheet.sheet1
    data1 = sheet1.get_all_records()
    df_creds = pd.DataFrame(data1)

    return df_creds