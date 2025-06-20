#!/usr/bin/env python3
"""
Production Procurement System with Integrated Twilio Calling
Demonstrates the full workflow with your proven calling pattern integrated
"""

from caller import *

def check_inventory_status():
    """Check inventory and return items that need reordering"""
    items_to_reorder = []
    
    for item_name, item in inventory_items.items():
        if item.quantity <= item.min_threshold:
            items_to_reorder.append(item_name)
    
    return items_to_reorder

def select_best_vendor_for_items(items: List[str]):
    """Select the best vendor based on scoring algorithm"""
    if not items:
        return None
    
    # Calculate scores for all vendors
    vendor_scores = {}
    for vendor_name, vendor in vendor_data.items():
        score = get_vendor_score(vendor, items)
        total_cost = calculate_total_cost(items, vendor)
        vendor_scores[vendor_name] = {
            'vendor': vendor,
            'score': score,
            'total_cost': total_cost
        }
    
    # Select best vendor
    best_vendor_name = max(vendor_scores.keys(), key=lambda x: vendor_scores[x]['score'])
    return vendor_scores[best_vendor_name]['vendor']

def run_full_procurement_demo():
    """Run a complete procurement demo with integrated calling"""
    print("=" * 70)
    print("PRODUCTION PROCUREMENT SYSTEM - FULL DEMO")
    print("=" * 70)
    
    # Step 1: Check inventory
    print("\n📦 STEP 1: CHECKING INVENTORY")
    print("-" * 30)
    items_to_reorder = check_inventory_status()
    
    if not items_to_reorder:
        print("✅ All inventory levels are sufficient. No procurement needed.")
        return
    
    print(f"📋 Items requiring reorder: {', '.join(items_to_reorder)}")
    
    # Step 2: Select best vendor
    print("\n🏢 STEP 2: VENDOR SELECTION")
    print("-" * 30)
    best_vendor = select_best_vendor_for_items(items_to_reorder)
    
    if not best_vendor:
        print("❌ No suitable vendor found.")
        return
    
    total_cost = calculate_total_cost(items_to_reorder, best_vendor)
    print(f"🎯 Selected Vendor: {best_vendor.name}")
    print(f"💰 Total Cost: ${total_cost:,.2f}")
    print(f"📞 Phone: {best_vendor.phone}")
    print(f"⭐ Rating: {best_vendor.rating}/5.0")
    
    # Step 3: Make phone call using integrated system
    print("\n📞 STEP 3: MAKING PROCUREMENT CALL")
    print("-" * 40)
    print("Using your proven Twilio integration...")
    
    call_sid = make_phone_call_with_retry(best_vendor, items_to_reorder)
    
    if call_sid and call_sid != "blocked_unauthorized_number":
        print(f"✅ Call completed successfully! SID: {call_sid}")
        call_success = True
    else:
        print("❌ Call failed or was blocked")
        call_success = False
    
    # Step 4: Send email confirmation
    print("\n📧 STEP 4: EMAIL CONFIRMATION")
    print("-" * 30)
    email_success = send_email_notification(best_vendor, items_to_reorder, total_cost)
    
    if email_success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Email failed (may need configuration)")
    
    # Step 5: Record the transaction
    print("\n📊 STEP 5: RECORDING TRANSACTION")
    print("-" * 35)
    
    record = ProcurementRecord(
        timestamp=datetime.datetime.now().isoformat(),
        items_required=items_to_reorder,
        selected_vendor=best_vendor.name,
        total_cost=total_cost,
        status="completed" if call_success else "call_failed",
        call_sid=call_sid,
        email_sent=email_success
    )
    
    # Use ProcurementManager to save data
    pm = ProcurementManager()
    pm.records.append(record)
    pm.save_data()
    pm.export_to_csv()
    
    print("✅ Transaction recorded successfully!")
    
    # Summary
    print("\n" + "=" * 70)
    print("PROCUREMENT SUMMARY")
    print("=" * 70)
    print(f"Items Ordered:    {', '.join(items_to_reorder)}")
    print(f"Vendor:           {best_vendor.name}")
    print(f"Total Cost:       ${total_cost:,.2f}")
    print(f"Phone Call:       {'✅ SUCCESS' if call_success else '❌ FAILED'}")
    print(f"Email:            {'✅ SENT' if email_success else '❌ FAILED'}")
    print(f"Call SID:         {call_sid or 'N/A'}")
    print(f"Status:           {record.status.upper()}")
    print("=" * 70)

def test_calling_only():
    """Test just the calling functionality"""
    print("=" * 50)
    print("TESTING INTEGRATED CALLING ONLY")
    print("=" * 50)
    
    # Use a vendor that has the allowed phone number
    items_needed = ["item1", "item3"]
    test_vendor = None
    
    # Find vendor with allowed phone number
    for vendor_name, vendor in vendor_data.items():
        if vendor.phone == ALLOWED_PHONE_NUMBER:
            test_vendor = vendor
            break
    
    if not test_vendor:
        print("❌ No vendor found with the allowed phone number!")
        return False
    
    print(f"Testing call to: {test_vendor.name}")
    print(f"Phone: {test_vendor.phone}")
    print(f"Items: {', '.join(items_needed)}")
    print()
    
    call_sid = make_phone_call_with_retry(test_vendor, items_needed)
    
    if call_sid and call_sid != "blocked_unauthorized_number":
        print(f"✅ CALL TEST PASSED! SID: {call_sid}")
        return True
    else:
        print("❌ CALL TEST FAILED")
        return False

def main():
    """Main function with menu options"""
    print("🏭 PRODUCTION PROCUREMENT SYSTEM")
    print("Using your proven Twilio calling integration")
    print()
    
    while True:
        print("\nChoose an option:")
        print("1. Run full procurement demo")
        print("2. Test calling functionality only")
        print("3. Test simple Twilio call")
        print("4. Check inventory only")
        print("5. View current vendors")
        print("6. Run original enhanced workflow")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            run_full_procurement_demo()
        
        elif choice == "2":
            test_calling_only()
        
        elif choice == "3":
            print("\nTesting simple Twilio call...")
            result = test_simple_twilio_call()
            if result:
                print(f"✅ Test successful! SID: {result}")
            else:
                print("❌ Test failed")
        
        elif choice == "4":
            print("\n📦 CURRENT INVENTORY STATUS:")
            print("-" * 30)
            for item_name, item in inventory_items.items():
                status = "🔴 LOW" if item.quantity <= item.min_threshold else "✅ OK"
                print(f"{item.name}: {item.quantity} units {status}")
        
        elif choice == "5":
            print("\n🏢 AVAILABLE VENDORS:")
            print("-" * 25)
            for vendor_name, vendor in vendor_data.items():
                print(f"{vendor.name}: ${vendor.price} - {vendor.phone} - ⭐{vendor.rating}")
        
        elif choice == "6":
            print("\nRunning original enhanced workflow...")
            run_enhanced_procurement_workflow()
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
