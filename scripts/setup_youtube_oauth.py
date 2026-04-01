"""
Helper script to set up YouTube OAuth2 credentials.
This script guides you through the setup process and validates your credentials.
"""

import os
import json
import sys

def check_credentials_file():
    """Check if credentials file exists and validate it."""
    creds_file = os.path.join(os.path.dirname(__file__), "..", "youtube_oauth_credentials.json")
    
    if not os.path.exists(creds_file):
        print("\n[INFO] Credentials file not found!")
        print(f"Expected location: {creds_file}")
        return None, creds_file
    
    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        
        # Check structure
        if "installed" in creds:
            client_id = creds["installed"].get("client_id")
            client_secret = creds["installed"].get("client_secret")
        elif "web" in creds:
            client_id = creds["web"].get("client_id")
            client_secret = creds["web"].get("client_secret")
        else:
            print("\n[ERROR] Invalid credentials file structure!")
            print("Expected 'installed' or 'web' key.")
            return None, creds_file
        
        if not client_id or not client_secret:
            print("\n[ERROR] Missing client_id or client_secret in credentials file!")
            return None, creds_file
        
        print(f"\n[OK] Credentials file found and valid!")
        print(f"  Client ID: {client_id[:30]}...")
        print(f"  Client Secret: {'*' * len(client_secret)}")
        return creds, creds_file
        
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Invalid JSON in credentials file: {e}")
        return None, creds_file
    except Exception as e:
        print(f"\n[ERROR] Error reading credentials file: {e}")
        return None, creds_file

def create_manual_credentials():
    """Guide user to create credentials file manually."""
    print("\n" + "="*60)
    print("Manual Credentials Setup")
    print("="*60)
    print("\nIf you can't download the JSON file, follow these steps:")
    print("\n1. Go to Google Cloud Console → APIs & Services → Credentials")
    print("2. Click on your OAuth 2.0 Client ID")
    print("3. Copy the Client ID and Client Secret")
    print("\nEnter your credentials below (or press Enter to skip):")
    
    client_id = input("\nClient ID: ").strip()
    if not client_id:
        print("\n[INFO] Skipped manual setup.")
        return None
    
    client_secret = input("Client Secret: ").strip()
    if not client_secret:
        print("\n[ERROR] Client Secret is required!")
        return None
    
    project_id = input("Project ID (optional, press Enter to use 'youtube-uploader'): ").strip()
    project_id = project_id or "youtube-uploader"
    
    # Create credentials structure
    creds = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }
    
    creds_file = os.path.join(os.path.dirname(__file__), "..", "youtube_oauth_credentials.json")
    
    try:
        with open(creds_file, 'w') as f:
            json.dump(creds, f, indent=2)
        print(f"\n[SUCCESS] Credentials file created: {creds_file}")
        return creds
    except Exception as e:
        print(f"\n[ERROR] Failed to create credentials file: {e}")
        return None

def instructions_for_download():
    """Print detailed instructions for downloading credentials."""
    print("\n" + "="*60)
    print("How to Download OAuth2 Credentials JSON")
    print("="*60)
    print("\nMethod 1: Right After Creation")
    print("  - When you create the OAuth client, a popup appears")
    print("  - Look for a 'Download JSON' button in that popup")
    print("  - Click it and save the file")
    
    print("\nMethod 2: From Credentials List")
    print("  1. Go to: https://console.cloud.google.com/apis/credentials")
    print("  2. Find your OAuth 2.0 Client ID in the list")
    print("  3. You have two options:")
    print("     a) Click the edit icon (✏️) or the name itself")
    print("     b) Look for a download icon (⬇️) next to it")
    print("  4. In the details page, look for 'Download JSON' button")
    
    print("\nMethod 3: Manual Creation")
    print("  - Copy Client ID and Client Secret from the details page")
    print("  - Use this script's manual setup (option 2)")
    
    print("\nMethod 4: From the Popup Window")
    print("  - If you see a popup with Client ID and Client Secret")
    print("  - There's usually a 'DOWNLOAD JSON' link/button")
    print("  - Click it to download the file")

def main():
    print("="*60)
    print("YouTube OAuth2 Credentials Setup")
    print("="*60)
    
    # Check if credentials already exist
    creds, creds_file = check_credentials_file()
    
    if creds:
        print("\n[SUCCESS] You're all set! Credentials file is valid.")
        print(f"\nNext step: Run the OAuth token generation script")
        print("  python scripts/generate_youtube_token.py")
        return
    
    # Credentials not found
    print("\n[INFO] No credentials file found. Let's set it up!")
    print("\nChoose an option:")
    print("1. Download JSON from Google Cloud Console (recommended)")
    print("2. Create credentials file manually (if you have Client ID/Secret)")
    print("3. Show detailed download instructions")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        instructions_for_download()
        print(f"\nOnce downloaded, save it as: {creds_file}")
        input("\nPress Enter after you've saved the file...")
        
        # Check again
        creds, _ = check_credentials_file()
        if creds:
            print("\n[SUCCESS] Credentials file detected! Setup complete.")
        else:
            print("\n[WARNING] File not found. Make sure it's named correctly.")
            print(f"Expected: {creds_file}")
    
    elif choice == "2":
        creds = create_manual_credentials()
        if creds:
            print("\n[SUCCESS] Setup complete!")
    
    elif choice == "3":
        instructions_for_download()
    
    elif choice == "4":
        print("\n[INFO] Exiting. Run this script again when ready.")
        sys.exit(0)
    
    else:
        print("\n[ERROR] Invalid choice!")

if __name__ == "__main__":
    main()

