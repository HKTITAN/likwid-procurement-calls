#!/usr/bin/env python3
"""Simple test script to check CSV loading"""

import os
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_vendors_from_csv():
    """Load vendor data from CSV file"""
    vendors = {}
    try:
        print("Loading vendors.csv...")
        with open('data/vendors.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vendor_id = row['vendor_id']
                vendors[vendor_id] = {
                    'name': row['vendor_name'],
                    'phone': row['phone_number'],
                    'email': row['email'],
                    'rating': float(row['rating']),
                    'delivery_time': int(row['delivery_time_days']),
                    'payment_terms': row['payment_terms'],
                    'status': row['status'],
                    'notes': row['notes']
                }
        print(f"Loaded {len(vendors)} vendors")
    except FileNotFoundError:
        logger.error("vendors.csv file not found")
    except Exception as e:
        logger.error(f"Error loading vendors: {e}")
        raise
    
    return vendors

def load_inventory_from_csv():
    """Load inventory data from CSV file"""
    inventory = {}
    try:
        print("Loading inventory.csv...")
        with open('data/inventory.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                item_id = row['item_id']
                inventory[item_id] = {
                    'name': row['item_name'],
                    'current_stock': int(row['current_stock']),
                    'min_threshold': int(row['min_threshold']),
                    'reorder_quantity': int(row['reorder_quantity']),
                    'unit_cost': float(row['unit_cost']),
                    'preferred_vendor_id': row['preferred_vendor_id'],
                    'alternative_vendor_ids': row['alternative_vendor_ids'].split(',') if row['alternative_vendor_ids'] else []
                }
        print(f"Loaded {len(inventory)} inventory items")
    except FileNotFoundError:
        logger.error("inventory.csv file not found")
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        raise
    
    return inventory

def load_vendor_items_mapping():
    """Load vendor-item mapping with pricing from CSV"""
    mapping = {}
    try:
        print("Loading vendor_items_mapping.csv...")
        with open('data/vendor_items_mapping.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vendor_id = row['vendor_id']
                item_id = row['item_id']
                
                if vendor_id not in mapping:
                    mapping[vendor_id] = {}
                
                mapping[vendor_id][item_id] = {
                    'vendor_item_name': row['vendor_item_name'],
                    'unit_price': float(row['unit_price']),
                    'minimum_order_qty': int(row['minimum_order_qty']),
                    'bulk_discount_qty': int(row['bulk_discount_qty']) if row['bulk_discount_qty'] else 0,
                    'bulk_discount_price': float(row['bulk_discount_price']) if row['bulk_discount_price'] else 0,
                    'availability_status': row['availability_status'],
                    'notes': row['notes']
                }
        print(f"Loaded mappings for {len(mapping)} vendors")
    except FileNotFoundError:
        logger.error("vendor_items_mapping.csv file not found")
    except Exception as e:
        logger.error(f"Error loading vendor items mapping: {e}")
        raise
    
    return mapping

if __name__ == "__main__":
    print("Testing CSV loading...")
    
    try:
        # Test loading each CSV file
        csv_vendors = load_vendors_from_csv()
        print(f"✅ Vendors loaded: {len(csv_vendors)}")
        
        csv_inventory = load_inventory_from_csv()
        print(f"✅ Inventory loaded: {len(csv_inventory)}")
        
        csv_vendor_mapping = load_vendor_items_mapping()
        print(f"✅ Vendor mapping loaded: {len(csv_vendor_mapping)}")
        
        print("\n✅ All CSV files loaded successfully!")
        
        # Show sample data
        print("\nSample vendor:", list(csv_vendors.keys())[0] if csv_vendors else "None")
        print("Sample inventory item:", list(csv_inventory.keys())[0] if csv_inventory else "None")
        print("Sample mapping vendor:", list(csv_vendor_mapping.keys())[0] if csv_vendor_mapping else "None")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
