from django import forms 

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

class BulkSMSForm(forms.Form):
    file = forms.FileField(
        label='Upload CSV/Excel File',
        help_text='File should contain columns: name, pcp_name, phone, device_name',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )