import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import pickle
import os
from constants.constants import SCOPES, CLIENT_SECRETS_FILE

def create_flow():
    """Create OAuth flow for web application"""
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8501"  # Streamlit default port
    )

def init_session_state():
    """Initialize session state variables"""
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None

def authenticate():
    """Handle authentication and session storage"""
    init_session_state()
    
    if st.session_state.is_authenticated:
        return True

    # Check for cached credentials
    cache_file = './.auth_cache'
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                cached_creds = pickle.load(f)
                credentials = Credentials.from_authorized_user_info(cached_creds, SCOPES)
                if credentials and not credentials.expired:
                    st.session_state.credentials = credentials_to_dict(credentials)
                    st.session_state.is_authenticated = True
                    return True
        except Exception:
            if os.path.exists(cache_file):
                os.remove(cache_file)

    # Get OAuth URL and handle callback
    flow = create_flow()
    if 'code' not in st.query_params:  # Updated line
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.link_button("Login with Google 🔑", auth_url)
        return False

    code = st.query_params['code']
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        st.session_state.credentials = credentials_to_dict(credentials)
        st.session_state.is_authenticated = True
        
        # Cache credentials
        with open(cache_file, 'wb') as f:
            pickle.dump(st.session_state.credentials, f)
            
        return True
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return False

def credentials_to_dict(credentials):
    """Convert credentials to dictionary format"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }