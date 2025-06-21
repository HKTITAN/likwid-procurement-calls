#!/usr/bin/env python3
"""
Simple test of voice procurement system
"""

try:
    from caller import csv_vendors, csv_inventory
    print("✅ Successfully loaded CSV data")
    print(f"📦 {len(csv_inventory)} inventory items loaded")
    print(f"🏢 {len(csv_vendors)} vendors loaded")
    
    # Test voice parsing
    from caller import parse_spoken_quote
    test_transcript = "USB cables 12 rupees, mouse 25 rupees"
    test_items = ['I001', 'I002']
    result = parse_spoken_quote(test_transcript, test_items)
    print(f"🎤 Voice parsing test: {result}")
    
    print("✅ Voice procurement system ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
