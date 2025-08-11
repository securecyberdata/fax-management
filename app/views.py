import os
import base64
import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import FaxRecord, SMSRecord, APIConfiguration
from .forms import (
    TelnyxConfigForm, HumbleFaxConfigForm, TwilioConfigForm,
    SendFaxForm, SendSMSForm, BulkFaxForm, BulkSMSForm
)
from .humblefax_service import HumbleFaxService
from .twilio_sms_service import TwilioSMSService
import requests

logger = logging.getLogger(__name__)

def dashboard(request):
    return render(request, 'app/dashboard.html')

def api_configuration(request):
    """View for configuring API settings"""
    if request.method == 'POST':
        service = request.POST.get('service')
        
        if service == 'telnyx':
            form = TelnyxConfigForm(request.POST)
            if form.is_valid():
                config, created = APIConfiguration.objects.get_or_create(
                    service='telnyx',
                    defaults=form.cleaned_data
                )
                if not created:
                    for field, value in form.cleaned_data.items():
                        setattr(config, field, value)
                    config.save()
                messages.success(request, 'Telnyx configuration saved successfully!')
                return redirect('api_configuration')
        elif service == 'humblefax':
            form = HumbleFaxConfigForm(request.POST)
            if form.is_valid():
                config, created = APIConfiguration.objects.get_or_create(
                    service='humblefax',
                    defaults=form.cleaned_data
                )
                if not created:
                    for field, value in form.cleaned_data.items():
                        setattr(config, field, value)
                    config.save()
                messages.success(request, 'HumbleFax configuration saved successfully!')
                return redirect('api_configuration')
        elif service == 'twilio':
            form = TwilioConfigForm(request.POST)
            if form.is_valid():
                config, created = APIConfiguration.objects.get_or_create(
                    service='twilio',
                    defaults=form.cleaned_data
                )
                if not created:
                    for field, value in form.cleaned_data.items():
                        setattr(config, field, value)
                    config.save()
                messages.success(request, 'Twilio configuration saved successfully!')
                return redirect('api_configuration')
    else:
        # Get existing configurations
        telnyx_config = APIConfiguration.objects.filter(service='telnyx').first()
        humblefax_config = APIConfiguration.objects.filter(service='humblefax').first()
        twilio_config = APIConfiguration.objects.filter(service='twilio').first()
        
        telnyx_form = TelnyxConfigForm(instance=telnyx_config)
        humblefax_form = HumbleFaxConfigForm(instance=humblefax_config)
        twilio_form = TwilioConfigForm(instance=twilio_config)
    
    context = {
        'telnyx_form': telnyx_form,
        'humblefax_form': humblefax_form,
        'twilio_form': twilio_form,
    }
    return render(request, 'app/api_configuration.html', context)

def test_humblefax_connection(request):
    try:
        config = APIConfiguration.objects.filter(service='humblefax', is_active=True).first()
        if not config:
            return JsonResponse({"status": "error", "message": "HumbleFax not configured"})
        
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
        form = SendFaxForm(request.POST)
        if form.is_valid():
            fax_to = form.cleaned_data['fax_to']
            media_url = form.cleaned_data['media_url']
            subject = form.cleaned_data.get('subject', '')
            
            # Get Telnyx configuration
            config = APIConfiguration.objects.filter(service='telnyx', is_active=True).first()
            if not config or not config.api_key:
                return HttpResponse("Telnyx not configured. Please configure API settings first.")
            
            try:
                # Define the API endpoint and authentication credentials
                endpoint = "https://api.telnyx.com/v2/faxes"
                api_key = config.api_key

                # Define the fax content and recipient information
                data = {
                    "media_url": media_url,
                    "connection_id": "2047423188568114992",
                    "to": fax_to,
                    "from": config.from_number or "+18177800212",
                }

                # Make the API request to send the fax
                response = requests.post(endpoint, json=data, headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                })

                # Check the API response to see if the fax was sent successfully
                if response.status_code == 201:
                    fax = response.json()
                    
                    # Save to database
                    FaxRecord.objects.create(
                        fax_id=fax['id'],
                        to_number=fax_to,
                        from_number=config.from_number or "+18177800212",
                        status='sent',
                        media_url=media_url,
                        subject=subject
                    )
                    
                    return HttpResponse(f"Fax sent successfully! Fax ID: {fax['id']}")
                else:
                    return HttpResponse(f"Fax failed to send. API response: {response.text}")
            
            except Exception as e:
                return HttpResponse(f"Error sending fax: {str(e)}")
    else:
        form = SendFaxForm()
    
    return render(request, 'send_fax.html', {'form': form})

