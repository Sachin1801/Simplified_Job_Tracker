import streamlit as st
from datetime import datetime
from constants.constants import CONNECTION_STATUS_OPTIONS, APPLICATION_STATUS_OPTIONS
from job_tracker.sheets import save_data_sheet
from job_tracker.utils import get_connection_request_message, get_recruiter_message
import pandas as pd
from job_tracker.config_manager import load_user_config, save_user_config

def add_application_page(df):
    st.header("📝 Add a New Job Application")
    with st.form("add_application_form", clear_on_submit=True):
        company = st.text_input("Company Name")
        job_links_input = st.text_area("Job Links (comma-separated if multiple)")
        date_applied = st.date_input("Date Applied", value=datetime.now().date())
        connection_status = st.selectbox("Connection/Referral Status", CONNECTION_STATUS_OPTIONS)
        application_status = st.selectbox("Application Status", APPLICATION_STATUS_OPTIONS)
        submitted = st.form_submit_button("➕ Add Application")
        
        if submitted:
            if company.strip() == "":
                st.warning("⚠️ Please enter a company name.")
            else:
                with st.spinner('Adding application...'):
                    job_links_list = [link.strip() for link in job_links_input.split(",") if link.strip()]
                    if not job_links_list:
                        job_links_list = ["N/A"]
                        
                    new_data = {
                        "company": company.strip(),
                        "job_links": "|".join(job_links_list),
                        "date_applied": date_applied.strftime("%Y-%m-%d"),
                        "connection_status": connection_status,
                        "application_status": application_status,
                    }
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    save_data_sheet(df)
                    st.success(f"✅ Application for '{company}' added successfully.")

def search_by_company_page(df):
    st.header("🔎 Search Applications by Company")
    company_names = sorted(df["company"].str.lower().unique())
    search_query = st.text_input("Start typing to search for a company:")
    suggestions = [name for name in company_names if search_query.lower() in name]
    selected_company = st.selectbox("Search Results:", suggestions) if suggestions else None
    
    if selected_company:
        display_and_update_applications(df, df[df["company"].str.lower() == selected_company])

def filter_by_date_page(df):
    st.header("📅 Filter Applications by Date")
    selected_date = st.date_input("📆 Select a Date")
    if st.button("📋 Show Applications"):
        date_str = selected_date.strftime("%Y-%m-%d")
        display_and_update_applications(df, df[df["date_applied"] == date_str])

def view_all_applications_page(df):
    st.header("📋 View All Applications")
    total_applications = len(df)
    st.markdown(f"### 🧾 Total Applications: **{total_applications}**")
    if total_applications > 0:
        st.dataframe(df)
    else:
        st.warning("No applications have been added yet!")

def display_and_update_applications(df, results):
    if results.empty:
        st.warning("❌ No applications found.")
        return
        
    st.success(f"✅ Found {len(results)} application(s):")
    for index, row in results.iterrows():
        job_links = row["job_links"].split("|")
        st.write("---")
        st.write(f"**📌 Company**: {row['company']}")
        st.write("🔗 **Existing Job Links**:")
        for link in job_links:
            st.write(f" - {link}")
            
        new_job_links = st.text_area("Add New Job Links (comma-separated)", key=f"new_links_{index}")
        st.write(f"📅 **Date Applied**: {row['date_applied']}")
        
        new_connection_status = st.selectbox(
            "🔄 Update Connection/Referral Status",
            CONNECTION_STATUS_OPTIONS,
            index=CONNECTION_STATUS_OPTIONS.index(row["connection_status"]),
            key=f"conn_{index}"
        )
        
        new_application_status = st.selectbox(
            "🔄 Update Application Status",
            APPLICATION_STATUS_OPTIONS,
            index=APPLICATION_STATUS_OPTIONS.index(row["application_status"]),
            key=f"app_{index}"
        )
        
        if new_connection_status == "Connection request pending":
            st.write("**==Connection Request Message==**")
            st.markdown(get_connection_request_message(row['company']))
            st.write("**==Message to Recruiter==**")
            st.markdown(get_recruiter_message(row['company']))
            
        if st.button(f"💾 Update '{row['company']}'", key=f"update_{index}"):
            update_application(df, index, row, new_job_links, new_connection_status, new_application_status)

def update_application(df, index, row, new_job_links, new_connection_status, new_application_status):
    with st.spinner('Updating application...'):
        if new_job_links.strip():
            new_links_list = [link.strip() for link in new_job_links.split(",") if link.strip()]
            all_links = row["job_links"].split("|") + new_links_list
            df.at[index, "job_links"] = "|".join(all_links)
        df.at[index, "connection_status"] = new_connection_status
        df.at[index, "application_status"] = new_application_status
        save_data_sheet(df)
        st.success(f"✅ Updated {row['company']}!")

def settings_page():
    st.header("⚙️ Settings")
    config = load_user_config()
    
    with st.form("user_settings"):
        name = st.text_input("Full Name", value=config.get('name', ''))
        email = st.text_input("Email", value=config.get('email', ''))
        linkedin_url = st.text_input("LinkedIn URL", value=config.get('linkedin_url', ''))
        portfolio_url = st.text_input("Portfolio URL", value=config.get('portfolio_url', ''))
        position = st.text_input("Target Position", value=config.get('position', ''))
        
        if st.form_submit_button("💾 Save Settings"):
            new_config = {
                "name": name,
                "email": email,
                "linkedin_url": linkedin_url,
                "portfolio_url": portfolio_url,
                "position": position
            }
            save_user_config(new_config)
            st.success("✅ Settings saved successfully!")
