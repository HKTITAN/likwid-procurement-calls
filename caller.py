import os
import json
import logging
import datetime
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
class ProcurementRecord:
    """Data model for procurement records"""
    timestamp: str
    items_required: List[str]
    selected_vendor: str
    total_cost: float
    status: str
    call_sid: Optional[str] = None
    email_sent: bool = False

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


def make_phone_call_with_retry(vendor: Vendor, items: List[str], max_retries: int = 3) -> Optional[str]:
    """
    Enhanced phone calling function with retry logic and phone number validation
    Uses direct REST API calls to bypass Windows Twilio SDK installation issues
    """
    logger.info(f"Attempting to call {vendor.name.upper()}")
    
    # Security check: only allow calls to the specified number
    if vendor.phone != ALLOWED_PHONE_NUMBER:
        logger.warning(f"SECURITY: Blocked call to {vendor.phone}. Only {ALLOWED_PHONE_NUMBER} is allowed.")
        print(f"--> SECURITY BLOCK: Call to {vendor.phone} not allowed. Only {ALLOWED_PHONE_NUMBER} is permitted.")
        return "blocked_unauthorized_number"
    
    # Validate credentials
    if not TWILIO_ACCOUNT_SID or "YOUR_TWILIO" in TWILIO_ACCOUNT_SID:
        logger.error("Twilio credentials not configured")
        print("--> ERROR: Twilio credentials not configured in .env file")
        return None

    # Create message for the procurement call
    call_message = f"Namaste, this is an automated procurement call from {CONFIG['company_name']}. You have been selected as our preferred supplier for {', '.join(items)} based on your competitive quote and excellent service record. A formal purchase order and email confirmation will be sent to you shortly. Thank you for your continued partnership with {CONFIG['company_name']}."

    for attempt in range(max_retries):
        try:
            logger.info(f"Initiating call to {vendor.name} at {vendor.phone} (Attempt {attempt + 1})")
            print(f"--> Making REAL call to {vendor.name} at {vendor.phone} (Attempt {attempt + 1})")

            # Use direct REST API approach to bypass SDK issues
            call_sid = make_twilio_call_direct_api(
                call_message, 
                vendor.phone, 
                TWILIO_PHONE_NUMBER,
                TWILIO_ACCOUNT_SID,
                TWILIO_AUTH_TOKEN
            )
            
            if call_sid:
                logger.info(f"Call initiated successfully! Call SID: {call_sid}")
                print(f"--> Call SUCCESS! SID: {call_sid}")
                
                # Log successful call for tracking
                with open("successful_calls.log", "a") as f:
                    f.write(f"{datetime.datetime.now()}: Called {vendor.name} at {vendor.phone} - SID: {call_sid}\n")
                
                return call_sid
            else:
                raise Exception("API call returned None")

        except Exception as e:
            logger.error(f"Call attempt {attempt + 1} failed: {e}")
            print(f"--> Call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {CONFIG['retry_delay']} seconds...")
                print(f"--> Retrying in {CONFIG['retry_delay']} seconds...")
                time.sleep(CONFIG['retry_delay'])
            else:
                logger.error("All call attempts failed")
                print("--> All call attempts failed")
    
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

def run_enhanced_procurement_workflow():
    """
    Enhanced procurement workflow with better decision making and error handling
    """
    pm = ProcurementManager()
    requirements = []
    
    try:
        # Step 1: Enhanced Inventory Check
        narrate_step(f"Starting comprehensive inventory check for {CONFIG['company_name']}.")
        
        for item_name, item in inventory_items.items():
            narrate_step(f"Checking stock for {item_name}. Current quantity: {item.quantity}, Minimum threshold: {item.min_threshold}")
            
            if item.quantity <= item.min_threshold:
                requirements.append(item_name)
                shortage = item.min_threshold - item.quantity
                narrate_step(f"{item_name} is below minimum threshold by {shortage} units. Adding to procurement list.")
            else:
                narrate_step(f"{item_name} stock levels are adequate. No action required.")
        
        if not requirements:
            narrate_step("All inventory levels are sufficient. No procurement needed.")
            return
        
        # Step 2: Enhanced Vendor Selection
        narrate_step(f"Analyzing {len(requirements)} items requiring procurement: {', '.join(requirements)}")
        narrate_step("Evaluating vendors based on price, rating, delivery time, and payment terms.")
        
        # Calculate scores for all vendors
        vendor_scores = {}
        for vendor_name, vendor in vendor_data.items():
            score = get_vendor_score(vendor, requirements)
            total_cost = calculate_total_cost(requirements, vendor)
            vendor_scores[vendor_name] = {
                'vendor': vendor,
                'score': score,
                'total_cost': total_cost
            }
            
            narrate_step(f"{vendor_name}: Total cost ₹{total_cost:.2f}, Rating {vendor.rating}/5, "
                        f"Delivery {vendor.delivery_time} days, Score {score:.3f}")
        
        # Select best vendor
        best_vendor_name = max(vendor_scores.keys(), key=lambda x: vendor_scores[x]['score'])
        best_vendor = vendor_scores[best_vendor_name]['vendor']
        total_cost = vendor_scores[best_vendor_name]['total_cost']
        
        narrate_step(f"Selected vendor: {best_vendor_name} with the highest overall score of "
                    f"{vendor_scores[best_vendor_name]['score']:.3f}")
        
        # Step 3: Approval Check
        if total_cost > CONFIG['auto_approve_threshold']:
            narrate_step(f"Order value ₹{total_cost:.2f} exceeds auto-approval threshold. "
                        f"Manual approval required.")
            # In a real system, this would trigger an approval workflow
            
        # Step 4: Execute Order
        narrate_step(f"Proceeding with order placement to {best_vendor_name}")
        
        # Make phone call
        call_sid = make_phone_call_with_retry(best_vendor, requirements)
        
        # Send email notification
        email_sent = send_email_notification(best_vendor, requirements, total_cost)
        
        # Step 5: Record Transaction
        record = ProcurementRecord(
            timestamp=datetime.datetime.now().isoformat(),
            items_required=requirements,
            selected_vendor=best_vendor_name,
            total_cost=total_cost,
            status="Completed" if (call_sid or email_sent) else "Failed",
            call_sid=call_sid,
            email_sent=email_sent
        )
        
        pm.procurement_history.append(record)
        pm.save_data()
        
        # Step 6: Summary
        narrate_step("Procurement workflow completed successfully!")
        print(f"\n{'='*60}")
        print("PROCUREMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Items Procured: {', '.join(requirements)}")
        print(f"Selected Vendor: {best_vendor_name}")
        print(f"Total Cost: ₹{total_cost:.2f}")
        print(f"Expected Delivery: {best_vendor.delivery_time} days")
        print(f"Call Status: {'Success' if call_sid else 'Failed/Simulated'}")
        print(f"Email Status: {'Sent' if email_sent else 'Failed/Not Configured'}")
        print(f"{'='*60}")
        
        # Export report
        pm.export_to_csv()
        
    except Exception as e:
        logger.error(f"Procurement workflow failed: {e}")
        narrate_step(f"Procurement workflow encountered an error: {str(e)}")


