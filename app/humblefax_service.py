import requests
import base64
import io
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class HumbleFaxService:
    def __init__(self):
        # HumbleFax API configuration with Access Key and Secret Key
        self.access_key = getattr(settings, 'HUMBLEFAX_ACCESS_KEY', 'your_humblefax_access_key_here')
        self.secret_key = getattr(settings, 'HUMBLEFAX_SECRET_KEY', 'your_humblefax_secret_key_here')
        self.base_url = "https://api.humblefax.com"
        self.from_number = getattr(settings, 'HUMBLEFAX_FROM_NUMBER', '+1234567890')
        
    def _get_auth_headers(self):
        """
        Generate authentication headers using Access Key and Secret Key
        """
        logger.info("=== GENERATING AUTH HEADERS ===")
        logger.info(f"Access Key: {self.access_key[:10]}..." if self.access_key else "None")
        logger.info(f"Secret Key: {self.secret_key[:10]}..." if self.secret_key else "None")
        
        # Create Basic Auth with Access Key as username and Secret Key as password
        auth_string = f"{self.access_key}:{self.secret_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"Generated Authorization header: Basic {auth_b64[:20]}...")
        return headers
    
    def get_fax_history(self, limit=50, offset=0, direction=None):
        """
        Get fax history (both sent and received faxes)
        
        Args:
            limit (int): Number of faxes to retrieve
            offset (int): Offset for pagination
            direction (str): 'outbound' for sent faxes, 'inbound' for received faxes, None for both
            
        Returns:
            list: List of fax records
        """
        try:
            headers = self._get_auth_headers()
            
            params = {
                "limit": limit,
                "offset": offset
            }
            
            all_faxes = []
            
            # Get sent faxes if direction is outbound or None
            if direction in [None, 'outbound']:
                try:
                    logger.info("Getting sent faxes from: https://api.humblefax.com/sentFaxes")
                    
                    response = requests.get(
                        f"{self.base_url}/sentFaxes",
                        headers=headers,
                        params=params,
                        timeout=30
                    )
                    
                    logger.info(f"Sent faxes response status: {response.status_code}")
                    logger.debug(f"Sent faxes response: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Handle the response structure that returns fax IDs
                        sent_fax_ids = []
                        if 'data' in result:
                            if 'sentFaxIds' in result['data']:
                                sent_fax_ids = result['data']['sentFaxIds']
                            elif 'sentFaxes' in result['data']:
                                # If full data is returned
                                sent_faxes = result['data']['sentFaxes']
                                for fax in sent_faxes:
                                    formatted_fax = {
                                        'id': fax.get('id') or fax.get('sentFaxId'),
                                        'to': fax.get('toNumber') or fax.get('to') or fax.get('recipient'),
                                        'from': fax.get('fromNumber') or fax.get('from') or fax.get('sender'),
                                        'status': fax.get('status', 'unknown'),
                                        'direction': 'outbound',
                                        'created_at': fax.get('createdAt') or fax.get('created_at') or fax.get('date'),
                                        'updated_at': fax.get('updatedAt') or fax.get('updated_at') or fax.get('modified'),
                                        'subject': fax.get('subject', ''),
                                        'message': fax.get('message', ''),
                                        'num_pages': fax.get('numPages') or fax.get('pages') or fax.get('pageCount', 0),
                                        'file_size': fax.get('fileSize') or fax.get('size', 0)
                                    }
                                    all_faxes.append(formatted_fax)
                        
                        # If we got fax IDs, fetch individual fax details
                        if sent_fax_ids:
                            logger.info(f"Retrieved {len(sent_fax_ids)} sent fax IDs, fetching details...")
                            
                            for fax_id in sent_fax_ids[:limit]:  # Limit the number of faxes to fetch
                                try:
                                    fax_detail = self.get_fax_detail(fax_id)
                                    if fax_detail:
                                        fax_detail['direction'] = 'outbound'  # Ensure direction is set
                                        all_faxes.append(fax_detail)
                                        logger.debug(f"Fetched sent fax details for ID: {fax_id}")
                                    else:
                                        logger.warning(f"Could not fetch details for sent fax ID: {fax_id}")
                                except Exception as e:
                                    logger.error(f"Error fetching sent fax details for ID {fax_id}: {str(e)}")
                        
                        logger.info(f"Retrieved {len([f for f in all_faxes if f.get('direction') == 'outbound'])} sent faxes")
                        
                except Exception as e:
                    logger.error(f"Error getting sent faxes: {str(e)}")
            
            # Get incoming faxes if direction is inbound or None
            if direction in [None, 'inbound']:
                try:
                    logger.info("Getting incoming faxes from: https://api.humblefax.com/incomingFaxes")
                    
                    response = requests.get(
                        f"{self.base_url}/incomingFaxes",
                        headers=headers,
                        params=params,
                        timeout=30
                    )
                    
                    logger.info(f"Incoming faxes response status: {response.status_code}")
                    logger.debug(f"Incoming faxes response: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Handle the response structure that returns fax IDs
                        incoming_fax_ids = []
                        if 'data' in result:
                            if 'incomingFaxIds' in result['data']:
                                incoming_fax_ids = result['data']['incomingFaxIds']
                            elif 'incomingFaxes' in result['data']:
                                # If full data is returned
                                incoming_faxes = result['data']['incomingFaxes']
                                for fax in incoming_faxes:
                                    formatted_fax = {
                                        'id': fax.get('id') or fax.get('incomingFaxId'),
                                        'to': fax.get('toNumber') or fax.get('to') or fax.get('recipient'),
                                        'from': fax.get('fromNumber') or fax.get('from') or fax.get('sender'),
                                        'status': fax.get('status', 'received'),
                                        'direction': 'inbound',
                                        'created_at': fax.get('createdAt') or fax.get('created_at') or fax.get('date'),
                                        'updated_at': fax.get('updatedAt') or fax.get('updated_at') or fax.get('modified'),
                                        'subject': fax.get('subject', ''),
                                        'message': fax.get('message', ''),
                                        'num_pages': fax.get('numPages') or fax.get('pages') or fax.get('pageCount', 0),
                                        'file_size': fax.get('fileSize') or fax.get('size', 0)
                                    }
                                    all_faxes.append(formatted_fax)
                        
                        # If we got fax IDs, fetch individual fax details
                        if incoming_fax_ids:
                            logger.info(f"Retrieved {len(incoming_fax_ids)} incoming fax IDs, fetching details...")
                            
                            for fax_id in incoming_fax_ids[:limit]:  # Limit the number of faxes to fetch
                                try:
                                    fax_detail = self.get_fax_detail(fax_id)
                                    if fax_detail:
                                        fax_detail['direction'] = 'inbound'  # Ensure direction is set
                                        all_faxes.append(fax_detail)
                                        logger.debug(f"Fetched incoming fax details for ID: {fax_id}")
                                    else:
                                        logger.warning(f"Could not fetch details for incoming fax ID: {fax_id}")
                                except Exception as e:
                                    logger.error(f"Error fetching incoming fax details for ID {fax_id}: {str(e)}")
                        
                        logger.info(f"Retrieved {len([f for f in all_faxes if f.get('direction') == 'inbound'])} incoming faxes")
                        
                except Exception as e:
                    logger.error(f"Error getting incoming faxes: {str(e)}")
            
            # Sort all faxes by created_at (newest first), handling None values
            def sort_key(fax):
                created_at = fax.get('created_at')
                if created_at is None:
                    return ''  # Put None values at the end
                return str(created_at)
            
            all_faxes.sort(key=sort_key, reverse=True)
            
            logger.info(f"Total faxes retrieved: {len(all_faxes)}")
            
            # Debug: Log a few sample faxes to see the data structure
            if all_faxes:
                logger.info("Sample fax data:")
                for i, fax in enumerate(all_faxes[:3]):
                    logger.info(f"Fax {i+1}: {fax}")
            else:
                logger.warning("No faxes retrieved - checking if data structure is correct")
            
            return all_faxes
                
        except Exception as e:
            logger.error(f"Error getting fax history: {str(e)}")
            return []
    
    def get_fax_detail(self, fax_id):
        """
        Get detailed information about a specific fax
        
        Args:
            fax_id (str): The fax ID
            
        Returns:
            dict: Fax details or None if not found
        """
        try:
            headers = self._get_auth_headers()
            
            # Try different possible endpoints for fax details
            possible_endpoints = [
                f"/sentFax/{fax_id}",  # Specific sent fax details
                f"/incomingFax/{fax_id}",  # Specific incoming fax details
                f"/sentFaxes/{fax_id}",  # Alternative sent fax details
                f"/incomingFaxes/{fax_id}",  # Alternative incoming fax details
            ]
            
            for endpoint in possible_endpoints:
                try:
                    logger.info(f"Getting fax details from: {self.base_url}{endpoint}")
                    
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=30
                    )
                    
                    logger.info(f"Fax detail response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.debug(f"Fax detail response: {result}")
                        
                        # Handle different response structures
                        fax_data = None
                        if 'data' in result:
                            if 'sentFax' in result['data']:
                                fax_data = result['data']['sentFax']
                            elif 'incomingFax' in result['data']:
                                fax_data = result['data']['incomingFax']
                            else:
                                fax_data = result['data']
                        else:
                            fax_data = result
                        
                        if fax_data:
                            formatted_fax = {
                                'id': fax_data.get('id') or fax_data.get('sentFaxId') or fax_data.get('incomingFaxId'),
                                'to': fax_data.get('toNumber') or fax_data.get('to') or fax_data.get('recipient'),
                                'from': fax_data.get('fromNumber') or fax_data.get('from') or fax_data.get('sender'),
                                'status': fax_data.get('status', 'unknown'),
                                'direction': fax_data.get('direction', 'outbound'),
                                'created_at': fax_data.get('createdAt') or fax_data.get('created_at') or fax_data.get('date'),
                                'updated_at': fax_data.get('updatedAt') or fax_data.get('updated_at') or fax_data.get('modified'),
                                'subject': fax_data.get('subject', ''),
                                'message': fax_data.get('message', ''),
                                'num_pages': fax_data.get('numPages') or fax_data.get('pages') or fax_data.get('pageCount', 0),
                                'file_size': fax_data.get('fileSize') or fax_data.get('size', 0),
                                'failure_reason': fax_data.get('failureReason') or fax_data.get('failure_reason', ''),
                                'media_url': fax_data.get('mediaUrl') or fax_data.get('media_url', ''),
                                'company_info': fax_data.get('companyInfo', ''),
                                'resolution': fax_data.get('resolution', ''),
                                'page_size': fax_data.get('pageSize', '')
                            }
                            
                            logger.info(f"Retrieved fax details for ID: {fax_id}")
                            return formatted_fax
                        
                    elif response.status_code == 404:
                        logger.info(f"Fax {fax_id} not found at {endpoint}, trying next...")
                        continue
                    else:
                        logger.warning(f"Endpoint {endpoint} returned {response.status_code}: {response.text}")
                        continue
                        
                except Exception as e:
                    logger.info(f"Request failed for {endpoint}: {str(e)}")
                    continue
            
            logger.error(f"All endpoints failed for fax detail {fax_id}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting fax detail for {fax_id}: {str(e)}")
            return None
    
    def resend_fax(self, fax_id):
        """
        Resend a fax using the original fax ID
        
        Args:
            fax_id (str): The original fax ID to resend
            
        Returns:
            dict: Resend result
        """
        try:
            # First get the original fax details
            original_fax = self.get_fax_detail(fax_id)
            
            if not original_fax:
                return {
                    'success': False,
                    'error': f"Original fax {fax_id} not found",
                    'message': 'Original fax not found'
                }
            
            # Create a new temporary fax with the same details
            headers = self._get_auth_headers()
            
            payload = {
                "toName": "Resend Recipient",
                "fromName": "Medical Office",
                "subject": f"Resend: {original_fax.get('subject', 'Medical Order')}",
                "message": f"Resending: {original_fax.get('message', 'Medical Order')}",
                "companyInfo": original_fax.get('company_info', 'Medical Office'),
                "fromNumber": int(original_fax.get('from', self.from_number).replace('+', '')),
                "recipients": [int(original_fax.get('to', '').replace('+', ''))],
                "resolution": original_fax.get('resolution', 'Fine'),
                "pageSize": original_fax.get('page_size', 'Letter'),
                "includeCoversheet": True
            }
            
            logger.info(f"Creating resend fax for original ID: {fax_id}")
            
            response = requests.post(
                f"{self.base_url}/tmpFax",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tmp_fax_id = result.get('data', {}).get('tmpFax', {}).get('id')
                
                if tmp_fax_id:
                    # Send the temporary fax
                    send_response = requests.post(
                        f"{self.base_url}/tmpFax/{tmp_fax_id}/send",
                        headers=headers,
                        timeout=30
                    )
                    
                    if send_response.status_code == 200:
                        send_result = send_response.json()
                        new_fax_id = send_result.get('data', {}).get('sentFax', {}).get('id')
                        
                        logger.info(f"Fax resent successfully. New ID: {new_fax_id}")
                        return {
                            'success': True,
                            'new_fax_id': new_fax_id,
                            'message': f'Fax resent successfully. New ID: {new_fax_id}'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Failed to send resend fax: {send_response.status_code}",
                            'message': 'Failed to send resend fax'
                        }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to create temporary fax for resend',
                        'message': 'Failed to create resend fax'
                    }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create resend fax: {response.status_code}",
                    'message': 'Failed to create resend fax'
                }
                
        except Exception as e:
            logger.error(f"Error resending fax {fax_id}: {str(e)}")
            return {
                'success': False,
                'error': f"Error resending fax: {str(e)}",
                'message': 'Error resending fax'
            }
    
    def send_fax(self, to_number, document_content, filename, patient_name=None):
        """
        Send a fax using HumbleFax API following the correct 3-step process:
        1. Create temporary fax
        2. Upload attachment
        3. Send the fax
        """
        logger.info(f"=== HUMBLEFAX SEND_FAX CALLED ===")
        logger.info(f"To number: {to_number}")
        logger.info(f"Filename: {filename}")
        logger.info(f"Patient name: {patient_name}")
        logger.info(f"Document content size: {len(document_content)} bytes")
        
        try:
            # Step 1: Create Temporary Fax
            logger.info("=== STEP 1: CREATING TEMPORARY FAX ===")
            tmp_fax_result = self._create_tmp_fax(to_number, patient_name)
            
            if not tmp_fax_result['success']:
                return tmp_fax_result
            
            tmp_fax_id = tmp_fax_result['tmp_fax_id']
            logger.info(f"Temporary fax created with ID: {tmp_fax_id}")
            
            # Step 2: Upload Attachment
            logger.info("=== STEP 2: UPLOADING ATTACHMENT ===")
            upload_result = self._upload_attachment(tmp_fax_id, document_content, filename)
            
            if not upload_result['success']:
                return upload_result
            
            logger.info("Attachment uploaded successfully")
            
            # Step 3: Send the Fax
            logger.info("=== STEP 3: SENDING THE FAX ===")
            send_result = self._send_tmp_fax(tmp_fax_id)
            
            if send_result['success']:
                logger.info(f"Fax sent successfully! Fax ID: {send_result.get('fax_id', 'N/A')}")
                return {
                    'success': True,
                    'fax_id': send_result.get('fax_id'),
                    'status': 'sent',
                    'message': 'Fax sent successfully',
                    'tmp_fax_id': tmp_fax_id
                }
            else:
                return send_result
                
        except Exception as e:
            logger.error(f"Unexpected error sending fax to {to_number}: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'message': 'An unexpected error occurred'
            }
    
    def _create_tmp_fax(self, to_number, patient_name=None):
        """
        Step 1: Create a temporary fax
        """
        try:
            headers = self._get_auth_headers()
            
            # Prepare the temporary fax payload
            payload = {
                "toName": patient_name or "Recipient",
                "fromName": "Medical Office",
                "subject": f"Medical Order - {patient_name}" if patient_name else "Medical Order",
                "message": f"Please find attached medical order for {patient_name}" if patient_name else "Please find attached medical order",
                "companyInfo": "Medical Office",
                "fromNumber": int(self.from_number.replace('+', '')),
                "recipients": [int(to_number.replace('+', ''))],
                "resolution": "Fine",
                "pageSize": "Letter",
                "includeCoversheet": True
            }
            
            logger.info(f"Creating temporary fax with payload: {payload}")
            
            response = requests.post(
                f"{self.base_url}/tmpFax",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Create tmpFax response status: {response.status_code}")
            logger.debug(f"Create tmpFax response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                tmp_fax_id = result.get('data', {}).get('tmpFax', {}).get('id')
                if tmp_fax_id:
                    return {
                        'success': True,
                        'tmp_fax_id': tmp_fax_id
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No tmpFax ID in response',
                        'message': 'Failed to get temporary fax ID'
                    }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}",
                    'message': 'Failed to create temporary fax'
                }
                
        except Exception as e:
            logger.error(f"Error creating temporary fax: {str(e)}")
            return {
                'success': False,
                'error': f"Error creating temporary fax: {str(e)}",
                'message': 'Failed to create temporary fax'
            }
    
    def _upload_attachment(self, tmp_fax_id, document_content, filename):
        """
        Step 2: Upload attachment to the temporary fax
        """
        try:
            # For file upload, we need to use multipart/form-data
            auth_string = f"{self.access_key}:{self.secret_key}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}"
            }
            
            # Create file-like object from document content
            files = {
                filename: ('document.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            logger.info(f"Uploading attachment to tmpFax ID: {tmp_fax_id}")
            
            response = requests.post(
                f"{self.base_url}/attachment/{tmp_fax_id}",
                headers=headers,
                files=files,
                timeout=60  # Longer timeout for file upload
            )
            
            logger.info(f"Upload attachment response status: {response.status_code}")
            logger.debug(f"Upload attachment response: {response.text}")
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Attachment uploaded successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}",
                    'message': 'Failed to upload attachment'
                }
                
        except Exception as e:
            logger.error(f"Error uploading attachment: {str(e)}")
            return {
                'success': False,
                'error': f"Error uploading attachment: {str(e)}",
                'message': 'Failed to upload attachment'
            }
    
    def _send_tmp_fax(self, tmp_fax_id):
        """
        Step 3: Send the temporary fax
        """
        try:
            headers = self._get_auth_headers()
            
            logger.info(f"Sending temporary fax with ID: {tmp_fax_id}")
            
            response = requests.post(
                f"{self.base_url}/tmpFax/{tmp_fax_id}/send",
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Send tmpFax response status: {response.status_code}")
            logger.debug(f"Send tmpFax response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                fax_id = result.get('data', {}).get('sentFax', {}).get('id')
                return {
                    'success': True,
                    'fax_id': fax_id,
                    'message': 'Fax sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}",
                    'message': 'Failed to send fax'
                }
                
        except Exception as e:
            logger.error(f"Error sending temporary fax: {str(e)}")
            return {
                'success': False,
                'error': f"Error sending temporary fax: {str(e)}",
                'message': 'Failed to send fax'
            }
    
    def test_connection(self):
        """
        Test the API connection and authentication
        
        Returns:
            dict: Connection test result
        """
        try:
            headers = self._get_auth_headers()
            
            # Try multiple endpoints to test connection
            test_endpoints = [
                "/sentFaxes",
                "/incomingFaxes",
                "/account"
            ]
            
            successful_endpoints = []
            
            for endpoint in test_endpoints:
                try:
                    logger.info(f"Testing endpoint: {endpoint}")
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        successful_endpoints.append(endpoint)
                        logger.info(f"Endpoint {endpoint} is accessible")
                    elif response.status_code == 401:
                        logger.error("HumbleFax API authentication failed")
                        return {
                            'success': False,
                            'error': 'Authentication failed - check your Access Key and Secret Key'
                        }
                    else:
                        logger.info(f"Endpoint {endpoint} returned {response.status_code}")
                        
                except Exception as e:
                    logger.info(f"Endpoint {endpoint} failed: {str(e)}")
            
            if successful_endpoints:
                logger.info(f"HumbleFax API connection test successful. Working endpoints: {successful_endpoints}")
                return {
                    'success': True,
                    'message': f'API connection successful. Working endpoints: {successful_endpoints}',
                    'endpoints': successful_endpoints
                }
            else:
                logger.error("No HumbleFax API endpoints are accessible")
                return {
                    'success': False,
                    'error': 'No accessible endpoints found. Check API documentation.'
                }
                
        except Exception as e:
            logger.error(f"Error testing HumbleFax API connection: {str(e)}")
            return {
                'success': False,
                'error': f"Connection error: {str(e)}"
            }
    
    def get_fax_status(self, fax_id):
        """
        Get the status of a sent fax
        
        Args:
            fax_id (str): The fax ID returned from send_fax
            
        Returns:
            dict: Fax status information
        """
        try:
            headers = self._get_auth_headers()
            
            # Try different possible endpoints
            possible_endpoints = [
                f"/api/faxes/{fax_id}",
                f"/api/v1/faxes/{fax_id}",
                f"/faxes/{fax_id}",
                f"/v1/faxes/{fax_id}"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        logger.error(f"Failed to get fax status for {fax_id} from {endpoint}. Status: {response.status_code}")
                        
                except Exception as e:
                    logger.info(f"Request failed for {endpoint}: {str(e)}")
                    continue
            
            logger.error(f"All endpoints failed for fax status {fax_id}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting fax status for {fax_id}: {str(e)}")
            return None
    
    def list_faxes(self, limit=50, offset=0):
        """
        Get a list of sent faxes
        
        Args:
            limit (int): Number of faxes to retrieve
            offset (int): Offset for pagination
            
        Returns:
            list: List of fax records
        """
        try:
            headers = self._get_auth_headers()
            
            params = {
                "limit": limit,
                "offset": offset
            }
            
            # Try different possible endpoints
            possible_endpoints = [
                "/api/faxes",
                "/api/v1/faxes",
                "/faxes",
                "/v1/faxes"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        return response.json().get('data', [])
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        logger.error(f"Failed to get fax list from {endpoint}. Status: {response.status_code}")
                        
                except Exception as e:
                    logger.info(f"Request failed for {endpoint}: {str(e)}")
                    continue
            
            logger.error("All endpoints failed for fax list")
            return []
                
        except Exception as e:
            logger.error(f"Error getting fax list: {str(e)}")
            return []
    
    def get_account_info(self):
        """
        Get account information and credits
        
        Returns:
            dict: Account information
        """
        try:
            headers = self._get_auth_headers()
            
            # Try different possible endpoints
            possible_endpoints = [
                "/api/account",
                "/api/v1/account",
                "/account",
                "/v1/account"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        logger.error(f"Failed to get account info from {endpoint}. Status: {response.status_code}")
                        
                except Exception as e:
                    logger.info(f"Request failed for {endpoint}: {str(e)}")
                    continue
            
            logger.error("All endpoints failed for account info")
            return None
                
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def cancel_fax(self, fax_id):
        """
        Cancel a pending fax
        
        Args:
            fax_id (str): The fax ID to cancel
            
        Returns:
            dict: Cancellation result
        """
        try:
            headers = self._get_auth_headers()
            
            # Try different possible endpoints
            possible_endpoints = [
                f"/api/faxes/{fax_id}",
                f"/api/v1/faxes/{fax_id}",
                f"/faxes/{fax_id}",
                f"/v1/faxes/{fax_id}"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    response = requests.delete(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Fax {fax_id} cancelled successfully")
                        return {
                            'success': True,
                            'message': 'Fax cancelled successfully'
                        }
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        logger.error(f"Failed to cancel fax {fax_id} from {endpoint}. Status: {response.status_code}")
                        
                except Exception as e:
                    logger.info(f"Request failed for {endpoint}: {str(e)}")
                    continue
            
            logger.error(f"All endpoints failed for cancelling fax {fax_id}")
            return {
                'success': False,
                'error': 'Failed to cancel fax - no valid endpoint found'
            }
                
        except Exception as e:
            logger.error(f"Error cancelling fax {fax_id}: {str(e)}")
            return {
                'success': False,
                'error': f"Error cancelling fax: {str(e)}"
            } 