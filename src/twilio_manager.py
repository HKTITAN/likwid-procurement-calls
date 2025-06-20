"""
Twilio Integration Module
Handles phone calls using direct REST API approach for Windows compatibility
"""

import requests
import base64
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TwilioManager:
    """Manages Twilio API calls using direct REST API approach"""
    
    def __init__(self, account_sid: str, auth_token: str, phone_number: str, allowed_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.allowed_number = allowed_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"
    
    def _create_auth_header(self) -> str:
        """Create basic auth header for Twilio API"""
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        return base64.b64encode(auth_bytes).decode('ascii')
    
    def make_call(self, to_number: str, message: str, max_retries: int = 3) -> Optional[str]:
        """
        Make a phone call using Twilio REST API
        
        Args:
            to_number: Phone number to call
            message: Message to speak
            max_retries: Maximum number of retry attempts
            
        Returns:
            Call SID if successful, None if failed
        """
        # Security check
        if to_number != self.allowed_number:
            logger.warning(f"SECURITY: Blocked call to {to_number}. Only {self.allowed_number} is allowed.")
            return "blocked_unauthorized_number"
        
        # Validate credentials
        if not self.account_sid or "YOUR_TWILIO" in self.account_sid:
            logger.error("Twilio credentials not configured")
            return None
        
        # Prepare TwiML
        twiml = f"<Response><Say voice='alice' language='en-IN'>{message}</Say></Response>"
        
        # API endpoint
        url = f"{self.base_url}/Calls.json"
        
        # Request data
        data = {
            'From': self.phone_number,
            'To': to_number,
            'Twiml': twiml
        }
        
        # Headers
        headers = {
            'Authorization': f'Basic {self._create_auth_header()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                logger.info(f"Making call attempt {attempt + 1} to {to_number}")
                
                response = requests.post(url, data=data, headers=headers, timeout=30)
                
                if response.status_code == 201:
                    call_data = response.json()
                    call_sid = call_data.get('sid')
                    status = call_data.get('status')
                    
                    logger.info(f"Call successful! SID: {call_sid}, Status: {status}")
                    
                    # Log successful call
                    self._log_successful_call(call_sid, to_number, status)
                    
                    return call_sid
                else:
                    logger.error(f"Call failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Call attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 3 seconds...")
                    import time
                    time.sleep(3)
        
        logger.error("All call attempts failed")
        return None
    
    def _log_successful_call(self, call_sid: str, to_number: str, status: str):
        """Log successful call to file"""
        try:
            log_entry = f"{datetime.now()}: Call to {to_number} - SID: {call_sid} - Status: {status}\n"
            with open("logs/successful_calls.log", "a") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Failed to log call: {e}")
    
    def make_procurement_call(self, vendor_name: str, vendor_phone: str, items: list, company_name: str) -> Optional[str]:
        """
        Make a specialized procurement call
        
        Args:
            vendor_name: Name of the vendor
            vendor_phone: Vendor's phone number
            items: List of items being ordered
            company_name: Company name for the message
            
        Returns:
            Call SID if successful, None if failed
        """
        message = (
            f"Namaste, this is an automated procurement call from {company_name}. "
            f"You have been selected as our preferred supplier for {', '.join(items)} "
            f"based on your competitive quote and excellent service record. "
            f"A formal purchase order and email confirmation will be sent to you shortly. "
            f"Thank you for your continued partnership with {company_name}."
        )
        
        logger.info(f"Making procurement call to {vendor_name} at {vendor_phone}")
        return self.make_call(vendor_phone, message)
    
    def make_test_call(self, company_name: str = "Bio Mac Lifesciences") -> Optional[str]:
        """
        Make a test call to verify system functionality
        
        Args:
            company_name: Company name for the test message
            
        Returns:
            Call SID if successful, None if failed
        """
        message = (
            f"Namaste, this is a test call from {company_name} procurement system. "
            f"This confirms that the automated calling system is working correctly "
            f"and ready for production use. Thank you."
        )
        
        logger.info(f"Making test call to {self.allowed_number}")
        return self.make_call(self.allowed_number, message)
    
    def get_call_status(self, call_sid: str) -> Optional[dict]:
        """
        Get the status of a call
        
        Args:
            call_sid: The call SID to check
            
        Returns:
            Call status information or None if failed
        """
        try:
            url = f"{self.base_url}/Calls/{call_sid}.json"
            headers = {
                'Authorization': f'Basic {self._create_auth_header()}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get call status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            return None
