import random

from Auth.models.permissions_model import Module, Permission
from Auth.models.user_model import User
from helpers.status_codes import EmptyParameters

# def validate_email(s):
#    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
#    if not re.match(pat,s):
#       raise InvalidEmail()


def check_required_fields(data, fields):
    empty_fields = [f"{field} is required" for field in fields if not data.get(field)]
    if empty_fields:
        default_detail = {
            "status": "error",
            "code": 309,
            "detail": empty_fields,
        }
        raise EmptyParameters(default_detail)


def generate_password_reset_code():
    reset_code = random.randint(100000, 999999)
    try:
        User.objects.get(password_reset_code=reset_code)
        generate_password_reset_code()
    except User.DoesNotExist:
        return reset_code


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


# Check user module permision
def check_permission(user, module_name, access_level):
    module = Module.objects.get(name=module_name)
    permission = Permission.objects.get(role_id=user.role_id, module=module)
    return permission.access_level in access_level


# Check Super Admin permissions
def check_super_admin(user):
    return user.is_admin
