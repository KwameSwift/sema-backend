from rest_framework.exceptions import APIException


class EmptyParameters(APIException):
    status_code = 309
    default_detail = {
        "status": "error",
        "code": status_code,
        "detail": "Empty parameter",
    }


def non_existing_data_exception(message):
    class DataDoesNotExist(APIException):
        status_code = 310
        default_detail = {
            "status": "error",
            "code": status_code,
            "detail": f"{message} does not exist",
        }

    return DataDoesNotExist


def duplicate_data_exception(message):
    class DuplicateData(APIException):
        status_code = 311
        default_detail = {
            "status": "error",
            "code": status_code,
            "detail": f"{message} already exists",
        }

    return DuplicateData


class WrongCredentials(APIException):
    status_code = 312
    default_detail = {
        "status": "error",
        "code": status_code,
        "detail": "Incorrect cedentials",
    }


class WrongCode(APIException):
    status_code = 313
    default_detail = {
        "status": "error",
        "code": status_code,
        "detail": "Code is invalid",
    }


class PasswordMismatch(APIException):
    status_code = 314
    default_detail = {
        "status": "error",
        "code": status_code,
        "detail": "Passwords do not match",
    }


def cannot_perform_action(message):
    class CannotPerformAction(APIException):
        status_code = 315
        default_detail = {"status": "error", "code": status_code, "detail": message}

    return CannotPerformAction


class WrongPassword(APIException):
    status_code = 316
    default_detail = {
        "status": "error",
        "code": status_code,
        "detail": "Wrong password",
    }


def action_authorization_exception(message):
    class InvalidAction(APIException):
        status_code = 317
        default_detail = {"status": "error", "code": status_code, "detail": message}

    return InvalidAction
