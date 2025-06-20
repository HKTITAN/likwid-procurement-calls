#!/usr/bin/env python3
"""
Test script for integrated Twilio calling functionality
Uses the exact working pattern you provided to ensure reliability
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

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    print("❌ Twilio package not available. Please install: pip install twilio")
    TWILIO_AVAILABLE = False
    exit(1)

# Your credentials from .env
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_phone = os.environ.get("TWILIO_PHONE_NUMBER", "+15017122661")
target_phone = os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")

def test_procurement_call():
    """Test a procurement call using your exact working pattern"""
    print("🔄 Testing procurement call integration...")
    print(f"   From: {twilio_phone}")
    print(f"   To: {target_phone}")
    
    if not account_sid or "YOUR_TWILIO" in account_sid:
        print("❌ Twilio credentials not configured properly")
        return False
    
    try:
        # Your exact working pattern
        client = Client(account_sid, auth_token)
        
        # Procurement-specific message
        twiml_content = """<Response><Say voice="alice" language="en-IN">Hello, this is an automated procurement call from Bio Mac Lifesciences. You have been selected as our preferred supplier for item1, item3 based on your competitive quote and excellent service record. A formal purchase order and email confirmation will be sent to you shortly. Thank you for your continued partnership with Bio Mac Lifesciences.</Say></Response>"""
        
        call = client.calls.create(
            twiml=twiml_content,
            to=target_phone,
            from_=twilio_phone
        )
        
        print(f"✅ Procurement call successful!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        
        # Log the call
        with open("successful_calls.log", "a") as f:
            import datetime
            f.write(f"{datetime.datetime.now()}: PROCUREMENT CALL TEST - SID: {call.sid}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Procurement call failed: {e}")
        return False

def test_simple_call():
    """Test a simple call using your exact working pattern"""
    print("🔄 Testing simple call...")
    
    if not account_sid or "YOUR_TWILIO" in account_sid:
        print("❌ Twilio credentials not configured properly")
        return False
    
    try:
        # Your exact working pattern
        client = Client(account_sid, auth_token)
        
        twiml_content = """<Response><Say voice="alice" language="en-IN">Hello, this is a test call from the integrated procurement system. The system is working correctly.</Say></Response>"""
        
        call = client.calls.create(
            twiml=twiml_content,
            to=target_phone,
            from_=twilio_phone
        )
        
        print(f"✅ Simple call successful!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple call failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRATED TWILIO CALLING TESTS")
    print("=" * 60)
    
    print(f"📞 Using your proven Twilio pattern")
    print(f"📋 Account SID: {account_sid[:10]}...{account_sid[-4:] if account_sid else 'NOT SET'}")
    print(f"📱 From Phone: {twilio_phone}")
    print(f"🎯 Target Phone: {target_phone}")
    print()
    
    # Test 1: Simple call
    print("TEST 1: Simple Call")
    print("-" * 20)
    success1 = test_simple_call()
    print()
    
    # Test 2: Procurement call
    print("TEST 2: Procurement Call")
    print("-" * 25)
    success2 = test_procurement_call()
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Simple Call:      {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Procurement Call: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! The integration is working correctly.")
        print("   Your procurement system is ready to make live calls.")
    else:
        print("\n⚠️  Some tests failed. Check your Twilio configuration.")
    
    print("=" * 60)
