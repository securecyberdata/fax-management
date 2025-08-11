import os
import base64
import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FaxRecord
from .humblefax_service import HumbleFaxService
from .twilio_sms_service import TwilioSMSService
import requests

logger = logging.getLogger(__name__)

def dashboard(request):
    return render(request, 'app/dashboard.html')

def test_humblefax_connection(request):
    try:
        humblefax = HumbleFaxService()
        result = humblefax.test_connection()
        return JsonResponse({"status": "success", "message": result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

def new(request): #type new to access docx file 
    return render(request, 'app/freestyle.html')

def gendocx(request):
    return render(request, 'app/freestyle_2.html')

def genknee(request):
    return render(request, 'app/CGM_DO.html')

def geninvoice(request):
    return render(request, 'app/invoice_gen.html')

def sendfax(request):
    if request.method == 'POST':
        fax_to = request.POST.get('fax_to')
        media_url = request.POST.get('media_url')
        
        if not fax_to or not media_url:
            return HttpResponse("Fax number and media URL are required")
        
        # Encode the fax content as a base64 string
        #fax_content_base64 = base64.b64encode(file_content).decode("utf-8")

        # Define the API endpoint and authentication credentials
        endpoint = "https://api.telnyx.com/v2/faxes"
        api_key = os.environ.get('TELNYX_API_KEY', '')

        # Define the fax content and recipient information
        data = {
            "media_url":media_url,
            "connection_id": "2047423188568114992",
            "to": fax_to, #email to fax numb
            "from": "+18177800212", #fax numb we r using.
            #"file_b64": fax_content_base64,
        }

        
        # Make the API request to send the fax
        response = requests.post(endpoint, json=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })

        # Check the API response to see if the fax was sent successfully
        if response.status_code == 201:
            fax = response.json()
            return HttpResponse(f"Fax sent successfully! Fax ID: {fax['id']}")
        else:
            return HttpResponse(f"Fax schedule for delivery. API response: {response.text}")
    
    return render(request, 'send_fax.html')

def fax_list(request):
    """
    Get fax history using HumbleFax API
    """
    try:
        logger.info("=== GETTING FAX HISTORY ===")
        
        # Initialize HumbleFax service
        humblefax = HumbleFaxService()
        
        # Get query parameters for filtering
        direction = request.GET.get('direction')  # 'outbound' or 'inbound'
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        logger.info(f"Getting fax history - direction: {direction}, limit: {limit}, offset: {offset}")
        
        # Get fax history from HumbleFax
        faxes = humblefax.get_fax_history(limit=limit, offset=offset, direction=direction)
        
        logger.info(f"Retrieved {len(faxes)} faxes from HumbleFax")
        
        # Format data for template
        fax_data = []
        for fax in faxes:
            fax_data.append((
                fax.get('id', 'N/A'),
                fax.get('to', 'N/A'),
                fax.get('from', 'N/A'),
                fax.get('status', 'unknown'),
                fax.get('updated_at', 'N/A'),
                fax.get('direction', 'outbound'),
                fax.get('subject', ''),
                fax.get('num_pages', 0)
            ))
        
        # Calculate page number for pagination
        page_number = (offset // limit) + 1
        
        context = {
            "fax_data": fax_data,
            "total_count": len(faxes),
            "direction": direction,
            "limit": limit,
            "offset": offset,
            "page_number": page_number
        }
        
        logger.info(f"Rendering template with {len(fax_data)} fax records")
        return render(request, 'fax_list.html', context)
            
    except Exception as e:
        error_msg = f"Error getting fax history: {str(e)}"
        logger.error(error_msg)
        return render(request, 'fax_list.html', {"error_msg": error_msg})

def fax_detail(request, fax_id):
    """
    Get detailed information about a specific fax using HumbleFax API
    """
    try:
        logger.info(f"=== GETTING FAX DETAILS FOR ID: {fax_id} ===")
        
        # Initialize HumbleFax service
        humblefax = HumbleFaxService()
        
        # Get fax details from HumbleFax
        fax_details = humblefax.get_fax_details(fax_id)
        
        if not fax_details:
            return render(request, 'fax_detail.html', {"error_msg": "Fax not found"})
        
        context = {
            "fax": fax_details
        }
        
        logger.info(f"Rendering fax details for ID: {fax_id}")
        return render(request, 'fax_detail.html', context)
            
    except Exception as e:
        error_msg = f"Error getting fax details: {str(e)}"
        logger.error(error_msg)
        return render(request, 'fax_detail.html', {"error_msg": error_msg})

def single_sms(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        
        if not phone_number or not message:
            return HttpResponse("Phone number and message are required")
        
        try:
            twilio_service = TwilioSMSService()
            result = twilio_service.send_sms(phone_number, message)
            return HttpResponse(f"SMS sent successfully! SID: {result}")
        except Exception as e:
            return HttpResponse(f"Error sending SMS: {str(e)}")
    
    return render(request, 'app/single_sms.html')

def bulk_sms(request):
    if request.method == 'POST':
        phone_numbers = request.POST.get('phone_numbers')
        message = request.POST.get('message')
        
        if not phone_numbers or not message:
            return HttpResponse("Phone numbers and message are required")
        
        # Split phone numbers by comma or newline
        phone_list = [phone.strip() for phone in phone_numbers.replace('\n', ',').split(',') if phone.strip()]
        
        if not phone_list:
            return HttpResponse("No valid phone numbers provided")
        
        try:
            twilio_service = TwilioSMSService()
            results = []
            
            for phone in phone_list:
                try:
                    result = twilio_service.send_sms(phone, message)
                    results.append(f"✓ {phone}: Success (SID: {result})")
                except Exception as e:
                    results.append(f"✗ {phone}: Failed - {str(e)}")
            
            return HttpResponse("<br>".join(results))
        except Exception as e:
            return HttpResponse(f"Error sending bulk SMS: {str(e)}")
    
    return render(request, 'app/bulk_sms.html')

def test_twilio_connection(request):
    try:
        twilio_service = TwilioSMSService()
        result = twilio_service.test_connection()
        return JsonResponse({"status": "success", "message": result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

def fax_resend(request, fax_id):
    """
    Resend a fax using HumbleFax API
    """
    try:
        logger.info(f"=== RESENDING FAX ID: {fax_id} ===")
        
        # Initialize HumbleFax service
        humblefax = HumbleFaxService()
        
        # Resend fax via HumbleFax
        result = humblefax.resend_fax(fax_id)
        
        if result:
            return JsonResponse({"status": "success", "message": f"Fax {fax_id} resent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Failed to resend fax"})
            
    except Exception as e:
        error_msg = f"Error resending fax: {str(e)}"
        logger.error(error_msg)
        return JsonResponse({"status": "error", "message": error_msg})

def bulk_fax_generator(request):
    return render(request, 'app/bulk_fax.html')

def bulk_fax_sender(request):
    if request.method == 'POST':
        fax_numbers = request.POST.get('fax_numbers')
        media_url = request.POST.get('media_url')
        
        if not fax_numbers or not media_url:
            return HttpResponse("Fax numbers and media URL are required")
        
        # Split fax numbers by comma or newline
        fax_list = [fax.strip() for fax in fax_numbers.replace('\n', ',').split(',') if fax.strip()]
        
        if not fax_list:
            return HttpResponse("No valid fax numbers provided")
        
        try:
            endpoint = "https://api.telnyx.com/v2/faxes"
            api_key = os.environ.get('TELNYX_API_KEY', '')
            
            results = []
            
            for fax_number in fax_list:
                try:
                    data = {
                        "media_url": media_url,
                        "connection_id": "2047423188568114992",
                        "to": fax_number,
                        "from": "+18177800212",
                    }
                    
                    response = requests.post(endpoint, json=data, headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    })
                    
                    if response.status_code == 201:
                        fax = response.json()
                        results.append(f"✓ {fax_number}: Success (Fax ID: {fax['id']})")
                    else:
                        results.append(f"✗ {fax_number}: Failed - {response.text}")
                        
                except Exception as e:
                    results.append(f"✗ {fax_number}: Error - {str(e)}")
            
            return HttpResponse("<br>".join(results))
        except Exception as e:
            return HttpResponse(f"Error sending bulk faxes: {str(e)}")
    
    return render(request, 'app/bulk_fax.html') 