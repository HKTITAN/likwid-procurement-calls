# Procurement Automation System Build Prompt

## Project Overview
Build a robust, production-ready procurement automation system that uses Twilio Voice AI (ConversationRelay) to call vendors, collect real-time price quotes via intelligent voice conversations, update CSVs, compare quotes, and place orders with the lowest-price vendor.

## Core Requirements

### 1. System Architecture
- **Main Language**: Python 3.8+
- **Primary Framework**: Flask for webhook server
- **Voice AI**: Twilio ConversationRelay with intelligent conversation handling
- **Data Storage**: CSV files (inventory.csv, vendors.csv, vendor_items_mapping.csv)
- **Real-time Processing**: Webhook-based quote collection during live calls

### 2. Key Workflows

#### Workflow A: Two-Phase Procurement
1. **Phase 1**: Call all vendors simultaneously to collect quotes
2. **Phase 2**: Compare all quotes and place order with cheapest vendor

#### Workflow B: Item-by-Item Procurement  
1. Call vendors one by one for detailed item-specific quotes
2. Use speech recognition to parse individual item prices
3. Confirm each price with vendor before proceeding

#### Workflow C: Voice AI Procurement (Primary Focus)
1. Use Twilio ConversationRelay to conduct intelligent conversations
2. AI agent asks for quotes item-by-item automatically
3. Real-time function calls to webhook server to record quotes
4. AI confirms each price before moving to next item

### 3. Technical Components Required

#### Core Files Structure:
```
project/
├── caller.py                 # Main orchestrator
├── voice_ai_webhook_server.py # Flask webhook server
├── requirements.txt          # Dependencies
├── .env                     # Configuration
├── data/
│   ├── inventory.csv
│   ├── vendors.csv
│   └── vendor_items_mapping.csv
├── logs/                    # Reports and logs
└── src/                     # Modular components
    ├── data_manager.py
    ├── models.py
    ├── procurement_engine.py
    └── twilio_manager.py
```

#### Required Python Packages:
```
twilio>=8.0.0
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
pandas>=2.0.0
speechrecognition>=3.10.0
pydub>=0.25.1
pyaudio>=0.2.11
python-dotenv>=1.0.0
elevenlabs>=0.2.26
```

### 4. Data Models

#### Inventory Item:
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
```

#### Vendor:
```python
@dataclass
class Vendor:
    name: str
    price: float
    phone: str
    email: str
    rating: float
    delivery_time: int
    payment_terms: str
```

#### Quote:
```python
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
```

### 5. Twilio Voice AI Implementation

#### ConversationRelay Configuration:
```python
voice_ai_config = {
    "conversationRelay": {
        "welcomeGreeting": "Namaste! This is [Company] procurement team calling for price quotes...",
        "voice": {"name": "en-IN-Neural2-A", "language": "en-IN"},
        "conversationProfile": {
            "llmWebhook": "https://your-webhook-url.ngrok.io",
            "interruptible": True,
            "responseType": "sync"
        },
        "systemMessage": "You are a professional procurement assistant...",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "record_item_quote",
                    "description": "Record confirmed price quote",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_name": {"type": "string"},
                            "unit_price": {"type": "number"},
                            "quantity": {"type": "integer"},
                            "confirmed": {"type": "boolean"}
                        }
                    }
                }
            }
        ]
    }
}
```

### 6. Webhook Server Requirements

#### Flask Server (`voice_ai_webhook_server.py`):
```python
@app.route('/voice-ai-webhook', methods=['POST'])
def handle_voice_ai_webhook():
    # Handle incoming AI function calls
    # Store quotes in real-time
    # Respond to AI with appropriate messages
    
@app.route('/conversation-status/<call_sid>')
def get_conversation_status(call_sid):
    # Return collected quotes for monitoring
```

### 7. Key Features to Implement

#### Inventory Management:
- Load inventory from CSV with proper column mapping
- Identify low/out-of-stock items automatically
- Calculate reorder quantities based on thresholds

#### Vendor Management:
- Load vendor data with phone numbers, emails, ratings
- Map vendors to items they can supply
- Handle vendor status (Active/Inactive/Blocked)

#### Quote Collection:
- **Classic Method**: Simple TTS message requesting quotes
- **Interactive Method**: Speech recognition to parse verbal quotes
- **AI Method**: ConversationRelay with intelligent conversation flow

#### Real-time Processing:
- Webhook server running on localhost:5000
- Live monitoring of AI conversations
- Function calls to record quotes during conversations
- Polling mechanism to fetch results

#### Quote Comparison:
- Sort quotes by total cost (lowest first)
- Calculate savings compared to highest quote
- Factor in vendor ratings, delivery time, payment terms

#### Order Placement:
- Automated call to winning vendor with order confirmation
- Email notifications with purchase order details
- CSV updates with final pricing and selections

#### Reporting:
- Generate detailed procurement reports
- Export to timestamped CSV files
- Log all successful calls and transactions

### 8. Security & Configuration

#### Environment Variables (.env):
```
# Twilio Credentials
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token  
TWILIO_PHONE_NUMBER=+1234567890

