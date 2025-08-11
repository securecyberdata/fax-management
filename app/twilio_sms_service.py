import requests
import logging
import re
from django.conf import settings

logger = logging.getLogger(__name__)

class TwilioSMSService:
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', 'your_twilio_account_sid_here')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', 'your_twilio_auth_token_here')
        self.from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '+1234567890')
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
    def _get_auth_headers(self):
        """
        Generate authentication headers for Twilio API
        """
        import base64
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        logger.info(f"Generated Twilio Authorization header: Basic {auth_b64[:20]}...")
        return headers
    
    def is_mobile_number(self, phone_number):
        """
        Check if the given phone number is a mobile number
        Uses Twilio's Lookup API to determine if it's a mobile number
        
        Args:
            phone_number (str): The phone number to check
            
        Returns:
            bool: True if mobile, False if landline or invalid
        """
        try:
            # Clean the phone number
            cleaned_number = re.sub(r'\D', '', str(phone_number))
            
            if len(cleaned_number) < 10:
                logger.warning(f"Phone number {phone_number} is too short")
                return False
            
            # Add country code if not present
            if len(cleaned_number) == 10:
                cleaned_number = f"1{cleaned_number}"
            
            # Use Twilio Lookup API to check carrier type
            lookup_url = f"https://lookups.twilio.com/v2/PhoneNumbers/{cleaned_number}"
            params = {
                "Fields": "carrier"
            }
            
            headers = self._get_auth_headers()
            
            logger.info(f"Checking if {cleaned_number} is a mobile number...")
            
            response = requests.get(
                lookup_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                carrier_info = result.get('carrier', {})
                carrier_type = carrier_info.get('type', '').lower()
                
                is_mobile = carrier_type in ['mobile', 'voip']
                logger.info(f"Phone number {cleaned_number} carrier type: {carrier_type}, is_mobile: {is_mobile}")
                
                return is_mobile
            else:
                logger.warning(f"Twilio Lookup API returned {response.status_code}: {response.text}")
                # If lookup fails, assume it's mobile to be safe
                return True
                
        except Exception as e:
            logger.error(f"Error checking if {phone_number} is mobile: {str(e)}")
            # If there's an error, assume it's mobile to be safe
            return True
    
    def format_phone_number(self, phone_number):
        """
        Format phone number for Twilio API
        
        Args:
            phone_number (str): The phone number to format
            
        Returns:
            str: Formatted phone number or None if invalid
        """
        try:
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', str(phone_number))
            
            # Check minimum length
            if len(digits_only) < 10:
                logger.warning(f"Phone number {phone_number} has only {len(digits_only)} digits")
                return None
            
            # Add country code if needed
            if len(digits_only) == 10:
                formatted_number = f"+1{digits_only}"
            elif len(digits_only) == 11 and digits_only.startswith('1'):
                formatted_number = f"+{digits_only}"
            else:
                formatted_number = f"+{digits_only}"
            
            logger.info(f"Formatted phone number {phone_number} -> {formatted_number}")
            return formatted_number
            
        except Exception as e:
            logger.error(f"Error formatting phone number {phone_number}: {str(e)}")
            return None
    
    def send_sms(self, to_number, message, name=None):
        """
        Send SMS using Twilio API
        
        Args:
            to_number (str): Recipient phone number
            message (str): Message content
            name (str): Recipient name for logging
            
        Returns:
            dict: SMS sending result
        """
        try:
            logger.info(f"=== SENDING SMS TO {name or 'Unknown'} ===")
            logger.info(f"To number: {to_number}")
            logger.info(f"Message: {message}")
            
            # Format phone number
            formatted_number = self.format_phone_number(to_number)
            if not formatted_number:
                return {
                    'success': False,
                    'error': f"Invalid phone number format: {to_number}",
                    'message': 'Invalid phone number format'
                }
            
            # Check if it's a mobile number
            if not self.is_mobile_number(formatted_number):
                return {
                    'success': False,
                    'error': f"Phone number {formatted_number} is not a mobile number",
                    'message': 'Phone number must be a mobile number'
                }
            
            # Prepare SMS data
            data = {
                "To": formatted_number,
                "From": self.from_number,
                "Body": message
            }
            
            headers = self._get_auth_headers()
            
            logger.info(f"Sending SMS via Twilio to {formatted_number}")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            logger.info(f"Twilio SMS response status: {response.status_code}")
            logger.debug(f"Twilio SMS response: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                sms_id = result.get('sid')
                
                logger.info(f"SMS sent successfully! SMS ID: {sms_id}")
                return {
                    'success': True,
                    'sms_id': sms_id,
                    'status': result.get('status', 'queued'),
                    'message': 'SMS sent successfully'
                }
            else:
                error_msg = f"Twilio API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'message': 'Failed to send SMS'
                }
                
        except Exception as e:
            error_msg = f"Error sending SMS: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Error sending SMS'
            }
    
    def send_prescription_sms(self, name, pcp_name, phone, device_name):
        """
        Send prescription order SMS with the specific message format
        
        Args:
            name (str): Patient name
            pcp_name (str): Doctor/PCP name
            phone (str): Patient phone number
            device_name (str): Device name
            
        Returns:
            dict: SMS sending result
        """
        try:
            # Format the message
            message = f"Hey! {name}! Your Signed Prescription Order has been Received from Doctor {pcp_name} for {device_name}. There is no Out-Of-Pocket Expense. Everything will be covered by Medicare."
            
            logger.info(f"Preparing prescription SMS for {name}")
            logger.info(f"Message: {message}")
            
            # Send the SMS
            return self.send_sms(phone, message, name)
            
        except Exception as e:
            error_msg = f"Error sending prescription SMS: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Error sending prescription SMS'
            }
    
    def test_connection(self):
        """
        Test Twilio API connection
        
        Returns:
            dict: Connection test result
        """
        try:
            headers = self._get_auth_headers()
            
            # Try to get account information
            account_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}.json"
            
            response = requests.get(
                account_url,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                account_name = result.get('friendly_name', 'Unknown')
                logger.info(f"Twilio API connection successful. Account: {account_name}")
                return {
                    'success': True,
                    'message': f'Twilio API connection successful. Account: {account_name}',
                    'account_name': account_name
                }
            elif response.status_code == 401:
                logger.error("Twilio API authentication failed")
                return {
                    'success': False,
                    'error': 'Authentication failed - check your Account SID and Auth Token'
                }
            else:
                logger.error(f"Twilio API connection test failed. Status: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error testing Twilio API connection: {str(e)}")
            return {
                'success': False,
                'error': f"Connection error: {str(e)}"
            } 