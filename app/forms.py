from django import forms
from .models import APIConfiguration

class UploadFileForm(forms.Form):
    file = forms.FileField()

class SingleSMSForm(forms.Form):
    name = forms.CharField(max_length=100, label='Patient Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    pcp_name = forms.CharField(max_length=100, label='Doctor/PCP Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, label='Phone Number', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1234567890'}))
    device_name = forms.CharField(max_length=100, label='Device Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CGM Device, Back Brace'}))
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, phone))
        if len(digits_only) < 10:
            raise forms.ValidationError("Phone number must have at least 10 digits.")
        return phone

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