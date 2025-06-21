#!/usr/bin/env python3
"""
Voice-Enabled Procurement Demo Script
====================================

This script demonstrates the new voice-enabled procurement workflow:
- Calls vendors and asks them to speak their quotes
- Uses speech recognition to capture pricing in real-time
- Updates CSV files with actual vendor quotes
- Compares all quotes and selects the cheapest

Usage:
    python demo_voice_procurement.py

Features:
- Interactive voice quote collection
- Real-time speech-to-text processing
- Automatic CSV updates with live pricing
- Intelligent quote parsing and comparison
"""

import sys
import os
from pathlib import Path

# Add the main directory to path so we can import caller
sys.path.insert(0, str(Path(__file__).parent))

from caller import (
    run_two_phase_procurement_workflow,
    make_interactive_quote_call,
    test_interactive_quote_call,
    show_csv_inventory_status,
    show_csv_vendor_info,
    test_simple_twilio_call,
    CONFIG,
    csv_inventory,
    csv_vendors,
    csv_vendor_mapping,
    SPEECH_RECOGNITION_AVAILABLE,
    AUDIO_PROCESSING_AVAILABLE
)

def demo_voice_features():
    """Display overview of voice-enabled features"""
    print("=" * 80)
    print("🎤 VOICE-ENABLED PROCUREMENT AUTOMATION SYSTEM")
    print("=" * 80)
    print()
    print("🗣️  VOICE FEATURES:")
    print("   ├── Real-time Quote Collection")
    print("   ├── Speech Recognition & Processing")
    print("   ├── Automatic Price Parsing")
    print("   ├── Live CSV Updates")
    print("   └── Intelligent Quote Comparison")
    print()
    print("📞 CALL WORKFLOW:")
    print("   Phase 1: Interactive Quote Calls")
    print("   ├── 1. Call vendor with TwiML")
    print("   ├── 2. Ask vendor to speak quotes")
    print("   ├── 3. Record vendor response")
    print("   ├── 4. Process speech to text")
    print("   ├── 5. Parse prices from speech")
    print("   └── 6. Update CSV in real-time")
    print()
    print("   Phase 2: Automated Comparison")
    print("   ├── 7. Compare all voice quotes")
    print("   ├── 8. Select cheapest vendor")
    print("   ├── 9. Call winner with order")
    print("   └── 10. Generate comprehensive report")
    print()
    print("🔧 SYSTEM CAPABILITIES:")
    speech_status = "✅ Available" if SPEECH_RECOGNITION_AVAILABLE else "❌ Not Available"
    audio_status = "✅ Available" if AUDIO_PROCESSING_AVAILABLE else "❌ Not Available"
    print(f"   Speech Recognition: {speech_status}")
    print(f"   Audio Processing: {audio_status}")
    print("=" * 80)
    print()

def show_voice_system_status():
    """Show current voice system status"""
    print("🎤 VOICE SYSTEM STATUS:")
    print("-" * 40)
    
    # Check dependencies
    if SPEECH_RECOGNITION_AVAILABLE:
        print("✅ Speech Recognition: Ready")
    else:
        print("❌ Speech Recognition: Install 'pip install SpeechRecognition'")
    
    if AUDIO_PROCESSING_AVAILABLE:
        print("✅ Audio Processing: Ready")
    else:
        print("❌ Audio Processing: Install 'pip install pydub'")
    
    print()
    
    # Count callable vendors
    callable_vendors = [v for v in csv_vendors.values() 
                       if v['status'] == 'Active' and 'CALLS BLOCKED' not in v['notes']]
    
    print(f"📞 Callable vendors for voice quotes: {len(callable_vendors)}")
    if callable_vendors:
        print("   Available for voice quote collection:")
        for vendor in callable_vendors:
            print(f"   • {vendor['name']}")
    
    print()
    
    # Show items needing procurement
    items_below_threshold = [item_id for item_id, item_info in csv_inventory.items()
                           if item_info['current_stock'] <= item_info['min_threshold']]
    
    if items_below_threshold:
        print("🚨 ITEMS FOR VOICE QUOTE COLLECTION:")
        for item_id in items_below_threshold[:5]:  # Show first 5
            item_info = csv_inventory[item_id]
            print(f"   • {item_info['name']}: {item_info['current_stock']} units "
                  f"(need {item_info['min_threshold'] - item_info['current_stock']} more)")
    else:
        print("✅ All inventory levels adequate")
    
    print()

def demo_voice_quote_parsing():
    """Demonstrate voice quote parsing capabilities"""
    print("🧠 VOICE QUOTE PARSING DEMO:")
    print("-" * 40)
    
    # Sample transcriptions to test parsing
    sample_transcriptions = [
        "USB cables 12 rupees per unit, wireless mouse 28 rupees each",
        "HDMI adapters cost 22 rupees, ethernet cables 9 rupees per piece",
        "Power banks are 35 rupees each, laptop stands 48 rupees per unit",
        "12.50 for USB cables, 25.75 for mouse, 18.25 for adapters"
    ]
    
    from caller import parse_spoken_quote
    
    test_items = ['I001', 'I002', 'I003', 'I004', 'I005']
    
    for i, transcript in enumerate(sample_transcriptions, 1):
        print(f"\nExample {i}:")
        print(f"   Transcript: \"{transcript}\"")
        
        parsed = parse_spoken_quote(transcript, test_items)
        if parsed:
            print("   Parsed quotes:")
            for item_id, price in parsed.items():
                item_name = csv_inventory.get(item_id, {}).get('name', item_id)
                print(f"     • {item_name}: ₹{price}")
        else:
            print("   ❌ No quotes parsed")
    
    print()

def voice_demo_menu():
    """Interactive voice demo menu"""
    while True:
        print("\n🎤 VOICE PROCUREMENT DEMO:")
        print("1. Show Voice System Overview")
        print("2. Check Voice System Status")
        print("3. Demo Voice Quote Parsing")
        print("4. Test Interactive Voice Quote Call")
        print("5. Run Complete Voice-Enabled Workflow")
        print("6. Test Twilio Connection")
        print("7. Exit Demo")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            demo_voice_features()
            show_voice_system_status()
        elif choice == '2':
            show_voice_system_status()
        elif choice == '3':
            demo_voice_quote_parsing()
        elif choice == '4':
            print("\n📞 TESTING VOICE QUOTE COLLECTION...")
            print("-" * 50)
            test_interactive_quote_call()
        elif choice == '5':
            print("\n🚀 STARTING VOICE-ENABLED PROCUREMENT WORKFLOW...")
            print("=" * 70)
            run_two_phase_procurement_workflow()
        elif choice == '6':
            print("\n📞 TESTING TWILIO CONNECTION...")
            print("-" * 40)
            test_simple_twilio_call()
        elif choice == '7':
            print("\n👋 Voice demo completed. Thank you!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main voice demo function"""
    print()
    demo_voice_features()
    show_voice_system_status()
    
    # Check system readiness
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("⚠️  WARNING: Speech recognition not available!")
        print("   Install with: pip install SpeechRecognition")
        print("   Voice quote collection will use fallback pricing")
        print()
    
    # Check if we should run automatically or interactively
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'auto':
        print("🚀 RUNNING AUTOMATIC VOICE-ENABLED WORKFLOW...")
        print("=" * 70)
        run_two_phase_procurement_workflow()
    else:
        voice_demo_menu()

if __name__ == "__main__":
    main()
