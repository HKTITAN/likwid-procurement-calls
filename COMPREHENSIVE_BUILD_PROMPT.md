# Comprehensive Build Prompt: AI-Powered Procurement Automation System

## Overview
Build a complete procurement automation system that uses **Twilio Voice AI (ConversationRelay)** to intelligently call vendors, collect real-time price quotes through AI-driven voice conversations, compare prices, and automatically place orders with the lowest-cost vendor. The system should support both classic workflows and advanced AI-driven conversations with robust error handling and comprehensive reporting.

## Core Requirements

### 1. System Architecture
- **Language**: Python 3.8+
- **Main Components**:
  - Procurement engine with CSV data management
  - Twilio Voice AI integration with ConversationRelay
  - Flask webhook server for real-time AI conversation handling
  - Email notification system
  - Comprehensive logging and reporting
  - Security controls for phone number validation

### 2. Data Models
Create the following data structures:

```python
@dataclass
class InventoryItem:
    name: str
    status: str  # "In-Stock", "Low Quantity", "Out of Stock"
    quantity: int
    min_threshold: int
    reorder_quantity: int
    unit_cost: float
    supplier: str

@dataclass
class Vendor:
    name: str
    price: float
    phone: str
    email: str
    rating: float
    delivery_time: int
    payment_terms: str

@dataclass
class VendorQuote:
    vendor_id: str
    vendor_name: str
    item_id: str
    quoted_price: float
    quantity: int
    total_cost: float
    quote_timestamp: str
    call_sid: str
    notes: str

@dataclass
class ProcurementRecord:
    timestamp: str
    items_required: List[str]
    selected_vendor: str
    total_cost: float
    status: str
    call_sid: str
    email_sent: bool
    quotes_collected: List[VendorQuote]
```

### 3. CSV Data Files Structure
Create three CSV files:

**inventory.csv**:
```csv
item_id,name,current_stock,min_threshold,reorder_quantity,unit_cost,supplier
item1,Surgical Gloves,100,50,200,25.0,vendor1
item2,Medical Masks,15,30,100,75.0,vendor2
```

**vendors.csv**:
```csv
vendor_id,name,phone,email,rating,delivery_time,payment_terms,status,notes
vendor1,MedSupply Corp,+918800000488,vendor1@example.com,4.5,5,15 days,Active,Reliable supplier
vendor2,HealthCare Plus,+918800000488,vendor2@example.com,4.2,7,30 days,Active,Good prices
```

**vendor_items_mapping.csv**:
```csv
vendor_id,item_id,unit_price,lead_time_days,availability
vendor1,item1,50.0,3,In-Stock
vendor2,item1,55.0,5,In-Stock
```

## 4. Core Functionality

### A. Two-Phase Procurement Workflow
1. **Phase 1: Quote Collection**
   - Check inventory levels against minimum thresholds
   - Identify items needing reordering
   - Call all eligible vendors for quotes using AI conversations
   - Collect real-time pricing through voice recognition

2. **Phase 2: Quote Comparison & Order Placement**
   - Compare all collected quotes
   - Select the cheapest vendor
   - Place final order call to winning vendor
   - Send email notifications
   - Generate comprehensive reports

### B. Twilio Voice AI Integration
Implement **ConversationRelay** with:
- AI-powered conversation management
- Item-by-item quote collection
- Real-time price confirmation
- Speech recognition and parsing
- Webhook server for function calls

**Voice AI Configuration**:
```python
{
    "conversationRelay": {
        "welcomeGreeting": "Namaste! This is [Company] procurement team...",
        "voice": {
            "name": "en-IN-Neural2-A",
            "language": "en-IN"
        },
        "conversationProfile": {
            "llmWebhook": "https://your-webhook-url.com/voice-ai-webhook",
            "interruptible": True,
            "responseType": "sync"
        },
        "systemMessage": "You are a professional procurement assistant...",
        "tools": [
            {"type": "function", "function": {"name": "record_item_quote"}},
            {"type": "function", "function": {"name": "complete_quote_collection"}}
        ]
    }
}
```

### C. Webhook Server for AI Conversations
Create a Flask server that handles:
- `record_item_quote` function calls
- `complete_quote_collection` function calls
- Real-time quote storage and retrieval
- Conversation status monitoring

**Key endpoints**:
- `POST /voice-ai-webhook` - Handle AI function calls
- `GET /conversation-status/<call_sid>` - Monitor conversation progress
- `GET /get-quotes/<conversation_sid>` - Retrieve collected quotes

### D. Security & Safety Features
- **Phone Number Validation**: Only allow calls to specified safe numbers
- **Environment Variables**: Store all API keys securely
- **Call Logging**: Track all successful and failed calls
- **Error Handling**: Graceful fallbacks for API failures

## 5. Required Integrations

### A. Twilio Voice AI
- Account SID and Auth Token
- ConversationRelay configuration
- TwiML generation for AI calls
- Call status monitoring

