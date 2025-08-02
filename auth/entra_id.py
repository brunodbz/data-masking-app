import msal
import requests
from flask import redirect, session, url_for, request
import os

def get_msal_app():
    return msal.ConfidentialClientApplication(
        os.environ.get('ENTRA_ID_CLIENT_ID'),
        authority=f"https://login.microsoftonline.com/{os.environ.get('ENTRA_ID_TENANT_ID')}",
        client_credential=os.environ.get('ENTRA_ID_CLIENT_SECRET')
    )

def get_auth_url():
    app = get_msal_app()
    auth_url = app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=os.environ.get('ENTRA_ID_REDIRECT_URI'),
        prompt="select_account",  # Força seleção de conta
        claims_challenge=None  # Será configurado para exigir MFA
    )
    return auth_url

def get_token_from_code(auth_code):
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        auth_code,
        scopes=["User.Read"],
        redirect_uri=os.environ.get('ENTRA_ID_REDIRECT_URI')
    )
    return result

def get_user_info(token):
    graph_api_url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(graph_api_url, headers=headers)
    return response.json()

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_mfa_auth_url():
    app = get_msal_app()
    
    # Claims para exigir MFA
    claims = {
        "id_token": {
            "amr": {
                "essential": True,
                "values": ["mfa"]
            }
        }
    }
    
    auth_url = app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=os.environ.get('ENTRA_ID_REDIRECT_URI'),
        prompt="select_account",
        claims=claims
    )
    return auth_url