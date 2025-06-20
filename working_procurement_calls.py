#!/usr/bin/env python3
"""
Working Twilio Integration for Enhanced Procurement System
This version uses the simplified approach that works with your setup
"""

import os
import sys
import time

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def working_twilio_call(message_text="Procurement notification", target_number="+918800000488"):
    """
    Working Twilio call function using your successful pattern
    """
    try:
        print("📞 Initiating Twilio call...")
        from twilio.rest import Client
        
        # Your working credentials
        account_sid = "AC820daae89092e30fee3487e80162d2e2"
        auth_token = "690636dcdd752868f4e77648dc0d49eb"
        client = Client(account_sid, auth_token)
        
        # Custom TwiML for procurement message
        twiml_content = f"""
        <Response>
            <Say voice="alice" language="en-IN">
                Hello, this is an automated call from Bio Mac Lifesciences procurement system.
                {message_text}
                A formal purchase order will be sent via email.
                Thank you for your partnership.
            </Say>
        </Response>
        """
        
        print(f"🔥 Making LIVE call to {target_number}...")
        
        # Use your working call pattern
        call = client.calls.create(
            twiml=twiml_content,
            to=target_number,
            from_="+14323484517"
        )
        
        print(f"✅ Call SUCCESS! SID: {call.sid}")
        return call.sid
        
    except Exception as e:
        print(f"❌ Call failed: {e}")
        return None

def run_procurement_with_working_calls():
    """
    Run procurement workflow with working call functionality
    """
    print("🏢 Enhanced Procurement System - LIVE CALLING VERSION")
    print("=" * 60)
    
    # Simulate procurement decision (using your enhanced logic)
    print("📊 Analyzing inventory...")
    items_needed = ["item2", "item3"]  # Low stock items
    
    print("🏆 Vendor selection...")
    selected_vendor = "vendor1"
    vendor_phone = "+918800000488"  # Your safe number
    total_cost = 12500
    
    print(f"✅ Selected: {selected_vendor}")
    print(f"💰 Total cost: Rs.{total_cost}")
    print(f"📞 Calling: {vendor_phone}")
    
    # Create procurement message
    message = f"You have been selected as our supplier for {', '.join(items_needed)} with total cost of {total_cost} rupees"
    
    # Make the actual call
    call_sid = working_twilio_call(message, vendor_phone)
    
    if call_sid:
        print("\n🎉 PROCUREMENT WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"📱 Call SID: {call_sid}")
        print("📞 The vendor should have received the call!")
        
        # Log the success
        with open("successful_calls.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Call SID: {call_sid} - Vendor: {selected_vendor} - Cost: Rs.{total_cost}\n")
        
        return True
    else:
        print("\n⚠️  Call failed, but procurement decision completed")
        return False

def test_call_only():
    """Just test the calling functionality"""
    print("🧪 TESTING LIVE CALL FUNCTIONALITY")
    print("=" * 40)
    
    test_message = "This is a test call from your enhanced procurement automation system. The system is working correctly and ready for live procurement notifications."
    
    result = working_twilio_call(test_message)
    
    if result:
        print("\n✅ CALL TEST SUCCESSFUL!")
        print("🎯 Your system is ready for live procurement calls!")
    else:
        print("\n❌ Call test failed")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_call_only()
    else:
        run_procurement_with_working_calls()
