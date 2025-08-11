
'''
import ftplib
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from docx2pdf import convert



# Replace 'testfile.txt' with the name of the file you want to upload
#with open('1.pdf', 'rb') as f:
#    ftp.storbinary('STOR 1.pdf', f)

# Get the URL of the uploaded file




def select_file(file_path):
    if file_path:
        try:
            with open(file_path, "rb") as file:
                convert(file.name)(file_path.replace(".docx", ".pdf"))
                messagebox.showinfo("Success", "The file has been successfully converted to PDF.")
        except:
            messagebox.showinfo("Failed to convert")

def upload_ftp(file_path):
    ftp = ftplib.FTP('ftp.rytsoft.com')
    ftp.login('rytsoftcrm@rytsoft.com', "(12345!L0veUSA67890)")
    url = f"https://ftp.rytsoft.com/rytsoftcrm"  # Replace 'ftp.example.com' with the actual FTP server hostname
    print(f"File uploaded successfully. URL: {url}")
    ftp.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
    select_file(file_path)
    upload_ftp(file_path)
'''
import ftplib
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from docx2pdf import convert
import os

def select_file():
    # Select the Word document to convert
    file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
    if file_path:
        try:
            # Convert the Word document to PDF
            pdf_path = file_path.replace(".docx", ".pdf")
            convert(file_path, pdf_path)
            print("I'm pdf_path (Before):  ", pdf_path)
            pdf_path = pdf_path.replace(os.path.sep, '/')
            print("I'm pdf_path (After):  ", pdf_path)
            messagebox.showinfo("Success", "The file has been successfully converted to PDF.")
            return pdf_path
        except:
            messagebox.showinfo("Failed to convert")

def upload_ftp(pdf_path):
    # Upload the PDF file to the FTP server
    with open(pdf_path, "rb") as file:
        ftp = ftplib.FTP('ftp.rytsoft.com')
        ftp.login('newcrmadm@rytsoft.com', '[12345l0VeU$@98765]')
        ftp.cwd('public_html/rytsoftcrm')  # Replace '/rytsoftcrm' with the directory on the FTP server where you want to upload the file
        pdf_filename = os.path.basename(pdf_path)
        ftp.storbinary(f"STOR {pdf_filename}", file)
        url = f"http://ftp.rytsoft.com/{pdf_path}"  # Replace 'ftp.example.com' with the actual FTP server hostname
        print(f"File uploaded successfully. URL: {pdf_filename}")
        ftp.quit()

if __name__ == "__main__":
    file_path = select_file()
    print("I'm from main calling file_path: ",file_path)
    if file_path:
        upload_ftp(file_path)






'''  working
ftp = ftplib.FTP('ftp.rytsoft.com')
ftp.login('rytsoftcrm@rytsoft.com', '(12345!L0veUSA67890)')
file_path = 'C:/Users/dared/Downloads/faxattach-ATT5997941955791813554.pdf'

# Replace 'testfile.txt' with the name of the file you want to upload
with open(file_path, 'rb') as f:
    ftp.cwd('/rytsoftcrm')
    pdf_filename = os.path.basename(file_path)
    #ftp.storbinary(f'STOR 1.pdf',f) Working
    ftp.storbinary(f"STOR {pdf_filename}",f)

# Get the URL of the uploaded file
url = f"https://ftp.rytsoft.com/{f}"  # Replace 'ftp.example.com' with the actual FTP server hostname
print(f"File uploaded successfully. URL: {url}")

ftp.quit()
'''

