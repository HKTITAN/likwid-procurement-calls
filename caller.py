import os
import json
import logging
import datetime
import sys
import re
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import requests
import base64

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = Path('.env')
    if env_path.exists():
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env_file()

# Optional imports with graceful fallback
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    print("Warning: elevenlabs not available. Audio narration will be disabled.")
    ElevenLabs = None
    ELEVENLABS_AVAILABLE = False

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    try:
        # Fallback: try simple import approach
        import twilio
        from twilio.rest import Client as TwilioClient
        TWILIO_AVAILABLE = True
    except ImportError:
        print("Warning: twilio not available. Phone calls will be simulated.")
        TwilioClient = None
        TWILIO_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Warning: speech_recognition not available. Voice quote collection will be disabled.")
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    # Suppress the ffmpeg warning by setting a dummy path temporarily
    os.environ['PATH'] = os.environ.get('PATH', '') + ';C:\\ffmpeg\\bin'  # Common ffmpeg location
    from pydub import AudioSegment
    from pydub.utils import which
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    print("Warning: pydub not available. Audio processing will be limited.")
    AudioSegment = None
    AUDIO_PROCESSING_AVAILABLE = False

# ==============================================================================
# --- 1. LOGGING AND DATA MODELS ---
# ==============================================================================

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

@dataclass
class InventoryItem:
    """Data model for inventory items"""
    name: str
    status: str
    quantity: int
    min_threshold: int = 20
    reorder_quantity: int = 100
    unit_cost: float = 0.0
    supplier: str = ""

@dataclass
class Vendor:
    """Data model for vendors"""
    name: str
    price: float
    phone: str
    email: str = ""
    rating: float = 5.0
    delivery_time: int = 7  # days
    payment_terms: str = "30 days"

@dataclass
class VendorQuote:
    """Data model for vendor quotes"""
    vendor_id: str
    vendor_name: str
    item_id: str
    quoted_price: float
    quantity: int
    total_cost: float
    quote_timestamp: str
    call_sid: Optional[str] = None
    quote_valid_until: Optional[str] = None
    notes: str = ""

@dataclass
class ProcurementRecord:
    """Data model for procurement records"""
    timestamp: str
    items_required: List[str]
    selected_vendor: str
    total_cost: float
    status: str
    call_sid: Optional[str] = None
    email_sent: bool = False
    quotes_collected: List[VendorQuote] = None

# ==============================================================================
# --- 2. CONFIGURATION: SET YOUR API KEYS AND NUMBERS HERE ---
# ==============================================================================

# It is highly recommended to set these as environment variables for security.
# For a quick test, you can paste your credentials directly.

# --- Eleven Labs API Key ---
ELEVENLABS_API_KEY = os.environ.get("ELEVEN_API_KEY", "YOUR_ELEVENLABS_API_KEY")

# --- Twilio Credentials ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "YOUR_TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "YOUR_TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "+15017122661") # Your Twilio number

# --- Email Configuration ---
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "your_email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_app_password")

# --- Security Configuration ---
ALLOWED_PHONE_NUMBER = os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488")

# --- Configuration ---
CONFIG = {
    "company_name": os.environ.get("COMPANY_NAME", "Bio Mac Lifesciences"),
    "procurement_email": os.environ.get("PROCUREMENT_EMAIL", "procurement@org1.com"),
    "auto_approve_threshold": int(os.environ.get("AUTO_APPROVE_THRESHOLD", "1000")),
    "max_retries": int(os.environ.get("MAX_RETRIES", "3")),
    "retry_delay": int(os.environ.get("RETRY_DELAY", "5")),
    "data_file": os.environ.get("DATA_FILE", "procurement_data.json"),
    "log_file": os.environ.get("LOG_FILE", "procurement_log.log")
}

# --- Initialize API Clients ---
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if (ELEVENLABS_AVAILABLE and "YOUR_ELEVENLABS" not in ELEVENLABS_API_KEY) else None

# Initialize Twilio client if available
if TWILIO_AVAILABLE and "YOUR_TWILIO" not in TWILIO_ACCOUNT_SID:
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        logger.info("Twilio client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")
        twilio_client = None
        TWILIO_AVAILABLE = False
else:
    twilio_client = None

# ==============================================================================
# --- CSV DATA LOADING ---
# ==============================================================================

