from rest_framework.exceptions import APIException

class EmptyParameters(APIException):
    status_code = 309
    default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": "Empty parameter",
    }

class InvalidData(APIException):
    status_code = 310
    default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": "Invalid data",
    }

class ContactAlreadyExists(APIException):
    status_code = 311
    default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": "Phone number already exists",
    }


class UserDoesNotExist(APIException):
    status_code = 312
    default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": "User does not exist",
    }


class UserAlreadyExists(APIException):
    status_code = 313
    default_detail = {
        "status": 'error',
        "code": status_code,
        "detail": "User already exists with same phone number"
    }

class KeyError(APIException):
    status_code = 314
    default_detail = {
        "status": 'error', 
        "code": status_code,
        "detail": "Key error"
        }

class WrongPassword(APIException):
    status_code = 315
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Password incorrect"
        }

class PasswordLengthValidation(APIException):
    status_code = 316
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Minimum 6 Characters"}

class PasswordMismatch(APIException):
    status_code = 317
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Passwords mismatch"}

class BorrowerDoesNotExist(APIException):
    status_code = 318
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Borrower does not exist"}
    
class BorrowerAlreadyExists(APIException):
    status_code = 319
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Borrower already exists"}
    
class FileDoesNotExist(APIException):
    status_code = 320
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "File does not exist"}
    
class GuarantorDoesNotExist(APIException):
    status_code = 321
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Guarantor does not exist"}
    
class GuarantorAlreadyExists(APIException):
    status_code = 322
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Guarantor already exists"}

class LoanDoesNotExist(APIException):
    status_code = 323
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Loan does not exist"}
    
class NextOfKinDoesNotExist(APIException):
    status_code = 324
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Next of kin does not exist"}

class UserAccountUnverified(APIException):
    status_code = 325
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Account deactivated. Please contact admin"}
    
class RepaymentDoesNotExist(APIException):
    status_code = 326
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Repayment does not exist"}
    
class TransactionDoesNotExist(APIException):
    status_code = 327
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Transaction does not exist"}
    
class CannotPerformAction(APIException):
    status_code = 328
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Entry approved, action can not be performed"}
    
class EarningDoesNotExist(APIException):
    status_code = 329
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Transaction does not exist"} 
    
class PayslipDoesNotExist(APIException):
    status_code = 330
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Payslip does not exist"} 
    

class TicketDoesNotExist(APIException):
    status_code = 331
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Ticket does not exist"}
    
class EntryDoesNotExist(APIException):
    status_code = 332
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Entry does not exist"}


class SomethingWentWrong(APIException):
    status_code = 333
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Something went wrong. Try again later!"}
    
class InvalidOTP(APIException):
    status_code = 334
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "Invalid OTP!"}

class OTPExpired(APIException):
    status_code = 335
    default_detail = {
        "status": 'error', 
        "code": status_code, 
        "detail": "OTP has expired!"}
