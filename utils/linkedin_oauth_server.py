"""
LinkedIn OAuth server to handle the 3-legged OAuth flow properly.
"""

import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv

load_dotenv()


class LinkedInOAuthHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from LinkedIn."""
    
    def do_GET(self):
        """Handle GET request from LinkedIn callback."""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            # Got authorization code, exchange for access token
            auth_code = query_params['code'][0]
            self.exchange_code_for_token(auth_code)
        elif 'error' in query_params:
            # OAuth error
            error = query_params['error'][0]
            error_desc = query_params.get('error_description', [''])[0]
            self.send_error_response(f"OAuth Error: {error} - {error_desc}")
        else:
            self.send_error_response("No authorization code received")
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token."""
        try:
            # Prepare token request
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/callback'),
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Exchange code for token
            response = requests.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                
                # Store token in environment file
                self.update_env_file(access_token)
                
                # Send success response
                self.send_success_response(access_token, token_data)
                
                # Store token globally for the server to access
                self.server.access_token = access_token
                
            else:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                self.send_error_response(error_msg)
                
        except Exception as e:
            self.send_error_response(f"Exception during token exchange: {str(e)}")
    
    def update_env_file(self, access_token):
        """Update the .env file with the new access token."""
        try:
            env_path = '.env'
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update or add the access token line
            token_line = f'LINKEDIN_ACCESS_TOKEN={access_token}\n'
            updated = False
            
            for i, line in enumerate(lines):
                if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                    lines[i] = token_line
                    updated = True
                    break
            
            if not updated:
                lines.append(token_line)
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
                
        except Exception as e:
            print(f"Warning: Could not update .env file: {e}")
    
    def send_success_response(self, access_token, token_data):
        """Send success response to browser."""
        expires_in = token_data.get('expires_in', 'N/A')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn OAuth Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .success {{ color: #28a745; }}
                .token {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; font-family: monospace; word-break: break-all; }}
                .info {{ background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1 class="success">✅ LinkedIn OAuth Success!</h1>
            <p>Your LinkedIn access token has been obtained and saved to your .env file.</p>
            
            <div class="info">
                <strong>Access Token:</strong>
                <div class="token">{access_token}</div>
            </div>
            
            <div class="info">
                <strong>Token Type:</strong> Bearer<br>
                <strong>Expires In:</strong> {expires_in} seconds
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Your .env file has been automatically updated</li>
                <li>You can now close this browser window</li>
                <li>Run the LinkedIn posting test: <code>poetry run python test_linkedin_posting.py</code></li>
            </ul>
            
            <p>You can now close this window and return to your terminal.</p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_error_response(self, error_msg):
        """Send error response to browser."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ color: #dc3545; }}
                .details {{ background: #f8d7da; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1 class="error">❌ LinkedIn OAuth Error</h1>
            <div class="details">{error_msg}</div>
            <p>Please check your LinkedIn app configuration and try again.</p>
        </body>
        </html>
        """
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_oauth_flow():
    """Start the complete LinkedIn OAuth flow."""
    # Check environment variables
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env file")
        return
    
    # Update redirect URI to use port 8000
    redirect_uri = 'http://localhost:8000/callback'
    
    print("🚀 Starting LinkedIn OAuth Flow")
    print("=" * 50)
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {redirect_uri}")
    print()
    
    # Start local server
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, LinkedInOAuthHandler)
    httpd.access_token = None
    
    print("🌐 Starting local server on http://localhost:8000")
    
    # Build authorization URL
    from urllib.parse import urlencode
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'w_member_social',
        'state': 'linkedin_oauth_flow'
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    
    print(f"🔗 Opening LinkedIn authorization URL in browser...")
    print(f"   {auth_url}")
    print()
    print("📋 Steps:")
    print("1. Browser will open automatically")
    print("2. Log into LinkedIn if needed")
    print("3. Authorize your application")
    print("4. You'll be redirected back to localhost:8000")
    print("5. Server will automatically exchange the code for access token")
    print()
    print("⏳ Waiting for OAuth callback...")
    print("   (Press Ctrl+C to stop)")
    
    # Open browser
    webbrowser.open(auth_url)
    
    try:
        # Handle one request (the OAuth callback)
        httpd.handle_request()
        
        if hasattr(httpd, 'access_token') and httpd.access_token:
            print()
            print("✅ OAuth flow completed successfully!")
            print(f"🔑 Access token: {httpd.access_token}")
            print("📝 Token saved to .env file")
            print()
            print("🧪 Ready to test! Run:")
            print("   poetry run python test_linkedin_posting.py")
        else:
            print("❌ OAuth flow failed - no access token received")
            
    except KeyboardInterrupt:
        print("\n⚠️ OAuth flow cancelled by user")
    except Exception as e:
        print(f"❌ Error during OAuth flow: {e}")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    start_oauth_flow()