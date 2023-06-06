import datetime

from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User
from helpers.functions import paginate_data
from helpers.status_codes import duplicate_data_exception, non_existing_data
from helpers.validations import check_required_fields
