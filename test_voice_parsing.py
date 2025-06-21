#!/usr/bin/env python3
"""
Test voice quote parsing functionality
"""

from caller import parse_spoken_quote, csv_inventory

def test_voice_parsing():
    print("🧠 TESTING VOICE QUOTE PARSING")
    print("=" * 50)
    
    # Sample transcriptions to test parsing
    test_cases = [
        "USB cables 12 rupees per unit, wireless mouse 28 rupees each",
        "HDMI adapters cost 22 rupees, ethernet cables 9 rupees per piece", 
        "Power banks are 35 rupees each, laptop stands 48 rupees per unit",
        "12.50 for USB cables, 25.75 for mouse, 18.25 for adapters",
        "The USB cables will be 15 rupees, mouse 30 rupees, HDMI 25 rupees"
    ]
    
    test_items = ['I001', 'I002', 'I003', 'I004', 'I005']
    
    for i, transcript in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"   📝 Transcript: \"{transcript}\"")
        
        parsed = parse_spoken_quote(transcript, test_items)
        if parsed:
            print("   ✅ Parsed quotes:")
            for item_id, price in parsed.items():
                item_name = csv_inventory.get(item_id, {}).get('name', item_id)
                print(f"      • {item_name}: ₹{price}")
        else:
            print("   ❌ No quotes parsed")
    
    print(f"\n✅ Voice quote parsing test completed!")

if __name__ == "__main__":
    test_voice_parsing()
