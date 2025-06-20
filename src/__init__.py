"""
Organized Procurement Automation System
Core package for procurement automation with CSV-based data management
"""

__version__ = "2.0.0"
__author__ = "Procurement System Team"

from .models import (
    InventoryItem,
    Vendor, 
    VendorItemMapping,
    ProcurementRecord,
    ProcurementConfig
)

from .data_manager import DataManager
from .twilio_manager import TwilioManager
from .procurement_engine import ProcurementEngine, VendorSelector

__all__ = [
    'InventoryItem',
    'Vendor',
    'VendorItemMapping', 
    'ProcurementRecord',
    'ProcurementConfig',
    'DataManager',
    'TwilioManager',
    'ProcurementEngine',
    'VendorSelector'
]