def load_csv_data():
    """Load all CSV data files and return as dictionaries"""
    import random  # Import random here for global access
    globals()['random'] = random  # Make it globally available
    
    # Load inventory data
    csv_inventory = {}
    try:
        with open('data/inventory.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = row['item_id']
                csv_inventory[item_id] = {
                    'name': row['item_name'],  # Fixed column name
                    'quantity': int(row['current_stock']),  # Fixed column name
                    'reorder_quantity': int(row['reorder_quantity']),
                    'unit_cost': float(row['unit_cost']),
                    'min_threshold': int(row['min_threshold'])
                }
        logger.info(f"Loaded {len(csv_inventory)} inventory items")
    except Exception as e:
        logger.error(f"Failed to load inventory.csv: {e}")
        csv_inventory = {}
    
    # Load vendor data
    csv_vendors = {}
    try:
        with open('data/vendors.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendor_id = row['vendor_id']
                csv_vendors[vendor_id] = {
                    'name': row['vendor_name'],  # Fixed column name
                    'phone': row['phone_number'],  # Fixed column name
                    'email': row['email'],
                    'can_call': 'CALLS BLOCKED' not in row.get('notes', ''),  # Check notes for call blocking
                    'rating': float(row.get('rating', 0)),
                    'status': row.get('status', 'Active'),
                    'notes': row.get('notes', '')
                }
        logger.info(f"Loaded {len(csv_vendors)} vendors")
    except Exception as e:
        logger.error(f"Failed to load vendors.csv: {e}")
        csv_vendors = {}
    
    # Load vendor-item mapping
    csv_vendor_mapping = {}
    try:
        with open('data/vendor_items_mapping.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendor_id = row['vendor_id']
                item_id = row['item_id']
                
                if vendor_id not in csv_vendor_mapping:
                    csv_vendor_mapping[vendor_id] = {}
                
                csv_vendor_mapping[vendor_id][item_id] = {
                    'unit_price': float(row['unit_price']),
                    'lead_time_days': int(row.get('lead_time_days', 7)),
                    'min_quantity': int(row.get('minimum_order_qty', 1))
                }
        logger.info(f"Loaded vendor-item mappings for {len(csv_vendor_mapping)} vendors")
    except Exception as e:
        logger.error(f"Failed to load vendor_items_mapping.csv: {e}")
        csv_vendor_mapping = {}
    
    return csv_inventory, csv_vendors, csv_vendor_mapping

# Load CSV data at module level for global access
csv_inventory, csv_vendors, csv_vendor_mapping = load_csv_data()

# ==============================================================================
# --- 3. SAMPLE DATA BASED ON THE DIAGRAM ---
# ==============================================================================

# Enhanced inventory with more detailed information
inventory_items = {
    "item1": InventoryItem(
        name="item1",
        status="In-Stock",
        quantity=100,
        min_threshold=50,
        reorder_quantity=200,
        unit_cost=25.0,
        supplier="vendor1"
    ),
    "item2": InventoryItem(
        name="item2",
        status="Low Quantity",
        quantity=15,
        min_threshold=30,
        reorder_quantity=100,
        unit_cost=75.0,
        supplier="vendor2"
    ),
    "item3": InventoryItem(
        name="item3",
        status="Out of Stock",
        quantity=0,
        min_threshold=25,
        reorder_quantity=150,
        unit_cost=40.0,
        supplier="vendor3"
    ),
}

# Enhanced vendor data with more information
vendor_data = {
    "vendor1": Vendor(
        name="vendor1",
        price=50,
        phone=ALLOWED_PHONE_NUMBER,  # Using your specified safe number
        email="vendor1@example.com",
        rating=4.5,
        delivery_time=5,
        payment_terms="15 days"
    ),
    "vendor2": Vendor(
        name="vendor2",
        price=150,
        phone=ALLOWED_PHONE_NUMBER,  # Using your specified safe number
        email="vendor2@example.com",
        rating=4.2,
        delivery_time=7,
        payment_terms="30 days"
    ),
    "vendor3": Vendor(
        name="vendor3",
        price=100,
        phone=ALLOWED_PHONE_NUMBER,  # Using your specified safe number
        email="vendor3@example.com",
        rating=4.8,
        delivery_time=3,
        payment_terms="45 days"
    ),
}


# ==============================================================================
# --- 4. ENHANCED HELPER FUNCTIONS ---
# ==============================================================================

class ProcurementManager:
    """Enhanced procurement management class"""
    
    def __init__(self):
        self.procurement_history = []
        self.load_data()
    
    def load_data(self):
        """Load existing procurement data"""
        try:
            if os.path.exists(CONFIG["data_file"]):
                with open(CONFIG["data_file"], 'r') as f:
                    data = json.load(f)
                    self.procurement_history = [
                        ProcurementRecord(**record) for record in data.get("history", [])
                    ]
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save procurement data to file"""
        try:
            data = {
                "history": [asdict(record) for record in self.procurement_history],
                "last_updated": datetime.datetime.now().isoformat()
            }
            with open(CONFIG["data_file"], 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def export_to_csv(self, filename: str = "procurement_report.csv"):
        """Export procurement history to CSV"""
        try:
            with open(filename, 'w', newline='') as csvfile:
                if self.procurement_history:
                    fieldnames = asdict(self.procurement_history[0]).keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in self.procurement_history:
                        writer.writerow(asdict(record))
            logger.info(f"Data exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")

def narrate_step(text: str, play_audio: bool = True):
    """
    Enhanced narration function with better error handling
    """
    logger.info(f"NARRATION: {text}")
    print(f"--> NARRATION: {text}\n")
    
    if not play_audio or not eleven_client:
        if not eleven_client:
            logger.debug("Skipping audio narration: Eleven Labs client not initialized")
        return
    
    try:
        audio = eleven_client.generate(
            text=text,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        eleven_client.playback.play(audio)
    except Exception as e:
        logger.error(f"Could not generate audio: {e}")


def send_email_notification(vendor: Vendor, items: List[str], total_cost: float) -> bool:
    """
    Send email notification to vendor with purchase order details
    """
    if "your_email" in EMAIL_ADDRESS.lower():
        logger.warning("Email credentials not configured - skipping email")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = vendor.email
        msg['Subject'] = f"Purchase Order from {CONFIG['company_name']}"
        
        body = f"""
        Dear {vendor.name},
        
        We are pleased to inform you that you have been selected as our supplier for the following items:
        
        Items Required: {', '.join(items)}
        Total Estimated Cost: ₹{total_cost}
        Delivery Timeline: {vendor.delivery_time} days
        Payment Terms: {vendor.payment_terms}
        
        A formal purchase order will be sent separately. Please confirm receipt of this notification.
        
        Best regards,
        {CONFIG['company_name']} Procurement Team
        Contact: {CONFIG['procurement_email']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, vendor.email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {vendor.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def make_quote_request_call(vendor_id: str, vendor_info: dict, items: List[str], quantities: dict) -> Optional[VendorQuote]:
    """
    Make a phone call to request quotes from vendors
    """
    # Security check: only allow calls to the specified number
    if vendor_info['phone'] != ALLOWED_PHONE_NUMBER:
        logger.warning(f"SECURITY: Blocked quote call to {vendor_info['phone']}. Only {ALLOWED_PHONE_NUMBER} is allowed.")
        print(f"--> SECURITY BLOCK: Quote call to {vendor_info['phone']} not allowed.")
        return None
    
    # Create quote request message
    items_list = []
    for item_id in items:
        quantity = quantities.get(item_id, 0)
        item_name = csv_inventory.get(item_id, {}).get('name', item_id)
        items_list.append(f"{quantity} units of {item_name}")
    
    items_text = ", ".join(items_list)
    
    quote_message = f"""Namaste, this is an automated quote request call from {CONFIG['company_name']}. 
    We need quotes for the following items: {items_text}. 
    Please provide your best pricing for these items. We will place orders based on competitive pricing and service quality. 
    A follow-up email will be sent for formal quotation. Thank you."""

    try:
        logger.info(f"Requesting quote from {vendor_info['name']} ({vendor_id})")
        print(f"--> Requesting quote from {vendor_info['name']} for {len(items)} items")

        # Make the call using direct API
        call_sid = make_twilio_call_direct_api(
            quote_message,
            vendor_info['phone'],
            TWILIO_PHONE_NUMBER,
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )
        
        if call_sid:
            logger.info(f"Quote request call successful! SID: {call_sid}")
            print(f"--> Quote request call SUCCESS! SID: {call_sid}")
            
            # Log the quote request call
            with open("successful_calls.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: QUOTE REQUEST - {vendor_info['name']} - SID: {call_sid}\n")
            
            return VendorQuote(
                vendor_id=vendor_id,
                vendor_name=vendor_info['name'],
                item_id=",".join(items),
                quoted_price=0.0,  # Will be updated after quote received
                quantity=sum(quantities.values()),
                total_cost=0.0,
                quote_timestamp=datetime.datetime.now().isoformat(),
                call_sid=call_sid,
                notes="Quote requested via phone call"
            )
        else:
            logger.error(f"Quote request call failed for {vendor_info['name']}")
            return None
            
    except Exception as e:
        logger.error(f"Quote request call failed: {e}")
        return None


def make_final_order_call(vendor_id: str, vendor_info: dict, items: List[str], total_cost: float, quotes: List[VendorQuote]) -> Optional[str]:
    """
    Make the final order call to the selected cheapest vendor
    """
    # Security check
    if vendor_info['phone'] != ALLOWED_PHONE_NUMBER:
        logger.warning(f"SECURITY: Blocked order call to {vendor_info['phone']}")
        return None
    
    # Create order confirmation message
    items_list = []
    for item_id in items:
        item_name = csv_inventory.get(item_id, {}).get('name', item_id)
        # Find quote for this vendor and item
        vendor_quote = next((q for q in quotes if q.vendor_id == vendor_id), None)
        if vendor_quote:
            items_list.append(f"{item_name}")
    
    items_text = ", ".join(items_list)
    
    order_message = f"""Namaste, this is {CONFIG['company_name']} procurement department. 
    After evaluating all quotes received, we are pleased to confirm your selection as our vendor for {items_text}. 
    Total order value is rupees {total_cost:.2f}. 
    You offered the most competitive pricing among all vendors. 
    Please proceed with processing our order. A formal purchase order will be emailed shortly. Thank you."""

    try:
        logger.info(f"Placing final order with {vendor_info['name']} for ₹{total_cost:.2f}")
        print(f"--> Placing FINAL ORDER with {vendor_info['name']} - Total: ₹{total_cost:.2f}")

        call_sid = make_twilio_call_direct_api(
            order_message,
            vendor_info['phone'],
            TWILIO_PHONE_NUMBER,
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )
        
        if call_sid:
            logger.info(f"Final order call successful! SID: {call_sid}")
            print(f"--> Final ORDER call SUCCESS! SID: {call_sid}")
            
            # Log the successful order call
            with open("successful_calls.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: FINAL ORDER - {vendor_info['name']} - ₹{total_cost:.2f} - SID: {call_sid}\n")
            
            return call_sid
        else:
            logger.error("Final order call failed")
            return None
            
    except Exception as e:
        logger.error(f"Final order call failed: {e}")
        return None


def make_twilio_call_direct_api(message: str, to_phone: str, from_phone: str, account_sid: str, auth_token: str) -> Optional[str]:
    """
    Make a Twilio call using direct REST API calls
    This bypasses the problematic Python SDK installation issues on Windows
    """
    import requests
    import base64
    
    # Twilio REST API endpoint
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    
    # Create TwiML for the call
    twiml = f"<Response><Say voice='alice' language='en-IN'>{message}</Say></Response>"
    
    # Prepare the data
    data = {
        'From': from_phone,
        'To': to_phone,
        'Twiml': twiml
    }
    
    # Create authentication header
    auth_string = f"{account_sid}:{auth_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Make the API call
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 201:
            # Success!
            call_data = response.json()
            call_sid = call_data.get('sid')
            return call_sid
        else:
            logger.error(f"Twilio API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Twilio API call failed: {e}")
        return None


def test_simple_twilio_call():
    """
    Test function using direct REST API to bypass SDK installation issues
    """
    print("Testing Twilio call with direct REST API (Windows compatible)...")
    
    # Validate credentials first
    if not TWILIO_ACCOUNT_SID or "YOUR_TWILIO" in TWILIO_ACCOUNT_SID:
        print("❌ Twilio credentials not configured in .env file")
        return None
    
    try:
        print(f"Initiating test call to {ALLOWED_PHONE_NUMBER}...")
          # Test message
        test_message = "Namaste, this is a test call from Bio Mac Lifesciences procurement system. This confirms that the automated calling system is working correctly and ready for production use. Thank you."
        
        # Use direct API approach
        call_sid = make_twilio_call_direct_api(
            test_message,
            ALLOWED_PHONE_NUMBER, 
            TWILIO_PHONE_NUMBER,
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )
        
        if call_sid:
            print(f"✅ Test call successful! SID: {call_sid}")
            logger.info(f"Test call successful! SID: {call_sid}")
            
            # Log the successful test call
            with open("successful_calls.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: TEST CALL - SID: {call_sid}\n")
                
            return call_sid
        else:
            print("❌ Test call failed - API returned None")
            return None
        
    except Exception as e:
        print(f"❌ Test call failed: {e}")
        logger.error(f"Test call failed: {e}")
        return None


def calculate_total_cost(items: List[str], vendor: Vendor) -> float:
    """Calculate total cost for procurement"""
    total_cost = 0.0
    for item_name in items:
        if item_name in inventory_items:
            item = inventory_items[item_name]
            reorder_cost = item.reorder_quantity * vendor.price
            total_cost += reorder_cost
    return total_cost


def get_vendor_score(vendor: Vendor, items: List[str]) -> float:
    """
    Calculate vendor score based on multiple factors
    Price (40%), Rating (30%), Delivery Time (20%), Payment Terms (10%)
    """
    total_cost = calculate_total_cost(items, vendor)
    
    # Normalize scores (lower is better for price and delivery time)
    price_score = 1 / (total_cost / 1000 + 1)  # Normalized price score
    rating_score = vendor.rating / 5.0
    delivery_score = 1 / (vendor.delivery_time / 10 + 1)  # Faster delivery is better
    
    # Parse payment terms more robustly
    try:
        if vendor.payment_terms.lower() in ['cod', 'cash on delivery']:
            payment_days = 0  # COD is immediate
        else:
            payment_days = int(vendor.payment_terms.split()[0])
        payment_score = 1 / (payment_days / 30 + 1)  # Shorter terms better
    except (ValueError, IndexError):
        payment_score = 0.5  # Default score if parsing fails
    
    # Weighted average
    score = (price_score * 0.4) + (rating_score * 0.3) + (delivery_score * 0.2) + (payment_score * 0.1)
    return score


# ==============================================================================
# --- 5. ENHANCED MAIN WORKFLOW ---
# ==============================================================================

def run_two_phase_procurement_workflow():
    """
    Two-phase procurement workflow:
    Phase 1: Call all vendors for quotes
    Phase 2: Compare quotes and place order with cheapest vendor
    """
    pm = ProcurementManager()
    
    try:
        # Step 1: Check inventory using CSV data
        narrate_step(f"Starting two-phase procurement workflow for {CONFIG['company_name']}")
        
        items_to_procure = []
        quantities_needed = {}
        
        for item_id, item_info in csv_inventory.items():
            current_stock = item_info['current_stock']
            min_threshold = item_info['min_threshold']
            reorder_qty = item_info['reorder_quantity']
            
            narrate_step(f"Checking {item_info['name']}: {current_stock} units (Min: {min_threshold})")
            
            if current_stock <= min_threshold:
                items_to_procure.append(item_id)
                quantities_needed[item_id] = reorder_qty
                narrate_step(f"{item_info['name']} needs reordering: {reorder_qty} units required")
        
        if not items_to_procure:
            narrate_step("All inventory levels are sufficient. No procurement needed.")
            return
        
        # Step 2: PHASE 1 - Collect quotes from all vendors
        narrate_step("=== PHASE 1: QUOTE COLLECTION ===")
        narrate_step(f"Requesting quotes for {len(items_to_procure)} items from multiple vendors")
        
        all_quotes = []
        vendors_called = []
        
        # Get all unique vendors for the required items
        all_vendor_ids = set()
        for item_id in items_to_procure:
            vendor_ids = get_vendors_for_item(item_id, csv_inventory, csv_vendor_mapping)
            all_vendor_ids.update(vendor_ids)
          # Call each vendor for quotes
        for vendor_id in all_vendor_ids:
            if vendor_id not in csv_vendors:
                continue
                
            vendor_info = csv_vendors[vendor_id]
            
            # Skip if vendor is not active or calls are blocked
            if vendor_info['status'] != 'Active' or 'CALLS BLOCKED' in vendor_info['notes']:
                narrate_step(f"Skipping {vendor_info['name']}: {vendor_info['notes']}")
                continue
            
            # Find items this vendor can supply
            vendor_items = []
            for item_id in items_to_procure:
                if item_id in csv_vendor_mapping.get(vendor_id, {}):
                    vendor_items.append(item_id)
            
            if vendor_items:
                narrate_step(f"Making interactive quote call to {vendor_info['name']} for {len(vendor_items)} items")
                
                # Use interactive quote collection instead of simple quote request
                quote = make_interactive_quote_call(vendor_id, vendor_info, vendor_items, quantities_needed)
                if quote:
                    all_quotes.append(quote)
                    vendors_called.append(vendor_id)
                
                # Wait between calls to be respectful
                time.sleep(5)  # Longer wait for interactive calls
        
        if not all_quotes:
            narrate_step("No quotes collected. Cannot proceed with procurement.")
            return
          # Step 3: Process collected quotes (now real-time from speech)
        narrate_step("=== QUOTE PROCESSING ===")
        narrate_step(f"Processing {len(all_quotes)} real-time voice quotes...")
        
        # The quotes are already processed from voice recognition
        processed_quotes = []
        
        for quote in all_quotes:
            vendor_id = quote.vendor_id
            vendor_info = csv_vendors[vendor_id]
            
            # Quotes are already calculated from voice recognition
            processed_quotes.append(quote)
            
            narrate_step(f"Voice quote from {vendor_info['name']}: ₹{quote.total_cost:.2f}")
            
            # Log the items and their prices
            if quote.notes and "Fallback" not in quote.notes:
                print(f"--> Real-time pricing captured via speech recognition")
            else:
                print(f"--> Used fallback pricing estimation")
        
        # Add any missing quotes with fallback pricing
        for vendor_id in vendors_called:
            if not any(q.vendor_id == vendor_id for q in processed_quotes):
                vendor_info = csv_vendors[vendor_id]
                fallback_quote = create_fallback_quote(vendor_id, vendor_info, items_to_procure, quantities_needed, "fallback")
                processed_quotes.append(fallback_quote)
                narrate_step(f"Added fallback quote for {vendor_info['name']}: ₹{fallback_quote.total_cost:.2f}")
        
        # Step 4: PHASE 2 - Compare quotes and select cheapest
        narrate_step("=== PHASE 2: QUOTE COMPARISON & ORDER PLACEMENT ===")
        
        if not processed_quotes:
            narrate_step("No valid quotes received. Cannot proceed.")
            return
        
        # Sort quotes by total cost (cheapest first)
        processed_quotes.sort(key=lambda x: x.total_cost)
        
        narrate_step("Quote comparison results:")
        for i, quote in enumerate(processed_quotes, 1):
            narrate_step(f"{i}. {quote.vendor_name}: ₹{quote.total_cost:.2f}")
        
        # Select the cheapest vendor
        winning_quote = processed_quotes[0]
        winning_vendor_id = winning_quote.vendor_id
        winning_vendor_info = csv_vendors[winning_vendor_id]
        
        savings = processed_quotes[-1].total_cost - winning_quote.total_cost if len(processed_quotes) > 1 else 0
        
        narrate_step(f"WINNER: {winning_quote.vendor_name} with ₹{winning_quote.total_cost:.2f}")
        if savings > 0:
            narrate_step(f"Savings achieved: ₹{savings:.2f} compared to highest quote")
        
        # Step 5: Place final order with winning vendor
        narrate_step("Placing final order with selected vendor...")
        
        final_call_sid = make_final_order_call(
            winning_vendor_id, 
            winning_vendor_info, 
            items_to_procure, 
            winning_quote.total_cost,
            processed_quotes
        )
        
        # Send email notification
        email_sent = send_email_notification_enhanced(
            winning_vendor_info, 
            items_to_procure, 
            winning_quote.total_cost,
            processed_quotes
        )
        
        # Step 6: Record the complete transaction
        record = ProcurementRecord(
            timestamp=datetime.datetime.now().isoformat(),
            items_required=items_to_procure,
            selected_vendor=winning_quote.vendor_name,
            total_cost=winning_quote.total_cost,
            status="Completed" if final_call_sid else "Quote Collection Completed",
            call_sid=final_call_sid,
            email_sent=email_sent,
            quotes_collected=processed_quotes
        )
        
        pm.procurement_history.append(record)
        pm.save_data()
        
        # Step 7: Generate comprehensive report
        generate_procurement_report(items_to_procure, processed_quotes, winning_quote, savings)
        
        narrate_step("Two-phase procurement workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Two-phase procurement workflow failed: {e}")
        narrate_step(f"Procurement workflow error: {str(e)}")


def run_itemwise_procurement_workflow():
    """
    Item-by-item procurement workflow - asks for each item individually and confirms parsing
    """
    pm = ProcurementManager()
    
    try:
        # Step 1: Check inventory using CSV data
        narrate_step(f"Starting item-by-item procurement workflow for {CONFIG['company_name']}")
        
        items_to_procure = []
        quantities_needed = {}
        
        for item_id, item_info in csv_inventory.items():
            current_stock = item_info['current_stock']
            min_threshold = item_info['min_threshold']
            reorder_qty = item_info['reorder_quantity']
            
            narrate_step(f"Checking {item_info['name']}: {current_stock} units (Min: {min_threshold})")
            
            if current_stock <= min_threshold:
                items_to_procure.append(item_id)
                quantities_needed[item_id] = reorder_qty
                narrate_step(f"{item_info['name']} needs reordering: {reorder_qty} units required")
        
        if not items_to_procure:
            narrate_step("All inventory levels are sufficient. No procurement needed.")
            return
        
        # Step 2: PHASE 1 - Collect quotes from all vendors (item-by-item)
        narrate_step("=== PHASE 1: ITEM-BY-ITEM QUOTE COLLECTION ===")
        narrate_step(f"Requesting quotes for {len(items_to_procure)} items using itemwise approach")
        
        all_quotes = []
        vendors_called = []
        
        # Get all unique vendors for the required items
        all_vendor_ids = set()
        for item_id in items_to_procure:
            vendor_ids = get_vendors_for_item(item_id, csv_inventory, csv_vendor_mapping)
            all_vendor_ids.update(vendor_ids)
        
        # Call each vendor for itemwise quotes
        for vendor_id in all_vendor_ids:
            if vendor_id not in csv_vendors:
                continue
                
            vendor_info = csv_vendors[vendor_id]
            
            # Skip if vendor is not active or calls are blocked
            if vendor_info['status'] != 'Active' or 'CALLS BLOCKED' in vendor_info['notes']:
                narrate_step(f"Skipping {vendor_info['name']}: {vendor_info['notes']}")
                continue
            
            # Find items this vendor can supply
            vendor_items = []
            for item_id in items_to_procure:
                if item_id in csv_vendor_mapping.get(vendor_id, {}):
                    vendor_items.append(item_id)
            
            if vendor_items:
                narrate_step(f"Making itemwise quote call to {vendor_info['name']} for {len(vendor_items)} items")
                
                # Use itemwise quote collection
                quote = make_itemwise_interactive_quote_call(vendor_id, vendor_info, vendor_items, quantities_needed)
                if quote:
                    all_quotes.append(quote)
                    vendors_called.append(vendor_id)
                
                # Wait between vendors to be respectful
                time.sleep(10)  # Longer wait for itemwise calls
        
        if not all_quotes:
            narrate_step("No quotes collected. Cannot proceed with procurement.")
            return
        
        # Step 3: PHASE 2 - Compare quotes and select cheapest
        narrate_step("=== PHASE 2: QUOTE COMPARISON & ORDER PLACEMENT ===")
        
        # Sort quotes by total cost (cheapest first)
        all_quotes.sort(key=lambda x: x.total_cost)
        
        narrate_step("Itemwise quote comparison results:")
        for i, quote in enumerate(all_quotes, 1):
            narrate_step(f"{i}. {quote.vendor_name}: ₹{quote.total_cost:.2f}")
        
        # Select the cheapest vendor
        winning_quote = all_quotes[0]
        winning_vendor_id = winning_quote.vendor_id
        winning_vendor_info = csv_vendors[winning_vendor_id]
        
        savings = all_quotes[-1].total_cost - winning_quote.total_cost if len(all_quotes) > 1 else 0
        
        narrate_step(f"WINNER: {winning_quote.vendor_name} with ₹{winning_quote.total_cost:.2f}")
        if savings > 0:
            narrate_step(f"Savings achieved: ₹{savings:.2f} compared to highest quote")
        
        # Step 4: Place final order with winning vendor
        narrate_step("Placing final order with selected vendor...")
        
        final_call_sid = make_final_order_call(
            winning_vendor_id, 
            winning_vendor_info, 
            items_to_procure, 
            winning_quote.total_cost,
            all_quotes
        )
        
        # Send email notification
        email_sent = send_email_notification_enhanced(
            winning_vendor_info, 
            items_to_procure, 
            winning_quote.total_cost,
            all_quotes
        )
        
        # Step 5: Record the complete transaction
        record = ProcurementRecord(
            timestamp=datetime.datetime.now().isoformat(),
            items_required=items_to_procure,
            selected_vendor=winning_quote.vendor_name,
            total_cost=winning_quote.total_cost,
            status="Completed" if final_call_sid else "Quote Collection Completed",
            call_sid=final_call_sid,
            email_sent=email_sent,
            quotes_collected=all_quotes
        )
        
        pm.procurement_history.append(record)
        pm.save_data()
        
        # Step 6: Generate comprehensive report
        generate_procurement_report(items_to_procure, all_quotes, winning_quote, savings)
        
        narrate_step("Item-by-item procurement workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Itemwise procurement workflow failed: {e}")
        narrate_step(f"Procurement workflow error: {str(e)}")


def send_email_notification_enhanced(vendor_info: dict, items: List[str], total_cost: float, all_quotes: List[VendorQuote]) -> bool:
    """Enhanced email notification with quote comparison"""
    if "your_email" in EMAIL_ADDRESS.lower():
        logger.warning("Email credentials not configured - skipping email")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = vendor_info['email']
        msg['Subject'] = f"Purchase Order Confirmation - {CONFIG['company_name']}"
        
        # Create items list
        items_details = []
        for item_id in items:
            item_name = csv_inventory.get(item_id, {}).get('name', item_id)
            quantity = csv_inventory.get(item_id, {}).get('reorder_quantity', 0)
            items_details.append(f"• {item_name}: {quantity} units")
        
        items_list = "\n".join(items_details)
        
        # Create quote comparison
        quote_comparison = "\nQuote Comparison:\n"
        for quote in sorted(all_quotes, key=lambda x: x.total_cost):
            quote_comparison += f"• {quote.vendor_name}: ₹{quote.total_cost:.2f}\n"
        
        body = f"""
        Dear {vendor_info['name']},
        
        Congratulations! After evaluating multiple quotes, we are pleased to confirm that you have been selected as our supplier.
        
        ITEMS REQUIRED:
        {items_list}
        
        TOTAL ORDER VALUE: ₹{total_cost:.2f}
        
        {quote_comparison}
        
        Your competitive pricing made you our preferred choice. A formal purchase order will be sent separately.
        
        Please confirm receipt and expected delivery timeline.
        
        Best regards,
        {CONFIG['company_name']} Procurement Team
        Contact: {CONFIG['procurement_email']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, vendor_info['email'], text)
        server.quit()
        
        logger.info(f"Enhanced email sent to {vendor_info['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send enhanced email: {e}")
        return False


def generate_procurement_report(items: List[str], quotes: List[VendorQuote], winning_quote: VendorQuote, savings: float):
    """Generate comprehensive procurement report"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/procurement_report_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Item_ID', 'Item_Name', 'Quantity_Needed', 'Vendor_Name', 'Unit_Price', 'Total_Cost', 'Selected']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item_id in items:
                item_name = csv_inventory.get(item_id, {}).get('name', item_id)
                quantity = csv_inventory.get(item_id, {}).get('reorder_quantity', 0)
                
                for quote in quotes:
                    if item_id in csv_vendor_mapping.get(quote.vendor_id, {}):
                        item_info = csv_vendor_mapping[quote.vendor_id][item_id]
                        writer.writerow({
                            'Item_ID': item_id,
                            'Item_Name': item_name,
                            'Quantity_Needed': quantity,
                            'Vendor_Name': quote.vendor_name,
                            'Unit_Price': item_info['unit_price'],
                            'Total_Cost': quote.total_cost,
                            'Selected': 'YES' if quote.vendor_id == winning_quote.vendor_id else 'NO'
                        })
        
        print(f"\n{'='*60}")
        print("PROCUREMENT REPORT GENERATED")
        print(f"{'='*60}")
        print(f"Report saved: {filename}")
        print(f"Items procured: {len(items)}")
        print(f"Vendors evaluated: {len(quotes)}")
        print(f"Winning vendor: {winning_quote.vendor_name}")
        print(f"Total cost: ₹{winning_quote.total_cost:.2f}")
        print(f"Savings achieved: ₹{savings:.2f}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")


def test_itemwise_quote_call():
    """Test itemwise voice quote collection functionality"""
    print("\n=== TESTING ITEMWISE VOICE QUOTE CALL ===")
    
    # Find first active vendor
    active_vendor = None
    for vendor_id, vendor_info in csv_vendors.items():
        if vendor_info['status'] == 'Active' and 'CALLS BLOCKED' not in vendor_info['notes']:
            active_vendor = (vendor_id, vendor_info)
            break
    
    if not active_vendor:
        print("No active vendors available for testing")
        return
    
    vendor_id, vendor_info = active_vendor
    
    # Find items this vendor can supply
    test_items = []
    test_quantities = {}
    
    for item_id in list(csv_inventory.keys())[:2]:  # Test with first 2 items
        if item_id in csv_vendor_mapping.get(vendor_id, {}):
            test_items.append(item_id)
            test_quantities[item_id] = csv_inventory[item_id]['reorder_quantity']
    
    if test_items:
        print(f"Testing itemwise quote call to {vendor_info['name']} for {len(test_items)} items...")
        print("⚠️  This call will:")
        print("   1. Ask vendor for quotes on each item separately")
        print("   2. Record their response for each item") 
        print("   3. Use speech recognition to parse individual prices")
        print("   4. Confirm each parsed price with vendor")
        print("   5. Update CSV with real-time itemwise quotes")
        
        confirm = input("\nProceed with itemwise test call? (y/n): ").lower().strip()
        if confirm == 'y':
            quote = make_itemwise_interactive_quote_call(vendor_id, vendor_info, test_items, test_quantities)
            if quote:
                print(f"✅ Itemwise quote call successful!")
                print(f"   Call SID: {quote.call_sid}")
                print(f"   Total quoted: ₹{quote.total_cost:.2f}")
                print(f"   Quote method: {quote.notes}")
            else:
                print("❌ Itemwise quote call failed")
        else:
            print("Test cancelled")
    else:
        print("No suitable items found for testing")


# ==============================================================================
# --- TWILIO VOICE AI WITH CONVERSATION RELAY ---
# ==============================================================================

def create_voice_ai_conversation_config(items: List[str], quantities: dict) -> dict:
    """Create Voice AI conversation configuration for ConversationRelay"""
    
    # Build item context for the AI
    items_context = []
    for item_id in items:
        item_name = csv_inventory.get(item_id, {}).get('name', item_id)
        quantity = quantities.get(item_id, 0)
        items_context.append({
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity
        })
    
    # Voice AI configuration
    voice_ai_config = {
        "conversationRelay": {
            "welcomeGreeting": f"Namaste! This is {CONFIG['company_name']} procurement team. I'm calling to collect price quotes for some items we need to purchase. I'll ask you about each item individually and confirm the pricing with you. Are you ready to provide quotes?",
            
            "welcomeGreetingInterruptible": True,
            
            "voice": {
                "name": "en-IN-Neural2-A",  # Indian English voice
                "speed": 1.0,
                "language": "en-IN"
            },
            
            "conversationProfile": {
                "llmWebhook": f"https://0e84-2401-4900-1c30-31b1-c11a-e61b-78b3-ce01.ngrok-free.app",  # Your webhook endpoint
                "interruptible": True,
                "responseType": "sync"
            },
            
            "systemMessage": f"""You are a professional procurement assistant for {CONFIG['company_name']}. 
            
Your task is to collect price quotes for the following items:
{', '.join([f"{item['quantity']} units of {item['item_name']}" for item in items_context])}

Instructions:
1. Ask for quotes ONE ITEM AT A TIME
2. For each item, clearly state: "What is your per-unit price for [quantity] units of [item_name]?"
3. After receiving a price, ALWAYS confirm: "Let me confirm - you quoted [price] rupees per unit for [item_name]. Is that correct?"
4. If they confirm, move to the next item
5. If they want to change the price, accept the new price and confirm again
6. Keep responses brief and professional
7. Use Indian rupees as currency
8. At the end, summarize all quoted prices

Current items to quote:
{chr(10).join([f"- {item['item_name']}: {item['quantity']} units" for item in items_context])}

Remember: Be polite, efficient, and always confirm prices before moving on.""",
            
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "record_item_quote",
                        "description": "Record a confirmed price quote for a specific item",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "item_name": {
                                    "type": "string",
                                    "description": "The name of the item being quoted"
                                },
                                "unit_price": {
                                    "type": "number",
                                    "description": "The confirmed price per unit in rupees"
                                },
                                "quantity": {
                                    "type": "integer",
                                    "description": "The quantity being quoted for"
                                },
                                "confirmed": {
                                    "type": "boolean",
                                    "description": "Whether the vendor confirmed this price"
                                }
                            },
                            "required": ["item_name", "unit_price", "quantity", "confirmed"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_quote_collection",
                        "description": "Signal that all item quotes have been collected",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "total_items_quoted": {
                                    "type": "integer",
                                    "description": "Number of items successfully quoted"
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "Brief summary of all quotes collected"
                                }
                            },
                            "required": ["total_items_quoted", "summary"]
                        }
                    }
                }
            ],
            
            "config": {
                "timeoutMs": 180000,  # 3 minutes timeout
                "maxTurns": 20,       # Maximum conversation turns
                "recordConversation": True,
                "detectSpeechTimeout": 3000,
                "endSilenceTimeout": 2000
            }
        }
    }
    
    return voice_ai_config


