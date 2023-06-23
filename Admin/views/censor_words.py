import os

from better_profanity import profanity
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from helpers.functions import local_file_upload

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


# Ad Censor Words to package
class AddCensorWords(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        file = request.FILES["file"]

        full_directory = f"{LOCAL_FILE_PATH}AbusiveWords"
        file_path = local_file_upload(full_directory, file)
        custom_bad_words = []
        with open(file_path, "r") as file:
            line = file.readline()
            while line:
                # Process the line text
                custom_bad_words.append(line.strip())
                # Read the next line
                line = file.readline()

        profanity.add_censor_words(custom_bad_words)

        if os.path.exists(file_path):
            os.remove(file_path)

        return JsonResponse(
            {
                "status": "success",
                "detail": "Words added successfully",
            },
            safe=False,
        )
