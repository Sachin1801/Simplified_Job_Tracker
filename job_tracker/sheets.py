import pandas as pd
import gspread
from google.oauth2.credentials import Credentials
import streamlit as st
from constants.constants import SCOPES

def get_google_sheet():
    """Authorize with stored credentials and return the first worksheet of 'job-tracker'."""
    creds = Credentials.from_authorized_user_info(info=st.session_state.credentials, scopes=SCOPES)
    gc = gspread.authorize(creds)
    try:
        sh = gc.open("job-tracker")
    except gspread.SpreadsheetNotFound:
        sh = gc.create("job-tracker")
    return sh.sheet1

def load_data_sheet():
    """Load data from the Google Sheet into a pandas DataFrame."""
    sheet = get_google_sheet()
    data = sheet.get_all_values()
    columns = ["company", "job_links", "date_applied", "connection_status", "application_status"]
    if not data or len(data) < 1:
        return pd.DataFrame(columns=columns)
    else:
        header = data[0]
        if header != columns:
            sheet.clear()
            sheet.append_row(columns)
            return pd.DataFrame(columns=columns)
        rows = data[1:]
        return pd.DataFrame(rows, columns=columns)

def save_data_sheet(df):
    """Save the pandas DataFrame to the Google Sheet."""
    sheet = get_google_sheet()
    sheet.clear()
    header = list(df.columns)
    sheet.append_row(header)
    for i in range(len(df)):
        row = df.iloc[i].tolist()
        sheet.append_row(row)