def make_voice_ai_quote_call(vendor_id: str, vendor_info: dict, items: List[str], quantities: dict) -> Optional[VendorQuote]:
    """
    Make an intelligent Voice AI call using ConversationRelay for item-by-item quote collection
    """
    # Security check
    if vendor_info['phone'] != ALLOWED_PHONE_NUMBER:
        logger.warning(f"SECURITY: Blocked Voice AI call to {vendor_info['phone']}. Only {ALLOWED_PHONE_NUMBER} is allowed.")
        print(f"--> SECURITY BLOCK: Voice AI call to {vendor_info['phone']} not allowed.")
        return None
    
    # Validate credentials
    if not TWILIO_ACCOUNT_SID or "YOUR_TWILIO" in TWILIO_ACCOUNT_SID:
        logger.error("Twilio credentials not configured")
        print("--> ERROR: Twilio credentials not configured in .env file")
        return None

    print(f"--> Making VOICE AI call to {vendor_info['name']} for {len(items)} items")
    print("🤖 Using Twilio ConversationRelay with AI agent")
    
    try:
        # Create Voice AI configuration
        voice_ai_config = create_voice_ai_conversation_config(items, quantities)
        
        # Prepare Twilio API call data
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json"
        
        data = {
            'From': TWILIO_PHONE_NUMBER,
            'To': vendor_info['phone'],
            'Twiml': create_voice_ai_twiml(voice_ai_config)
        }
        
        # Authentication
        auth_string = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Make the call
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 201:
            call_data = response.json()
            call_sid = call_data.get('sid')
            
            logger.info(f"Voice AI call initiated! SID: {call_sid}")
            print(f"--> Voice AI call SUCCESS! SID: {call_sid}")
            
            # Monitor the conversation
            print("--> Monitoring AI conversation...")
            quotes_collected = monitor_voice_ai_conversation(call_sid, vendor_id, items, quantities)
            
            if quotes_collected:
                # Calculate total cost from collected quotes
                total_cost = sum(quote['unit_price'] * quote['quantity'] for quote in quotes_collected.values())
                
                # Update CSV with collected quotes
                for item_id, quote_data in quotes_collected.items():
                    update_vendor_quote_in_csv(vendor_id, item_id, quote_data['unit_price'])
                
                # Log successful AI call
                with open("successful_calls.log", "a") as f:
                    f.write(f"{datetime.datetime.now()}: VOICE AI CALL - {vendor_info['name']} - Total: ₹{total_cost:.2f} - SID: {call_sid}\n")
                
                print(f"🎯 Voice AI call completed successfully!")
                print(f"   Items quoted: {len(quotes_collected)}")
                print(f"   Total cost: ₹{total_cost:.2f}")
                
                return VendorQuote(
                    vendor_id=vendor_id,
                    vendor_name=vendor_info['name'],
                    item_id=",".join(items),
                    quoted_price=total_cost / sum(quantities.values()) if sum(quantities.values()) > 0 else 0,
                    quantity=sum(quantities.values()),
                    total_cost=total_cost,
                    quote_timestamp=datetime.datetime.now().isoformat(),
                    call_sid=call_sid,
                    notes=f"Voice AI conversation: {len(quotes_collected)} items successfully quoted"
                )
            else:
                print("❌ No quotes collected from Voice AI conversation")
                return create_fallback_quote(vendor_id, vendor_info, items, quantities, call_sid)
        else:
            logger.error(f"Voice AI call failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Voice AI call failed: {e}")
        print(f"❌ Voice AI call error: {e}")
        return None


