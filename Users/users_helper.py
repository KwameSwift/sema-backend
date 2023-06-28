import os

import fitz
from PIL import Image

from helpers.functions import local_file_upload
from helpers.status_codes import cannot_perform_action
from Utilities.models.documents_model import UserDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")

def upload_profile_image(profile_image, user):
    
    base_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}"
    full_directory = f"{base_directory}/User_Documents/Profile_Image"
    if os.path.exists(full_directory):
        os.remove(full_directory)
    profile_path = local_file_upload(full_directory, profile_image)
    UserDocuments.objects.filter(owner=user, document_type="Profile Image").delete()
    user.profile_image = profile_path
    user.save()

    pro_image = {
        "owner_id": user.user_key,
        "document_type": "Profile Image",
        "document_location": profile_path,
    }

    UserDocuments.objects.create(**pro_image)
    