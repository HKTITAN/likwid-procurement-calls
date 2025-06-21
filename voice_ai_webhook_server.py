#!/usr/bin/env python3
"""
Twilio Voice AI Webhook Server for ConversationRelay
Handles AI function calls for intelligent quote collection
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_ai_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global storage for conversation states
conversation_states = {}
collected_quotes = {}

@dataclass
class ItemQuote:
    item_name: str
    unit_price: float
    quantity: int
    confirmed: bool
    timestamp: str

@dataclass
class ConversationState:
    call_sid: str
    vendor_id: str
    items_to_quote: List[Dict]
    quoted_items: Dict[str, ItemQuote]
    current_item_index: int
    conversation_complete: bool
    started_at: str


def initialize_database():
    """Initialize SQLite database for storing conversation data"""
    conn = sqlite3.connect('voice_ai_quotes.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            call_sid TEXT PRIMARY KEY,
            vendor_id TEXT,
            started_at TEXT,
            completed_at TEXT,
            status TEXT,
            total_items INTEGER,
            quoted_items INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT,
            item_name TEXT,
            unit_price REAL,
            quantity INTEGER,
            confirmed BOOLEAN,
            timestamp TEXT,
            FOREIGN KEY (call_sid) REFERENCES conversations (call_sid)
        )
    ''')
    
    conn.commit()
    conn.close()


def save_conversation_to_db(conversation: ConversationState):
    """Save conversation state to database"""
    conn = sqlite3.connect('voice_ai_quotes.db')
    cursor = conn.cursor()
    
    # Insert or update conversation
    cursor.execute('''
        INSERT OR REPLACE INTO conversations 
        (call_sid, vendor_id, started_at, status, total_items, quoted_items)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        conversation.call_sid,
        conversation.vendor_id,
        conversation.started_at,
        'active' if not conversation.conversation_complete else 'completed',
        len(conversation.items_to_quote),
        len(conversation.quoted_items)
    ))
    
    # Insert quotes
    for item_name, quote in conversation.quoted_items.items():
        cursor.execute('''
            INSERT OR REPLACE INTO item_quotes 
            (call_sid, item_name, unit_price, quantity, confirmed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            conversation.call_sid,
            quote.item_name,
            quote.unit_price,
            quote.quantity,
            quote.confirmed,
            quote.timestamp
        ))
    
    conn.commit()
    conn.close()


@app.route('/voice-ai-webhook', methods=['POST'])
def handle_voice_ai_webhook():
    """Main webhook endpoint for Twilio Voice AI ConversationRelay"""
    
    try:
        # Parse incoming request
        data = request.get_json()
        if not data:
            logger.error("No JSON data received in webhook")
            return jsonify({"error": "No data received"}), 400
        
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # Extract call information
        call_sid = data.get('CallSid')
        event_type = data.get('EventType', 'function_call')
        
        if not call_sid:
            logger.error("No CallSid in webhook data")
            return jsonify({"error": "CallSid required"}), 400
        
        # Handle different event types
        if event_type == 'conversation_start':
            return handle_conversation_start(data)
        elif event_type == 'function_call':
            return handle_function_call(data)
        elif event_type == 'conversation_end':
            return handle_conversation_end(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return jsonify({"message": "Event processed"}), 200
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


def handle_conversation_start(data: dict) -> tuple:
    """Handle conversation start event"""
    call_sid = data.get('CallSid')
    
    # Initialize conversation state (this would typically come from your main system)
    # For now, we'll create a mock state
    conversation = ConversationState(
        call_sid=call_sid,
        vendor_id=data.get('vendor_id', 'unknown'),
        items_to_quote=[
            {"item_name": "Steel Rods", "quantity": 100},
            {"item_name": "Cement Bags", "quantity": 50},
            {"item_name": "Bricks", "quantity": 1000}
        ],
        quoted_items={},
        current_item_index=0,
        conversation_complete=False,
        started_at=datetime.now().isoformat()
    )
    
    conversation_states[call_sid] = conversation
    save_conversation_to_db(conversation)
    
    logger.info(f"Started conversation for call {call_sid}")
    
    return jsonify({
        "message": "Conversation started",
        "call_sid": call_sid,
        "items_to_quote": len(conversation.items_to_quote)
    }), 200


def handle_function_call(data: dict) -> tuple:
    """Handle AI function calls for quote recording"""
    call_sid = data.get('CallSid')
    function_name = data.get('function_name')
    function_args = data.get('function_arguments', {})
    
    if call_sid not in conversation_states:
        logger.error(f"No conversation state found for call {call_sid}")
        return jsonify({"error": "Conversation not found"}), 404
    
    conversation = conversation_states[call_sid]
    
    if function_name == 'record_item_quote':
        return handle_record_item_quote(conversation, function_args)
    elif function_name == 'complete_quote_collection':
        return handle_complete_quote_collection(conversation, function_args)
    else:
        logger.warning(f"Unknown function: {function_name}")
        return jsonify({"error": f"Unknown function: {function_name}"}), 400


def handle_record_item_quote(conversation: ConversationState, args: dict) -> tuple:
    """Handle recording of individual item quotes"""
    try:
        item_name = args.get('item_name')
        unit_price = float(args.get('unit_price', 0))
        quantity = int(args.get('quantity', 0))
        confirmed = bool(args.get('confirmed', False))
        
        if not all([item_name, unit_price > 0, quantity > 0]):
            return jsonify({
                "error": "Invalid quote data",
                "message": "Please provide valid item name, price, and quantity"
            }), 400
        
        # Create quote record
        quote = ItemQuote(
            item_name=item_name,
            unit_price=unit_price,
            quantity=quantity,
            confirmed=confirmed,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the quote
        conversation.quoted_items[item_name] = quote
        
        # Update conversation state
        conversation.current_item_index += 1
        
        # Save to database
        save_conversation_to_db(conversation)
        
        logger.info(f"Recorded quote: {item_name} @ ₹{unit_price} per unit (confirmed: {confirmed})")
        
        # Determine next action
        remaining_items = len(conversation.items_to_quote) - len(conversation.quoted_items)
        
        if remaining_items > 0:
            next_item = None
            for item in conversation.items_to_quote:
                if item['item_name'] not in conversation.quoted_items:
                    next_item = item
                    break
            
            response_message = f"Thank you! I've recorded ₹{unit_price} per unit for {item_name}. "
            if next_item:
                response_message += f"Now, what is your per-unit price for {next_item['quantity']} units of {next_item['item_name']}?"
        else:
            response_message = f"Perfect! I've recorded ₹{unit_price} per unit for {item_name}. That completes all our items. Let me summarize the quotes."
        
        return jsonify({
            "success": True,
            "message": response_message,
            "quote_recorded": {
                "item": item_name,
                "price": unit_price,
                "quantity": quantity,
                "confirmed": confirmed
            },
            "remaining_items": remaining_items
        }), 200
        
    except Exception as e:
        logger.error(f"Error recording quote: {e}")
        return jsonify({"error": f"Failed to record quote: {str(e)}"}), 500


def handle_complete_quote_collection(conversation: ConversationState, args: dict) -> tuple:
    """Handle completion of quote collection"""
    try:
        total_items_quoted = args.get('total_items_quoted', 0)
        summary = args.get('summary', '')
        
        # Mark conversation as complete
        conversation.conversation_complete = True
        
        # Calculate totals
        total_cost = sum(quote.unit_price * quote.quantity for quote in conversation.quoted_items.values())
        
        # Save final state
        save_conversation_to_db(conversation)
        
        # Store in global collected quotes for retrieval by main system
        collected_quotes[conversation.call_sid] = {
            'vendor_id': conversation.vendor_id,
            'quotes': {item_name: asdict(quote) for item_name, quote in conversation.quoted_items.items()},
            'total_cost': total_cost,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Completed quote collection for call {conversation.call_sid}: {total_items_quoted} items, ₹{total_cost} total")
        
        # Generate summary message
        summary_message = f"Thank you for providing quotes for all {total_items_quoted} items. "
        summary_message += f"The total cost would be ₹{total_cost:.2f}. "
        summary_message += "We'll review your quotes and get back to you soon. Thank you for your time!"
        
        return jsonify({
            "success": True,
            "message": summary_message,
            "conversation_complete": True,
            "summary": {
                "total_items": total_items_quoted,
                "total_cost": total_cost,
                "quotes": list(conversation.quoted_items.keys())
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error completing quote collection: {e}")
        return jsonify({"error": f"Failed to complete collection: {str(e)}"}), 500


def handle_conversation_end(data: dict) -> tuple:
    """Handle conversation end event"""
    call_sid = data.get('CallSid')
    
    if call_sid in conversation_states:
        conversation = conversation_states[call_sid]
        conversation.conversation_complete = True
        save_conversation_to_db(conversation)
        
        logger.info(f"Conversation ended for call {call_sid}")
    
    return jsonify({"message": "Conversation ended"}), 200


@app.route('/get-quotes/<call_sid>', methods=['GET'])
def get_collected_quotes(call_sid: str):
    """API endpoint to retrieve collected quotes for a specific call"""
    if call_sid in collected_quotes:
        return jsonify(collected_quotes[call_sid]), 200
    else:
        return jsonify({"error": "No quotes found for this call"}), 404


@app.route('/conversation-status/<call_sid>', methods=['GET'])
def get_conversation_status(call_sid: str):
    """Get the current status of a conversation"""
    if call_sid in conversation_states:
        conversation = conversation_states[call_sid]
        return jsonify({
            "call_sid": call_sid,
            "vendor_id": conversation.vendor_id,
            "total_items": len(conversation.items_to_quote),
            "quoted_items": len(conversation.quoted_items),
            "current_item_index": conversation.current_item_index,
            "conversation_complete": conversation.conversation_complete,
            "quotes": {name: asdict(quote) for name, quote in conversation.quoted_items.items()}
        }), 200
    else:
        return jsonify({"error": "Conversation not found"}), 404


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_conversations": len(conversation_states)
    }), 200


if __name__ == '__main__':
    # Initialize database
    initialize_database()
    
    # Print startup information
    print("🤖 Twilio Voice AI Webhook Server Starting...")
    print("📞 Endpoints:")
    print("   POST /voice-ai-webhook - Main webhook for ConversationRelay")
    print("   GET  /get-quotes/<call_sid> - Retrieve collected quotes")
    print("   GET  /conversation-status/<call_sid> - Get conversation status")
    print("   GET  /health - Health check")
    print("")
    print("🔧 Configuration:")
    print("   Database: voice_ai_quotes.db")
    print("   Log file: voice_ai_webhook.log")
    print("   Port: 5000")
    print("")
    print("🚀 Ready for Twilio Voice AI ConversationRelay calls!")
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
