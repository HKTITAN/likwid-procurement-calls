#!/usr/bin/env python3
"""
Working Twilio Call Script - Windows Compatible
This bypasses the problematic Twilio installation issues on Windows
"""

import os
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urlencode
import base64

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

# Your credentials
account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "AC820daae89092e30fee3487e80162d2e2")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "690636dcdd752868f4e77648dc0d49eb")
from_phone = os.environ.get("TWILIO_PHONE_NUMBER", "+14323484517")
to_phone = os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")

def make_twilio_call_direct_api(message="Hello, this is a test call from the procurement system."):
    """
    Make a Twilio call using direct REST API calls
    This bypasses the problematic Python SDK installation
    """
    
    print("🔄 Making Twilio call using direct REST API...")
    print(f"   From: {from_phone}")
    print(f"   To: {to_phone}")
    
    # Twilio REST API endpoint
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    
    # Create TwiML for the call
    twiml = f"<Response><Say voice='alice' language='en-IN'>{message}</Say></Response>"
    
    # Prepare the data
    data = {
        'From': from_phone,
        'To': to_phone,
        'Twiml': twiml
    }
    
    # Create authentication header
    auth_string = f"{account_sid}:{auth_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Make the API call
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 201:
            # Success!
            call_data = response.json()
            call_sid = call_data.get('sid')
            status = call_data.get('status')
            
            print(f"✅ CALL SUCCESSFUL!")
            print(f"   Call SID: {call_sid}")
            print(f"   Status: {status}")
            
            # Log the successful call
            import datetime
            with open("successful_calls.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: DIRECT API CALL - SID: {call_sid} - Status: {status}\n")
            
            return call_sid
            
        else:
            print(f"❌ CALL FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ API CALL ERROR: {e}")
        return None

def test_procurement_call():
    """Test a procurement call using direct API"""
    message = "Hello, this is an automated procurement call from Bio Mac Lifesciences. You have been selected as our preferred supplier based on your competitive quote and excellent service record. A formal purchase order and email confirmation will be sent to you shortly. Thank you for your continued partnership with Bio Mac Lifesciences."
    
    return make_twilio_call_direct_api(message)

def test_simple_call():
    """Test a simple call using direct API"""
    message = "Hello, this is a test call from the integrated procurement system. The system is working correctly using direct API calls."
    
    return make_twilio_call_direct_api(message)

if __name__ == "__main__":
    print("=" * 70)
    print("WINDOWS-COMPATIBLE TWILIO CALLING")
    print("=" * 70)
    print("Using direct REST API calls to bypass SDK installation issues")
    print()
    
    print(f"📋 Account SID: {account_sid[:10]}...{account_sid[-4:]}")
    print(f"📱 From: {from_phone}")
    print(f"🎯 To: {to_phone}")
    print()
    
    # Test 1: Simple call
    print("TEST 1: Simple Call")
    print("-" * 20)
    success1 = test_simple_call()
    print()
    
    if success1:
        # Test 2: Procurement call
        print("TEST 2: Procurement Call")
        print("-" * 25)
        success2 = test_procurement_call()
        print()
    else:
        success2 = False
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Simple Call:      {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Procurement Call: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Direct API calling is working perfectly!")
        print("   This method can be integrated into the procurement system.")
    else:
        print("\n⚠️  Some tests failed. Check your Twilio configuration.")
    
    print("=" * 70)
