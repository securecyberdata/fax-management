from pdf2docx import Converter
import os

# # # dir_path for input reading and output files & a for loop # # #

path_input = "C:/pythonProject/pdf/html2pdf/django-html-2-pdf/htmltopdf/braces/Knee code updated.pdf"
path_output = 'C:/pythonProject/pdf/html2pdf/django-html-2-pdf/htmltopdf/braces/output/'
cv = Converter(path_input)
cv.convert(path_output+'Knee code updated.docx')
cv.close()
#print(file)


'''
for file in os.listdir(path_input):
    cv = Converter(path_input+file)
    cv.convert(path_output+file+'.docx', start=0, end=None)
    cv.close()

    print(file)
    '''
"C:\pythonProject\pdf\html2pdf\django-html-2-pdf\htmltopdf\braces\Knee code updated.pdf"