#Python
import io
import re
import datetime
import os

#Django
from django.http import HttpResponse
from datetime import date
from django.shortcuts import render
from django.utils.six import BytesIO
from django.views.decorators.clickjacking import xframe_options_exempt

#DRF
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

#XML
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree

#PDF
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage


# Create your views here.
def extract_text_by_page(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            # close open handles
            converter.close()
            fake_file_handle.close()


def extract_text(pdf_path):
    fh = open(os.getcwd()+"/TXT/ASGPN0660F_Equity&Commodity_Signed.txt",
              "w", encoding='utf-8')
    for page in extract_text_by_page(pdf_path):
        fh.write(page)
    fh.close()

# @xframe_options_exempt


@api_view(['POST', 'GET'])
def scrap_data(request):
    extract_text(
        pdf_path=os.getcwd()+'/PDF/ASGPN0660F_Equity&Commodity_Signed.pdf')
    # Open the file back and read the contents
    with open(os.getcwd()+"/TXT/ASGPN0660F_Equity&Commodity_Signed.txt", "r", encoding='UTF8') as f:
        if f.mode == 'r':
            contents = f.read()
        top = Element('Customer')
        child = SubElement(top, 'Name')
        Name = re.search('MR(.*)Maiden Name If', contents)
        child.text = Name.group(1)
        Address = re.search(
            'Client Name(.*)Verification of the client signature done by Name of Employee', contents)
        address = re.search('Address(.*)City/Town/Village', Address.group(1))
        City = re.search('City/Town/Village(.*)PIN Code', Address.group(1))
        PIN_Code = re.search('PIN Code(.*)State', Address.group(1))
        State = re.search('State(.*)Tel No.', Address.group(1))
        email = re.findall('\S+@\S+', contents)
        child = SubElement(top, 'Email')
        child.text = email[-1]
        Pan = re.search("PAN(.*)SecondNAHolder", contents)
        Pan_No = re.findall('[A-Z]{5}\d{4}[A-Z]{1}', Pan.group(1))
        mobile_no = re.findall('\d{2}-\d{10}', contents)
        child = SubElement(top, 'Address')
        child.text = address.group(1)
        child = SubElement(top, 'PIN_CODE')
        child.text = PIN_Code.group(1)
        child = SubElement(top, 'State')
        child.text = State.group(1)
        child = SubElement(top, 'City')
        child.text = City.group(1)
        child = SubElement(top, 'Mobile')
        child.text = mobile_no[-1]
        child = SubElement(top, 'Pan_NO')
        child.text = Pan_No[0]
        Aadhaar = re.search("IDClient ID(.*)UID IDDear Sir/Madam,", contents)
        child = SubElement(top, 'Aadhaar')
        child.text = Aadhaar.group(1)
        Customer_Ref_No = re.findall('[A-Z]{2}\d{4}', contents)
        child = SubElement(top, 'Customer_Ref_No')
        child.text = Customer_Ref_No[0]
        DOB = re.search(r'\d{2}/\d{2}/\d{4}', contents)
        Date_Of_Birth = datetime.datetime.strptime(
            DOB.group(), '%m/%d/%Y').date().strftime("%Y-%m-%d")
        child = SubElement(top, 'Date_Of_Birth')
        child.text = Date_Of_Birth
        data = tostring(top)
        Customer = open(
            os.getcwd()+"/XML/Customer.xml", "wb")
        Customer.write(data)
        data_stream = BytesIO(data)
        parsed_data = XMLParser().parse(data_stream)
        print(parsed_data)
        print(data_stream)
        test = ElementTree(top)
        print(test)
        content = JSONRenderer().render(parsed_data).decode("utf-8")
        print(content)
        print(os.getcwd())
        return Response(content, content_type="application/json; charset=utf-8")
        # content = {'please move along': 'nothing to see here'}
        # return Response(parsed_data, status=status.HTTP_404_NOT_FOUND)

# def get_xml(request):
#     return Response(open("D:/Mahendran/Projects/Python/Django/pdf_scraper/XML/Customer.xml").read(), content_type="text/xml; charset=utf-8")
# def get_xml(request):
