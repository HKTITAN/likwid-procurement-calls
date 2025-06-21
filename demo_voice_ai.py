#!/usr/bin/env python3
"""
Twilio Voice AI ConversationRelay Demo
Demonstrates intelligent procurement calls with AI-driven quote collection
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def print_header():
    """Print demo header"""
    print("=" * 80)
    print("🤖 TWILIO VOICE AI CONVERSATIONRELAY DEMO")
    print("   Intelligent Procurement Quote Collection")
    print("=" * 80)
    print()

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    
    # Check if webhook server file exists
    if not Path("voice_ai_webhook_server.py").exists():
        print("❌ voice_ai_webhook_server.py not found")
        return False
    
    # Check if caller.py exists
    if not Path("caller.py").exists():
        print("❌ caller.py not found")
        return False
        
    # Check if CSV data files exist
    data_files = ['data/inventory.csv', 'data/vendors.csv', 'data/vendor_items_mapping.csv']
    for file_path in data_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found")
            return False
    
    print("✅ All prerequisite files found")
    return True

def start_webhook_server():
    """Start the webhook server in a separate process"""
    print("🚀 Starting Voice AI Webhook Server...")
    
    try:
        # Start the webhook server
        process = subprocess.Popen(
            [sys.executable, "voice_ai_webhook_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ Webhook server started successfully!")
            print("   Server URL: http://localhost:5000")
            print("   Webhook endpoint: http://localhost:5000/voice-ai-webhook")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Failed to start webhook server")
            print(f"   Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting webhook server: {e}")
        return None

def demonstrate_voice_ai_config():
    """Demonstrate Voice AI configuration"""
    print("\n📋 VOICE AI CONFIGURATION DEMO")
    print("-" * 50)
    
    # Import the caller module
    try:
        sys.path.insert(0, '.')
        import caller
        
        # Show sample Voice AI configuration
        sample_items = ['item1', 'item2']
        sample_quantities = {'item1': 100, 'item2': 50}
        
        config = caller.create_voice_ai_conversation_config(sample_items, sample_quantities)
        
        print("🤖 Voice AI ConversationRelay Configuration:")
        print(f"   Welcome Greeting: {config['conversationRelay']['welcomeGreeting'][:100]}...")
        print(f"   Voice: {config['conversationRelay']['voice']['name']}")
        print(f"   Language: {config['conversationRelay']['voice']['language']}")
        print(f"   Timeout: {config['conversationRelay']['config']['timeoutMs']}ms")
        print(f"   Max Turns: {config['conversationRelay']['config']['maxTurns']}")
        print(f"   Functions Available: {len(config['conversationRelay']['tools'])}")
        
        for i, tool in enumerate(config['conversationRelay']['tools'], 1):
            print(f"      {i}. {tool['function']['name']}: {tool['function']['description']}")
        
        print("✅ Voice AI configuration ready!")
        
    except Exception as e:
        print(f"❌ Error demonstrating config: {e}")

def demonstrate_twiml_generation():
    """Demonstrate TwiML generation for ConversationRelay"""
    print("\n📞 TWIML GENERATION DEMO")
    print("-" * 50)
    
    try:
        import caller
        
        # Create sample config
        sample_items = ['item1']
        sample_quantities = {'item1': 50}
        config = caller.create_voice_ai_conversation_config(sample_items, sample_quantities)
        
        # Generate TwiML
        twiml = caller.create_voice_ai_twiml(config)
        
        print("📄 Generated TwiML for ConversationRelay:")
        print(twiml[:500] + "..." if len(twiml) > 500 else twiml)
        print("✅ TwiML generation successful!")
        
    except Exception as e:
        print(f"❌ Error generating TwiML: {e}")

def demonstrate_conversation_monitoring():
    """Demonstrate conversation monitoring"""
    print("\n👁️ CONVERSATION MONITORING DEMO")
    print("-" * 50)
    
    try:
        import requests
        
        # Test webhook server health
        print("🏥 Testing webhook server health...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Webhook server is healthy!")
            print(f"   Status: {health_data['status']}")
            print(f"   Active conversations: {health_data['active_conversations']}")
            print(f"   Timestamp: {health_data['timestamp']}")
        else:
            print(f"⚠️ Webhook server responded with status: {response.status_code}")
            
        # Simulate conversation status check
        print("\n🔍 Simulating conversation status check...")
        mock_call_sid = "CA1234567890abcdef1234567890abcdef"
        status_response = requests.get(f"http://localhost:5000/conversation-status/{mock_call_sid}")
        
        if status_response.status_code == 404:
            print("✅ Correctly handles non-existent conversations")
        else:
            print(f"   Status response: {status_response.status_code}")
        
    except requests.RequestException as e:
        print(f"❌ Error testing webhook server: {e}")
        print("   Make sure the webhook server is running")

def simulate_ai_conversation():
    """Simulate an AI conversation flow"""
    print("\n🎭 AI CONVERSATION SIMULATION")
    print("-" * 50)
    
    print("🤖 Simulating AI agent conversation:")
    print("   AI: Namaste! This is Bio Mac Lifesciences procurement team...")
    print("   Vendor: Hello, yes I can provide quotes.")
    print("   AI: What is your per-unit price for 100 units of Steel Rods?")
    print("   Vendor: Our price is 250 rupees per unit.")
    print("   AI: Let me confirm - you quoted 250 rupees per unit for Steel Rods. Is that correct?")
    print("   Vendor: Yes, that's correct.")
    print("   AI: 📝 [Function Call: record_item_quote]")
    print("       - item_name: Steel Rods")
    print("       - unit_price: 250")
    print("       - quantity: 100")
    print("       - confirmed: true")
    print("   AI: Thank you! Now, what is your per-unit price for 50 units of Cement Bags?")
    print("   Vendor: 180 rupees per bag.")
    print("   AI: Let me confirm - you quoted 180 rupees per unit for Cement Bags. Is that correct?")
    print("   Vendor: Yes, confirmed.")
    print("   AI: 📝 [Function Call: record_item_quote]")
    print("   AI: Perfect! That completes all our items.")
    print("   AI: 🏁 [Function Call: complete_quote_collection]")
    print("       - total_items_quoted: 2")
    print("       - summary: Steel Rods: ₹250/unit, Cement Bags: ₹180/unit")
    print("   AI: Thank you for providing quotes. Total would be ₹34,000. We'll be in touch!")
    
    print("\n✅ AI conversation simulation complete!")
    print("   Real conversations would be processed by the webhook server")

def run_procurement_demo():
    """Run a procurement demo using the Voice AI system"""
    print("\n🏭 PROCUREMENT WORKFLOW DEMO")
    print("-" * 50)
    
    try:
        import caller
        
        print("📊 Loading procurement system...")
        print(f"   Inventory items: {len(caller.csv_inventory)}")
        print(f"   Vendors: {len(caller.csv_vendors)}")
        print(f"   Vendor mappings: {len(caller.csv_vendor_mapping)}")
        
        # Show some sample data
        if caller.csv_inventory:
            print("\n📦 Sample inventory items:")
            for i, (item_id, item_data) in enumerate(list(caller.csv_inventory.items())[:3]):
                print(f"   {i+1}. {item_data['name']}: {item_data['quantity']} units")
        
        if caller.csv_vendors:
            print("\n🏢 Sample vendors:")
            for i, (vendor_id, vendor_data) in enumerate(list(caller.csv_vendors.items())[:3]):
                callable_status = "📞" if vendor_data.get('can_call', False) else "❌"
                print(f"   {i+1}. {vendor_data['name']} {callable_status}")
        
        # Simulate Voice AI workflow selection
        print("\n🤖 Voice AI workflow would:")
        print("   1. Analyze inventory and identify items to reorder")
        print("   2. Find callable vendors for each item")
        print("   3. Generate AI conversation configuration")
        print("   4. Make ConversationRelay calls to vendors")
        print("   5. Monitor AI conversations via webhooks")
        print("   6. Collect and process quote data")
        print("   7. Compare quotes and select best vendor")
        print("   8. Generate procurement report")
        
        print("\n✅ Procurement demo complete!")
        
    except Exception as e:
        print(f"❌ Error in procurement demo: {e}")

def show_integration_steps():
    """Show next steps for full integration"""
    print("\n🔗 INTEGRATION STEPS")
    print("-" * 50)
    
    steps = [
        "1. Deploy webhook server to a public URL (ngrok, Heroku, AWS, etc.)",
        "2. Update webhook URL in voice_ai_conversation_config",
        "3. Configure Twilio account with ConversationRelay features",
        "4. Set up proper Twilio credentials in .env file",
        "5. Configure allowed phone numbers for security",
        "6. Test with real phone calls to your allowed number",
        "7. Monitor conversations and quote collection",
        "8. Integrate with your existing procurement workflow"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n🔧 Configuration needed:")
    print("   - Twilio Account SID and Auth Token")
    print("   - Twilio Phone Number with Voice capabilities")
    print("   - ConversationRelay enabled on your Twilio account")
    print("   - Public webhook URL (use ngrok for testing)")
    print("   - Proper .env file with all credentials")

def cleanup_demo():
    """Clean up demo resources"""
    print("\n🧹 Demo completed!")
    print("   Webhook server is still running for testing")
    print("   Press Ctrl+C to stop the webhook server")
    print("   All demo data is preserved")

def main():
    """Main demo function"""
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please ensure all files are present.")
        return
    
    # Start webhook server
    webhook_process = start_webhook_server()
    if not webhook_process:
        print("❌ Cannot continue without webhook server")
        return
    
    try:
        # Run demo sections
        demonstrate_voice_ai_config()
        demonstrate_twiml_generation()
        demonstrate_conversation_monitoring()
        simulate_ai_conversation()
        run_procurement_demo()
        show_integration_steps()
        cleanup_demo()
        
        print("\n🎉 VOICE AI CONVERSATIONRELAY DEMO COMPLETE!")
        print("   The system is ready for Twilio Voice AI integration")
        print("   Webhook server will continue running...")
        
        # Keep the webhook server running
        print("\nPress Ctrl+C to stop the webhook server and exit")
        webhook_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
        if webhook_process:
            webhook_process.terminate()
            print("   Webhook server stopped")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        if webhook_process:
            webhook_process.terminate()
    finally:
        if webhook_process and webhook_process.poll() is None:
            webhook_process.terminate()

if __name__ == "__main__":
    main()
