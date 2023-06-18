import os

from helpers.functions import local_file_upload
from Utilities.models.documents_model import BlogDocuments

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


def create_cover_image(cover_image, blog, user):
    try:
        for image in cover_image:
            base_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}"
            full_directory = f"{base_directory}/Blog_Documents/{blog.title}"
            cover_image_path = local_file_upload(full_directory, image)

            blog.cover_image = cover_image_path
            blog.save()

            blog_image = {
                "owner_id": user.user_key,
                "blog_id": blog.id,
                "document_location": cover_image_path,
            }

        BlogDocuments.objects.create(**blog_image)
    except TypeError:
        pass


def create_other_blog_documents(files, blog, user):
    try:
        for img in files:
            base_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}"
            full_directory = f"{base_directory}/Blog_Documents/{blog.title}"
            filepath = local_file_upload(full_directory, img)

            new_blog_image = {
                "owner_id": user.user_key,
                "blog_id": blog.id,
                "document_location": filepath,
            }

            BlogDocuments.objects.create(**new_blog_image)
    except TypeError:
        pass
