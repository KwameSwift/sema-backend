import os
import datetime
import requests
from Auth.models import User
from Auth.models.user_model import Country
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models.user_model import User, UserRole
from helpers.email_sender import send_email
from helpers.functions import generate_random_string, paginate_data
from helpers.status_codes import (action_authorization_exception, cannot_perform_action,
                                  duplicate_data_exception,
                                  non_existing_data_exception)
from helpers.validations import check_required_fields, check_super_admin



class AddCountries(APIView):
    def post(self, request, *args, **kwargs):

        countries_data = []
        response = requests.get(url=os.environ.get("COUNTRIES_API"))
        data = response.json()
        for country in data:
            countries_data.append(
                Country(
                    name = country['name'],
                    abbreviation = country['alpha3Code'],
                    calling_code = '+'+country['callingCodes'][0],
                    flag = country['flags']['png'],
                )
                )
        Country.objects.bulk_create(countries_data, batch_size=10000, ignore_conflicts=True)
        log_msg = '========= Uploading ' + str(len(countries_data)) + ' records ============'
        print(log_msg)

        return JsonResponse({'detail': 'Countries loaded successfully'}, safe=False)


class DropDowns(APIView):
    def get(self, request,*args, **kwargs):
        drop_type = self.kwargs['drop_type']
        
        if drop_type == 1:
            data = UserRole.objects.all().values('id', 'name') 
        elif drop_type == 2:
            data = Country.objects.all().values('id', 'name', 'calling_code')
        else:
            raise cannot_perform_action("Invalid drop_type")
        return JsonResponse(
                {
                    "status": "success",
                    "detail": "Data fetched successfully",
                    'data': list(data)
                },
                safe=False,
            )