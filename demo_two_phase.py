#!/usr/bin/env python3
"""
Two-Phase Procurement Demo Script
=================================

This script demonstrates the new two-phase procurement workflow:
Phase 1: Call vendors for quotes
Phase 2: Compare prices and order from cheapest vendor

Usage:
    python demo_two_phase.py

Features:
- Loads inventory and vendor data from CSV files
- Identifies items needing reordering
- Calls multiple vendors for quotes
- Updates CSV with real-time pricing
- Compares all quotes and selects cheapest
- Places final order with winning vendor
- Generates comprehensive procurement report
"""

import sys
import os
from pathlib import Path

# Add the main directory to path so we can import caller
sys.path.insert(0, str(Path(__file__).parent))

from caller import (
    run_two_phase_procurement_workflow,
    show_csv_inventory_status,
    show_csv_vendor_info,
    test_simple_twilio_call,
    CONFIG,
    csv_inventory,
    csv_vendors,
    csv_vendor_mapping
)

def demo_overview():
    """Display overview of the two-phase procurement system"""
    print("=" * 80)
    print("🏢 TWO-PHASE PROCUREMENT AUTOMATION SYSTEM")
    print("=" * 80)
    print()
    print("📋 WORKFLOW OVERVIEW:")
    print("   Phase 1: Quote Collection")
    print("   ├── 1. Check inventory levels from CSV")
    print("   ├── 2. Identify items below minimum threshold")
    print("   ├── 3. Call ALL eligible vendors for quotes")
    print("   ├── 4. Update CSV with real-time pricing")
    print("   └── 5. Log all quote requests")
    print()
    print("   Phase 2: Price Comparison & Order")
    print("   ├── 6. Compare all received quotes")
    print("   ├── 7. Select vendor with lowest total cost")
    print("   ├── 8. Call winning vendor to place order")
    print("   ├── 9. Send confirmation email")
    print("   └── 10. Generate procurement report")
    print()
    print("💡 BENEFITS:")
    print("   • Ensures competitive pricing")
    print("   • Transparent vendor selection")
    print("   • Automated quote comparison")
    print("   • Real-time price updates")
    print("   • Comprehensive audit trail")
    print("=" * 80)
    print()

def show_system_status():
    """Show current system status"""
    print("📊 CURRENT SYSTEM STATUS:")
    print("-" * 40)
    
    # Count inventory items
    total_items = len(csv_inventory)
    items_below_threshold = sum(1 for item in csv_inventory.values() 
                               if item['current_stock'] <= item['min_threshold'])
    
    print(f"Total inventory items: {total_items}")
    print(f"Items below threshold: {items_below_threshold}")
    print()
    
    # Count vendors
    total_vendors = len(csv_vendors)
    active_vendors = sum(1 for v in csv_vendors.values() if v['status'] == 'Active')
    callable_vendors = sum(1 for v in csv_vendors.values() 
                          if v['status'] == 'Active' and 'CALLS BLOCKED' not in v['notes'])
    
    print(f"Total vendors: {total_vendors}")
    print(f"Active vendors: {active_vendors}")
    print(f"Callable vendors: {callable_vendors}")
    print()
    
    # Show items needing procurement
    if items_below_threshold > 0:
        print("🚨 ITEMS REQUIRING PROCUREMENT:")
        for item_id, item_info in csv_inventory.items():
            if item_info['current_stock'] <= item_info['min_threshold']:
                shortage = item_info['min_threshold'] - item_info['current_stock']
                print(f"   • {item_info['name']}: {item_info['current_stock']} units "
                      f"(need {shortage} more)")
        print()
    else:
        print("✅ All inventory levels are adequate")
        print()

def demo_menu():
    """Interactive demo menu"""
    while True:
        print("\n🎯 DEMO OPTIONS:")
        print("1. Show System Overview")
        print("2. Check Current Inventory Status")
        print("3. View Vendor Information")
        print("4. Run Complete Two-Phase Workflow")
        print("5. Test Twilio Connection")
        print("6. Exit Demo")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            demo_overview()
            show_system_status()
        elif choice == '2':
            show_csv_inventory_status()
        elif choice == '3':
            show_csv_vendor_info()
        elif choice == '4':
            print("\n🚀 STARTING TWO-PHASE PROCUREMENT WORKFLOW...")
            print("=" * 60)
            run_two_phase_procurement_workflow()
        elif choice == '5':
            print("\n📞 TESTING TWILIO CONNECTION...")
            print("-" * 40)
            test_simple_twilio_call()
        elif choice == '6':
            print("\n👋 Demo completed. Thank you!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main demo function"""
    print()
    demo_overview()
    show_system_status()
    
    # Check if we should run automatically or interactively
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'auto':
        print("🚀 RUNNING AUTOMATIC TWO-PHASE WORKFLOW...")
        print("=" * 60)
        run_two_phase_procurement_workflow()
    else:
        demo_menu()

if __name__ == "__main__":
    main()
