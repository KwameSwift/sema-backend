import re
import uuid
# from Loan.models.loan_model import Loan

from helpers.status_codes import EmptyParameters

# def validate_email(s):
#    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
#    if not re.match(pat,s):
#       raise InvalidEmail()

def check_parameters(data, param):
   if not data:
      status_code = 309
      default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": param + " is required",
      }
      raise EmptyParameters(default_detail)
   
# def generate_reset_code():
#    loan_id = uuid.uuid4().hex[:6]
#    keys = Loan.objects.filter(id=loan_id)
#    while keys.exists():
#       keys = Loan.objects.filter(id=loan_id)
#       loan_id = 'LLMS'+uuid.uuid4().hex[:6]
#    return loan_id.upper()

def flatten_list(input_list: list, output_list: list):
   for item in input_list:
         if type(item) is list:
            flatten_list(item, output_list)
         else:
            output_list.append(item)
            
def capitalizeFirstLetters(name: str):
   splt_name = str(name).split(" ")
   try:
      nm_1 = splt_name[0]
      nm_2 = splt_name[1]
      final_name = nm_1.capitalize() + " " + nm_2.capitalize()
   except IndexError:
      final_name = name.capitalize()
   
   return final_name


def unique_list(list_of_items):
   unique_list = []
   for x in list_of_items:
      if x not in unique_list:
         unique_list.append(x)
   return unique_list
      