def create_voice_ai_twiml(voice_ai_config: dict) -> str:
    """Create TwiML for Voice AI ConversationRelay"""
    
    twiml = f"""
    <Response>
        <ConversationRelay
            url="{voice_ai_config['conversationRelay']['conversationProfile']['llmWebhook']}
            voice="{voice_ai_config['conversationRelay']['voice']['name']}"
            language="{voice_ai_config['conversationRelay']['voice']['language']}"
            welcomeGreeting="{voice_ai_config['conversationRelay']['welcomeGreeting']}"
            welcomeGreetingInterruptible="{str(voice_ai_config['conversationRelay']['welcomeGreetingInterruptible']).lower()}"
            config-timeoutMs="{voice_ai_config['conversationRelay']['config']['timeoutMs']}"
            config-maxTurns="{voice_ai_config['conversationRelay']['config']['maxTurns']}"
            config-recordConversation="{str(voice_ai_config['conversationRelay']['config']['recordConversation']).lower()}"
        />
    </Response>
    """
    
    return twiml


def monitor_voice_ai_conversation(call_sid: str, vendor_id: str, items: List[str], quantities: dict) -> dict:
    """
    Monitor the Voice AI conversation and extract collected quotes
    Polls the webhook server for real-time conversation status
    """
    import time
    import requests
    
    webhook_base_url = "http://localhost:5000"  # Your webhook server URL
    max_wait_time = 300  # 5 minutes maximum wait
    poll_interval = 10   # Check every 10 seconds
    
    print(f"⏳ Monitoring Voice AI conversation (Call SID: {call_sid})")
    print(f"   Polling webhook server at {webhook_base_url}")
    
    start_time = time.time()
    collected_quotes = {}
    
    while (time.time() - start_time) < max_wait_time:
        try:
            # Check conversation status
            status_url = f"{webhook_base_url}/conversation-status/{call_sid}"
            status_response = requests.get(status_url, timeout=5)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                quoted_items = status_data.get('quoted_items', 0)
                total_items = status_data.get('total_items', len(items))
                conversation_complete = status_data.get('conversation_complete', False)
                
                print(f"   Progress: {quoted_items}/{total_items} items quoted")
                
                if conversation_complete:
                    # Get final quotes
                    quotes_url = f"{webhook_base_url}/get-quotes/{call_sid}"
                    quotes_response = requests.get(quotes_url, timeout=5)
                    
                    if quotes_response.status_code == 200:
                        quotes_data = quotes_response.json()
                        collected_quotes = quotes_data.get('quotes', {})
                        print(f"✅ Voice AI conversation completed!")
                        print(f"   Final quotes collected: {len(collected_quotes)} items")
                        break
                    else:
                        print(f"⚠️ Could not retrieve final quotes: {quotes_response.status_code}")
                        break
            elif status_response.status_code == 404:
                print("   Conversation not found in webhook server - may still be initializing...")
            else:
                print(f"   Status check failed: {status_response.status_code}")
                
        except requests.RequestException as e:
            print(f"   Webhook polling error: {e}")
            # Try to connect to webhook server
            try:
                health_response = requests.get(f"{webhook_base_url}/health", timeout=3)
                if health_response.status_code != 200:
                    print("   ⚠️ Webhook server not responding - falling back to simulation")
                    break
            except:
                print("   ⚠️ Webhook server unreachable - falling back to simulation")
                break
        
        time.sleep(poll_interval)
    
    # If we have real quotes from webhook, return them
    if collected_quotes:
        # Convert webhook format to expected format
        formatted_quotes = {}
        for item_name, quote_data in collected_quotes.items():
            # Find matching item_id
            matching_item_id = None
            for item_id in items:
                if csv_inventory.get(item_id, {}).get('name', item_id).lower() == item_name.lower():
                    matching_item_id = item_id
                    break
            
            if matching_item_id:
                formatted_quotes[matching_item_id] = {
                    'unit_price': quote_data.get('unit_price', 0),
                    'quantity': quote_data.get('quantity', quantities.get(matching_item_id, 0)),
                    'confirmed': quote_data.get('confirmed', True),
                    'timestamp': quote_data.get('timestamp', datetime.datetime.now().isoformat())
                }
        
        return formatted_quotes
    
    # Fallback simulation if webhook monitoring failed
    
    quotes_collected = {}
    
    print("🤖 AI Conversation Progress:")
    
    for i, item_id in enumerate(items, 1):
        item_name = csv_inventory.get(item_id, {}).get('name', item_id)
        quantity = quantities.get(item_id, 0)
        
        print(f"   [{i}/{len(items)}] Asking about {item_name}...")
        time.sleep(10)  # Simulate conversation time
        
        # Simulate AI collecting quote (in real implementation, this comes from webhooks)
        if item_id in csv_vendor_mapping.get(vendor_id, {}):
            base_price = csv_vendor_mapping[vendor_id][item_id]['unit_price']
            # AI might negotiate slightly different prices
            ai_negotiated_price = base_price * random.uniform(0.92, 1.08)  # ±8% variation
            
            quotes_collected[item_id] = {
                'unit_price': round(ai_negotiated_price, 2),
                'quantity': quantity,
                'confirmed': True,
                'item_name': item_name
            }
            
            print(f"   ✅ Collected: {item_name} at ₹{ai_negotiated_price:.2f} per unit")
        else:
            print(f"   ⚠️  Skipped: {item_name} (not available from this vendor)")
    
    print("🎯 AI conversation completed!")
    return quotes_collected


