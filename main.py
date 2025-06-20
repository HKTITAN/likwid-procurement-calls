#!/usr/bin/env python3
"""
Organized Procurement Automation System
Main entry point for the restructured codebase
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import ProcurementConfig
from src.procurement_engine import ProcurementEngine
from src.data_manager import DataManager

# Load environment variables
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

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'procurement_system.log'),
            logging.StreamHandler()
        ]
    )

def create_config() -> ProcurementConfig:
    """Create configuration from environment variables"""
    return ProcurementConfig(
        company_name=os.environ.get("COMPANY_NAME", "Bio Mac Lifesciences"),
        procurement_email=os.environ.get("PROCUREMENT_EMAIL", "procurement@org1.com"),
        auto_approve_threshold=float(os.environ.get("AUTO_APPROVE_THRESHOLD", "1000.0")),
        max_retries=int(os.environ.get("MAX_RETRIES", "3")),
        retry_delay=int(os.environ.get("RETRY_DELAY", "5")),
        allowed_phone_number=os.environ.get("ALLOWED_PHONE_NUMBER", "+918800000488"),
        
        # Twilio settings
        twilio_account_sid=os.environ.get("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.environ.get("TWILIO_AUTH_TOKEN", ""),
        twilio_phone_number=os.environ.get("TWILIO_PHONE_NUMBER", ""),
        
        # Email settings
        smtp_server=os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.environ.get("SMTP_PORT", "587"))
    )

def show_system_status(engine: ProcurementEngine):
    """Display system status and statistics"""
    print("=" * 70)
    print("PROCUREMENT SYSTEM STATUS")
    print("=" * 70)
    
    status = engine.get_system_status()
    
    print(f"🏢 Company: {engine.config.company_name}")
    print(f"📞 Authorized Phone: {engine.config.allowed_phone_number}")
    print(f"📧 Procurement Email: {engine.config.procurement_email}")
    print()
    
    print("📊 SYSTEM STATISTICS:")
    print(f"   Total Vendors: {status['total_vendors']}")
    print(f"   Authorized Vendors: {status['authorized_vendors']}")
    print(f"   Total Items: {status['total_items']}")
    print(f"   Items Needing Reorder: {status['items_needing_reorder']}")
    print(f"   Vendor-Item Mappings: {status['total_vendor_item_mappings']}")
    print(f"   Procurement Records: {status['total_procurement_records']}")
    print()
    
    twilio_status = "✅ READY" if status['twilio_configured'] else "❌ NOT CONFIGURED"
    print(f"📱 Twilio Status: {twilio_status}")
    
    if status['items_needing_reorder'] > 0:
        print(f"⚠️  {status['items_needing_reorder']} items need reordering!")
    else:
        print("✅ All inventory levels are adequate")

def show_inventory_status(engine: ProcurementEngine):
    """Show detailed inventory status"""
    print("\n📦 DETAILED INVENTORY STATUS:")
    print("-" * 50)
    
    items_needing_reorder = engine.data_manager.get_items_needing_reorder()
    
    for item in engine.data_manager.inventory.values():
        status_icon = "🔴" if item.needs_reorder else "✅"
        criticality = "⚡" if item.criticality == "High" else "🔹" if item.criticality == "Medium" else "🔸"
        
        print(f"{status_icon} {criticality} {item.item_name}")
        print(f"    Stock: {item.current_stock} {item.unit} (Min: {item.min_threshold})")
        print(f"    Category: {item.category} > {item.subcategory}")
        print(f"    Preferred Vendor: {item.preferred_vendor_id}")
        print()

def show_vendor_status(engine: ProcurementEngine):
    """Show vendor status and capabilities"""
    print("\n🏢 VENDOR STATUS:")
    print("-" * 40)
    
    for vendor in engine.data_manager.vendors.values():
        call_status = "✅ AUTHORIZED" if vendor.is_authorized_for_calls else "🚫 BLOCKED"
        
        print(f"📍 {vendor.vendor_name} ({vendor.vendor_id})")
        print(f"    Contact: {vendor.contact_person} - {vendor.phone_number}")
        print(f"    Call Status: {call_status}")
        print(f"    Rating: ⭐{vendor.rating}/5.0")
        print(f"    Delivery: {vendor.delivery_time_days} days")
        print(f"    Payment: {vendor.payment_terms}")
        print(f"    Minimum Order: ${vendor.minimum_order_value:,.2f}")
        print()

def run_test_call(engine: ProcurementEngine):
    """Run a test call"""
    if not engine.twilio_manager:
        print("❌ Twilio not configured. Cannot make test call.")
        return
    
    print("\n📞 MAKING TEST CALL...")
    print("-" * 25)
    
    call_sid = engine.twilio_manager.make_test_call(engine.config.company_name)
    
    if call_sid and call_sid != "blocked_unauthorized_number":
        print(f"✅ Test call successful!")
        print(f"   Call SID: {call_sid}")
        print(f"   Called: {engine.config.allowed_phone_number}")
    else:
        print("❌ Test call failed")

def run_full_procurement_cycle(engine: ProcurementEngine):
    """Run the complete procurement automation cycle"""
    print("\n🚀 RUNNING FULL PROCUREMENT CYCLE")
    print("=" * 50)
    
    result = engine.run_full_procurement_cycle()
    
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    print(f"Items Processed: {result['items_processed']}")
    print(f"Orders Created: {result['orders_created']}")
    print(f"Calls Made: {result['calls_made']}")
    
    if result.get('total_cost'):
        print(f"Total Cost: ${result['total_cost']:,.2f}")
    
    if result.get('records'):
        print("\n📋 PROCUREMENT RECORDS CREATED:")
        for record in result['records']:
            print(f"   Order {record.order_number}: {record.selected_vendor_name}")
            print(f"   Items: {', '.join(record.items_required)}")
            print(f"   Cost: ${record.total_cost:,.2f}")
            print(f"   Status: {record.status}")
            if record.call_sid:
                print(f"   Call SID: {record.call_sid}")
            print()

def interactive_menu(engine: ProcurementEngine):
    """Run interactive menu"""
    while True:
        print("\n" + "=" * 70)
        print("ORGANIZED PROCUREMENT AUTOMATION SYSTEM")
        print("=" * 70)
        print("1. Show System Status")
        print("2. Show Inventory Status")
        print("3. Show Vendor Status")
        print("4. Run Test Call")
        print("5. Run Full Procurement Cycle")
        print("6. Export Data to CSV")
        print("7. Exit")
        print("-" * 30)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            show_system_status(engine)
        
        elif choice == "2":
            show_inventory_status(engine)
        
        elif choice == "3":
            show_vendor_status(engine)
        
        elif choice == "4":
            run_test_call(engine)
        
        elif choice == "5":
            run_full_procurement_cycle(engine)
        
        elif choice == "6":
            engine.data_manager.export_to_csv()
            print("✅ Data exported to CSV successfully!")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main entry point"""
    print("🏭 ORGANIZED PROCUREMENT AUTOMATION SYSTEM")
    print("Loading configuration and data...")
    
    # Setup
    setup_logging()
    config = create_config()
    
    # Initialize system
    try:
        engine = ProcurementEngine(config)
        logging.info("Procurement system initialized successfully")
        
        # Show initial status
        show_system_status(engine)
        
        # Run interactive menu
        interactive_menu(engine)
        
    except Exception as e:
        logging.error(f"Failed to initialize system: {e}")
        print(f"❌ System initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
