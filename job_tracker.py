import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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

def authenticate_google_sheets(json_file):
    """
    Authenticate and return a Google Sheets client using the uploaded JSON file.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Read the uploaded JSON file correctly
        creds_dict = json.load(json_file)  # Load JSON content from file
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client, None  # Return client object
    except Exception as e:
        return None, str(e)  # Return error message if authentication fails

def load_data(client, sheet_name):
    """
    Load job applications from a user-specified Google Sheet into a DataFrame.
    """
    try:
        sheet = client.open(sheet_name).sheet1
        data = sheet.get_all_records()

        if data:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(columns=["company", "job_links", "date_applied", "connection_status", "application_status"])

        return df, None  # Return data
    except Exception as e:
        return None, str(e)  # Return error message


def save_data(client, sheet_name, df):
    """
    Save job applications from DataFrame to a user-specified Google Sheet.
    """
    try:
        sheet = client.open(sheet_name).sheet1
        sheet.clear()  # Clear existing data

        # Add column headers
        sheet.append_row(df.columns.tolist())

        # Append data rows
        for row in df.values.tolist():
            sheet.append_row(row)

        return None  # No error
    except Exception as e:
        return str(e)  # Return error message

def add_application_page(df, client, sheet_name):
    st.header("📝 Add a New Job Application")

    with st.form("add_application_form", clear_on_submit=True):
        company = st.text_input("Company Name")
        job_links_input = st.text_area("Job Links (comma-separated if multiple)")

        # Date Picker
        date_applied = st.date_input("Date Applied", value=datetime.now().date())

        # Dropdown Select for Connection Status
        connection_status = st.selectbox(
            "Connection/Referral Status", CONNECTION_STATUS_OPTIONS
        )

        # Dropdown Select for Application Status
        application_status = st.selectbox(
            "Application Status", APPLICATION_STATUS_OPTIONS
        )

        submitted = st.form_submit_button("➕ Add Application")
        if submitted:
            if company.strip() == "":
                st.warning("⚠️ Please enter a company name.")
            else:
                job_links_list = [
                    link.strip() for link in job_links_input.split(",") if link.strip()
                ]
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
                error = save_data(client, sheet_name, df)

                if error:
                    st.error(f"❌ Failed to Save Data: {error}")
                else:
                    st.success(f"✅ Application for '{company}' added successfully!")



def search_by_company_page(df):
    st.header("🔎 Search Applications by Company")

    # Get the unique company names and sort them alphabetically
    company_names = sorted(df["company"].str.lower().unique())

    # Dynamic filtering based on user input
    search_query = st.text_input("Start typing to search for a company:")
    suggestions = [name for name in company_names if search_query.lower() in name]

    # Show the filtered suggestions as a dropdown
    selected_company = (
        st.selectbox("Search Results:", suggestions) if suggestions else None
    )

    if selected_company:
        results = df[df["company"].str.lower() == selected_company]

        if results.empty:
            st.warning(f"❌ No applications found for '{selected_company}'.")
        else:
            st.success(
                f"✅ Found {len(results)} application(s) for '{selected_company}':"
            )
            for index, row in results.iterrows():
                job_links = row["job_links"].split("|")
                st.write("---")
                st.write(f"**📌 Company**: {row['company']}")

                # Display existing job links
                st.write("🔗 **Existing Job Links**:")
                for link in job_links:
                    st.write(f" - {link}")

                # Add new job links
                new_job_links = st.text_area(
                    "Add New Job Links (comma-separated)", key=f"new_links_{index}"
                )

                st.write(f"📅 **Date Applied**: {row['date_applied']}")

                # Editable Connection Status Dropdown
                new_connection_status = st.selectbox(
                    "🔄 Update Connection/Referral Status",
                    CONNECTION_STATUS_OPTIONS,
                    index=CONNECTION_STATUS_OPTIONS.index(row["connection_status"]),
                    key=f"conn_{index}",
                )

                # Editable Application Status Dropdown
                new_application_status = st.selectbox(
                    "🔄 Update Application Status",
                    APPLICATION_STATUS_OPTIONS,
                    index=APPLICATION_STATUS_OPTIONS.index(row["application_status"]),
                    key=f"app_{index}",
                )

                # Connection Request Message
                if new_connection_status == "Connection request pending":
                    st.write("**==Connection Request Message==**")
                    st.markdown(
                        f"""
                        Hi,  

                        I'm interested in applying for the **Summer Intern 2025** at **{row['company']}** and would love to connect.  
                        I noticed your experience at the company and was hoping to learn more about your journey.  
                        I would greatly appreciate a referral for the position.  

                        Best regards,  
                        Adamay Mann 
                        """
                    )

                # Recruiter Connection Message
                st.write("**==Message to Recruiter==**")
                st.markdown(
                    f"""
                    Hi [Recruiter's Name],  

                    I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                    ([Portfolio](https://adamaymann.servatom.com/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                    and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                    Best regards,  
                    Adamay Mann 
                    Email: am14579.edu  
                    LinkedIn: [Adamay Mann](https://www.linkedin.com/in/adamaymann7/)  
                    """
                )
                ##You can put your own email and portfolio link later above to make this your own personal message

                if st.button(f"💾 Update '{row['company']}'", key=f"update_{index}"):
                    # Process new job links if provided
                    if new_job_links.strip():
                        new_links_list = [
                            link.strip()
                            for link in new_job_links.split(",")
                            if link.strip()
                        ]
                        all_links = job_links + new_links_list
                        df.at[index, "job_links"] = "|".join(all_links)

                    df.at[index, "connection_status"] = new_connection_status
                    df.at[index, "application_status"] = new_application_status
                    save_data(df)
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

                # Display existing job links
                st.write("🔗 **Existing Job Links**:")
                for link in job_links:
                    st.write(f" - {link}")

                # Add new job links
                new_job_links = st.text_area(
                    "Add New Job Links (comma-separated)", key=f"new_links_date_{index}"
                )

                st.write(f"📅 **Date Applied**: {row['date_applied']}")

                # Editable Connection Status Dropdown
                new_connection_status = st.selectbox(
                    "🔄 Update Connection/Referral Status",
                    CONNECTION_STATUS_OPTIONS,
                    index=CONNECTION_STATUS_OPTIONS.index(row["connection_status"]),
                    key=f"conn_date_{index}",
                )

                # Editable Application Status Dropdown
                new_application_status = st.selectbox(
                    "🔄 Update Application Status",
                    APPLICATION_STATUS_OPTIONS,
                    index=APPLICATION_STATUS_OPTIONS.index(row["application_status"]),
                    key=f"app_date_{index}",
                )

                # Display Connection Request Message if applicable
                if new_connection_status == "Connection request pending":
                    st.write("**==Connection Request Message==**")
                    st.markdown(
                        f"""
                        Hi,  

                        I'm interested in applying for the **Summer Intern 2025** at **{row['company']}** and would love to connect.  
                        I noticed your experience at the company and was hoping to learn more about your journey.  
                        I would greatly appreciate a referral for the position.  

                        Best regards,  
                        Adamay Mann
                        """
                    )

                    # Display Recruiter Message
                    st.write("**==Message to Recruiter==**")
                    st.markdown(
                        f"""
                        Hi [Recruiter's Name],  

                        I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                        ([Portfolio](https://adamaymann.servatom.com/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                        and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                        Best regards,  
                        Adamay Mann  
                        Email: am14579@nyu.edu  
                        LinkedIn: [Adamay Mann](https://www.linkedin.com/in/adamaymann7/)  
                        """
                    )

                if st.button(
                    f"💾 Update '{row['company']}'", key=f"update_date_{index}"
                ):
                    # Process new job links if provided
                    if new_job_links.strip():
                        new_links_list = [
                            link.strip()
                            for link in new_job_links.split(",")
                            if link.strip()
                        ]
                        all_links = job_links + new_links_list
                        df.at[index, "job_links"] = "|".join(all_links)

                    df.at[index, "connection_status"] = new_connection_status
                    df.at[index, "application_status"] = new_application_status
                    save_data(df)
                    st.success(f"✅ Updated {row['company']}!")


def view_all_applications_page(df):
    st.header("📋 View All Applications")

    # Count the total number of applications
    total_applications = len(df)
    st.markdown(f"### 🧾 Total Applications: **{total_applications}**")

    # Display the entire CSV as a table
    if total_applications > 0:
        st.dataframe(df)
    else:
        st.warning("No applications have been added yet!")

def main():
    st.title("📊 Job Application Tracker")

    # Step 1: User uploads Google Cloud credentials JSON file
    st.sidebar.header("🔐 Google Sheets Setup")
    json_file = st.sidebar.file_uploader("Upload your Google Cloud JSON file", type=["json"])
    sheet_name = st.sidebar.text_input("Enter your Google Sheet name", "Job Applications")

    if json_file and st.sidebar.button("🔗 Connect to Google Sheets"):
        # Authenticate using the uploaded JSON file
        client, error = authenticate_google_sheets(json_file)

        if error:
            st.sidebar.error(f"❌ Authentication Failed: {error}")
        else:
            st.sidebar.success("✅ Successfully Connected to Google Sheets!")
            df, error = load_data(client, sheet_name)

            if error:
                st.error(f"❌ Failed to Load Data: {error}")
            else:
                st.session_state["df"] = df  # Store in session state
                st.session_state["client"] = client
                st.session_state["sheet_name"] = sheet_name
                st.success("📋 Data Loaded Successfully!")

    # Proceed only if data is available
    if "df" in st.session_state and "client" in st.session_state:
        df = st.session_state["df"]
        client = st.session_state["client"]
        sheet_name = st.session_state["sheet_name"]

        # Sidebar Navigation
        page_selection = st.sidebar.radio(
            "Navigation",
            [
                "📌 Add Application",
                "🔎 Search by Company",
                "📅 Filter by Date",
                "📋 View All Applications",
            ],
        )

        if page_selection == "📌 Add Application":
            add_application_page(df, client, sheet_name)
        elif page_selection == "🔎 Search by Company":
            search_by_company_page(df)
        elif page_selection == "📅 Filter by Date":
            filter_by_date_page(df)
        elif page_selection == "📋 View All Applications":
            view_all_applications_page(df)



if __name__ == "__main__":
    main()