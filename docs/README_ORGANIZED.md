# Organized Procurement Automation System

## 🏗️ **Codebase Organization**

### **Directory Structure**
```
├── main.py                     # Main application entry point
├── src/                        # Core source code
│   ├── models.py              # Data models and structures
│   ├── data_manager.py        # CSV data operations
│   ├── twilio_manager.py      # Twilio API integration
│   └── procurement_engine.py  # Core business logic
├── data/                       # Data files
│   ├── vendors.csv            # Vendor information
│   ├── inventory.csv          # Inventory items
│   └── vendor_items_mapping.csv # Vendor-item relationships
├── tests/                      # Test suite
│   └── test_system.py         # Comprehensive tests
├── logs/                       # Log files
├── docs/                       # Documentation
├── .env                        # Environment configuration
└── requirements.txt           # Python dependencies
```

### **Core Components**

#### **1. Data Models (`src/models.py`)**
- `InventoryItem`: Inventory management with stock levels, thresholds
- `Vendor`: Vendor information with contact details and ratings
- `VendorItemMapping`: Price and availability mapping between vendors and items
- `ProcurementRecord`: Transaction records with call tracking
- `ProcurementConfig`: System configuration settings

#### **2. Data Manager (`src/data_manager.py`)**
- CSV-based data loading and management
- Inventory and vendor data operations
- Procurement record persistence
- Export functionality for reports

#### **3. Twilio Manager (`src/twilio_manager.py`)**
- Direct REST API integration (Windows-compatible)
- Security enforcement (only authorized numbers)
- Retry logic and error handling
- Call logging and status tracking

#### **4. Procurement Engine (`src/procurement_engine.py`)**
- Intelligent vendor selection algorithm
- Multi-criteria scoring (price, rating, delivery, service)
- Complete procurement workflow automation
- System status and monitoring

## 📊 **CSV Data Structure**

### **Vendors CSV (`data/vendors.csv`)**
6 vendors with complete business information:
- **V001**: TechSupply Solutions (✅ **AUTHORIZED FOR CALLS**)
- **V002-V006**: Metro Electronics, Global Components, Rapid Parts, Budget Electronics, Premium Tech (🚫 **CALLS BLOCKED**)

**Columns**: vendor_id, vendor_name, contact_person, phone_number, email, address, city, state, country, postal_code, rating, delivery_time_days, payment_terms, minimum_order_value, tax_id, established_year, primary_category, secondary_category, website, notes, status

### **Inventory CSV (`data/inventory.csv`)**
10 realistic electronics items with varying stock levels:
- **I001**: USB-C Cables (15 units, threshold: 50) 🔴 **NEEDS REORDER**
- **I002**: Wireless Mouse (8 units, threshold: 25) 🔴 **NEEDS REORDER**
- **I003**: HDMI Adapters (12 units, threshold: 30) 🔴 **NEEDS REORDER**
- **I004**: Power Banks (22 units, threshold: 40) 🔴 **NEEDS REORDER**
- **I005**: Ethernet Cables (35 units, threshold: 60) 🔴 **NEEDS REORDER**
- **I006**: Laptop Stands (18 units, threshold: 20) 🔴 **NEEDS REORDER**
- **I007**: Bluetooth Headphones (5 units, threshold: 15) 🔴 **NEEDS REORDER**
- **I008**: USB Hubs (28 units, threshold: 35) 🔴 **NEEDS REORDER**
- **I009**: Phone Chargers (42 units, threshold: 75) 🔴 **NEEDS REORDER**
- **I010**: Monitor Arms (6 units, threshold: 12) 🔴 **NEEDS REORDER**

**Columns**: item_id, item_name, category, subcategory, description, unit, current_stock, min_threshold, reorder_quantity, unit_cost, preferred_vendor_id, alternative_vendor_ids, last_ordered_date, supplier_part_number, internal_part_number, storage_location, shelf_life_days, criticality, usage_rate_monthly, lead_time_days, quality_grade, certifications, notes

### **Vendor-Item Mapping CSV (`data/vendor_items_mapping.csv`)**
Comprehensive pricing and availability matrix:
- **24 vendor-item combinations** with realistic pricing
- Different prices, minimum quantities, and bulk discounts per vendor
- Quality, delivery, and service ratings
- Lead times and availability status

**Columns**: vendor_id, item_id, vendor_item_name, vendor_part_number, unit_price, minimum_order_qty, bulk_discount_qty, bulk_discount_price, lead_time_days, availability_status, last_price_update, quality_rating, delivery_rating, service_rating, total_orders, last_order_date, preferred_supplier, notes

## 🚀 **Usage**

### **Quick Start**
```bash
# Run the main application
python main.py

# Run comprehensive tests
python tests/test_system.py
```

### **Main Menu Options**
1. **Show System Status** - Overview of vendors, inventory, and system health
2. **Show Inventory Status** - Detailed inventory with reorder needs
3. **Show Vendor Status** - Vendor capabilities and authorization
4. **Run Test Call** - Test Twilio integration
5. **Run Full Procurement Cycle** - Complete automation workflow
6. **Export Data to CSV** - Generate reports
7. **Exit**

### **Automated Workflow**
The system automatically:
1. **Scans inventory** for items below threshold
2. **Selects best vendors** using multi-criteria scoring
3. **Makes authorized phone calls** to vendors
4. **Records all transactions** with call tracking
5. **Exports reports** for audit and analysis

## 🛡️ **Security Features**

- **Phone Authorization**: Only `+918800000488` can receive calls
- **Credential Validation**: Twilio credentials verified before calls
- **Call Logging**: All calls logged with SID and status
- **Error Handling**: Comprehensive retry logic and fallbacks

## 📈 **Business Intelligence**

### **Vendor Scoring Algorithm**
- **Price Weight**: 40% (lower cost preferred)
- **Rating Weight**: 30% (quality, delivery, service)
- **Delivery Weight**: 20% (faster delivery preferred)
- **Service Weight**: 10% (availability bonus)

### **Realistic Test Scenario**
- **10 items** currently need reordering
- **6 vendors** available with varying capabilities
- **Only 1 vendor** authorized for phone calls
- **$2,000+** total procurement value
- **Multiple price points** and bulk discounts

## 🔧 **Configuration**

All settings managed via `.env` file:
```
COMPANY_NAME=Bio Mac Lifesciences
TWILIO_ACCOUNT_SID=AC820daae89092e30fee3487e80162d2e2
TWILIO_AUTH_TOKEN=690636dcdd752868f4e77648dc0d49eb
TWILIO_PHONE_NUMBER=+14323484517
ALLOWED_PHONE_NUMBER=+918800000488
AUTO_APPROVE_THRESHOLD=1000
```

## 📋 **Benefits of Organization**

✅ **Modular Architecture**: Clear separation of concerns  
✅ **Data-Driven**: CSV-based configuration for easy updates  
✅ **Testable**: Comprehensive test suite included  
✅ **Scalable**: Easy to add vendors, items, and features  
✅ **Professional**: Production-ready code structure  
✅ **Documented**: Clear documentation and examples  
✅ **Realistic**: Real-world business scenarios and data  

## 🎯 **Ready for Production**

The organized codebase provides:
- Clean, maintainable code structure
- Realistic business data for testing
- Comprehensive vendor and inventory management
- Working Twilio integration with security
- Complete audit trail and reporting
- Easy configuration and deployment
