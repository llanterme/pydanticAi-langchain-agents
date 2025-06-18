"""
LinkedIn OAuth authentication utilities.
"""

import os
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()


class LinkedInAuth:
    """Handle LinkedIn OAuth 2.0 authentication flow."""
    
    AUTHORIZATION_BASE_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, redirect_uri: Optional[str] = None):
        """
        Initialize LinkedIn OAuth client.
        
        Args:
            client_id: LinkedIn app client ID (defaults to LINKEDIN_CLIENT_ID env var)
            client_secret: LinkedIn app client secret (defaults to LINKEDIN_CLIENT_SECRET env var)
            redirect_uri: OAuth redirect URI (defaults to LINKEDIN_REDIRECT_URI env var)
        """
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/login")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("LinkedIn client_id and client_secret are required")
        
        self.scope = ["w_member_social"]
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get the authorization URL for LinkedIn OAuth flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to visit
        """
        linkedin = OAuth2Session(
            self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            state=state
        )
        authorization_url, state = linkedin.authorization_url(
            self.AUTHORIZATION_BASE_URL,
            state=state
        )
        return authorization_url
    
    def get_access_token(self, authorization_response_url: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_response_url: The full callback URL with authorization code
            
        Returns:
            Token dictionary containing access_token and other info
        """
        linkedin = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri
        )
        
        token = linkedin.fetch_token(
            self.TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.client_secret
        )
        return token
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New token dictionary
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()
    
    def is_token_valid(self, access_token: str) -> bool:
        """
        Check if an access token is still valid.
        
        Args:
            access_token: The access token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://api.linkedin.com/v2/people/~",
            headers=headers
        )
        return response.status_code == 200