def fax_list(request):
    """
    Get fax history from database
    """
    try:
        faxes = FaxRecord.objects.all()
        
        # Format data for template
        fax_data = []
        for fax in faxes:
            fax_data.append((
                fax.fax_id,
                fax.to_number,
                fax.from_number,
                fax.status,
                fax.updated_at,
                fax.direction,
                fax.subject,
                fax.num_pages
            ))
        
        context = {
            "fax_data": fax_data,
            "total_count": len(faxes),
        }
        
        return render(request, 'fax_list.html', context)
            
    except Exception as e:
        error_msg = f"Error getting fax history: {str(e)}"
        logger.error(error_msg)
        return render(request, 'fax_list.html', {"error_msg": error_msg})

def fax_detail(request, fax_id):
    """
    Get detailed information about a specific fax
    """
    try:
        fax = FaxRecord.objects.filter(fax_id=fax_id).first()
        
        if not fax:
            return render(request, 'fax_detail.html', {"error_msg": "Fax not found"})
        
        context = {
            "fax": fax
        }
        
        return render(request, 'fax_detail.html', context)
            
    except Exception as e:
        error_msg = f"Error getting fax details: {str(e)}"
        logger.error(error_msg)
        return render(request, 'fax_detail.html', {"error_msg": error_msg})

def single_sms(request):
    if request.method == 'POST':
        form = SendSMSForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            
            # Get Twilio configuration
            config = APIConfiguration.objects.filter(service='twilio', is_active=True).first()
            if not config or not config.account_sid or not config.auth_token:
                return HttpResponse("Twilio not configured. Please configure API settings first.")
            
            try:
                twilio_service = TwilioSMSService()
                result = twilio_service.send_sms(phone_number, message)
                
                # Save to database
                SMSRecord.objects.create(
                    sid=result,
                    to_number=phone_number,
                    from_number=config.from_number or "+15612209629",
                    message=message,
                    status='sent'
                )
                
                return HttpResponse(f"SMS sent successfully! SID: {result}")
            except Exception as e:
                return HttpResponse(f"Error sending SMS: {str(e)}")
    else:
        form = SendSMSForm()
    
    return render(request, 'app/single_sms.html', {'form': form})

def bulk_sms(request):
    if request.method == 'POST':
        form = BulkSMSForm(request.POST)
        if form.is_valid():
            phone_numbers = form.cleaned_data['phone_numbers']
            message = form.cleaned_data['message']
            
            # Get Twilio configuration
            config = APIConfiguration.objects.filter(service='twilio', is_active=True).first()
            if not config or not config.account_sid or not config.auth_token:
                return HttpResponse("Twilio not configured. Please configure API settings first.")
            
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
                        
                        # Save to database
                        SMSRecord.objects.create(
                            sid=result,
                            to_number=phone,
                            from_number=config.from_number or "+15612209629",
                            message=message,
                            status='sent'
                        )
                    except Exception as e:
                        results.append(f"✗ {phone}: Failed - {str(e)}")
                
                return HttpResponse("<br>".join(results))
            except Exception as e:
                return HttpResponse(f"Error sending bulk SMS: {str(e)}")
    else:
        form = BulkSMSForm()
    
    return render(request, 'app/bulk_sms.html', {'form': form})

