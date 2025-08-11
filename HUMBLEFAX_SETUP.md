# HumbleFax API Integration Setup

This guide will help you set up the HumbleFax API integration for automatic fax sending.

## Prerequisites

1. A HumbleFax account with API access
2. Your HumbleFax API Access Key and Secret Key
3. A verified fax number to send from

## Configuration

### Option 1: Environment Variables (Recommended)

Set the following environment variables:

```bash
export HUMBLEFAX_ACCESS_KEY="0a80daf11e930e43ea174b7e"
export HUMBLEFAX_SECRET_KEY="4f5305567e39032f83498e0b"
export HUMBLEFAX_FROM_NUMBER="+14695019073"
```

### Option 2: Direct Settings Configuration

Edit `blank_django/settings.py` and replace the placeholder values:

```python
HUMBLEFAX_ACCESS_KEY = '0a80daf11e930e43ea174b7e'
HUMBLEFAX_SECRET_KEY = '4f5305567e39032f83498e0b'
HUMBLEFAX_FROM_NUMBER = '+14695019073'
```

## Authentication Method

The integration uses Basic Authentication with:
- **Access Key** as the username
- **Secret Key** as the password

The credentials are base64 encoded and sent in the Authorization header.

## Features

### Single Fax Generation
- Check the "Automatically send fax to PCP after generation" checkbox
- The system will generate the document and automatically send it to the PCP fax number
- You'll receive a success message with the fax ID if sent successfully

### Bulk Fax Generation
- Check the "Automatically send faxes to PCP after generation" checkbox
- Upload your CSV/Excel file with PCP fax numbers
- The system will generate all documents and send faxes automatically
- You'll receive a summary of successful and failed fax sends

## CSV/Excel File Requirements

Your input file must include these columns:
- `name` - Patient name
- `dob` - Date of birth
- `phone` - Patient phone
- `address` - Patient address
- `city` - Patient city
- `state` - Patient state
- `zip` - Patient ZIP code
- `medicare` - Medicare number
- `pcp_name` - PCP name
- `pcp_address` - PCP address
- `pcp_city` - PCP city
- `pcp_state` - PCP state
- `pcp_zip` - PCP ZIP code
- `pcp_phone` - PCP phone
- `pcp_fax` - PCP fax number (required for auto-send)
- `pcp_npi` - PCP NPI

## API Endpoints

The integration uses the following HumbleFax API endpoints:
- `POST /v1/faxes` - Send a fax
- `GET /v1/faxes/{fax_id}` - Get fax status
- `GET /v1/faxes` - List faxes

## Troubleshooting

1. **Authentication errors**: Verify your Access Key and Secret Key are correct
2. **Fax not sending**: Check that the PCP fax number is in the correct format (e.g., +1234567890)
3. **API errors**: Verify your HumbleFax account has sufficient credits
4. **Network errors**: Check your internet connection and HumbleFax service status

## Logs

All fax sending activities are logged in `bulk_fax.log` for debugging purposes. The service includes detailed logging for:
- API request/response details
- Authentication headers (without exposing credentials)
- Success/failure status for each fax

## Security Notes

- Never commit your actual Access Key or Secret Key to version control
- Use environment variables for production deployments
- Regularly rotate your API credentials
- The service uses Basic Authentication with base64 encoding 