import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from Auth.models import User
from Blog.models.blog_model import BlogPost
from helpers.functions import delete_file, upload_file
from helpers.status_codes import cannot_perform_action
from helpers.validations import check_permission, check_super_admin

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


class UploadFile(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        file_type = request.data.get("file_type")
        user = self.request.user

        # if not check_permission(self.request.user, "Blog", [2]):
        #     raise cannot_perform_action("Unauthorized to perform action")

        for file in files:
            file_name = str(file.name)
            new_name = file_name.replace(" ", "_")
            fs = FileSystemStorage(location=LOCAL_FILE_PATH)
            fs.save(new_name, file)

            file_path = LOCAL_FILE_PATH + new_name

            subdirectory = f"{user.first_name}_{user.last_name}"
            file_path = upload_file(file_path, subdirectory)
            if os.path.exists(file_path):
                os.remove(file_path)

        return JsonResponse(
            {"status": "success", "detail": "File uploaded successfully"},
            safe=False,
        )
