import os
from PIL import Image
import fitz

from helpers.functions import local_file_upload
from Utilities.models.documents_model import BlogDocuments
from helpers.status_codes import cannot_perform_action

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")


def create_cover_image(cover_image, blog, user):
    base_directory = f"{LOCAL_FILE_PATH}{user.first_name}_{user.last_name}"
    full_directory = f"{base_directory}/Blog_Documents/{blog.title}"
    image_file_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".tiff",
        ".bmp",
        ".svg",
        ".raw",
        ".webp",
    ]
    try:
        for image in cover_image:
            # Get the file extension
            file_extension = os.path.splitext(image.name)[1]
            
            if file_extension.lower() in image_file_extensions:
                cover_image_path = local_file_upload(full_directory, image)

                blog.cover_image = cover_image_path
                blog.save()

                blog_image = {
                    "owner_id": user.user_key,
                    "blog_id": blog.id,
                    "document_location": cover_image_path,
                }

                BlogDocuments.objects.create(**blog_image)
            elif file_extension.lower() == '.pdf':
                from django.core.files.storage import FileSystemStorage
                file_name = str(image.name)

                new_filename = file_name.replace(" ", "_")
                fs = FileSystemStorage(location=full_directory)
                fs.save(new_filename, image)
                file_path = f"{full_directory}/{new_filename}"
                file_docs = {
                    "owner_id": user.user_key,
                    "blog_id": blog.id,
                    "document_location": file_path,
                }

                BlogDocuments.objects.create(**file_docs)
                thumbnail_path=f"{base_directory}/Blog_Documents/{blog.title}/thumbnail.jpg"
                
                # Load the first page of the PDF using PyMuPDF
                size=(368, 300)
                doc = fitz.open(file_path)
                page = doc.load_page(0)
                pix = page.get_pixmap()

                # Convert the PyMuPDF pixmap to PIL image
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Resize the image to the desired thumbnail size
                image.thumbnail(size)

                # Save the thumbnail image
                image.save(thumbnail_path)
                
                blog.cover_image = thumbnail_path
                blog.save()
                
                file_doc = {
                    "owner_id": user.user_key,
                    "blog_id": blog.id,
                    "document_location": thumbnail_path,
                }

                BlogDocuments.objects.create(**file_doc)
                
            else:
                raise cannot_perform_action("Invalid file type")
            
            
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
