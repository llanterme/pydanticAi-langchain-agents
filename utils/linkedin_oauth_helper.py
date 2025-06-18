"""
Helper script to obtain LinkedIn OAuth access token.
"""

import os
from dotenv import load_dotenv
from utils.linkedin_auth import LinkedInAuth

load_dotenv()


def get_authorization_url():
    """Get LinkedIn authorization URL for OAuth flow."""
    auth = LinkedInAuth()
    auth_url = auth.get_authorization_url()
    
    print("LinkedIn OAuth Setup")
    print("=" * 50)
    print(f"1. Visit this URL to authorize your app:")
    print(f"   {auth_url}")
    print()
    print("2. After authorization, you'll be redirected to your callback URL")
    print("3. Copy the full callback URL and use it in get_access_token()")
    print()
    return auth_url


def get_access_token(callback_url: str):
    """
    Exchange authorization code for access token.
    
    Args:
        callback_url: The full callback URL with authorization code
    """
    auth = LinkedInAuth()
    try:
        token = auth.get_access_token(callback_url)
        
        print("Access Token Retrieved Successfully!")
        print("=" * 50)
        print(f"Access Token: {token['access_token']}")
        print(f"Token Type: {token.get('token_type', 'Bearer')}")
        print(f"Expires In: {token.get('expires_in', 'N/A')} seconds")
        
        if token.get('refresh_token'):
            print(f"Refresh Token: {token['refresh_token']}")
        
        print()
        print("Add this to your .env file:")
        print(f"LINKEDIN_ACCESS_TOKEN={token['access_token']}")
        
        return token
        
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


if __name__ == "__main__":
    print("LinkedIn OAuth Helper")
    print("Choose an option:")
    print("1. Get authorization URL")
    print("2. Exchange callback URL for access token")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        get_authorization_url()
    elif choice == "2":
        callback_url = input("Enter the full callback URL: ").strip()
        if callback_url:
            get_access_token(callback_url)
        else:
            print("No callback URL provided.")
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")