def run_procurement_workflow():
    """
    Legacy workflow for backward compatibility
    """
    print("Running legacy procurement workflow...")
    run_enhanced_procurement_workflow()


def interactive_mode():
    """
    Interactive mode for manual control
    """
    print("\n=== INTERACTIVE PROCUREMENT SYSTEM ===")
    print("1. Run Full Procurement Workflow")
    print("2. Check Inventory Status")
    print("3. View Vendor Information")
    print("4. View Procurement History")
    print("5. Export Data to CSV")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            run_enhanced_procurement_workflow()
        elif choice == '2':
            show_inventory_status()
        elif choice == '3':
            show_vendor_info()
        elif choice == '4':
            show_procurement_history()
        elif choice == '5':
            pm = ProcurementManager()
            pm.export_to_csv()
            print("Data exported to procurement_report.csv")
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


def show_inventory_status():
    """Display current inventory status"""
    print("\n=== INVENTORY STATUS ===")
    for item_name, item in inventory_items.items():
        status_color = "🔴" if item.quantity == 0 else "🟡" if item.quantity <= item.min_threshold else "🟢"
        print(f"{status_color} {item_name}: {item.quantity} units "
              f"(Min: {item.min_threshold}, Reorder: {item.reorder_quantity})")


def show_vendor_info():
    """Display vendor information"""
    print("\n=== VENDOR INFORMATION ===")
    for vendor_name, vendor in vendor_data.items():
        print(f"\n{vendor_name.upper()}:")
        print(f"  Price: ₹{vendor.price}")
        print(f"  Rating: {vendor.rating}/5")
        print(f"  Delivery: {vendor.delivery_time} days")
        print(f"  Payment Terms: {vendor.payment_terms}")
        print(f"  Contact: {vendor.phone}")
        print(f"  Email: {vendor.email}")


def show_procurement_history():
    """Display procurement history"""
    pm = ProcurementManager()
    if not pm.procurement_history:
        print("No procurement history found.")
        return
    
    print("\n=== PROCUREMENT HISTORY ===")
    for i, record in enumerate(pm.procurement_history[-5:], 1):  # Show last 5 records
        print(f"\n{i}. {record.timestamp}")
        print(f"   Items: {', '.join(record.items_required)}")
        print(f"   Vendor: {record.selected_vendor}")
        print(f"   Cost: ₹{record.total_cost:.2f}")
        print(f"   Status: {record.status}")


# ==============================================================================
# --- 6. MAIN EXECUTION ---
# ==============================================================================

def main():
    """Main function with command line options"""
    import sys
    
    print(f"🏢 {CONFIG['company_name']} - Enhanced Procurement Automation System")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'interactive':
            interactive_mode()
        elif mode == 'legacy':
            run_procurement_workflow()
        elif mode == 'status':
            show_inventory_status()
        elif mode == 'vendors':
            show_vendor_info()
        elif mode == 'history':
            show_procurement_history()
        elif mode == 'test-call':
            print("🧪 Testing Twilio Phone Call Functionality")
            print("-" * 50)
            test_simple_twilio_call()
        else:
            print("Usage: python caller.py [interactive|legacy|status|vendors|history|test-call]")
            print("\nAvailable modes:")
            print("  interactive  - Interactive menu system")
            print("  legacy       - Original workflow")
            print("  status       - Show inventory status")
            print("  vendors      - Show vendor information")
            print("  history      - Show procurement history")
            print("  test-call    - Test phone call functionality")
    else:
        # Default: run enhanced workflow
        run_enhanced_procurement_workflow()


if __name__ == "__main__":
    main()