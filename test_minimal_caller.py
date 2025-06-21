#!/usr/bin/env python3
"""
Minimal version of caller.py to test CSV loading without audio dependencies
"""

import os
import csv
import sys
import json
import logging
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    from pathlib import Path
    env_path = Path('.env')
    if env_path.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env_file()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procurement_log.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "company_name": os.environ.get("COMPANY_NAME", "Bio Mac Lifesciences"),
    "procurement_email": os.environ.get("PROCUREMENT_EMAIL", "procurement@org1.com"),
    "auto_approve_threshold": int(os.environ.get("AUTO_APPROVE_THRESHOLD", "1000")),
    "max_retries": int(os.environ.get("MAX_RETRIES", "3")),
    "retry_delay": int(os.environ.get("RETRY_DELAY", "5")),
    "data_file": os.environ.get("DATA_FILE", "procurement_data.json"),
    "log_file": os.environ.get("LOG_FILE", "procurement_log.log")
}

# ==============================================================================
# --- CSV DATA MANAGEMENT ---
# ==============================================================================

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
        print(f"✅ Loaded {len(vendors)} vendors")
    except FileNotFoundError:
        logger.error("vendors.csv file not found")
        return {}
    except Exception as e:
        logger.error(f"Error loading vendors: {e}")
        return {}
    
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
        print(f"✅ Loaded {len(inventory)} inventory items")
    except FileNotFoundError:
        logger.error("inventory.csv file not found")
        return {}
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        return {}
    
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
        print(f"✅ Loaded mappings for {len(mapping)} vendors")
    except FileNotFoundError:
        logger.error("vendor_items_mapping.csv file not found")
        return {}
    except Exception as e:
        logger.error(f"Error loading vendor items mapping: {e}")
        return {}
    
    return mapping

def show_csv_inventory_status(csv_inventory):
    """Display current inventory status from CSV"""
    print("\n=== CSV INVENTORY STATUS ===")
    for item_id, item_info in csv_inventory.items():
        current_stock = item_info['current_stock']
        min_threshold = item_info['min_threshold']
        
        if current_stock == 0:
            status_color = "🔴"
        elif current_stock <= min_threshold:
            status_color = "🟡"
        else:
            status_color = "🟢"
            
        print(f"{status_color} {item_info['name']} ({item_id}): {current_stock} units "
              f"(Min: {min_threshold}, Reorder: {item_info['reorder_quantity']})")

def show_csv_vendor_info(csv_vendors):
    """Display vendor information from CSV"""
    print("\n=== CSV VENDOR INFORMATION ===")
    for vendor_id, vendor_info in csv_vendors.items():
        print(f"\n{vendor_info['name']} ({vendor_id}):")
        print(f"  Phone: {vendor_info['phone']}")
        print(f"  Email: {vendor_info['email']}")
        print(f"  Rating: {vendor_info['rating']}/5")
        print(f"  Delivery: {vendor_info['delivery_time']} days")
        print(f"  Payment: {vendor_info['payment_terms']}")
        print(f"  Status: {vendor_info['status']}")
        print(f"  Notes: {vendor_info['notes']}")

def main():
    """Main function to test CSV loading"""
    
    print(f"🏢 {CONFIG['company_name']} - CSV Loading Test")
    print("=" * 60)
    
    try:
        # Load CSV data
        print("\n📊 Loading CSV data...")
        csv_vendors = load_vendors_from_csv()
        csv_inventory = load_inventory_from_csv()
        csv_vendor_mapping = load_vendor_items_mapping()
        
        print(f"\n✅ CSV Loading Complete!")
        print(f"   Vendors: {len(csv_vendors)}")
        print(f"   Inventory items: {len(csv_inventory)}")
        print(f"   Vendor mappings: {len(csv_vendor_mapping)}")
        
        # Show some sample data
        if len(sys.argv) > 1 and sys.argv[1] == 'show':
            show_csv_inventory_status(csv_inventory)
            show_csv_vendor_info(csv_vendors)
        
        # Check for items that need reordering
        items_to_reorder = []
        for item_id, item_info in csv_inventory.items():
            if item_info['current_stock'] <= item_info['min_threshold']:
                items_to_reorder.append(item_id)
        
        if items_to_reorder:
            print(f"\n⚠️  Items needing reorder: {len(items_to_reorder)}")
            for item_id in items_to_reorder:
                item_name = csv_inventory[item_id]['name']
                current_stock = csv_inventory[item_id]['current_stock']
                min_threshold = csv_inventory[item_id]['min_threshold']
                print(f"   • {item_name}: {current_stock} units (Min: {min_threshold})")
        else:
            print("\n✅ All inventory levels are sufficient")
        
        print("\n🎯 CSV loading test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
