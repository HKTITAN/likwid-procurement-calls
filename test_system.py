#!/usr/bin/env python3
"""
Quick test script for the two-phase procurement system
"""

try:
    from caller import (
        csv_inventory, 
        csv_vendors, 
        csv_vendor_mapping,
        get_vendors_for_item,
        load_vendors_from_csv,
        load_inventory_from_csv,
        load_vendor_items_mapping
    )
    
    print("✅ Successfully imported two-phase procurement system")
    print(f"📦 Loaded {len(csv_inventory)} inventory items")
    print(f"🏢 Loaded {len(csv_vendors)} vendors")
    print(f"🔗 Loaded {sum(len(items) for items in csv_vendor_mapping.values())} vendor-item mappings")
    
    # Test inventory analysis
    items_below_threshold = []
    for item_id, item_info in csv_inventory.items():
        if item_info['current_stock'] <= item_info['min_threshold']:
            items_below_threshold.append(item_id)
    
    print(f"\n📊 INVENTORY ANALYSIS:")
    print(f"Items below threshold: {len(items_below_threshold)}")
    
    if items_below_threshold:
        print("Items needing procurement:")
        for item_id in items_below_threshold[:3]:  # Show first 3
            item = csv_inventory[item_id]
            print(f"  • {item['name']}: {item['current_stock']} units (min: {item['min_threshold']})")
    
    # Test vendor availability
    print(f"\n🏢 VENDOR ANALYSIS:")
    active_vendors = [v for v in csv_vendors.values() if v['status'] == 'Active']
    callable_vendors = [v for v in active_vendors if 'CALLS BLOCKED' not in v['notes']]
    
    print(f"Active vendors: {len(active_vendors)}")
    print(f"Callable vendors: {len(callable_vendors)}")
    
    if callable_vendors:
        print("Vendors available for calls:")
        for vendor in callable_vendors:
            print(f"  • {vendor['name']}")
    
    # Test vendor-item mapping
    if items_below_threshold:
        test_item = items_below_threshold[0]
        vendors_for_item = get_vendors_for_item(test_item, csv_inventory, csv_vendor_mapping)
        print(f"\n🔍 TEST ITEM ANALYSIS:")
        print(f"Item: {csv_inventory[test_item]['name']}")
        print(f"Vendors who can supply this item: {len(vendors_for_item)}")
        for vendor_id in vendors_for_item:
            if vendor_id in csv_vendors:
                vendor_name = csv_vendors[vendor_id]['name']
                price = csv_vendor_mapping[vendor_id][test_item]['unit_price']
                print(f"  • {vendor_name}: ₹{price}")
    
    print(f"\n✅ System validation completed successfully!")
    print(f"🚀 Ready to run two-phase procurement workflow")
    
except Exception as e:
    print(f"❌ Error during system validation: {e}")
    import traceback
    traceback.print_exc()
