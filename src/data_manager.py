"""
Data Manager for CSV-based data operations
Handles loading and saving of vendor, inventory, and mapping data
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import Vendor, InventoryItem, VendorItemMapping, ProcurementRecord, ProcurementConfig

logger = logging.getLogger(__name__)


class DataManager:
    """Manages all data operations for the procurement system"""
    
    def __init__(self, config: ProcurementConfig):
        self.config = config
        self.vendors: Dict[str, Vendor] = {}
        self.inventory: Dict[str, InventoryItem] = {}
        self.vendor_items: Dict[str, List[VendorItemMapping]] = {}
        self.procurement_records: List[ProcurementRecord] = []
        
        # Ensure data directories exist
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # Load all data
        self.load_all_data()
    
    def load_all_data(self):
        """Load all data from CSV files"""
        try:
            self.load_vendors()
            self.load_inventory()
            self.load_vendor_items()
            self.load_procurement_records()
            logger.info("All data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def load_vendors(self):
        """Load vendors from CSV file"""
        vendors_file = Path(self.config.vendors_csv)
        if not vendors_file.exists():
            logger.warning(f"Vendors file not found: {vendors_file}")
            return
        
        try:
            with open(vendors_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    vendor = Vendor(
                        vendor_id=row['vendor_id'],
                        vendor_name=row['vendor_name'],
                        contact_person=row['contact_person'],
                        phone_number=row['phone_number'],
                        email=row['email'],
                        address=row['address'],
                        city=row['city'],
                        state=row['state'],
                        country=row['country'],
                        postal_code=row['postal_code'],
                        rating=float(row['rating']),
                        delivery_time_days=int(row['delivery_time_days']),
                        payment_terms=row['payment_terms'],
                        minimum_order_value=float(row['minimum_order_value']),
                        tax_id=row.get('tax_id', ''),
                        established_year=int(row.get('established_year', 2000)),
                        primary_category=row.get('primary_category', ''),
                        secondary_category=row.get('secondary_category', ''),
                        website=row.get('website', ''),
                        notes=row.get('notes', ''),
                        status=row.get('status', 'Active')
                    )
                    self.vendors[vendor.vendor_id] = vendor
            
            logger.info(f"Loaded {len(self.vendors)} vendors")
        except Exception as e:
            logger.error(f"Error loading vendors: {e}")
    
    def load_inventory(self):
        """Load inventory from CSV file"""
        inventory_file = Path(self.config.inventory_csv)
        if not inventory_file.exists():
            logger.warning(f"Inventory file not found: {inventory_file}")
            return
        
        try:
            with open(inventory_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item = InventoryItem(
                        item_id=row['item_id'],
                        item_name=row['item_name'],
                        category=row['category'],
                        subcategory=row['subcategory'],
                        description=row['description'],
                        unit=row['unit'],
                        current_stock=int(row['current_stock']),
                        min_threshold=int(row['min_threshold']),
                        reorder_quantity=int(row['reorder_quantity']),
                        unit_cost=float(row['unit_cost']),
                        preferred_vendor_id=row['preferred_vendor_id'],
                        alternative_vendor_ids=row.get('alternative_vendor_ids', ''),
                        last_ordered_date=row.get('last_ordered_date', ''),
                        supplier_part_number=row.get('supplier_part_number', ''),
                        internal_part_number=row.get('internal_part_number', ''),
                        storage_location=row.get('storage_location', ''),
                        shelf_life_days=int(row.get('shelf_life_days', 365)),
                        criticality=row.get('criticality', 'Medium'),
                        usage_rate_monthly=int(row.get('usage_rate_monthly', 0)),
                        lead_time_days=int(row.get('lead_time_days', 7)),
                        quality_grade=row.get('quality_grade', 'Grade-A'),
                        certifications=row.get('certifications', ''),
                        notes=row.get('notes', '')
                    )
                    self.inventory[item.item_id] = item
            
            logger.info(f"Loaded {len(self.inventory)} inventory items")
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
    
    def load_vendor_items(self):
        """Load vendor-item mappings from CSV file"""
        mapping_file = Path(self.config.vendor_items_csv)
        if not mapping_file.exists():
            logger.warning(f"Vendor items mapping file not found: {mapping_file}")
            return
        
        try:
            with open(mapping_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    mapping = VendorItemMapping(
                        vendor_id=row['vendor_id'],
                        item_id=row['item_id'],
                        vendor_item_name=row['vendor_item_name'],
                        vendor_part_number=row['vendor_part_number'],
                        unit_price=float(row['unit_price']),
                        minimum_order_qty=int(row['minimum_order_qty']),
                        bulk_discount_qty=int(row['bulk_discount_qty']),
                        bulk_discount_price=float(row['bulk_discount_price']),
                        lead_time_days=int(row['lead_time_days']),
                        availability_status=row['availability_status'],
                        last_price_update=row['last_price_update'],
                        quality_rating=float(row['quality_rating']),
                        delivery_rating=float(row['delivery_rating']),
                        service_rating=float(row['service_rating']),
                        total_orders=int(row.get('total_orders', 0)),
                        last_order_date=row.get('last_order_date', ''),
                        preferred_supplier=row.get('preferred_supplier', 'No').lower() == 'yes',
                        notes=row.get('notes', '')
                    )
                    
                    if mapping.item_id not in self.vendor_items:
                        self.vendor_items[mapping.item_id] = []
                    self.vendor_items[mapping.item_id].append(mapping)
            
            total_mappings = sum(len(mappings) for mappings in self.vendor_items.values())
            logger.info(f"Loaded {total_mappings} vendor-item mappings for {len(self.vendor_items)} items")
        except Exception as e:
            logger.error(f"Error loading vendor items: {e}")
    
    def load_procurement_records(self):
        """Load procurement records from JSON file"""
        records_file = Path(self.config.data_file)
        if not records_file.exists():
            logger.info("No existing procurement records file found")
            return
        
        try:
            with open(records_file, 'r') as file:
                data = json.load(file)
                for record_data in data.get('records', []):
                    record = ProcurementRecord(**record_data)
                    self.procurement_records.append(record)
            
            logger.info(f"Loaded {len(self.procurement_records)} procurement records")
        except Exception as e:
            logger.error(f"Error loading procurement records: {e}")
    
    def save_procurement_records(self):
        """Save procurement records to JSON file"""
        try:
            records_data = {
                'records': [record.to_dict() for record in self.procurement_records],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config.data_file, 'w') as file:
                json.dump(records_data, file, indent=2)
            
            logger.info(f"Saved {len(self.procurement_records)} procurement records")
        except Exception as e:
            logger.error(f"Error saving procurement records: {e}")
    
    def get_items_needing_reorder(self) -> List[InventoryItem]:
        """Get list of items that need reordering"""
        return [item for item in self.inventory.values() if item.needs_reorder]
    
    def get_vendor_by_id(self, vendor_id: str) -> Optional[Vendor]:
        """Get vendor by ID"""
        return self.vendors.get(vendor_id)
    
    def get_item_by_id(self, item_id: str) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        return self.inventory.get(item_id)
    
    def get_vendors_for_item(self, item_id: str) -> List[VendorItemMapping]:
        """Get all vendors that supply a specific item"""
        return self.vendor_items.get(item_id, [])
    
    def get_authorized_vendors(self) -> List[Vendor]:
        """Get vendors authorized for phone calls"""
        return [vendor for vendor in self.vendors.values() if vendor.is_authorized_for_calls]
    
    def export_to_csv(self, filename: str = None):
        """Export procurement records to CSV"""
        if not filename:
            filename = f"logs/procurement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                if not self.procurement_records:
                    return
                
                fieldnames = list(self.procurement_records[0].to_dict().keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in self.procurement_records:
                    writer.writerow(record.to_dict())
            
            logger.info(f"Exported {len(self.procurement_records)} records to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def add_procurement_record(self, record: ProcurementRecord):
        """Add a new procurement record"""
        self.procurement_records.append(record)
        self.save_procurement_records()
    
    def update_inventory_stock(self, item_id: str, new_stock: int):
        """Update inventory stock level"""
        if item_id in self.inventory:
            self.inventory[item_id].current_stock = new_stock
            logger.info(f"Updated stock for {item_id}: {new_stock}")
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        items_needing_reorder = len(self.get_items_needing_reorder())
        authorized_vendors = len(self.get_authorized_vendors())
        total_records = len(self.procurement_records)
        
        return {
            'total_vendors': len(self.vendors),
            'total_items': len(self.inventory),
            'items_needing_reorder': items_needing_reorder,
            'authorized_vendors': authorized_vendors,
            'total_procurement_records': total_records,
            'total_vendor_item_mappings': sum(len(mappings) for mappings in self.vendor_items.values())
        }
