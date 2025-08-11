from django import forms
from .models import APIConfiguration

class SingleFaxForm(forms.Form):
    """Simple form for single fax generation"""
    DEVICE_CHOICES = [
        ('cgm', 'CGM (Continuous Glucose Monitor)'),
        ('ankle', 'Ankle Brace'),
        ('knee', 'Knee Brace'),
        ('back', 'Back Brace'),
        ('hip', 'Hip Brace'),
        ('shoulder', 'Shoulder Brace'),
        ('wrist', 'Wrist Brace'),
    ]
    
    # Device Selection
    device_type = forms.ChoiceField(
        choices=DEVICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        required=True,
        label='Select Device Type'
    )
    
    # Patient Information
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter patient name'
        }),
        required=True,
        label='Patient Name'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number'
        }),
        label='Phone'
    )
    
    address = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address'
        }),
        label='Address'
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        }),
        label='City'
    )
    
    state = forms.CharField(
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
            'maxlength': '2'
        }),
        label='State'
    )
    
    zip = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP Code',
            'maxlength': '10'
        }),
        label='ZIP'
    )
    
    dob = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date of Birth'
    )
    
    medicare = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Medicare information'
        }),
        label='Medicare'
    )
    
    # PCP Information
    pcp_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primary Care Physician name'
        }),
        label='PCP Name'
    )
    
    pcp_address = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP address'
        }),
        label='PCP Address'
    )
    
    pcp_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP city'
        }),
        label='PCP City'
    )
    
    pcp_state = forms.CharField(
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP state',
            'maxlength': '2'
        }),
        label='PCP State'
    )
    
    pcp_zip = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP ZIP',
            'maxlength': '10'
        }),
        label='PCP ZIP'
    )
    
    pcp_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP phone'
        }),
        label='PCP Phone'
    )
    
    pcp_fax = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP fax'
        }),
        label='PCP Fax'
    )
    
    pcp_npi = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PCP NPI number'
        }),
        label='PCP NPI'
    )

class BulkUploadForm(forms.Form):
    """Form for bulk fax generation from CSV/Excel files"""
    DEVICE_CHOICES = [
        ('cgm', 'CGM (Continuous Glucose Monitor)'),
        ('ankle', 'Ankle Brace'),
        ('knee', 'Knee Brace'),
        ('back', 'Back Brace'),
        ('hip', 'Hip Brace'),
        ('shoulder', 'Shoulder Brace'),
        ('wrist', 'Wrist Brace'),
    ]
    
    device_type = forms.ChoiceField(
        choices=DEVICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        required=True,
        label='Select Device Type for All Records'
    )
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        required=True,
        label='Upload CSV or Excel File',
        help_text='File should contain columns: name, phone, address, city, state, zip, dob, medicare, pcp_name, pcp_address, pcp_city, pcp_state, pcp_zip, pcp_phone, pcp_fax, pcp_npi'
    )

class TelnyxConfigForm(forms.ModelForm):
    """Form for Telnyx API configuration"""
    class Meta:
        model = APIConfiguration
        fields = ['api_key', 'from_number']
        widgets = {
            'api_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Telnyx API key'
            }),
            'from_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Telnyx phone number (e.g., +1234567890)'
            })
        }

class HumbleFaxConfigForm(forms.ModelForm):
    """Form for HumbleFax API configuration"""
    class Meta:
        model = APIConfiguration
        fields = ['api_key', 'secret_key', 'from_number']
        widgets = {
            'api_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your HumbleFax access key'
            }),
            'secret_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your HumbleFax secret key'
            }),
            'from_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your HumbleFax phone number'
            })
        }

class TwilioConfigForm(forms.ModelForm):
    """Form for Twilio API configuration"""
    class Meta:
        model = APIConfiguration
        fields = ['account_sid', 'auth_token', 'from_number']
        widgets = {
            'account_sid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Twilio Account SID'
            }),
            'auth_token': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Twilio Auth Token'
            }),
            'from_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Twilio phone number'
            })
        }

class SendFaxForm(forms.Form):
    """Form for sending faxes"""
    fax_to = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter fax number (e.g., +1234567890)'
        })
    )
    media_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter media URL (PDF, image, etc.)'
        })
    )
    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject (optional)'
        })
    )

class SendSMSForm(forms.Form):
    """Form for sending SMS"""
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number (e.g., +1234567890)'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your message'
        })
    )

class BulkFaxForm(forms.Form):
    """Form for bulk fax operations"""
    fax_numbers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter fax numbers (one per line or comma-separated)'
        })
    )
    media_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter media URL (PDF, image, etc.)'
        })
    )
    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject (optional)'
        })
    )

class BulkSMSForm(forms.Form):
    """Form for bulk SMS operations"""
    phone_numbers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter phone numbers (one per line or comma-separated)'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your message'
        })
    )