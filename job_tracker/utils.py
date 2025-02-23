from job_tracker.config_manager import load_user_config

def get_connection_request_message(company):
    config = load_user_config()
    return f"""
        Hi,  
        I'm interested in applying for the **{config.get('position', 'position')}** at **{company}** and would love to connect.  
        I noticed your experience at the company and was hoping to learn more about your journey.  
        I would greatly appreciate a referral for the position.  

        Best regards,  
        {config.get('name', 'Your Name')}  
    """

def get_recruiter_message(company):
    config = load_user_config()
    return f"""
        Hi [Recruiter's Name],  
        I hope you're doing well! I'm a passionate software engineer and competitive programmer, actively building innovative projects  
        ([Portfolio]({config.get('portfolio_url', '')})). I'm eager to apply for a Software Engineer Intern role at **{company}**  
        and would love to interview if I'm a good fit. Any advice for improvement would also be greatly appreciated!  

        Best regards,  
        {config.get('name', 'Your Name')}  
        Email: {config.get('email', '')}  
        LinkedIn: [{config.get('name', 'Your Name')}]({config.get('linkedin_url', '')})  
    """
