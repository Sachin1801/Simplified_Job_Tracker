import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Define the scopes and client secrets file
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]
CLIENT_SECRETS_FILE = "client_secret.json"

# Define the dropdown options
CONNECTION_STATUS_OPTIONS = [
    "Connection request pending",
    "Connection sent",
    "Waiting for referral",
    "Applied with referral",
]

APPLICATION_STATUS_OPTIONS = [
    "Applied",
    "Positive Response received (further rounds)",
    "Rejected",
]

########################################
# Google Sheets Helper Functions
########################################

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

########################################
# OAuth Authorization Flow (OOB)
########################################

def initiate_auth():
    """Initiate the OAuth flow (Desktop app OOB) and return the auth URL."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # OOB redirect for desktop apps
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url

def exchange_code_for_token(code):
    """Exchange the manually entered authorization code for tokens."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

########################################
# Main Application Functions
########################################

def main():
    st.title("📊 Job Application Tracker (Desktop App OOB Flow)")
    
    # If not authenticated, prompt the user to sign in manually
    if "credentials" not in st.session_state or st.session_state.credentials is None:
        st.warning("Please sign in with Google to continue.")
        if st.button("Sign in with Google"):
            auth_url = initiate_auth()
            st.markdown(
                f'<a href="{auth_url}">Click here to authorize</a>',
                unsafe_allow_html=True
            )
            st.info("After authorizing, copy the authorization code shown by Google and paste it below.")
        code = st.text_input("Enter authorization code:")
        if code:
            try:
                st.session_state.credentials = exchange_code_for_token(code)
                st.success("Authorization successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Authorization failed: {e}")
        return
    else:
        df = load_data_sheet()

    # Sidebar Navigation
    page_selection = st.sidebar.radio(
        "Navigation",
        ["📌 Add Application", "🔎 Search by Company", "📅 Filter by Date", "📋 View All Applications"]
    )

    if page_selection == "📌 Add Application":
        add_application_page(df)
    elif page_selection == "🔎 Search by Company":
        search_by_company_page(df)
    elif page_selection == "📅 Filter by Date":
        filter_by_date_page(df)
    elif page_selection == "📋 View All Applications":
        view_all_applications_page(df)

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
                job_links_list = [link.strip() for link in job_links_input.split(",") if link.strip()]
                if not job_links_list:
                    job_links_list = ["N/A"]
                date_str = date_applied.strftime("%Y-%m-%d")
                new_data = {
                    "company": company.strip(),
                    "job_links": "|".join(job_links_list),
                    "date_applied": date_str,
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
        results = df[df["company"].str.lower() == selected_company]
        if results.empty:
            st.warning(f"❌ No applications found for '{selected_company}'.")
        else:
            st.success(f"✅ Found {len(results)} application(s) for '{selected_company}':")
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
                    st.markdown(f"""
                        Hi,  
                        I'm interested in applying for the **Summer Intern 2025** at **{row['company']}** and would love to connect.  
                        I noticed your experience at the company and was hoping to learn more about your journey.  
                        I would greatly appreciate a referral for the position.  

                        Best regards,  
                        Sachin Adlakha  
                    """)
                st.write("**==Message to Recruiter==**")
                st.markdown(f"""
                    Hi [Recruiter's Name],  
                    I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                    ([Portfolio](https://sachinadlakha3d.vercel.app/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                    and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                    Best regards,  
                    Sachin Adlakha  
                    Email: sa9082@nyu.edu  
                    LinkedIn: [Sachin Adlakha](https://www.linkedin.com/in/sachin-adlakha/)  
                """)
                if st.button(f"💾 Update '{row['company']}'", key=f"update_{index}"):
                    if new_job_links.strip():
                        new_links_list = [link.strip() for link in new_job_links.split(",") if link.strip()]
                        all_links = job_links + new_links_list
                        df.at[index, "job_links"] = "|".join(all_links)
                    df.at[index, "connection_status"] = new_connection_status
                    df.at[index, "application_status"] = new_application_status
                    save_data_sheet(df)
                    st.success(f"✅ Updated {row['company']}!")

def filter_by_date_page(df):
    st.header("📅 Filter Applications by Date")
    selected_date = st.date_input("📆 Select a Date")
    if st.button("📋 Show Applications"):
        date_str = selected_date.strftime("%Y-%m-%d")
        results = df[df["date_applied"] == date_str]
        if results.empty:
            st.warning(f"❌ No applications found for {date_str}.")
        else:
            st.success(f"✅ Found {len(results)} applications on {date_str}:")
            for index, row in results.iterrows():
                job_links = row["job_links"].split("|")
                st.write("---")
                st.write(f"**📌 Company**: {row['company']}")
                st.write("🔗 **Existing Job Links**:")
                for link in job_links:
                    st.write(f" - {link}")
                new_job_links = st.text_area("Add New Job Links (comma-separated)", key=f"new_links_date_{index}")
                st.write(f"📅 **Date Applied**: {row['date_applied']}")
                new_connection_status = st.selectbox(
                    "🔄 Update Connection/Referral Status",
                    CONNECTION_STATUS_OPTIONS,
                    index=CONNECTION_STATUS_OPTIONS.index(row["connection_status"]),
                    key=f"conn_date_{index}"
                )
                new_application_status = st.selectbox(
                    "🔄 Update Application Status",
                    APPLICATION_STATUS_OPTIONS,
                    index=APPLICATION_STATUS_OPTIONS.index(row["application_status"]),
                    key=f"app_date_{index}"
                )
                if new_connection_status == "Connection request pending":
                    st.write("**==Connection Request Message==**")
                    st.markdown(f"""
                        Hi,  
                        I'm interested in applying for the **Summer Intern 2025** at **{row['company']}** and would love to connect.  
                        I noticed your experience at the company and was hoping to learn more about your journey.  
                        I would greatly appreciate a referral for the position.  

                        Best regards,  
                        Sachin Adlakha  
                    """)
                    st.write("**==Message to Recruiter==**")
                    st.markdown(f"""
                        Hi [Recruiter's Name],  
                        I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                        ([Portfolio](https://sachinadlakha3d.vercel.app/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                        and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                        Best regards,  
                        Sachin Adlakha  
                        Email: sa9082@nyu.edu  
                        LinkedIn: [Sachin Adlakha](https://www.linkedin.com/in/sachin-adlakha/)  
                    """)
                if st.button(f"💾 Update '{row['company']}'", key=f"update_date_{index}"):
                    if new_job_links.strip():
                        new_links_list = [link.strip() for link in new_job_links.split(",") if link.strip()]
                        all_links = job_links + new_links_list
                        df.at[index, "job_links"] = "|".join(all_links)
                    df.at[index, "connection_status"] = new_connection_status
                    df.at[index, "application_status"] = new_application_status
                    save_data_sheet(df)
                    st.success(f"✅ Updated {row['company']}!")

def view_all_applications_page(df):
    st.header("📋 View All Applications")
    total_applications = len(df)
    st.markdown(f"### 🧾 Total Applications: **{total_applications}**")
    if total_applications > 0:
        st.dataframe(df)
    else:
        st.warning("No applications have been added yet!")

if __name__ == "__main__":
    main()
