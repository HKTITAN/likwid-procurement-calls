#!/usr/bin/env python3
"""
Test the Fixed Twilio Integration
Tests the new direct API approach in caller.py
"""

from caller import test_simple_twilio_call, CONFIG, ALLOWED_PHONE_NUMBER

def main():
    print("=" * 60)
    print("TESTING FIXED TWILIO INTEGRATION")
    print("=" * 60)
    print("Using direct REST API to bypass Windows SDK issues")
    print()
    
    print(f"🏢 Company: {CONFIG['company_name']}")
    print(f"📞 Target Phone: {ALLOWED_PHONE_NUMBER}")
    print()
    
    print("Running test call...")
    result = test_simple_twilio_call()
    
    print()
    if result:
        print("🎉 SUCCESS! The fixed integration is working!")
        print(f"   Call SID: {result}")
        print("   Check successful_calls.log for details")
        print("   Your procurement system is ready for production!")
    else:
        print("❌ Test failed. Check your Twilio credentials.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
