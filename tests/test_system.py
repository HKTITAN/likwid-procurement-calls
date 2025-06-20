#!/usr/bin/env python3
"""
Test Suite for Organized Procurement System
Comprehensive tests for all components
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import ProcurementConfig, Vendor, InventoryItem
from src.data_manager import DataManager
from src.procurement_engine import ProcurementEngine, VendorSelector
from src.twilio_manager import TwilioManager

def test_data_loading():
    """Test CSV data loading"""
    print("🧪 Testing Data Loading...")
    
    config = ProcurementConfig()
    data_manager = DataManager(config)
    
    print(f"   ✅ Loaded {len(data_manager.vendors)} vendors")
    print(f"   ✅ Loaded {len(data_manager.inventory)} inventory items")
    print(f"   ✅ Loaded {sum(len(mappings) for mappings in data_manager.vendor_items.values())} vendor-item mappings")
    
    # Test specific data
    if "V001" in data_manager.vendors:
        vendor = data_manager.vendors["V001"]
        print(f"   ✅ Vendor V001: {vendor.vendor_name} - {vendor.phone_number}")
        print(f"   ✅ Authorized for calls: {vendor.is_authorized_for_calls}")
    
    if "I001" in data_manager.inventory:
        item = data_manager.inventory["I001"]
        print(f"   ✅ Item I001: {item.item_name} - Stock: {item.current_stock}")
        print(f"   ✅ Needs reorder: {item.needs_reorder}")
    
    return True

def test_vendor_selection():
    """Test vendor selection logic"""
    print("\n🧪 Testing Vendor Selection...")
    
    config = ProcurementConfig()
    data_manager = DataManager(config)
    selector = VendorSelector(config)
    
    # Get items needing reorder
    items_needing_reorder = data_manager.get_items_needing_reorder()
    
    if items_needing_reorder:
        item = items_needing_reorder[0]
        vendor_mappings = data_manager.get_vendors_for_item(item.item_id)
        
        if vendor_mappings:
            selection = selector.select_best_vendor_for_item(item, vendor_mappings, data_manager.vendors)
            
            if selection:
                vendor, mapping, score = selection
                print(f"   ✅ Selected vendor for {item.item_name}: {vendor.vendor_name}")
                print(f"   ✅ Price: ${mapping.get_effective_price(item.reorder_quantity):.2f}")
                print(f"   ✅ Score: {score:.3f}")
                return True
            else:
                print("   ❌ No vendor selected")
                return False
        else:
            print("   ❌ No vendor mappings found")
            return False
    else:
        print("   ℹ️  No items need reordering")
        return True

def test_twilio_manager():
    """Test Twilio manager (if configured)"""
    print("\n🧪 Testing Twilio Manager...")
    
    # Load environment variables
    from main import load_env_file
    load_env_file()
    
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    phone_number = os.environ.get("TWILIO_PHONE_NUMBER", "")
    allowed_number = os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")
    
    if not account_sid or "YOUR_TWILIO" in account_sid:
        print("   ⚠️  Twilio not configured - skipping live test")
        return True
    
    try:
        twilio_manager = TwilioManager(account_sid, auth_token, phone_number, allowed_number)
        print("   ✅ Twilio manager created successfully")
        
        # Test authorization check
        unauthorized_result = twilio_manager.make_call("+919999999999", "Test message")
        if unauthorized_result == "blocked_unauthorized_number":
            print("   ✅ Security check working - unauthorized number blocked")
        else:
            print("   ❌ Security check failed")
            return False
        
        # Optionally make a real test call
        test_call = input("   Make a real test call? (y/N): ").strip().lower()
        if test_call == 'y':
            call_sid = twilio_manager.make_test_call()
            if call_sid and call_sid != "blocked_unauthorized_number":
                print(f"   ✅ Test call successful! SID: {call_sid}")
            else:
                print("   ❌ Test call failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Twilio manager test failed: {e}")
        return False

def test_procurement_engine():
    """Test the complete procurement engine"""
    print("\n🧪 Testing Procurement Engine...")
    
    from main import create_config
    config = create_config()
    
    try:
        engine = ProcurementEngine(config)
        print("   ✅ Procurement engine initialized")
        
        # Test inventory check
        items_needed = engine.check_inventory_and_get_requirements()
        print(f"   ✅ Found {len(items_needed)} items needing reorder")
        
        if items_needed:
            # Test procurement plan creation
            plan = engine.create_procurement_plan(items_needed)
            print(f"   ✅ Procurement plan created: {plan['status']}")
            
            if plan['status'] == 'plan_created':
                print(f"   ✅ Total cost: ${plan['total_cost']:,.2f}")
                print(f"   ✅ Vendor groups: {len(plan['vendor_groups'])}")
                
                # Test plan execution (without actually making calls)
                print("   ⚠️  Skipping plan execution to avoid unwanted calls")
        
        # Test system status
        status = engine.get_system_status()
        print(f"   ✅ System status retrieved: {status['system_ready']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Procurement engine test failed: {e}")
        return False

def test_csv_export():
    """Test CSV export functionality"""
    print("\n🧪 Testing CSV Export...")
    
    config = ProcurementConfig()
    data_manager = DataManager(config)
    
    try:
        # Create a test filename
        test_filename = "logs/test_export.csv"
        data_manager.export_to_csv(test_filename)
        
        # Check if file was created
        if Path(test_filename).exists():
            print(f"   ✅ CSV export successful: {test_filename}")
            
            # Clean up test file
            Path(test_filename).unlink()
            print("   ✅ Test file cleaned up")
            
            return True
        else:
            print("   ❌ CSV export failed - file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ CSV export test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Vendor Selection", test_vendor_selection),
        ("Twilio Manager", test_twilio_manager),
        ("Procurement Engine", test_procurement_engine),
        ("CSV Export", test_csv_export)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    run_all_tests()
