#!/usr/bin/env python3
"""
Simple Twilio Test Script
Based on your working Twilio code pattern
"""

# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

def test_twilio_call():
    """Test Twilio call using your exact working pattern"""
    
    # Set environment variables for your credentials
    # Read more at http://twil.io/secure
    account_sid = "AC820daae89092e30fee3487e80162d2e2"
    auth_token = "690636dcdd752868f4e77648dc0d49eb"
    client = Client(account_sid, auth_token)

    # Custom message for procurement system
    twiml_message = """
    <Response>
        <Say voice="alice" language="en-IN">
            Hello, this is a test call from Bio Mac Lifesciences procurement automation system. 
            This call confirms that your enhanced procurement system is working correctly and can make real phone calls. 
            The system has successfully analyzed inventory, selected the best vendor, and is now notifying you of the procurement decision. 
            Thank you for testing the enhanced procurement system.
        </Say>
    </Response>
    """

    try:
        print("🔥 Making LIVE test call to +918800000488...")
        print("📞 This will be a REAL phone call!")
        print("-" * 50)
        
        call = client.calls.create(
            twiml=twiml_message,  # Custom message
            to="+918800000488",
            from_="+14323484517"
        )

        print(f"✅ SUCCESS! Call initiated successfully!")
        print(f"📱 Call SID: {call.sid}")
        print(f"📞 Called: +918800000488")
        print(f"📤 From: +14323484517")
        print("\n🎉 Your enhanced procurement system can now make REAL phone calls!")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ ERROR: Call failed - {e}")
        return None

def test_basic_call():
    """Test with your original demo URL"""
    account_sid = "AC820daae89092e30fee3487e80162d2e2"
    auth_token = "690636dcdd752868f4e77648dc0d49eb"
    client = Client(account_sid, auth_token)

    try:
        print("📞 Testing basic call with demo URL...")
        
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to="+918800000488",
            from_="+14323484517"
        )

        print(f"✅ Basic call successful! SID: {call.sid}")
        return call.sid
        
    except Exception as e:
        print(f"❌ Basic call failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Twilio Phone Call Test")
    print("=" * 40)
    print("This will make REAL phone calls to +918800000488")
    
    # Test 1: Basic call with demo URL
    print("\n1️⃣  Testing basic call...")
    basic_result = test_basic_call()
    
    if basic_result:
        print("\n2️⃣  Testing custom procurement message...")
        custom_result = test_twilio_call()
        
        if custom_result:
            print("\n🎊 ALL TESTS PASSED!")
            print("Your enhanced procurement system is ready for live phone calls!")
        else:
            print("\n⚠️  Custom message failed, but basic calling works")
    else:
        print("\n❌ Basic calling failed - check credentials and phone number verification")
