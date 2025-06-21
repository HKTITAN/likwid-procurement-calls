# 🎤 Voice-Enabled Procurement Automation System

## Revolutionary Voice Quote Collection

This system has been enhanced with **real-time voice quote collection** that automatically captures vendor pricing during phone calls using speech recognition technology.

## 🚀 How It Works

### The Voice-Enabled Workflow

1. **📞 Interactive Calls**: System calls vendors and asks them to speak their quotes
2. **🎤 Voice Recording**: Records vendor responses using Twilio TwiML
3. **🧠 Speech Recognition**: Converts speech to text using advanced AI
4. **💰 Price Parsing**: Intelligently extracts pricing from spoken responses
5. **📊 Real-time Updates**: Updates CSV files with actual vendor quotes
6. **🏆 Smart Comparison**: Compares all voice quotes and selects cheapest

### Sample Call Flow

**System**: *"Namaste, this is Bio Mac Lifesciences calling for price quotes. We need quotes for 200 units of USB-C Cables, 100 units of Wireless Mouse. Please provide your best pricing for each item. After I finish speaking, please state your prices clearly."*

**Vendor**: *"USB cables will be 12 rupees per unit, wireless mouse 28 rupees each"*

**System**: ✅ *Automatically parses: USB-C Cables = ₹12/unit, Wireless Mouse = ₹28/unit*

## 🎯 Key Features

### Real-Time Quote Collection
- **Live Speech Processing**: Captures vendor quotes as they speak
- **Intelligent Parsing**: Understands various ways vendors state prices
- **Automatic CSV Updates**: Updates pricing data in real-time
- **Fallback Mechanisms**: Uses estimated pricing if speech fails

### Advanced Voice Recognition
- **Multiple Price Formats**: Handles "12 rupees", "₹12", "12 per unit", etc.
- **Item Matching**: Maps spoken item names to inventory IDs
- **Context Awareness**: Understands pricing context and quantities
- **Error Recovery**: Graceful handling of unclear audio

### Smart Quote Comparison
- **Real-time Analysis**: Compares actual spoken quotes
- **Cost Optimization**: Always selects the cheapest total cost
- **Transparent Process**: Shows all quotes received
- **Audit Trail**: Complete record of voice quotes and decisions

## 🔧 Technical Implementation

### Voice Processing Stack
```
Twilio Call → TwiML Recording → Speech-to-Text → Price Parsing → CSV Update
```

### Dependencies
- **SpeechRecognition**: For voice processing
- **pydub**: For audio manipulation  
- **Twilio**: For phone calls and recording
- **requests**: For API communication

### Quote Parsing Patterns
The system recognizes multiple pricing formats:
- `"USB cables 12 rupees per unit"`
- `"Wireless mouse costs 25 rupees"`
- `"HDMI adapters at 18 rupees each"`
- `"12.50 for cables, 25.75 for mouse"`

## 📞 Usage Examples

### Basic Voice-Enabled Procurement
```powershell
# Run complete voice workflow
python caller.py voice

# Run with interactive menu
python caller.py interactive

# Test voice quote collection
python caller.py test-voice
```

### Demo and Testing
```powershell
# Voice system demo
python demo_voice_procurement.py

# Test voice parsing
python test_voice_parsing.py

# Quick workflow test
python caller.py two-phase
```

## 🎤 Voice System Status

When you run the system, check these indicators:

✅ **Speech Recognition: Ready** - Voice quotes will be processed  
✅ **Audio Processing: Ready** - Audio files will be handled  
📞 **Callable vendors: X** - Number of vendors available for calls  

## 📊 Sample Output

```
🎤 VOICE-ENABLED PROCUREMENT AUTOMATION SYSTEM
================================================================

--> Making INTERACTIVE quote call to TechSupply Solutions for 4 items
--> Interactive quote call SUCCESS! SID: CA1234567890abcdef
--> Waiting for vendor response...
--> Transcription received: "USB cables twelve rupees per unit, wireless mouse twenty-eight rupees each, HDMI adapters twenty-two rupees, ethernet cables nine rupees per piece"
--> Parsed 4 quotes from speech
--> USB-C Cables: ₹12.0 per unit (Total: ₹2400.0)
--> Wireless Mouse: ₹28.0 per unit (Total: ₹2800.0)  
--> HDMI Adapters: ₹22.0 per unit (Total: ₹3300.0)
--> Ethernet Cables: ₹9.0 per unit (Total: ₹2700.0)

=== PHASE 2: QUOTE COMPARISON & ORDER PLACEMENT ===
Voice quote from TechSupply Solutions: ₹11,200.00
Real-time pricing captured via speech recognition
```

## 🛡️ Security Features

### Phone Number Restrictions
- Only calls allowed numbers for safety
- Complete audit trail of all calls
- Security blocks for unauthorized numbers

### Data Protection
- Encrypted API communications
- Secure credential handling
- Complete call logging for compliance

## ⚠️ Prerequisites

### Required Packages
```bash
pip install SpeechRecognition pydub pyaudio requests
```

### Twilio Setup
- Valid Twilio account with calling capability
- Phone number configured for outbound calls
- API credentials in `.env` file

### Audio Requirements
- Clear phone line quality for speech recognition
- Vendor must speak clearly and distinctly
- Background noise minimization

## 🎯 Benefits

### Cost Savings
- **Always Get Best Price**: Real voice quotes ensure competitive pricing
- **No Manual Entry**: Eliminates human error in quote collection
- **Instant Comparison**: Real-time price comparison across vendors

### Efficiency Gains
- **Automated Process**: No manual quote collection required
- **Real-time Updates**: CSV files updated during calls
- **Instant Decisions**: Immediate vendor selection based on voice quotes

### Transparency
- **Complete Audit Trail**: Every quote recorded and logged
- **Speech Transcripts**: Full record of vendor responses
- **Decision Justification**: Clear rationale for vendor selection

## 🔮 Future Enhancements

- **Multi-language Support**: Hindi, Tamil, other regional languages
- **Voice Biometrics**: Vendor identity verification
- **AI Negotiation**: Automated price negotiation
- **Real-time Translation**: Cross-language quote collection

---

*This voice-enabled system represents the cutting edge of procurement automation, ensuring you always get the best deals through intelligent voice processing.*
