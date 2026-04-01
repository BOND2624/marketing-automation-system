"""
Generate OAuth2 token for YouTube video uploads.
Run this once to authenticate and generate a reusable token.
"""

import os
import json
import sys

def generate_token():
    """Generate OAuth2 token from credentials."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("\n[ERROR] Required packages not installed!")
        print("Install them with: pip install google-auth-oauthlib google-auth-httplib2")
        print("\nOr using uv:")
        print("  uv pip install google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)
    
    # Paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    creds_file = os.path.join(project_root, "youtube_oauth_credentials.json")
    token_file = os.path.join(project_root, "youtube_token.json")
    
    # Check credentials file
    if not os.path.exists(creds_file):
        print(f"\n[ERROR] Credentials file not found: {creds_file}")
        print("\nPlease run: python scripts/setup_youtube_oauth.py")
        print("This will help you set up the credentials file.")
        sys.exit(1)
    
    print("="*60)
    print("YouTube OAuth2 Token Generation")
    print("="*60)
    print(f"\nCredentials file: {creds_file}")
    print(f"Token will be saved to: {token_file}")
    
    # Check if token already exists
    if os.path.exists(token_file):
        print("\n[INFO] Token file already exists!")
        choice = input("Generate new token? (y/n): ").strip().lower()
        if choice != 'y':
            print("\n[INFO] Using existing token.")
            return
    
    # OAuth2 scopes for YouTube upload and metadata reading
    SCOPES = [
        'https://www.googleapis.com/auth/youtube',  # Full access to ensure we can read all data
        'https://www.googleapis.com/auth/youtube.upload'
    ]
    
    print("\n[INFO] Starting OAuth2 flow...")
    print("  - A browser window will open")
    print("  - Sign in with your Google account")
    print("  - Grant permission for YouTube upload")
    print("  - You'll be redirected back automatically")
    
    try:
        # Load credentials
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_file,
            SCOPES
        )
        
        # Local callback URI must match Google Cloud Console *exactly* (scheme/host/port/path).
        # Default run_local_server() uses http://localhost:8080/ (trailing slash) — many people
        # only register http://localhost:8080 → redirect_uri_mismatch. We omit the slash
        # so it matches the usual "Web application" redirect entry.
        _host = "localhost"
        _port = 8080
        _redirect = f"http://{_host}:{_port}"
        print("\n[INFO] Opening browser for authentication...")
        print(f"\n[INFO] OAuth redirect URI (must be in Google Cloud → Credentials → your client):")
        print(f"     {_redirect}")
        print("\nIf you still see redirect_uri_mismatch:")
        print("  - Add the URI above under Authorized redirect URIs (same OAuth client as client_id in JSON).")
        print("  - Or create a 'Desktop' client, download JSON (type 'installed'), and use that file.\n")

        try:
            creds = flow.run_local_server(
                host=_host,
                port=_port,
                prompt="consent",
                redirect_uri_trailing_slash=False,
            )
        except OSError:
            print("[WARNING] Port 8080 in use, using a random port...")
            print("[INFO] Add the printed redirect URI to Google Cloud, then run again with 8080 free,")
            print("      or add each random URI after Google shows it in the error details.\n")
            creds = flow.run_local_server(
                host=_host,
                port=0,
                prompt="consent",
                redirect_uri_trailing_slash=False,
            )
        
        # Save token for future use
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "="*60)
        print("[SUCCESS] Token generated and saved!")
        print("="*60)
        print(f"\nToken saved to: {token_file}")
        print("\nYou can now use this token for YouTube video uploads!")
        print("\nThe token will be reused automatically on future runs.")
        
    except FileNotFoundError:
        print(f"\n[ERROR] Credentials file not found: {creds_file}")
        print("Run: python scripts/setup_youtube_oauth.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Token generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    generate_token()