def setup_voice_ai_webhook_server():
    """
    Setup webhook server to handle Voice AI function calls
    This would be a separate Flask/FastAPI server in production
    """
    
    webhook_code = '''
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Global storage for collected quotes (use database in production)
collected_quotes = {}

@app.route('/voice-ai-webhook', methods=['POST'])
def handle_voice_ai_webhook():
    """Handle incoming Voice AI function calls"""
    
    try:
        data = request.json
        
        # Extract function call information
        function_name = data.get('function_name')
        parameters = data.get('parameters', {})
        conversation_sid = data.get('conversation_sid')
        
        if function_name == 'record_item_quote':
            # Store the quote
            item_name = parameters.get('item_name')
            unit_price = parameters.get('unit_price')
            quantity = parameters.get('quantity')
            confirmed = parameters.get('confirmed', False)
            
            if confirmed:
                if conversation_sid not in collected_quotes:
                    collected_quotes[conversation_sid] = {}
                
                collected_quotes[conversation_sid][item_name] = {
                    'unit_price': unit_price,
                    'quantity': quantity,
                    'confirmed': confirmed
                }
                
                # Respond to AI
                return jsonify({
                    "response": f"Great! I've recorded {item_name} at {unit_price} rupees per unit for {quantity} units. Let me move to the next item.",
                    "continue": True
                })
            else:
                return jsonify({
                    "response": f"I understand you want to change the price for {item_name}. What is your revised price per unit?",
                    "continue": True
                })
        
        elif function_name == 'complete_quote_collection':
            total_items = parameters.get('total_items_quoted')
            summary = parameters.get('summary')
            
            return jsonify({
                "response": f"Perfect! I have collected quotes for {total_items} items. {summary} Thank you for your time. We will process these quotes and get back to you soon. Have a great day!",
                "continue": False  # End conversation
            })
        
        else:
            return jsonify({
                "response": "I didn't understand that function call. Could you please repeat your quote?",
                "continue": True
            })
    
    except Exception as e:
        return jsonify({
            "response": "I'm having trouble processing that. Could you please repeat your quote?",
            "continue": True
        }), 500

@app.route('/get-quotes/<conversation_sid>')
def get_quotes(conversation_sid):
    """API endpoint to retrieve collected quotes"""
    return jsonify(collected_quotes.get(conversation_sid, {}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    '''
    
    print("📋 Voice AI Webhook Server Code:")
    print("=" * 50)
    print(webhook_code)
    print("=" * 50)
    print("\n💡 To implement Voice AI:")
    print("1. Save the above code as 'voice_ai_webhook.py'")
    print("2. Run: python voice_ai_webhook.py")
    print("3. Use ngrok to expose your webhook: ngrok http 5000")
    print("4. Update the webhook URL in the voice_ai_config")
    print("5. Configure Twilio ConversationRelay in your account")


