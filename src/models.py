"""
Data Models for the Procurement System
Defines the core data structures used throughout the application
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import datetime


@dataclass
class InventoryItem:
    """Data model for inventory items"""
    item_id: str
    item_name: str
    category: str
    subcategory: str
    description: str
    unit: str
    current_stock: int
    min_threshold: int
    reorder_quantity: int
    unit_cost: float
    preferred_vendor_id: str
    alternative_vendor_ids: str = ""
    last_ordered_date: str = ""
    supplier_part_number: str = ""
    internal_part_number: str = ""
    storage_location: str = ""
    shelf_life_days: int = 365
    criticality: str = "Medium"
    usage_rate_monthly: int = 0
    lead_time_days: int = 7
    quality_grade: str = "Grade-A"
    certifications: str = ""
    notes: str = ""

    @property
    def needs_reorder(self) -> bool:
        """Check if item needs reordering"""
        return self.current_stock <= self.min_threshold

    @property
    def stock_status(self) -> str:
        """Get stock status description"""
        if self.current_stock <= self.min_threshold:
            return "LOW"
        elif self.current_stock <= self.min_threshold * 1.5:
            return "MEDIUM"
        else:
            return "OK"


@dataclass
class Vendor:
    """Data model for vendors"""
    vendor_id: str
    vendor_name: str
    contact_person: str
    phone_number: str
    email: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    rating: float
    delivery_time_days: int
    payment_terms: str
    minimum_order_value: float
    tax_id: str = ""
    established_year: int = 2000
    primary_category: str = ""
    secondary_category: str = ""
    website: str = ""
    notes: str = ""
    status: str = "Active"

    @property
    def is_authorized_for_calls(self) -> bool:
        """Check if vendor is authorized for phone calls"""
        return self.phone_number == "+918800000488"

    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        return f"{self.address}, {self.city}, {self.state} {self.postal_code}, {self.country}"


@dataclass
class VendorItemMapping:
    """Data model for vendor-item relationships with pricing"""
    vendor_id: str
    item_id: str
    vendor_item_name: str
    vendor_part_number: str
    unit_price: float
    minimum_order_qty: int
    bulk_discount_qty: int
    bulk_discount_price: float
    lead_time_days: int
    availability_status: str
    last_price_update: str
    quality_rating: float
    delivery_rating: float
    service_rating: float
    total_orders: int = 0
    last_order_date: str = ""
    preferred_supplier: bool = False
    notes: str = ""

    @property
    def overall_rating(self) -> float:
        """Calculate overall vendor rating for this item"""
        return (self.quality_rating + self.delivery_rating + self.service_rating) / 3

    def get_effective_price(self, quantity: int) -> float:
        """Get price based on quantity (with bulk discount)"""
        if quantity >= self.bulk_discount_qty:
            return self.bulk_discount_price
        return self.unit_price


@dataclass
class ProcurementRecord:
    """Data model for procurement records"""
    record_id: str
    timestamp: str
    items_required: List[str]
    selected_vendor_id: str
    selected_vendor_name: str
    total_cost: float
    total_items: int
    status: str
    call_sid: Optional[str] = None
    email_sent: bool = False
    approval_required: bool = False
    approved_by: str = ""
    approval_date: str = ""
    order_number: str = ""
    expected_delivery_date: str = ""
    actual_delivery_date: str = ""
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ProcurementConfig:
    """Configuration settings for the procurement system"""
    company_name: str = "Bio Mac Lifesciences"
    procurement_email: str = "procurement@org1.com"
    auto_approve_threshold: float = 1000.0
    max_retries: int = 3
    retry_delay: int = 5
    allowed_phone_number: str = "+918800000488"
    
    # File paths
    data_file: str = "data/procurement_data.json"
    log_file: str = "logs/procurement_log.log"
    inventory_csv: str = "data/inventory.csv"
    vendors_csv: str = "data/vendors.csv"
    vendor_items_csv: str = "data/vendor_items_mapping.csv"
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    # Twilio settings
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Scoring weights for vendor selection
    price_weight: float = 0.4
    rating_weight: float = 0.3
    delivery_weight: float = 0.2
    service_weight: float = 0.1
