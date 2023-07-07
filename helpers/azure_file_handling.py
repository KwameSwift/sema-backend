import json
import os
import shutil
from os import path

import fitz
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings
from django.core.files.storage import FileSystemStorage
from pdf2image import convert_from_path

import requests

from helpers.status_codes import cannot_perform_action
from Utilities.models.documents_model import BlogDocuments, UserDocuments

STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT")
STORAGE_ACCOUNT_PROTOCOL = os.environ.get("STORAGE_ACCOUNT_PROTOCOL")
STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
STORAGE_ACCOUNT_CORE = os.environ.get("STORAGE_ACCOUNT_CORE")
BLOB_BASE_URL = os.environ.get("BLOB_BASE_URL")

account_key = ";AccountKey="
endpoint = "DefaultEndpointsProtocol=https;AccountName="
core = ";EndpointSuffix=core.windows.net"

LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH")
# Get the connection string from the Azure portal
connection_string = (
    f"{endpoint}{STORAGE_ACCOUNT}{account_key}{STORAGE_ACCOUNT_KEY}{core}"
)

# Create a blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)



def upload_image_cover_or_pdf_to_azure(file, blog, user):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    blog_title = str(blog.title).replace(" ", "_")
    user_name = (f"{user.first_name}-{user.last_name}").lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Blog_Documents/{blog_title}"
    file_url = ""

    container_name = user_name

    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)
    file_path = f"{full_directory}/{new_filename}"
    blob_name = f"Blog_Documents/{blog_title}/{new_filename}"

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

    file_extension = os.path.splitext(file.name)[1]

    if file_extension.lower() in image_file_extensions:
        try:
            # Upload a file to the container
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data)

            # Return blob url
            file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"
            blog.cover_image = file_url
            blog.image_key = blob_name
            blog.save()
            
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            return file_url
        except ResourceExistsError:
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            pass

    elif file_extension.lower() == ".pdf":
        try:
            # Upload a file to the container
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data)

                # Return blob url
                file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"
                file_docs = {
                    "owner_id": user.user_key,
                    "blog_id": blog.id,
                    "document_location": file_url,
                    "document_key": blob_name
                }
                BlogDocuments.objects.create(**file_docs)

                thumbnail_path = f"{full_directory}/cover_image.jpg"
                
                images = convert_from_path(
                    file_path,
                    dpi=300,
                    # poppler_path=r"C:\Users\MSI\Downloads\poppler-0.68.0\bin",
                )
                if images:
                    images[0].save(thumbnail_path, format="JPEG", quality=100)

                return (
                    thumbnail_path,
                    blog_title,
                    container_name,
                )

        except ResourceExistsError:
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            pass
    else:
        raise cannot_perform_action("Invalid file format")



def upload_thumbnail(file_path, blog_title, container_name):
    blob_name = f"Blog_Documents/{blog_title}/cover_image.jpg"
    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
        
    # Upload a file to the container
    with open(file_path, "rb") as data:
        container_client.upload_blob(
            name=blob_name,
            data=data,
            content_settings=ContentSettings(content_type="image/jpeg"),
        )

    file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"

    return file_url, blob_name



def upload_cover_image(request, res_data, blog, user_name):
    current_host = request.get_host()
    data = {
        "file_path": res_data[0],
        "blog_title": res_data[1],
        "container_name": res_data[2],
        "user_name": user_name
    }

    # Set the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Send a GET request to the same server
    response = requests.post(f"http://{current_host}/blog/upload-thumbnail/", data=json.dumps(data), headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        blog.cover_image = response_data["resp_data"][0]
        blog.image_key = response_data["resp_data"][1]
        blog.save()
        
    return True


def create_other_blog_documents(files, blog, user):
    try:
        for img in files:
            file_name = str(img.name).lower()
            new_filename = file_name.replace(" ", "_")
            blog_title = str(blog.title).replace(" ", "_")
            user_name = (f"{user.first_name}-{user.last_name}").lower()
            base_directory = f"{LOCAL_FILE_PATH}{user_name}"
            full_directory = f"{base_directory}/Blog_Documents/{blog_title}"
            container_name = user_name

            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()
                
            fs = FileSystemStorage(location=full_directory)
            fs.save(new_filename, img)
            file_path = f"{full_directory}/{new_filename}"
            blob_name = f"Blog_Documents/{blog_title}/{new_filename}"
            
            # Upload a file to the container
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data)
            
            # Return blob url
            file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"
            new_blog_doc = {
                "owner_id": user.user_key,
                "blog_id": blog.id,
                "document_location": file_url,
                "document_key": f"{container_name}/{blob_name}",
            }

            BlogDocuments.objects.create(**new_blog_doc)
            
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
    except ResourceExistsError:
        if path.exists(f"media/{user_name}"):
            shutil.rmtree(f"media/{user_name}")
        pass


def delete_blob(container_name, blob_name):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)
    try:
        # Delete the blob
        blob_client = container_client.get_blob_client(f"{blob_name}")
        blob_client.delete_blob()
    except ResourceNotFoundError:
        pass
    
    
def upload_profile_image(file, user):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    user_name = (f"{user.first_name}-{user.last_name}").lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Profile_Image"
    file_url = ""

    container_name = user_name

    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)
    file_path = f"{full_directory}/{new_filename}"
    blob_name = f"/Profile_Image/{new_filename}"
    try:
        # Upload a file to the container
        with open(file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data)
    except ResourceExistsError:
        if path.exists(f"media/{user_name}"):
            shutil.rmtree(f"media/{user_name}")
        pass
    
   # Return blob url
    file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"
    pro_image = {
        "owner_id": user.user_key,
        "document_type": "Profile Image",
        "document_location": file_url,
        "document_key": f"{container_name}/{blob_name}",
    }

    UserDocuments.objects.create(**pro_image)
    
    if path.exists(f"media/{user_name}"):
        shutil.rmtree(f"media/{user_name}")