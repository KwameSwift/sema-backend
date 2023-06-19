import os

import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from Auth.models.permissions_model import Module

from Auth.models.user_model import Country, UserRole
from helpers.status_codes import cannot_perform_action


class AddCountries(APIView):
    def post(self, request, *args, **kwargs):
        countries_data = []
        response = requests.get(url=os.environ.get("COUNTRIES_API"))
        data = response.json()
        for country in data:
            countries_data.append(
                Country(
                    name=country["name"],
                    abbreviation=country["alpha3Code"],
                    calling_code="+" + country["callingCodes"][0],
                    flag=country["flags"]["png"],
                )
            )
        Country.objects.bulk_create(
            countries_data, batch_size=10000, ignore_conflicts=True
        )
        log_msg = (
            "========= Uploading " + str(len(countries_data)) + " records ============"
        )
        print(log_msg)

        return JsonResponse({"detail": "Countries loaded successfully"}, safe=False)


class DropDowns(APIView):
    def get(self, request, *args, **kwargs):
        drop_type = self.kwargs["drop_type"]

        if drop_type == 1:
            data = UserRole.objects.all().values("id", "name", "created_on").order_by("-created_on")
        elif drop_type == 2:
            data = Country.objects.all().values("id", "name", "calling_code")
        elif drop_type == 3:
            data = Module.objects.all().values("id", "name", "created_on").order_by("-created_on")
        else:
            raise cannot_perform_action("Invalid drop_type")
        return JsonResponse(
            {
                "status": "success",
                "detail": "Data fetched successfully",
                "data": list(data),
            },
            safe=False,
        )
