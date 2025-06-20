#!/usr/bin/env python3
"""
Quick Twilio Phone Call Test - Simplified Version
"""

def quick_call_test():
    """Simplified call test"""
    try:
        print("Importing Twilio...")
        from twilio.rest import Client
        
        print("✅ Twilio import successful!")
        
        # Your credentials
        account_sid = "AC820daae89092e30fee3487e80162d2e2"
        auth_token = "690636dcdd752868f4e77648dc0d49eb"
        
        print("Creating Twilio client...")
        client = Client(account_sid, auth_token)
        
        print("✅ Twilio client created successfully!")
        
        print("🔥 MAKING LIVE CALL TO +918800000488...")
        print("📞 This is a REAL phone call!")
        
        # Make the call using your exact pattern
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to="+918800000488",
            from_="+14323484517"
        )

        print(f"🎉 SUCCESS! Call SID: {call.sid}")
        print("📱 The phone should be ringing now!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Call Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Twilio Test")
    print("=" * 30)
    success = quick_call_test()
    
    if success:
        print("\n✅ Your enhanced procurement system can make REAL calls!")
        print("🎯 Ready to integrate with the full procurement workflow!")
    else:
        print("\n⚠️  Phone calling needs troubleshooting")
        print("💡 The procurement system will work in simulation mode")
