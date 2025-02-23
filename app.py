import streamlit as st
from auth.auth import authenticate
from job_tracker.sheets import load_data_sheet
from job_tracker.pages import (
    add_application_page,
    search_by_company_page,
    filter_by_date_page,
    view_all_applications_page
)

def main():
    st.title("📊 Job Application Tracker (Desktop App OOB Flow)")
    
    # Authentication Check
    if not authenticate():
        st.warning("Please login with Google to continue")
        return


    # Load data and setup navigation
    df = load_data_sheet()
    
    page_selection = st.sidebar.radio(
        "Navigation",
        ["📌 Add Application", "🔎 Search by Company", "📅 Filter by Date", "📋 View All Applications"]
    )

    # Route to appropriate page
    if page_selection == "📌 Add Application":
        add_application_page(df)
    elif page_selection == "🔎 Search by Company":
        search_by_company_page(df)
    elif page_selection == "📅 Filter by Date":
        filter_by_date_page(df)
    elif page_selection == "📋 View All Applications":
        view_all_applications_page(df)

if __name__ == "__main__":
    main()
