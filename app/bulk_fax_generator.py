import pandas as pd
import os
import zipfile
from datetime import datetime
from docx import Document
import tempfile
import shutil
from docxtpl import DocxTemplate
import io
from django.conf import settings
import logging
from .humblefax_service import HumbleFaxService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bulk_fax.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BulkFaxGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = settings.BASE_DIR
        self.humblefax = HumbleFaxService()
        logger.info(f"Initialized BulkFaxGenerator with temp_dir: {self.temp_dir}")
        logger.info(f"Base directory: {self.base_dir}")
        
    def read_input_file(self, file_path):
        """Read CSV or Excel file and return a pandas DataFrame"""
        logger.info(f"Reading input file: {file_path}")
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                logger.info(f"Successfully read CSV file with {len(df)} rows")
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
                logger.info(f"Successfully read Excel file with {len(df)} rows")
            else:
                raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
            
            logger.info(f"Columns found in file: {', '.join(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Error reading input file: {str(e)}")
            raise

    def generate_fax_for_record(self, record, template_path, auto_send=False):
        """Generate a single fax document for a record"""
        logger.info(f"Generating fax for record with template: {template_path}")
        try:
            # Get absolute path for template
            template_abs_path = os.path.join(self.base_dir, template_path)
            logger.info(f"Template absolute path: {template_abs_path}")
            
            if not os.path.exists(template_abs_path):
                logger.error(f"Template file not found: {template_abs_path}")
                raise ValueError(f"Template file not found: {template_abs_path}")
            
            # Use DocxTemplate for better template handling
            doc = DocxTemplate(template_abs_path)
            logger.info("Successfully loaded template")
            
            # Prepare the context with all possible fields
            context = {
                "name": record.get('name', ''),
                "phone": record.get('phone', ''),
                "dob": record.get('dob', ''),
                "email": record.get('email', ''),
                "address": record.get('address', ''),
                "city": record.get('city', ''),
                "state": record.get('state', ''),
                "zip": record.get('zip', ''),
                "insurance": record.get('insurance', ''),
                "medicare": record.get('medicare', ''),
                "pcp_name": record.get('pcp_name', ''),
                "pcp_phone": record.get('pcp_phone', ''),
                "pcp_npi": record.get('pcp_npi', ''),
                "pcp_fax": record.get('pcp_fax', ''),
                "pcp_address": record.get('pcp_address', ''),
                "pcp_city": record.get('pcp_city', ''),
                "pcp_state": record.get('pcp_state', ''),
                "pcp_zip": record.get('pcp_zip', ''),
                "date": record.get('date', ''),
                "height": record.get('height', ''),
                "weight": record.get('weight', '')
            }
            logger.info(f"Prepared context for template with name: {context['name']}")

            # Render the template with the context
            doc.render(context)
            logger.info("Successfully rendered template")
            
            # Determine fax type for filename
            template_name = os.path.basename(template_path)
            fax_type_mapping = {
                'do.docx': 'CGM-Template',
                'Back_DO.docx': 'Back-Brace',
                'Ankle_DO.docx': 'Ankle-Brace',
                'Hip_DO.docx': 'Hip-Brace',
                'Elbow_DO.docx': 'Elbow-Brace',
                'Shoulder_DO.docx': 'Shoulder-Brace',
                'lymphodema-Arms.docx': 'Lymphodema-Arms',
                'lymphodema-full-legs.docx': 'Lymphodema-full-legs',
                'lymphodema-leg.docx': 'Lymphodema-leg',
            }
            fax_type = fax_type_mapping.get(template_name, 'Unknown-Type')

            # Get patient name and sanitize for filename
            patient_name = record.get('name', 'NoName')
            # Replace spaces and potentially other unsafe characters with hyphens
            safe_patient_name = "".join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in patient_name.replace(' ', '-'))
            # Avoid multiple consecutive hyphens
            safe_patient_name = '-'.join(filter(None, safe_patient_name.split('-')))

            # Save the generated document with the new naming convention
            output_filename = f"{safe_patient_name}-{fax_type}.docx"
            output_path = os.path.join(self.temp_dir, output_filename)
            doc.save(output_path)
            logger.info(f"Saved generated fax to: {output_path}")
            
            # Auto-send fax if requested and PCP fax number is provided
            fax_result = None
            if auto_send and record.get('pcp_fax'):
                try:
                    # Read the generated document
                    with open(output_path, 'rb') as f:
                        doc_content = f.read()
                    
                    # Send fax using HumbleFax
                    fax_result = self.humblefax.send_fax(
                        to_number=record.get('pcp_fax'),
                        document_content=doc_content,
                        filename=output_filename,
                        patient_name=patient_name
                    )
                    
                    if fax_result['success']:
                        logger.info(f"Fax sent successfully to {record.get('pcp_fax')} for patient {patient_name}. Fax ID: {fax_result.get('fax_id', 'N/A')}")
                    else:
                        logger.warning(f"Failed to send fax to {record.get('pcp_fax')} for patient {patient_name}: {fax_result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error sending fax for patient {patient_name}: {str(e)}")
                    fax_result = {
                        'success': False,
                        'error': str(e),
                        'message': 'Error sending fax'
                    }
            
            return {
                'path': output_path,
                'filename': output_filename,
                'fax_result': fax_result
            }
            
        except Exception as e:
            logger.error(f"Error generating fax: {str(e)}")
            raise

    def process_bulk_faxes(self, input_file_path, template_path, auto_send=False):
        """Process bulk faxes from input file"""
        logger.info(f"Starting bulk fax processing with template: {template_path}, auto_send: {auto_send}")
        try:
            # Read input file
            df = self.read_input_file(input_file_path)
            
            # Validate required columns
            required_columns = ['name', 'dob', 'phone', 'address', 'city', 'state', 'zip', 
                              'medicare', 'pcp_name', 'pcp_address', 'pcp_city', 
                              'pcp_state', 'pcp_zip', 'pcp_phone', 'pcp_fax', 'pcp_npi']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {', '.join(missing_columns)}")
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Generate faxes for each record
            generated_files = []
            fax_results = []
            for index, record in df.iterrows():
                try:
                    logger.info(f"Processing record {index + 1} of {len(df)}")
                    result = self.generate_fax_for_record(record.to_dict(), template_path, auto_send)
                    generated_files.append(result['path'])
                    if result.get('fax_result'):
                        fax_results.append({
                            'record_index': index + 1,
                            'patient_name': record.get('name', 'Unknown'),
                            'fax_number': record.get('pcp_fax', 'N/A'),
                            'fax_result': result['fax_result']
                        })
                    logger.info(f"Successfully generated fax for record {index + 1}")
                except Exception as e:
                    logger.error(f"Error processing record {index + 1}: {str(e)}")
                    continue
            
            if not generated_files:
                logger.error("No faxes were generated successfully")
                raise Exception("No faxes were generated successfully")
            
            # Create ZIP file
            zip_path = os.path.join(self.temp_dir, f"generated_faxes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            logger.info(f"Creating ZIP file at: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in generated_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            logger.info(f"Successfully created ZIP file with {len(generated_files)} faxes")
            
            # Return results
            return {
                'zip_path': zip_path,
                'generated_count': len(generated_files),
                'fax_results': fax_results
            }
            
        except Exception as e:
            logger.error(f"Error in process_bulk_faxes: {str(e)}")
            raise
        finally:
            logger.info("Cleaning up temporary directory") 