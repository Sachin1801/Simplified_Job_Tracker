import streamlit as st
import pandas as pd
import os
from datetime import datetime

CSV_FILE = "job_applications.csv"

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


def load_data():
    """
    Loads the job applications data from CSV into a pandas DataFrame.
    If CSV does not exist, create an empty DataFrame.
    """
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8")
    else:
        df = pd.DataFrame(
            columns=[
                "company",
                "job_links",
                "date_applied",
                "connection_status",
                "application_status",
            ]
        )
    return df


def save_data(df):
    """
    Saves the DataFrame to a CSV file.
    """
    df.to_csv(CSV_FILE, index=False, encoding="utf-8")


def main():
    st.title("📊 Job Application Tracker")

    # Load the data
    df = load_data()

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

                df = df.append(new_data, ignore_index=True)
                save_data(df)

                st.success(f"✅ Application for '{company}' added successfully.")


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
                        Sachin Adlakha  
                        """
                    )

                # Recruiter Connection Message
                st.write("**==Message to Recruiter==**")
                st.markdown(
                    f"""
                    Hi [Recruiter's Name],  

                    I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                    ([Portfolio](https://sachinadlakha3d.vercel.app/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                    and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                    Best regards,  
                    Sachin Adlakha  
                    Email: sa9082@nyu.edu  
                    LinkedIn: [Sachin Adlakha](https://www.linkedin.com/in/sachin-adlakha/)  
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
                        Sachin Adlakha  
                        """
                    )

                    # Display Recruiter Message
                    st.write("**==Message to Recruiter==**")
                    st.markdown(
                        f"""
                        Hi [Recruiter's Name],  

                        I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
                        ([Portfolio](https://sachinadlakha3d.vercel.app/)). I'm eager to apply for a Software Engineer Intern role at **{row['company']}**  
                        and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

                        Best regards,  
                        Sachin Adlakha  
                        Email: sa9082@nyu.edu  
                        LinkedIn: [Sachin Adlakha](https://www.linkedin.com/in/sachin-adlakha/)  
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


if __name__ == "__main__":
    main()
