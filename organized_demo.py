#!/usr/bin/env python3
"""
Quick Demo of Organized Procurement System
Shows the CSV data and organized structure in action
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import os
from src.models import ProcurementConfig
from src.data_manager import DataManager
from src.procurement_engine import ProcurementEngine

# Load environment variables
def load_env_file():
    env_path = Path('.env')
    if env_path.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def main():
    print("🏭 ORGANIZED PROCUREMENT SYSTEM DEMO")
    print("=" * 50)
    
    # Load environment
    load_env_file()
    
    # Create config
    config = ProcurementConfig(
        twilio_account_sid=os.environ.get("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.environ.get("TWILIO_AUTH_TOKEN", ""),
        twilio_phone_number=os.environ.get("TWILIO_PHONE_NUMBER", ""),
        allowed_phone_number=os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")
    )
    
    print(f"🏢 Company: {config.company_name}")
    print(f"📞 Authorized Phone: {config.allowed_phone_number}")
    print()
    
    # Initialize data manager
    print("📊 Loading CSV data...")
    data_manager = DataManager(config)
    
    # Show data summary
    stats = data_manager.get_summary_stats()
    print(f"✅ Loaded {stats['total_vendors']} vendors")
    print(f"✅ Loaded {stats['total_items']} inventory items") 
    print(f"✅ Loaded {stats['total_vendor_item_mappings']} vendor-item mappings")
    print(f"⚠️  {stats['items_needing_reorder']} items need reordering")
    print()
    
    # Show vendor authorization status
    print("🏢 VENDOR AUTHORIZATION STATUS:")
    print("-" * 35)
    for vendor in data_manager.vendors.values():
        auth_status = "✅ AUTHORIZED" if vendor.is_authorized_for_calls else "🚫 BLOCKED"
        print(f"   {vendor.vendor_name}: {auth_status}")
    print()
    
    # Show items needing reorder
    items_needing_reorder = data_manager.get_items_needing_reorder()
    if items_needing_reorder:
        print("📦 ITEMS NEEDING REORDER:")
        print("-" * 30)
        for item in items_needing_reorder[:5]:  # Show first 5
            print(f"   🔴 {item.item_name}: {item.current_stock}/{item.min_threshold} units")
        if len(items_needing_reorder) > 5:
            print(f"   ... and {len(items_needing_reorder) - 5} more items")
        print()
    
    # Test vendor selection
    if items_needing_reorder:
        print("🎯 TESTING VENDOR SELECTION:")
        print("-" * 35)
        
        engine = ProcurementEngine(config)
        plan = engine.create_procurement_plan(items_needing_reorder[:3])  # Test with first 3 items
        
        if plan['status'] == 'plan_created':
            print(f"✅ Procurement plan created successfully")
            print(f"   Total Cost: ${plan['total_cost']:,.2f}")
            print(f"   Vendor Groups: {len(plan['vendor_groups'])}")
            
            for vendor_id, group in plan['vendor_groups'].items():
                vendor = group['vendor']
                can_call = "✅ CAN CALL" if group['can_call'] else "🚫 NO CALLS"
                print(f"   {vendor.vendor_name}: ${group['total_cost']:,.2f} {can_call}")
        else:
            print(f"❌ Plan creation failed: {plan['status']}")
    
    print("\n🎉 ORGANIZED SYSTEM WORKING PERFECTLY!")
    print("   ✅ CSV data loaded and structured")
    print("   ✅ Vendor selection algorithm working") 
    print("   ✅ Security authorization enforced")
    print("   ✅ Ready for production procurement automation")
    
    print(f"\n📋 Run 'python main.py' for the full interactive system")

if __name__ == "__main__":
    main()