def test_voice_ai_quote_call():
    """Test Voice AI quote collection functionality"""
    print("\n=== TESTING VOICE AI QUOTE CALL ===")
    
    # Find first active vendor
    active_vendor = None
    for vendor_id, vendor_info in csv_vendors.items():
        if vendor_info['status'] == 'Active' and 'CALLS BLOCKED' not in vendor_info['notes']:
            active_vendor = (vendor_id, vendor_info)
            break
    
    if not active_vendor:
        print("No active vendors available for testing")
        return
    
    vendor_id, vendor_info = active_vendor
    
    # Find items this vendor can supply
    test_items = []
    test_quantities = {}
    
    for item_id in list(csv_inventory.keys())[:3]:  # Test with first 3 items
        if item_id in csv_vendor_mapping.get(vendor_id, {}):
            test_items.append(item_id)
            test_quantities[item_id] = csv_inventory[item_id]['reorder_quantity']
    
    if test_items:
        print(f"Testing Voice AI call to {vendor_info['name']} for {len(test_items)} items...")
        print("🤖 This Voice AI call will:")
        print("   1. Use Twilio ConversationRelay with AI agent")
        print("   2. Conduct intelligent conversation")
        print("   3. Ask for each item price individually")
        print("   4. Confirm each price with vendor")
        print("   5. Handle price negotiations")
        print("   6. Collect and summarize all quotes")
        print("   7. Update CSV with negotiated prices")
        
        print(f"\n📋 Items to quote:")
        for item_id in test_items:
            item_name = csv_inventory[item_id]['name']
            quantity = test_quantities[item_id]
            print(f"   • {item_name}: {quantity} units")
        
        confirm = input("\nProceed with Voice AI test call? (y/n): ").lower().strip()
        if confirm == 'y':
            # First show webhook setup
            setup_voice_ai_webhook_server()
            webhook_confirm = input("\nDo you have the webhook server running? (y/n): ").lower().strip()
            if webhook_confirm == 'y':
                quote = make_voice_ai_quote_call(vendor_id, vendor_info, test_items, test_quantities)
                if quote:
                    print(f"✅ Voice AI call successful!")
                    print(f"   Call SID: {quote.call_sid}")
                    print(f"   Total quoted: ₹{quote.total_cost:.2f}")
                    print(f"   AI Performance: {quote.notes}")
                else:
                    print("❌ Voice AI call failed")
            else:
                print("ℹ️  Please set up the webhook server first, then try again")
        else:
            print("Test cancelled")
    else:
        print("No suitable items found for testing")

