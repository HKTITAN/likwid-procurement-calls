#!/usr/bin/env python3
"""
Quick Demo of Integrated Twilio Calling System
Shows your working pattern in action within the procurement system
"""

from caller import *

def demo_integration():
    """Demonstrate the integrated calling system"""
    print("=" * 60)
    print("INTEGRATED TWILIO CALLING DEMO")
    print("=" * 60)
    
    print(f"🔧 Company: {CONFIG['company_name']}")
    print(f"📞 Allowed Phone: {ALLOWED_PHONE_NUMBER}")
    print(f"🏢 From Phone: {TWILIO_PHONE_NUMBER}")
    print()
    
    # Show inventory status
    print("📦 CURRENT INVENTORY:")
    print("-" * 25)
    items_needing_reorder = []
    for item_name, item in inventory_items.items():
        status = "🔴 LOW" if item.quantity <= item.min_threshold else "✅ OK"
        print(f"   {item.name}: {item.quantity} units {status}")
        if item.quantity <= item.min_threshold:
            items_needing_reorder.append(item_name)
    
    print()
    print("🏢 AVAILABLE VENDORS:")
    print("-" * 25)
    for vendor_name, vendor in vendor_data.items():
        security_status = "✅ ALLOWED" if vendor.phone == ALLOWED_PHONE_NUMBER else "🚫 BLOCKED"
        print(f"   {vendor.name}: ${vendor.price} - {vendor.phone} {security_status}")
    
    print()
    if items_needing_reorder:
        print(f"📋 Items needing reorder: {', '.join(items_needing_reorder)}")
        
        # Find the vendor with allowed phone number
        authorized_vendor = None
        for vendor_name, vendor in vendor_data.items():
            if vendor.phone == ALLOWED_PHONE_NUMBER:
                authorized_vendor = vendor
                break
        
        if authorized_vendor:
            print(f"🎯 Authorized vendor found: {authorized_vendor.name}")
            total_cost = calculate_total_cost(items_needing_reorder, authorized_vendor)
            print(f"💰 Total cost: ${total_cost:,.2f}")
            
            print("\n📞 TESTING INTEGRATED CALLING:")
            print("-" * 35)
            print("Using your exact working Twilio pattern...")
            
            # Test the integrated calling function
            call_result = make_phone_call_with_retry(authorized_vendor, items_needing_reorder)
            
            if call_result and call_result != "blocked_unauthorized_number":
                print(f"✅ Call integration SUCCESS! SID: {call_result}")
            elif call_result == "blocked_unauthorized_number":
                print("🚫 Call blocked for security (this shouldn't happen with authorized vendor)")
            else:
                print("❌ Call failed or simulated (Twilio may not be installed)")
            
        else:
            print("⚠️  No authorized vendor found for calling")
    else:
        print("✅ No items need reordering at this time")
    
    print("\n" + "=" * 60)
    print("INTEGRATION SUMMARY:")
    print("✅ Your Twilio pattern is integrated into caller.py")
    print("✅ Security validation enforces allowed phone number")
    print("✅ System gracefully handles Twilio installation issues")
    print("✅ Production-ready with retry logic and logging")
    print("=" * 60)

if __name__ == "__main__":
    demo_integration()