def test_twilio_connection(request):
    try:
        config = APIConfiguration.objects.filter(service='twilio', is_active=True).first()
        if not config:
            return JsonResponse({"status": "error", "message": "Twilio not configured"})
        
        twilio_service = TwilioSMSService()
        result = twilio_service.test_connection()
        return JsonResponse({"status": "success", "message": result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

def fax_resend(request, fax_id):
    """
    Resend a fax
    """
    try:
        fax = FaxRecord.objects.filter(fax_id=fax_id).first()
        if not fax:
            return JsonResponse({"status": "error", "message": "Fax not found"})
        
        # Get Telnyx configuration
        config = APIConfiguration.objects.filter(service='telnyx', is_active=True).first()
        if not config or not config.api_key:
            return JsonResponse({"status": "error", "message": "Telnyx not configured"})
        
        # Resend fax via Telnyx
        endpoint = "https://api.telnyx.com/v2/faxes"
        api_key = config.api_key
        
        data = {
            "media_url": fax.media_url,
            "connection_id": "2047423188568114992",
            "to": fax.to_number,
            "from": config.from_number or "+18177800212",
        }
        
        response = requests.post(endpoint, json=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        
        if response.status_code == 201:
            new_fax = response.json()
            # Create new record for resent fax
            FaxRecord.objects.create(
                fax_id=new_fax['id'],
                to_number=fax.to_number,
                from_number=config.from_number or "+18177800212",
                status='sent',
                media_url=fax.media_url,
                subject=f"Resent: {fax.subject or ''}"
            )
            return JsonResponse({"status": "success", "message": f"Fax {fax_id} resent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Failed to resend fax"})
            
    except Exception as e:
        error_msg = f"Error resending fax: {str(e)}"
        logger.error(error_msg)
        return JsonResponse({"status": "error", "message": error_msg})

def bulk_fax_generator(request):
    form = BulkFaxForm()
    return render(request, 'app/bulk_fax.html', {'form': form})

def bulk_fax_sender(request):
    if request.method == 'POST':
        form = BulkFaxForm(request.POST)
        if form.is_valid():
            fax_numbers = form.cleaned_data['fax_numbers']
            media_url = form.cleaned_data['media_url']
            subject = form.cleaned_data.get('subject', '')
            
            # Get Telnyx configuration
            config = APIConfiguration.objects.filter(service='telnyx', is_active=True).first()
            if not config or not config.api_key:
                return HttpResponse("Telnyx not configured. Please configure API settings first.")
            
            # Split fax numbers by comma or newline
            fax_list = [fax.strip() for fax in fax_numbers.replace('\n', ',').split(',') if fax.strip()]
            
            if not fax_list:
                return HttpResponse("No valid fax numbers provided")
            
            try:
                endpoint = "https://api.telnyx.com/v2/faxes"
                api_key = config.api_key
                
                results = []
                
                for fax_number in fax_list:
                    try:
                        data = {
                            "media_url": media_url,
                            "connection_id": "2047423188568114992",
                            "to": fax_number,
                            "from": config.from_number or "+18177800212",
                        }
                        
                        response = requests.post(endpoint, json=data, headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        })
                        
                        if response.status_code == 201:
                            fax = response.json()
                            results.append(f"✓ {fax_number}: Success (Fax ID: {fax['id']})")
                            
                            # Save to database
                            FaxRecord.objects.create(
                                fax_id=fax['id'],
                                to_number=fax_number,
                                from_number=config.from_number or "+18177800212",
                                status='sent',
                                media_url=media_url,
                                subject=subject
                            )
                        else:
                            results.append(f"✗ {fax_number}: Failed - {response.text}")
                            
                    except Exception as e:
                        results.append(f"✗ {fax_number}: Error - {str(e)}")
                
                return HttpResponse("<br>".join(results))
            except Exception as e:
                return HttpResponse(f"Error sending bulk faxes: {str(e)}")
    else:
        form = BulkFaxForm()
    
    return render(request, 'app/bulk_fax.html', {'form': form}) 