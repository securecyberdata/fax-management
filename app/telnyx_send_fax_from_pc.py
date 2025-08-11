import requests
import base64
import os


TELNYX_API_ENDPOINT = 'https://api.telnyx.com/v2/media'
TELNYX_API_KEY = os.environ.get('TELNYX_API_KEY', '')


# Upload file to Telnyx Media Storage
media_url = 'C:/Users/dared/Downloads/BONITA R ANDERSON-7404236724-(CGM).pdf'

#"C:\Users\dared\Downloads\BONITA R ANDERSON-7404236724-(CGM).pdf"

data = {
    #"media":"C:/Users/dared/Downloads/BONITA R ANDERSON-7404236724-(CGM).pdf",
    'title':'New',
    'media_url':'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
}

response = requests.post(TELNYX_API_ENDPOINT,json=data,
    headers={"Content-Type": "application/json","Authorization": f"Bearer {TELNYX_API_KEY}"},
)

print(response.text)


# Generate link to file

with open(media_url, 'rb') as file:
    file_contents = file.read()
    file_base64 = base64.b64encode(file_contents).decode('utf-8') 