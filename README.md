# 📊 Job Application Tracker

A simple, user-friendly tool to track and manage your job applications! This application is built using **Python** and **Streamlit**, allowing you to add, search, and filter job applications while maintaining a local CSV database.

---

## ✨ Features
- Add job applications with details like:
  - **Company Name**
  - **Job Links** (multiple links supported)
  - **Application Date**
  - **Connection/Referral Status**
  - **Application Status**
- **Real-Time Search**: Search for applications by company name with real-time filtering (case-insensitive).
- **Filter by Date**: View applications submitted on specific dates.
- **View All Applications**: Display all your job applications with a total application count.
- **Status Management**:
  - Dropdown menus for:
    - Connection/Referral Status: `Connection request pending`, `Connection sent`, `Waiting for referral`, `Applied with referral`.
    - Application Status: `Applied`, `Positive response received`, `Rejected`.

---

## 🛠️ Installation and Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd Job_Application_Tracker
```

## 2️⃣Create a virtual environment
```python3 -m venv venv```

## 3️⃣Activate the virtual environment
```source venv/bin/activate  # On macOS/Linux```
```venv\Scripts\activate     # On Windows```

## 4️⃣Install Python Libraries and Start Application
```pip install -r requirements.txt```
```streamlit run job_tracker.py```

## Project Structure
Job_Application_Tracker/
├── job_tracker.py         # Main Streamlit application script
├── requirements.txt       # Python dependencies
├── .gitignore             # Excluded files (CSV, virtual environment, etc.)
├── README.md              # Project documentation

## 🤝 Contributing
Contributions are welcome! Feel free to fork this repository, create a feature branch, and submit a pull request.

### Steps to Contribute:
1. **Fork the repository.**
2. **Clone your fork:**
    ```bash
    git clone https://github.com/<your-username>/<repo-name>.git
    ```
3. **Create a new branch:**
    ```bash
    git checkout -b feature/your-feature-name
    ```
4. **Make your changes and test them.**
5. **Commit your changes:**
    ```bash
    git commit -m "Add your message here"
    ```
6. **Push to your fork:**
    ```bash
    git push origin feature/your-feature-name
    ```
7. **Open a pull request!**

📝 Notes
- **Data Privacy**: Your job application data is stored locally in job_applications.csv and is not pushed to GitHub.
- **Virtual Environment**: Each user should create their own virtual environment to manage dependencies.

📜 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it as needed.

💬 Questions or Suggestions?
Feel free to open an issue on GitHub or contact me directly for support.

This README ensures clarity for anyone cloning the repository and setting it up. Let me know if further tweaks are needed! 🚀
