#!/usr/bin/env python3
"""
Direct test using your exact working Twilio pattern
This demonstrates that your code works and can be integrated
"""

import os
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = Path('.env')
    if env_path.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env_file()

# Download the helper library from https://www.twilio.com/docs/python/install
try:
    from twilio.rest import Client
    print("✅ Twilio module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Twilio: {e}")
    exit(1)

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "AC820daae89092e30fee3487e80162d2e2")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "690636dcdd752868f4e77648dc0d49eb")
from_phone = os.environ.get("TWILIO_PHONE_NUMBER", "+14323484517")
to_phone = os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")

print("=" * 60)
print("DIRECT TWILIO TEST - YOUR WORKING PATTERN")
print("=" * 60)
print(f"📋 Account SID: {account_sid[:10]}...{account_sid[-4:]}")
print(f"📱 From: {from_phone}")
print(f"🎯 To: {to_phone}")
print()

try:
    print("Creating Twilio client...")
    client = Client(account_sid, auth_token)
    print("✅ Client created successfully")
    
    print("Initiating call...")
    
    # Your exact working pattern with procurement message
    call = client.calls.create(
        twiml="<Response><Say voice='alice' language='en-IN'>Hello, this is an automated procurement call from Bio Mac Lifesciences. You have been selected as our preferred supplier based on your competitive quote. A formal purchase order will be sent shortly. Thank you for your partnership.</Say></Response>",
        to=to_phone,
        from_=from_phone
    )
    
    print(f"✅ CALL SUCCESSFUL!")
    print(f"   Call SID: {call.sid}")
    print(f"   Status: {call.status}")
    
    # Log the successful call
    import datetime
    with open("successful_calls.log", "a") as f:
        f.write(f"{datetime.datetime.now()}: DIRECT TEST CALL - SID: {call.sid} - Status: {call.status}\n")
    
    print("\n🎉 SUCCESS: Your Twilio integration is working perfectly!")
    print("   This pattern can be used in the procurement system.")
    
except Exception as e:
    print(f"❌ CALL FAILED: {e}")
    print("   Check your Twilio credentials and phone numbers.")

print("=" * 60)
