# 🏢 Enhanced Procurement Automation System

An intelligent procurement automation system that manages inventory, evaluates vendors, and automates purchase orders through phone calls and email notifications.

## 🚀 Features

### Core Functionality
- **Intelligent Inventory Management**: Automated stock level monitoring with configurable thresholds
- **Multi-factor Vendor Selection**: Evaluates vendors based on price, rating, delivery time, and payment terms
- **Automated Communications**: Phone calls via Twilio and email notifications
- **Comprehensive Logging**: Detailed logging with file and console output
- **Data Persistence**: JSON-based data storage with CSV export capabilities
- **Error Handling**: Robust error handling with retry mechanisms

### Enhanced Features
- **Interactive Mode**: Command-line interface for manual operations
- **Procurement History**: Track and analyze past procurement activities
- **Smart Scoring**: Advanced vendor scoring algorithm
- **Cost Calculations**: Automatic cost calculations with approval thresholds
- **Audio Narration**: Text-to-speech narration of workflow steps

## 📋 Prerequisites

- Python 3.8 or higher
- Valid API keys for:
  - Eleven Labs (for text-to-speech)
  - Twilio (for phone calls)
  - Email service (for notifications)

## 🛠️ Installation

1. **Clone or download the project files**
   ```bash
   cd "c:\Users\harsh\My Drive\1. Projects\Likwid Mails"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   copy .env.template .env
   # Edit .env file with your actual credentials
   ```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file based on `.env.template` and configure:

- **ELEVEN_API_KEY**: Your Eleven Labs API key
- **TWILIO_ACCOUNT_SID**: Your Twilio Account SID
- **TWILIO_AUTH_TOKEN**: Your Twilio Auth Token
- **TWILIO_PHONE_NUMBER**: Your Twilio phone number
- **EMAIL_ADDRESS**: Your email address
- **EMAIL_PASSWORD**: Your email app password

### System Configuration
Modify the `CONFIG` dictionary in `caller.py`:

```python
CONFIG = {
    "company_name": "Your Company Name",
    "procurement_email": "procurement@yourcompany.com",
    "auto_approve_threshold": 1000,  # Auto-approve orders below this amount
    "max_retries": 3,
    "retry_delay": 5,
}
```

## 🚦 Usage

### Basic Usage
```bash
python caller.py
```

### Command Line Options
```bash
# Interactive mode
python caller.py interactive

# Legacy mode (original functionality)
python caller.py legacy

# Check inventory status
python caller.py status

# View vendor information
python caller.py vendors

# View procurement history
python caller.py history
```

### Interactive Mode
The interactive mode provides a menu-driven interface:

1. Run Full Procurement Workflow
2. Check Inventory Status
3. View Vendor Information
4. View Procurement History
5. Export Data to CSV
6. Exit

## 📊 Data Models

### Inventory Item
```python
@dataclass
class InventoryItem:
    name: str
    status: str
    quantity: int
    min_threshold: int = 20
    reorder_quantity: int = 100
    unit_cost: float = 0.0
    supplier: str = ""
```

### Vendor
```python
@dataclass
class Vendor:
    name: str
    price: float
    phone: str
    email: str = ""
    rating: float = 5.0
    delivery_time: int = 7  # days
    payment_terms: str = "30 days"
```

### Procurement Record
```python
@dataclass
class ProcurementRecord:
    timestamp: str
    items_required: List[str]
    selected_vendor: str
    total_cost: float
    status: str
    call_sid: Optional[str] = None
    email_sent: bool = False
```

## 🧮 Vendor Scoring Algorithm

The system uses a weighted scoring algorithm to select the best vendor:

- **Price (40%)**: Lower cost is better
- **Rating (30%)**: Higher rating is better
- **Delivery Time (20%)**: Faster delivery is better
- **Payment Terms (10%)**: Shorter payment terms are better

## 📁 File Structure

```
Likwid Mails/
├── caller.py              # Main application
├── requirements.txt       # Python dependencies
├── .env.template         # Environment variables template
├── README.md             # This file
├── procurement_data.json # Data storage (auto-generated)
├── procurement_log.log   # System logs (auto-generated)
└── procurement_report.csv # CSV export (auto-generated)
```

## 🔧 Customization

### Adding New Inventory Items
```python
inventory_items["new_item"] = InventoryItem(
    name="new_item",
    status="In-Stock",
    quantity=50,
    min_threshold=20,
    reorder_quantity=100,
    unit_cost=30.0,
    supplier="preferred_vendor"
)
```

### Adding New Vendors
```python
vendor_data["new_vendor"] = Vendor(
    name="new_vendor",
    price=75,
    phone="+1234567890",
    email="contact@newvendor.com",
    rating=4.5,
    delivery_time=5,
    payment_terms="20 days"
)
```

## 📝 Logging

The system provides comprehensive logging:

- **Console Output**: Real-time status updates
- **File Logging**: Detailed logs saved to `procurement_log.log`
- **Error Tracking**: All errors are logged with timestamps
- **Audit Trail**: Complete record of all procurement activities

## 🛡️ Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables for sensitive data**
3. **Use app passwords for email services**
4. **Verify phone numbers before testing**
5. **Rotate API keys regularly**
6. **Monitor logs for suspicious activity**

## 🐛 Troubleshooting

### Common Issues

1. **Audio not playing**: Check Eleven Labs API key and internet connection
2. **Phone calls failing**: Verify Twilio credentials and phone number format
3. **Emails not sending**: Check SMTP settings and app password
4. **Permission errors**: Ensure write permissions for data and log files

### Debug Mode
Enable debug logging by modifying the logging configuration:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Future Enhancements

- Web-based dashboard
- Database integration
- Advanced analytics and reporting
- Multi-company support
- API endpoints for integration
- Mobile app support
- Automated invoice processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and commercial use. Please ensure compliance with all API terms of service.

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review system logs in `procurement_log.log`
- Verify configuration in `.env` file

---

**Happy Procuring! 🛒**
