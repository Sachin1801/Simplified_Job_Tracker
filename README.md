# Job Application Tracker

A simple and intuitive tool built with **Python** and **Streamlit** that lets you track, update, and manage your job applications. The app uses Google Sheets as a backend data store so that your data is always in sync, and it features Google OAuth-based authentication to secure your information.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Google Authentication Setup](#google-authentication-setup)
- [Usage](#usage)
- [Development Details](#development-details)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Add Applications:** Input new job applications with details such as:
  - Company Name
  - One or more Job Links
  - Date of Application
  - Connection/Referral Status (e.g. "Connection request pending", "Applied with referral")
  - Application Status (e.g. "Applied", "Positive Response received", "Rejected")
  
- **Search & Filter:** 
  - Search for applications by company name with real-time suggestions.
  - Filter applications by the date they were applied.
  
- **View & Update:** 
  - View a complete list of your job applications.
  - Update job details such as adding new job links or modifying the connection and application statuses.
  
- **Pre-written Messages:** For each application, the app displays pre-generated messages that you can use to send connection requests or approach recruiters.

- **Google Sheets Integration:** 
  - The app stores and updates your job application data in a Google Sheet named `job-tracker`.
  - If the sheet does not exist, it will be automatically created.
  
- **Secure Authentication:** 
  - Uses Google OAuth to authenticate users.
  - Credentials are cached locally to streamline the login process.

---

## Project Structure

```

├── app.py                     # Main Streamlit application script
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # List of required Python packages
├── uv.lock                    # Lock file for Python version and dependencies
├── .python-version            # Python version (3.12)
├── auth/
│   └── auth.py                # Google OAuth authentication handling
├── constants/
│   └── constants.py           # Global constants (SCOPES, client secrets file, options)
└── job_tracker/
    ├── pages.py               # UI pages for adding, searching, filtering and viewing applications
    ├── sheets.py              # Functions to load and save data to Google Sheets
    └── utils.py               # Helper functions for generating message templates
```

---

## Installation and Setup

### 1. Prerequisites

- **Python 3.12** is required (see `.python-version`).
- A Google account to access and manage your Google Sheets.

### 2. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/<your-username>/sachin1801-simplified_job_tracker.git
cd sachin1801-simplified_job_tracker
```

### 3. Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

Alternatively, if you use the `pyproject.toml` setup, you can use your preferred build tool (such as Poetry or pip with PEP 621 support).

---

## Google Authentication Setup

1. **Create Google OAuth Credentials:**

   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project (or select an existing one).
   - Navigate to **APIs & Services > Credentials**.
   - Click **Create Credentials** and choose **OAuth client ID**.
   - Set the application type to **Web application**.
   - Under **Authorized redirect URIs**, add:  
     `http://localhost:8501`
   - Download the JSON file and save it as `client_secret.json` in the root directory of your project.

2. **Configure Scopes:**

   The file [`constants/constants.py`](./constants/constants.py) contains the following scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`
   
   These scopes allow the app to read, write, and manage your job tracker Google Sheet.

---

## Usage

1. **Run the Application:**

   Start the Streamlit app by running:

   ```bash
   streamlit run app.py
   ```

2. **Authentication:**

   - On first launch, you will be prompted to log in with your Google account.
   - Click the **"Login with Google 🔑"** button to authorize.
   - Upon successful authentication, your credentials will be cached locally (in `.auth_cache`) and stored in your session.

3. **Navigating the App:**

   - **Add Application:** Use the form to input new job application details.
   - **Search by Company:** Type in a company name to see suggestions and view matching applications.
   - **Filter by Date:** Select a date to view all applications submitted on that day.
   - **View All Applications:** See an overview of all job applications and update details as needed.

4. **Updating Applications:**

   - When viewing an application, you can add new job links or update the connection and application status using the provided options.
   - Pre-generated messages are displayed if the connection status is set to "Connection request pending."

---

## Development Details

- **Authentication Module (`auth/auth.py`):**  
  Handles the OAuth flow using the Google Auth libraries. It manages session state and caches credentials locally.

- **Google Sheets Integration (`job_tracker/sheets.py`):**  
  Uses the `gspread` library to interact with Google Sheets. It includes functions to load the data into a Pandas DataFrame and to save updates back to the sheet.

- **User Interface (`job_tracker/pages.py`):**  
  Contains the Streamlit pages for various functionalities (adding, searching, filtering, viewing, and updating applications).

- **Utility Functions (`job_tracker/utils.py`):**  
  Provides helper functions for generating connection request and recruiter messages tailored for the company.

- **Constants (`constants/constants.py`):**  
  Stores global constants such as OAuth scopes, the client secrets file location, and pre-defined options for connection and application statuses.

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork the repository.**
2. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and test them.**
4. **Commit your changes with a descriptive commit message:**

   ```bash
   git commit -m "Add feature/bug fix description"
   ```

5. **Push to your fork and open a pull request.**

Please ensure your code adheres to the project's style and includes appropriate documentation.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For any questions, feedback, or issues, please open an issue on GitHub or contact [Sachin Adlakha](https://www.linkedin.com/in/sachin-adlakha/) via LinkedIn or email at **sa9082@nyu.edu**.

---

Enjoy tracking your job applications and best of luck with your career search!