### B. Optional Integrations
- **ElevenLabs**: For enhanced voice narration
- **Email SMTP**: For vendor notifications
- **Speech Recognition**: For fallback voice processing

## 6. Workflows to Implement

### Classic Workflow Functions:
```python
def run_two_phase_procurement_workflow()
def make_quote_request_call(vendor_id, vendor_info, items, quantities)
def make_final_order_call(vendor_id, vendor_info, items, total_cost, quotes)
```

### AI-Driven Workflow Functions:
```python
def make_voice_ai_quote_call(vendor_id, vendor_info, items, quantities)
def create_voice_ai_conversation_config(items, quantities)
def monitor_voice_ai_conversation(call_sid, vendor_id, items, quantities)
```

### Utility Functions:
```python
def load_csv_data()
def narrate_step(text, play_audio=True)
def send_email_notification_enhanced(vendor_info, items, total_cost, quotes)
def generate_procurement_report(items, quotes, winning_quote, savings)
```

## 7. Testing Functions

Implement comprehensive test functions:
```python
def test_simple_twilio_call()
def test_voice_ai_quote_call()
def test_itemwise_quote_call()
def run_itemwise_procurement_workflow()
```

## 8. Configuration & Environment Setup

### Required Environment Variables:
```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15017122661

# Security
ALLOWED_PHONE_NUMBER=+918800000488

# Optional Integrations
ELEVEN_API_KEY=your_elevenlabs_key
SMTP_SERVER=smtp.gmail.com
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Company Configuration
COMPANY_NAME=Your Company Name
PROCUREMENT_EMAIL=procurement@company.com
```

### Required Python Packages:
```txt
twilio>=8.0.0
requests>=2.28.0
flask>=2.3.0
flask-cors>=4.0.0
pandas>=1.5.0
python-dotenv>=1.0.0
speechrecognition>=3.10.0
pydub>=0.25.0
pyaudio>=0.2.11
elevenlabs>=0.2.0
```

## 9. File Structure
```
procurement-system/
├── caller.py                    # Main system logic
├── voice_ai_webhook_server.py   # Flask webhook server
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── data/
│   ├── inventory.csv
│   ├── vendors.csv
│   └── vendor_items_mapping.csv
├── logs/
│   ├── procurement_system.log
│   ├── successful_calls.log
│   └── procurement_report_*.csv
└── tests/
    └── test_system.py
```

## 10. Key Features to Implement

### A. Intelligent Conversation Flow
- AI asks for quotes one item at a time
- Confirms each price before moving to next item
- Handles price changes and corrections
- Professional Indian English communication

### B. Real-Time Quote Processing
- Speech-to-text conversion
- Price extraction and validation
- Immediate CSV updates
- Fallback pricing mechanisms

### C. Comprehensive Reporting
- Detailed procurement reports
- Quote comparison analysis
- Cost savings calculations
- Call success/failure tracking

### D. Error Handling & Fallbacks
- Graceful API failure handling
- Fallback quote estimation
- Retry mechanisms with delays
- Comprehensive logging

## 11. Production Deployment

### A. Webhook Server Deployment
- Deploy Flask server to cloud (Heroku, AWS, etc.)
- Configure ngrok for development
- Set up proper SSL/HTTPS
- Implement rate limiting and security

### B. Monitoring & Analytics
- Call success rate tracking
- Quote accuracy monitoring
- Cost savings analytics
- Vendor performance metrics

## 12. Advanced Features (Optional)

### A. Machine Learning Integration
- Quote prediction based on historical data
- Vendor performance scoring
- Demand forecasting

### B. Dashboard & UI
- Web interface for monitoring
- Real-time call status
- Historical analytics
- Manual quote entry

### C. Integration Capabilities
- ERP system integration
- Inventory management system sync
- Accounting software connection

## Success Criteria

The completed system should:
1. ✅ Make real Twilio Voice AI calls to vendors
2. ✅ Collect itemized quotes through AI conversations
3. ✅ Compare quotes and select cheapest vendor automatically
4. ✅ Place final orders with winning vendors
5. ✅ Generate comprehensive procurement reports
6. ✅ Handle errors gracefully with fallback mechanisms
7. ✅ Provide detailed logging and monitoring
8. ✅ Maintain security with phone number validation
9. ✅ Support both classic and AI-driven workflows
10. ✅ Scale to handle multiple items and vendors

## Delivery Requirements

1. **Complete Python codebase** with all functions implemented
2. **Working webhook server** for AI conversation handling
3. **Sample CSV data files** with test data
4. **Comprehensive documentation** with setup instructions
5. **Test suite** covering all major functionality
6. **Environment configuration** templates
7. **Deployment guide** for production setup

## Budget Estimate

The system requires:
- **Twilio Voice API**: ~$0.05-0.15 per minute for voice calls
- **ConversationRelay**: ~$0.25-0.50 per conversation
- **Cloud hosting**: ~$10-50/month for webhook server
- **Development time**: 2-4 weeks for full implementation

This system will provide a complete, production-ready procurement automation solution with advanced AI capabilities and comprehensive vendor management.