# Email Settings
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ElevenLabs API (optional for narration)
ELEVEN_API_KEY=your_elevenlabs_key

# Security
ALLOWED_PHONE_NUMBER=+918800000488  # Only allow calls to this number

# Company Details
COMPANY_NAME=Bio Mac Lifesciences
PROCUREMENT_EMAIL=procurement@company.com
```

#### Security Features:
- Restrict all outbound calls to one allowed phone number during testing
- Validate all phone numbers before making calls
- Log all call attempts and results
- Graceful fallback if external APIs fail

### 9. CSV Data Structure

#### inventory.csv:
```csv
item_id,name,current_stock,min_threshold,reorder_quantity,unit_cost,supplier
item1,Product A,100,50,200,25.0,vendor1
item2,Product B,15,30,100,75.0,vendor2
```

#### vendors.csv:
```csv
vendor_id,name,phone,email,rating,delivery_time,payment_terms,status,notes
vendor1,ABC Supplies,+918800000488,vendor1@example.com,4.5,5,15 days,Active,Reliable supplier
vendor2,XYZ Corp,+918800000488,vendor2@example.com,4.2,7,30 days,Active,Good pricing
```

#### vendor_items_mapping.csv:
```csv
vendor_id,item_id,unit_price,last_updated
vendor1,item1,50.0,2024-01-15
vendor1,item2,120.0,2024-01-15
vendor2,item1,55.0,2024-01-15
```

### 10. Demo Scripts Required

#### test_voice_ai_quote_call():
- Test Voice AI conversation with one vendor
- Verify webhook integration
- Confirm quote parsing and storage

#### run_two_phase_procurement_workflow():
- Full end-to-end procurement process
- Multiple vendor quote collection
- Automatic winner selection and order placement

#### test_itemwise_quote_call():
- Item-by-item quote collection testing
- Speech recognition validation
- CSV update verification

### 11. Deployment Requirements

#### Local Development:
- Python virtual environment setup
- ngrok for webhook URL exposure
- Flask development server for webhooks

#### Production Considerations:
- Webhook server deployed on cloud (Heroku, AWS, Azure)
- Database instead of CSV files
- Rate limiting for API calls
- Enhanced error handling and retry logic
- Monitoring and alerting

### 12. Success Criteria

#### Functional Requirements:
1. ✅ System can load inventory and vendor data from CSV files
2. ✅ System identifies items needing reorder automatically  
3. ✅ System makes automated calls to vendors using Twilio
4. ✅ Voice AI conducts intelligent conversations item-by-item
5. ✅ Real-time quote collection via webhook function calls
6. ✅ Automatic quote comparison and vendor selection
7. ✅ Order placement call to winning vendor
8. ✅ Email notifications with detailed purchase orders
9. ✅ Comprehensive reporting with cost savings analysis
10. ✅ Security restrictions prevent unauthorized calls

#### Technical Requirements:
1. ✅ Clean, modular, well-documented code
2. ✅ Proper error handling and logging
3. ✅ CSV data validation and column mapping
4. ✅ Webhook server with real-time processing
5. ✅ Environment-based configuration
6. ✅ Speech recognition integration
7. ✅ Twilio ConversationRelay integration
8. ✅ Graceful fallbacks for missing dependencies

### 13. Provided Reference

#### Workflow Diagram:
The system should follow this logical flow:
1. Check Inventory → 2. Identify Low Stock → 3. Send Requirements to Vendors → 4. Collect Quotes → 5. Compare Quotes → 6. Place Order with Cheapest Vendor

#### Sample Company Profile:
- **Company**: Bio Mac Lifesciences
- **Industry**: Life Sciences/Medical Supplies
- **Use Case**: Automated procurement for laboratory supplies
- **Volume**: Medium-scale procurement with multiple vendors
- **Geography**: India (hence Indian English voice and Rupee currency)

### 14. Optional Enhancements

#### Advanced Features:
- Multi-language support for different regions
- Integration with inventory management systems
- Automated PO generation and DocuSign integration  
- Vendor performance analytics and scoring
- SMS notifications for urgent stock-outs
- WhatsApp Business API integration
- Machine learning for demand forecasting

#### UI/Dashboard:
- Web-based dashboard for monitoring
- Real-time call status updates
- Quote comparison visualizations
- Vendor performance metrics

---

## Deliverables Expected

1. **Complete working Python system** with all files and dependencies
2. **Detailed documentation** with setup and usage instructions
3. **Sample CSV data files** for testing
4. **Demo scripts** showing each workflow in action
5. **Deployment guide** for production use
6. **Video demonstration** of the system working end-to-end

## Timeline Estimate: 2-3 weeks for full implementation

This system combines traditional procurement workflows with cutting-edge AI voice technology to create a fully automated, intelligent procurement solution that can save significant time and money through competitive quote collection and automated vendor selection.
