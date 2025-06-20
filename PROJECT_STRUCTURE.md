# Likwid Mails - Procurement Automation System

## Clean Project Structure

```
Likwid Mails/
├── .env                      # Environment variables (user credentials)
├── .env.template            # Template for environment setup
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── README.md              # Main project documentation
├── main.py                # Main entry point with interactive menu
├── organized_demo.py      # Quick demonstration script
│
├── src/                   # Core application modules
│   ├── __init__.py       # Package initialization
│   ├── models.py         # Data models (Vendor, Item, Order)
│   ├── data_manager.py   # CSV data management
│   ├── twilio_manager.py # Twilio API integration
│   └── procurement_engine.py # Core business logic
│
├── data/                  # CSV data files
│   ├── vendors.csv       # Vendor information and contact details
│   ├── inventory.csv     # Current inventory levels
│   └── vendor_items_mapping.csv # Vendor-item relationships and pricing
│
├── tests/                 # Test suite
│   └── test_system.py    # Comprehensive system tests
│
├── logs/                  # Generated logs and reports
│   ├── procurement_system.log    # System operation logs
│   ├── successful_calls.log      # Call history
│   └── procurement_report_*.csv  # Generated reports
│
└── docs/                  # Documentation
    └── README_ORGANIZED.md # Detailed technical documentation
```

## Key Features

✅ **Modular Architecture**: Clean separation of concerns with dedicated modules
✅ **CSV-Based Data Management**: Realistic vendor and inventory data
✅ **Twilio Integration**: Direct REST API calls for Windows compatibility
✅ **Security Enforcement**: Restricted to authorized phone number (+918800000488)
✅ **Comprehensive Testing**: Full test suite with mocking
✅ **Logging & Reporting**: Detailed logs and CSV reports
✅ **Production Ready**: Error handling, validation, and monitoring

## Usage

### Quick Start
```bash
python organized_demo.py
```

### Interactive Menu
```bash
python main.py
```

### Run Tests
```bash
python -m pytest tests/ -v
```

## Environment Setup

1. Copy `.env.template` to `.env`
2. Add your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   ```
3. Install dependencies: `pip install -r requirements.txt`

## Data Management

- **vendors.csv**: Vendor contact information and capabilities
- **inventory.csv**: Current stock levels with reorder points
- **vendor_items_mapping.csv**: Pricing and vendor-item relationships

All data is loaded and managed through the `DataManager` class with proper validation and error handling.

## Security

- Phone calls restricted to: +918800000488
- Environment-based credential management
- Input validation and sanitization
- Secure API communication

---

**Status**: ✅ Production Ready
**Last Updated**: June 20, 2025