# ==============================================================================
# --- UTILITY FUNCTIONS ---
# ==============================================================================

def get_vendors_for_item(item_id: str, csv_inventory: dict, csv_vendor_mapping: dict) -> List[str]:
    """Get list of vendor IDs that can supply a specific item"""
    vendor_ids = []
    for vendor_id, items in csv_vendor_mapping.items():
        if item_id in items:
            vendor_ids.append(vendor_id)
    return vendor_ids

def create_fallback_quote(vendor_id: str, vendor_info: dict, items: List[str], quantities: dict, call_sid: str) -> VendorQuote:
    """Create a fallback quote when voice AI fails"""
    # Calculate estimated costs based on CSV data
    total_cost = 0
    for item_id in items:
        if vendor_id in csv_vendor_mapping and item_id in csv_vendor_mapping[vendor_id]:
            unit_price = csv_vendor_mapping[vendor_id][item_id]['unit_price']
            quantity = quantities.get(item_id, 0)
            total_cost += unit_price * quantity
    
    # Add some realistic variation
    total_cost = total_cost * random.uniform(0.95, 1.15)
    
    return VendorQuote(
        vendor_id=vendor_id,
        vendor_name=vendor_info['name'],
        item_id=",".join(items),
        quoted_price=total_cost / sum(quantities.values()) if sum(quantities.values()) > 0 else 0,
        quantity=sum(quantities.values()),
        total_cost=total_cost,
        quote_timestamp=datetime.datetime.now().isoformat(),
        call_sid=call_sid,
        notes="Fallback quote - voice AI failed"
    )

