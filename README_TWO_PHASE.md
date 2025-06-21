# Two-Phase Procurement Automation System

## Overview

This system implements an advanced two-phase procurement workflow that ensures competitive pricing through automated vendor quote collection and comparison.

## 🔄 Two-Phase Workflow

### Phase 1: Quote Collection
1. **Inventory Analysis**: Check current stock levels against minimum thresholds
2. **Vendor Identification**: Find all vendors who can supply required items
3. **Quote Requests**: Call each vendor to request pricing quotes
4. **Real-time Updates**: Update CSV files with current market pricing
5. **Quote Logging**: Track all quote requests and responses

### Phase 2: Price Comparison & Ordering
6. **Quote Analysis**: Compare all received quotes side-by-side
7. **Vendor Selection**: Automatically select vendor with lowest total cost
8. **Order Placement**: Call winning vendor to confirm order
9. **Documentation**: Send email confirmation and generate reports
10. **Audit Trail**: Maintain complete procurement history

## 🚀 Quick Start

### Basic Usage
```powershell
# Run the complete two-phase workflow
python caller.py

# Run specific workflow modes
python caller.py two-phase    # Two-phase procurement
python caller.py interactive  # Interactive menu
python caller.py test-call    # Test phone connectivity

# Run the demo
python demo_two_phase.py      # Interactive demo
python demo_two_phase.py auto # Automatic workflow
```

### Configuration Required

Create a `.env` file with your credentials:
```env
# Twilio Configuration (Required for calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+15017122661

# Security Configuration
ALLOWED_PHONE_NUMBER=+918800000488

# Company Information
COMPANY_NAME=Bio Mac Lifesciences
PROCUREMENT_EMAIL=procurement@biomacsci.com

# Email Configuration (Optional)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Eleven Labs (Optional - for voice narration)
ELEVEN_API_KEY=your_elevenlabs_api_key
```

## 📁 Data Files

The system uses three CSV files for data management:

### 1. `data/inventory.csv`
- Current stock levels
- Minimum thresholds
- Reorder quantities
- Preferred vendors

### 2. `data/vendors.csv`
- Vendor contact information
- Ratings and delivery times
- Payment terms
- Call permissions

### 3. `data/vendor_items_mapping.csv`
- Item-specific pricing
- Bulk discounts
- Availability status
- **Updated in real-time with quotes**

## 🔧 Key Features

### Automated Quote Collection
- Calls multiple vendors simultaneously
- Requests competitive pricing
- Updates pricing data in real-time
- Maintains quote history

### Intelligent Price Comparison
- Compares total costs across all vendors
- Considers bulk discounts
- Factors in delivery terms
- Selects optimal vendor automatically

### Security & Compliance
- Phone number restrictions for safety
- Complete audit trail
- Email confirmations
- Comprehensive reporting

### Real-time Data Management
- Updates CSV files with current pricing
- Maintains historical quote data
- Generates detailed procurement reports
- Tracks savings achieved

## 📞 Call Workflow

### Quote Request Calls
```
"Namaste, this is an automated quote request call from [Company Name]. 
We need quotes for the following items: [Item List]. 
Please provide your best pricing for these items. 
We will place orders based on competitive pricing and service quality."
```

### Final Order Calls
```
"Namaste, this is [Company Name] procurement department. 
After evaluating all quotes received, we are pleased to confirm 
your selection as our vendor for [Items]. 
You offered the most competitive pricing among all vendors. 
Total order value is ₹[Amount]."
```

## 📊 Reports Generated

### 1. Procurement Report (`logs/procurement_report_YYYYMMDD_HHMMSS.csv`)
- Item-by-item vendor comparison
- Pricing analysis
- Selected vendor information
- Savings calculation

### 2. Call Logs (`successful_calls.log`)
- All successful phone calls
- Call SIDs for tracking
- Timestamps and purposes

### 3. System Logs (`procurement_log.log`)
- Complete system activity
- Error tracking
- Decision audit trail

## 🎯 Usage Examples

### Example 1: Check System Status
```python
from caller import show_csv_inventory_status, show_csv_vendor_info

# Check which items need reordering
show_csv_inventory_status()

# View available vendors
show_csv_vendor_info()
```

### Example 2: Run Quote Collection Only
```python
from caller import run_two_phase_procurement_workflow

# This will:
# 1. Identify items needing procurement
# 2. Call vendors for quotes
# 3. Update CSV with current pricing
# 4. Compare quotes and select winner
# 5. Place final order
run_two_phase_procurement_workflow()
```

### Example 3: Test Connectivity
```python
from caller import test_simple_twilio_call

# Test Twilio phone system
test_simple_twilio_call()
```

## 🔍 Sample Output

```
🏢 Bio Mac Lifesciences - Two-Phase Procurement Automation System
============================================================

--> NARRATION: Starting two-phase procurement workflow for Bio Mac Lifesciences

=== PHASE 1: QUOTE COLLECTION ===
--> NARRATION: Requesting quotes for 3 items from multiple vendors
--> Requesting quote from TechSupply Solutions for 2 items
--> Quote request call SUCCESS! SID: CA1234567890abcdef
--> Requesting quote from Metro Electronics Hub for 3 items
--> Quote request call SUCCESS! SID: CA0987654321fedcba

=== QUOTE PROCESSING ===
--> NARRATION: Processing 2 quote responses...
--> NARRATION: Quote received from TechSupply Solutions: ₹2,850.00
--> NARRATION: Quote received from Metro Electronics Hub: ₹3,125.00

=== PHASE 2: QUOTE COMPARISON & ORDER PLACEMENT ===
--> NARRATION: Quote comparison results:
1. TechSupply Solutions: ₹2,850.00
2. Metro Electronics Hub: ₹3,125.00

--> NARRATION: WINNER: TechSupply Solutions with ₹2,850.00
--> NARRATION: Savings achieved: ₹275.00 compared to highest quote
--> Placing FINAL ORDER with TechSupply Solutions - Total: ₹2,850.00
```

## ⚠️ Important Notes

### Security
- Only calls to `ALLOWED_PHONE_NUMBER` are permitted
- All other numbers are blocked for safety
- Complete audit trail maintained

### Testing
- Use `test-call` mode to verify Twilio connectivity
- Run `demo_two_phase.py` for comprehensive testing
- Check logs for debugging information

### Data Integrity
- CSV files are automatically updated with new quotes
- Backup original data before running
- System maintains historical pricing data

## 🤝 Support

For issues or questions:
1. Check the logs directory for error details
2. Verify your `.env` configuration
3. Test Twilio connectivity with `test-call` mode
4. Review the CSV data files for accuracy

## 📋 Requirements

- Python 3.7+
- Twilio account with valid credentials
- CSV data files properly formatted
- Network connectivity for API calls

---

*This system ensures competitive procurement through automated vendor comparison and intelligent price analysis.*
