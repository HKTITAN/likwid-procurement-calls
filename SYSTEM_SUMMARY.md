# AI-Powered Procurement Automation System - Summary

## Project Overview

Build a complete procurement automation system using **Python 3.8+** and **Twilio Voice AI (ConversationRelay)** that intelligently calls vendors to collect real-time price quotes through AI-driven voice conversations. The system automatically checks inventory levels from CSV files (inventory.csv, vendors.csv, vendor_items_mapping.csv), identifies items needing reorder, makes simultaneous calls to multiple vendors using an AI agent that conducts professional conversations in Indian English, collects itemized quotes through webhook-based function calls to a Flask server, compares all received quotes, and automatically places orders with the cheapest vendor while sending email notifications and generating comprehensive reports. Key features include security restrictions for phone number validation, graceful fallbacks for API failures, speech recognition integration, real-time quote processing via webhooks, two-phase procurement workflows (quote collection → comparison → order placement), and support for both classic TTS calls and advanced AI conversations. The system requires Twilio ConversationRelay, Flask webhook server, CSV data management, email notifications, comprehensive logging, and can be deployed locally with ngrok or in production on cloud platforms. This creates a fully automated, intelligent procurement solution that saves time and money through competitive quote collection and automated vendor selection, complete with detailed reporting and cost savings analysis.

---

**Tech Stack**: Python, Twilio ConversationRelay, Flask, CSV data storage, Speech Recognition, Email SMTP  
**Timeline**: 2-3 weeks for full implementation  
**Key APIs**: Twilio Voice AI, Optional ElevenLabs for narration  
**Security**: Phone number validation, environment-based configuration, call logging  
**Deliverables**: Complete Python system, webhook server, CSV templates, demo scripts, documentation
