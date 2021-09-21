import pdfkit as pdf
import jinja2 
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(BASE_DIR, 'aero_infos_management/aero_info_management/templates'))
print(BASE_DIR)
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE1 = "notam.html"
TEMPLATE_FILE2 = "supp_aip.html"
TEMPLATE_FILE3 = "aic.html"
template1 = templateEnv.get_template(TEMPLATE_FILE1)
template2 = templateEnv.get_template(TEMPLATE_FILE2)
template3 = templateEnv.get_template(TEMPLATE_FILE3)
# This data can come from database query

def generate(data, type_ddia):
    if type_ddia == 'demandenotam':
        sourceHtml = template1.render(json_data=data) 
    elif type_ddia == 'demandesupp':
        sourceHtml = template2.render(json_data=data) 
    elif type_ddia == 'demandeaic':
        sourceHtml = template3.render(json_data=data) 
    return pdf.from_string(sourceHtml,"api/files/ddia.pdf")        



def generate_aic(data):
    sourceHtml = template3.render(json_data=data) 
    pdf.from_string(sourceHtml,"filesDDIA/aic.pdf")
    
def generate_notam(data):
    sourceHtml = template1.render(json_data=data) 
    pdf.from_string(sourceHtml,"filesDDIA/notam.pdf")

def generate_supp(data):
    sourceHtml = template2.render(json_data=data) 
    pdf.from_string(sourceHtml,"filesDDIA/suppaip.pdf")

def delete_aic():
    os.remove("filesDDIA/aic.pdf")

def delete_notam():
    os.remove("filesDDIA/notam.pdf")

def delete_supp():
    os.remove("filesDDIA/suppaip.pdf")


# body = {
# "dataNOTAM":{
#     "id": "string",
#     "ident_ddia": "string",
#     "deposit_datetime": "Date",
#     "unit":{   "id": "string",
#                 "email": "string",
#                 "name": "string",
#                 "phone_number": "string",
#                 "fax": "string",
#                 "address": "string",
#                 "rsfta": "string",} ,
#     "location_indicator": "string",
#     "state": "string",
#     "publication_code": "string",
#     "code_notam_replaceorcancel": "string",
#     "range_action": "string",
#     "type_notam": "string",
#     "coords": "string",
#     "validity_period_type": "string",
#     "start_val_period": "string",
#     "end_val_period": "string",
#     "daily_freq_type": "string",
#     "daily_freq_start": "string",
#     "daily_freq_end": "string",
#     "lower_vertical_limit": "string",
#     "upper_vertical_limit": "string",
#     "descriptive_text": "string",
# },
# "dataSUPPAIP":{
#     "id": "string",
#     "ident_ddia": "string",
#     "deposit_datetime": "Date",
#     "unit": {   "id": "string",
#                 "email": "string",
#                 "name": "string",
#                 "phone_number": "string",
#                 "fax": "string",
#                 "address": "string",
#                 "rsfta": "string",},
#     "location_indicator": "string",
#     "state:": "string",
#     "code_ddia_replaced": "string",
#     "publication_code": "string",
#     "type_suppaip": "string",
#     "object": "string",
#     "aip_target_sections": "string",
#     "start_val_period": "Date",
#     "end_val_period": "Date",
#     "descriptive_text": "string",
# },
# "dataAIC":{
#     "id": "string",
#     "ident_ddia": "string",
#     "deposit_datetime": "Date",
#     "unit": {   "id": "string",
#                 "email": "string",
#                 "name": "string",
#                 "phone_number": "string",
#                 "fax": "string",
#                 "address": "string",
#                 "rsfta": "string",},
#     "location_indicator": "string",
#     "state:": "string",
#     "code_ddia_replaced": "string",
#     "publication_code": "string",
#     "subject": "string",
#     "object": "string",
#     "descriptive_text": "string",
# }
# }
# This renders template with dynamic data 
