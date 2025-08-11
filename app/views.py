import os
import base64
import logging
import csv
import tempfile
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import FaxRecord, SMSRecord, APIConfiguration
from .forms import (
    TelnyxConfigForm, HumbleFaxConfigForm, TwilioConfigForm,
    SendFaxForm, SendSMSForm, BulkFaxForm, BulkSMSForm, SingleFaxForm, BulkUploadForm
)
from .document_generator import DocumentGenerator
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
    if request.method == 'POST':
        form = SingleFaxForm(request.POST)
        if form.is_valid():
            # Process the form data and generate fax document
            device_type = form.cleaned_data['device_type']
            
            # Convert form data to dictionary
            form_data = {
                'name': form.cleaned_data.get('name', ''),
                'phone': form.cleaned_data.get('phone', ''),
                'address': form.cleaned_data.get('address', ''),
                'city': form.cleaned_data.get('city', ''),
                'state': form.cleaned_data.get('state', ''),
                'zip': form.cleaned_data.get('zip', ''),
                'dob': form.cleaned_data.get('dob', ''),
                'medicare': form.cleaned_data.get('medicare', ''),
                'pcp_name': form.cleaned_data.get('pcp_name', ''),
                'pcp_address': form.cleaned_data.get('pcp_address', ''),
                'pcp_city': form.cleaned_data.get('pcp_city', ''),
                'pcp_state': form.cleaned_data.get('pcp_state', ''),
                'pcp_zip': form.cleaned_data.get('pcp_zip', ''),
                'pcp_phone': form.cleaned_data.get('pcp_phone', ''),
                'pcp_fax': form.cleaned_data.get('pcp_fax', ''),
                'pcp_npi': form.cleaned_data.get('pcp_npi', ''),
            }
            
            try:
                # Generate the document
                doc_generator = DocumentGenerator()
                temp_path, filename = doc_generator.generate_from_template(form_data, device_type)
                
                # Read the generated file
                with open(temp_path, 'rb') as f:
                    file_content = f.read()
                
                # Clean up temporary file
                os.remove(temp_path)
                
                # Return the file for download
                response = HttpResponse(file_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
                
            except Exception as e:
                # If document generation fails, show error message
                return HttpResponse("""
                    <div style='text-align: center; padding: 50px;'>
                        <h2 style='color: red;'>✗ Error Generating Document</h2>
                        <p>An error occurred while generating the document: {}</p>
                        <br>
                        <a href="{}" class="btn btn-primary">Try Again</a>
                        <a href="{}" class="btn btn-secondary">Back to Dashboard</a>
                    </div>
                """.format(
                    str(e),
                    request.path,
                    reverse('dashboard')
                ))
    else:
        form = SingleFaxForm()
    
    return render(request, 'app/freestyle.html', {'form': form})

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
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            device_type = form.cleaned_data['device_type']
            csv_file = form.cleaned_data['csv_file']
            
            try:
                # Process the CSV file
                if csv_file.name.endswith('.csv'):
                    # Process CSV file
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    records = list(reader)
                else:
                    # For Excel files, we'll need to add xlrd or openpyxl support later
                    return HttpResponse("Excel file support coming soon. Please use CSV format for now.")
                
                if not records:
                    return HttpResponse("No records found in the CSV file.")
                
                # Generate documents for each record
                doc_generator = DocumentGenerator()
                generated_files = []
                
                for i, record in enumerate(records):
                    try:
                        # Convert CSV record to form data format
                        form_data = {
                            'name': record.get('name', ''),
                            'phone': record.get('phone', ''),
                            'address': record.get('address', ''),
                            'city': record.get('city', ''),
                            'state': record.get('state', ''),
                            'zip': record.get('zip', ''),
                            'dob': record.get('dob', ''),
                            'medicare': record.get('medicare', ''),
                            'pcp_name': record.get('pcp_name', ''),
                            'pcp_address': record.get('pcp_address', ''),
                            'pcp_city': record.get('pcp_city', ''),
                            'pcp_state': record.get('pcp_state', ''),
                            'pcp_zip': record.get('pcp_zip', ''),
                            'pcp_phone': record.get('pcp_phone', ''),
                            'pcp_fax': record.get('pcp_fax', ''),
                            'pcp_npi': record.get('pcp_npi', ''),
                        }
                        
                        # Generate document
                        temp_path, filename = doc_generator.generate_from_template(form_data, device_type)
                        generated_files.append((temp_path, filename))
                        
                    except Exception as e:
                        print(f"Error processing record {i+1}: {e}")
                        continue
                
                if not generated_files:
                    return HttpResponse("Failed to generate any documents. Please check your CSV format.")
                
                # Create a ZIP file containing all generated documents
                import zipfile
                zip_path = os.path.join(tempfile.gettempdir(), f"bulk_fax_{device_type}.zip")
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for temp_path, filename in generated_files:
                        zipf.write(temp_path, filename)
                        # Clean up individual temp files
                        os.remove(temp_path)
                
                # Read and return the ZIP file
                with open(zip_path, 'rb') as f:
                    zip_content = f.read()
                
                # Clean up ZIP file
                os.remove(zip_path)
                
                # Return the ZIP file for download
                response = HttpResponse(zip_content, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="bulk_fax_{device_type}.zip"'
                return response
                
            except Exception as e:
                return HttpResponse("""
                    <div style='text-align: center; padding: 50px;'>
                        <h2 style='color: red;'>✗ Error Processing File</h2>
                        <p>An error occurred while processing the file: {}</p>
                        <br>
                        <a href="{}" class="btn btn-primary">Try Again</a>
                        <a href="{}" class="btn btn-secondary">Back to Dashboard</a>
                    </div>
                """.format(
                    str(e),
                    request.path,
                    reverse('dashboard')
                ))
    else:
        form = BulkUploadForm()
    
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