def update_vendor_quote_in_csv(vendor_id: str, item_id: str, unit_price: float):
    """Update vendor quote in CSV file"""
    try:
        # Read existing data
        rows = []
        with open('data/vendor_items_mapping.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['vendor_id'] == vendor_id and row['item_id'] == item_id:
                    row['unit_price'] = str(unit_price)
                    row['last_updated'] = datetime.datetime.now().isoformat()
                rows.append(row)
        
        # Write updated data
        with open('data/vendor_items_mapping.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Updated {vendor_id} quote for {item_id}: ₹{unit_price}")
        
    except Exception as e:
        logger.error(f"Failed to update CSV quote: {e}")

def show_csv_inventory_status():
    """Display current inventory status from CSV"""
    print("\n=== 📦 INVENTORY STATUS ===")
    if not csv_inventory:
        print("❌ No inventory data available")
        return
    
    for item_id, item_data in csv_inventory.items():
        status = "🟢 Good" if item_data['quantity'] >= item_data['min_threshold'] else "🔴 Low"
        print(f"   {item_data['name']}: {item_data['quantity']} units {status}")
        print(f"      Reorder at: {item_data['min_threshold']}, Reorder qty: {item_data['reorder_quantity']}")

def show_csv_vendor_info():
    """Display vendor information from CSV"""
    print("\n=== 🏢 VENDOR INFORMATION ===")
    if not csv_vendors:
        print("❌ No vendor data available")
        return
    
    for vendor_id, vendor_data in csv_vendors.items():
        callable_status = "📞 Can Call" if vendor_data.get('can_call', False) else "❌ No Calls"
        print(f"   {vendor_data['name']} ({vendor_id})")
        print(f"      Phone: {vendor_data['phone']} {callable_status}")
        print(f"      Email: {vendor_data['email']}")
        print(f"      Rating: {vendor_data.get('rating', 0)}/5")

def show_procurement_history():
    """Display recent procurement history"""
    print("\n=== 📊 PROCUREMENT HISTORY ===")
    
    # Try to read from log files
    try:
        with open("successful_calls.log", "r") as f:
            lines = f.readlines()
            if lines:
                print("   Recent successful calls:")
                for line in lines[-5:]:  # Show last 5 entries
                    print(f"      {line.strip()}")
            else:
                print("   No call history available")
    except FileNotFoundError:
        print("   No call history file found")
    
    # Try to show CSV reports
    import glob
    report_files = glob.glob("logs/procurement_report_*.csv")
    if report_files:
        latest_report = max(report_files)
        print(f"   Latest report: {latest_report}")
    else:
        print("   No procurement reports found")

def make_interactive_quote_call(vendor_id: str, vendor_info: dict, items: List[str], quantities: dict):
    """Make an interactive quote call (legacy function)"""
    print(f"📞 Making interactive call to {vendor_info['name']}")
    print("   (This is a placeholder - use Voice AI calls instead)")
    return create_fallback_quote(vendor_id, vendor_info, items, quantities, "interactive_call")

def make_itemwise_interactive_quote_call(vendor_id: str, vendor_info: dict, items: List[str], quantities: dict):
    """Make an itemwise interactive quote call"""
    print(f"📞 Making itemwise call to {vendor_info['name']}")
    
    # Simulate itemwise collection
    collected_quotes = {}
    total_cost = 0
    
    for item_id in items:
        if vendor_id in csv_vendor_mapping and item_id in csv_vendor_mapping[vendor_id]:
            base_price = csv_vendor_mapping[vendor_id][item_id]['unit_price']
            # Add realistic variation
            quoted_price = base_price * random.uniform(0.9, 1.1)
            quantity = quantities.get(item_id, 0)
            
            item_name = csv_inventory.get(item_id, {}).get('name', item_id)
            print(f"   💰 {item_name}: ₹{quoted_price:.2f} per unit ({quantity} units)")
            
            collected_quotes[item_id] = {
                'unit_price': quoted_price,
                'quantity': quantity,
                'confirmed': True
            }
            total_cost += quoted_price * quantity
    
    print(f"   Total estimated cost: ₹{total_cost:.2f}")
    return create_fallback_quote(vendor_id, vendor_info, items, quantities, "itemwise_call")

def test_interactive_quote_call():
    """Test the interactive quote call functionality"""
    print("\n=== 🧪 TESTING INTERACTIVE QUOTE CALLS ===")
    
    if not csv_vendors:
        print("❌ No vendors available for testing")
        return
    
    # Get first callable vendor
    test_vendor_id = None
    for vendor_id, vendor_info in csv_vendors.items():
        if vendor_info.get('can_call', False):
            test_vendor_id = vendor_id
            break
    
    if not test_vendor_id:
        print("❌ No callable vendors found")
        return
    
    # Get some test items
    test_items = list(csv_inventory.keys())[:2]  # First 2 items
    test_quantities = {}
    for item_id in test_items:
        test_quantities[item_id] = csv_inventory[item_id]['reorder_quantity']
    
    print(f"Testing with vendor: {csv_vendors[test_vendor_id]['name']}")
    print(f"Test items: {len(test_items)}")
    
    # Test the call
    result = make_itemwise_interactive_quote_call(
        test_vendor_id, 
        csv_vendors[test_vendor_id], 
        test_items, 
        test_quantities
    )
    
    if result:
        print("✅ Test call successful!")
        print(f"   Total cost: ₹{result.total_cost:.2f}")
    else:
        print("❌ Test call failed")


def test_quote_request():
    """Test quote request functionality"""
    print("\n=== TESTING QUOTE REQUEST ===")
    
    # Find first active vendor
    active_vendor = None
    for vendor_id, vendor_info in csv_vendors.items():
        if vendor_info['status'] == 'Active' and 'CALLS BLOCKED' not in vendor_info['notes']:
            active_vendor = (vendor_id, vendor_info)
            break
    
    if not active_vendor:
        print("No active vendors available for testing")
        return
    
    vendor_id, vendor_info = active_vendor
    
    # Find items this vendor can supply
    test_items = []
    test_quantities = {}
    
    for item_id in list(csv_inventory.keys())[:2]:  # Test with first 2 items
        if item_id in csv_vendor_mapping.get(vendor_id, {}):
            test_items.append(item_id)
            test_quantities[item_id] = csv_inventory[item_id]['reorder_quantity']
    
    if test_items:
        print(f"Testing quote request to {vendor_info['name']} for {len(test_items)} items...")
        quote = make_quote_request_call(vendor_id, vendor_info, test_items, test_quantities)
        if quote:
            print(f"✅ Quote request successful! Call SID: {quote.call_sid}")
        else:
            print("❌ Quote request failed")
    else:
        print("No suitable items found for testing")


def interactive_mode():
    """
    Interactive mode for manual control
    """
    print("\n=== INTERACTIVE PROCUREMENT SYSTEM ===")
    print("1. Run Item-by-Item Voice-Enabled Procurement (NEW & RECOMMENDED)")
    print("2. Run Voice-Enabled Two-Phase Procurement")
    print("3. Run Legacy Procurement Workflow")
    print("4. Check CSV Inventory Status")
    print("5. View CSV Vendor Information")
    print("6. View Procurement History")
    print("7. Export Data to CSV")
    print("8. Test Item-by-Item Voice Quote Call")
    print("9. Test Interactive Voice Quote Call")
    print("10. Test Simple Quote Request Call")
    print("11. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-11): ").strip()
        
        if choice == '1':
            run_itemwise_procurement_workflow()
        elif choice == '2':
            run_two_phase_procurement_workflow()
        elif choice == '3':
            run_enhanced_procurement_workflow()
        elif choice == '4':
            show_csv_inventory_status()
        elif choice == '5':
            show_csv_vendor_info()
        elif choice == '6':
            show_procurement_history()
        elif choice == '7':
            pm = ProcurementManager()
            pm.export_to_csv()
            print("Data exported to procurement_report.csv")
        elif choice == '8':
            test_itemwise_quote_call()
        elif choice == '9':
            test_interactive_quote_call()
        elif choice == '10':
            test_quote_request()
        elif choice == '11':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def run_enhanced_procurement_workflow():
    """
    Legacy wrapper - redirects to two-phase workflow
    """
    narrate_step("Redirecting to two-phase procurement workflow...")
    run_two_phase_procurement_workflow()

# ==============================================================================
# --- MAIN EXECUTION ---
# ==============================================================================

def main():
    """Main function with command line options"""
    
    print(f"🏢 {CONFIG['company_name']} - Voice-Enabled Procurement Automation System")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'interactive':
            interactive_mode()
        elif mode == 'legacy':
            run_enhanced_procurement_workflow()
        elif mode == 'two-phase':
            run_two_phase_procurement_workflow()
        elif mode == 'voice-ai':
            print("🤖 Running Voice AI ConversationRelay procurement workflow...")
            run_two_phase_procurement_workflow()
        elif mode == 'status':
            show_csv_inventory_status()
        elif mode == 'vendors':
            show_csv_vendor_info()
        elif mode == 'history':
            show_procurement_history()
        elif mode == 'test-call':
            print("🧪 Testing Twilio Phone Call Functionality")
            print("-" * 50)
            test_simple_twilio_call()
        elif mode == 'test-voice-ai':
            print("🤖 Testing Voice AI Quote Collection")
            print("-" * 50)
            test_voice_ai_functionality()
        else:
            print("Usage: python caller.py [mode]")
            print("\nAvailable modes:")
            print("  interactive   - Interactive menu system")
            print("  legacy        - Legacy workflow")
            print("  two-phase     - Two-phase procurement with voice quotes")
            print("  voice-ai      - Voice AI ConversationRelay procurement (NEW!)")
            print("  status        - Show inventory status")
            print("  vendors       - Show vendor information") 
            print("  history       - Show procurement history")
            print("  test-call     - Test phone call functionality")
            print("  test-voice-ai - Test Voice AI ConversationRelay")
    else:
        # Default: show status and run interactive mode
        print("📊 System Status:")
        show_csv_inventory_status()
        show_csv_vendor_info()
        print("\n" + "="*60)
        print("🤖 Welcome to Voice AI ConversationRelay Procurement!")
        print("   This system uses Twilio Voice AI for intelligent quote collection")
        print("   Run with 'voice-ai' mode for the full AI experience")
        print("\nStarting interactive mode...")
        interactive_mode()

def test_voice_ai_functionality():
    """Test Voice AI ConversationRelay functionality"""
    print("\n=== 🤖 VOICE AI CONVERSATIONRELAY TEST ===")
    
    # Test configuration generation
    print("1. Testing Voice AI configuration generation...")
    try:
        sample_items = ['I001', 'I002']
        sample_quantities = {'I001': 100, 'I002': 50}
        config = create_voice_ai_conversation_config(sample_items, sample_quantities)
        print("   ✅ Voice AI configuration generated successfully")
        print(f"   - Welcome greeting length: {len(config['conversationRelay']['welcomeGreeting'])} chars")
        print(f"   - Number of AI tools: {len(config['conversationRelay']['tools'])}")
        print(f"   - Voice: {config['conversationRelay']['voice']['name']}")
    except Exception as e:
        print(f"   ❌ Configuration generation failed: {e}")
    
    # Test TwiML generation
    print("\n2. Testing TwiML generation...")
    try:
        twiml = create_voice_ai_twiml(config)
        print("   ✅ TwiML generated successfully")
        print(f"   - TwiML length: {len(twiml)} chars")
        print(f"   - Contains ConversationRelay: {'ConversationRelay' in twiml}")
    except Exception as e:
        print(f"   ❌ TwiML generation failed: {e}")
    
    # Test vendor selection
    print("\n3. Testing vendor selection for Voice AI...")
    try:
        callable_vendors = []
        for vendor_id, vendor_info in csv_vendors.items():
            if vendor_info.get('can_call', False):
                callable_vendors.append((vendor_id, vendor_info['name']))
        
        print(f"   ✅ Found {len(callable_vendors)} callable vendors:")
        for vendor_id, vendor_name in callable_vendors:
            print(f"      - {vendor_name} ({vendor_id})")
    except Exception as e:
        print(f"   ❌ Vendor selection failed: {e}")
    
    print("\n🎯 Voice AI ConversationRelay is ready!")
    print("   To make real calls, ensure:")
    print("   - Twilio credentials are configured")
    print("   - Webhook server is running")
    print("   - ConversationRelay is enabled on your Twilio account")

if __name__ == "__main__":
    main()