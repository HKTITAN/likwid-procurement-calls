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