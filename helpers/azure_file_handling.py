import json
import os
import shutil
from os import path

import fitz
import requests
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings
from django.core.files.storage import FileSystemStorage
from pdf2image import convert_from_path

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


def shorten_url(url):
    import pyshorteners

    # Create an instance of the Shortener class
    shortener = pyshorteners.Shortener()

    # Shorten the URL using the default shortening service (TinyURL)
    short_url = shortener.tinyurl.short(url)
    return short_url


def upload_image_cover_or_pdf_to_azure(file, blog, user):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    blog_title = str(blog.title).replace(" ", "_")
    user_name = f"{user.first_name}-{user.last_name}".lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Blog_Documents/{blog_title}"

    container_client = blob_service_client.get_container_client(user_name)
    if not container_client.exists():
        container_client.create_container(public_access="blob")

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
            file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"
            shortened_url = shorten_url(file_url)
            blog.cover_image = shortened_url
            blog.image_key = blob_name
            blog.save()

            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            return shortened_url
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
            file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"
            shortened_url = shorten_url(file_url)
            file_docs = {
                "owner_id": user.user_key,
                "blog_id": blog.id,
                "document_location": shortened_url,
                "document_key": blob_name,
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
            blob_name = f"Blog_Documents/{blog_title}/cover_image.jpg"
            return (
                thumbnail_path,
                blob_name,
                user_name,
            )

        except ResourceExistsError:
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            pass
    else:
        raise cannot_perform_action("Invalid file format")


def upload_thumbnail(file_path, blob_name, container_name):
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # Upload a file to the container
    try:
        with open(file_path, "rb") as data:
            container_client.upload_blob(
                name=blob_name,
                data=data,
                content_settings=ContentSettings(content_type="image/jpeg"),
            )

            file_url = f"{BLOB_BASE_URL}/{container_name}/{blob_name}"
            return file_url, blob_name
    except ResourceExistsError:
        if path.exists(f"media/{container_name}"):
            shutil.rmtree(f"media/{container_name}")
        pass


def upload_poll_document(file, user, poll_question):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    question = str(poll_question).replace(" ", "_").strip("?")
    user_name = f"{user.first_name}-{user.last_name}".lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Poll_Documents/{question}"

    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)
    file_path = f"{full_directory}/{new_filename}"
    blob_name = f"Poll_Documents/{question}/{new_filename}"
    container_client = blob_service_client.get_container_client(user_name)
    if not container_client.exists():
        container_client.create_container(public_access="blob")

    # Upload a file to the container
    with open(file_path, "rb") as data:
        container_client.upload_blob(
            name=blob_name,
            data=data
        )

    file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"

    return file_url, blob_name


def upload_poll_file_or_pdf_to_azure(file, user, poll):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    question = str(poll.question).replace(" ", "_").strip("?")
    user_name = f"{user.first_name}-{user.last_name}".lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Poll_Documents/{question}"

    container_client = blob_service_client.get_container_client(user_name)
    if not container_client.exists():
        container_client.create_container(public_access="blob")

    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)
    file_path = f"{full_directory}/{new_filename}"
    blob_name = f"Poll_Documents/{question}/{new_filename}"

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
            file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"
            shortened_url = shorten_url(file_url)
            poll.file_location = shortened_url
            poll.file_key = blob_name
            poll.save()

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
            file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"
            shortened_url = shorten_url(file_url)
            poll.file_location = shortened_url
            poll.file_key = blob_name
            poll.save()
            thumbnail_path = f"{full_directory}/poll_thumbnail.jpg"
            images = convert_from_path(
                file_path,
                dpi=300,
                # poppler_path=r"C:\Users\MSI\Downloads\poppler-0.68.0\bin",
            )
            if images:
                images[0].save(thumbnail_path, format="JPEG", quality=100)
            blob_name = f"Poll_Documents/{question}/poll_thumbnail.jpg"
            return (
                thumbnail_path,
                blob_name,
                user_name,
            )

        except ResourceExistsError:
            print("File already exists")
            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
            pass
    else:
        raise cannot_perform_action("Invalid file format")


def upload_cover_image(request, res_data, blog=None, poll=None):
    current_host = request.get_host()
    data = {
        "file_path": res_data[0],
        "blob_name": res_data[1],
        "container_name": res_data[2]
    }

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Send a POST request to the same server
    response = requests.post(
        f"https://{current_host}/blog/upload-thumbnail/",
        data=json.dumps(data),
        headers=headers,
    )
    response_data = response.json()
    shortened_url = shorten_url(response_data["resp_data"][0])
    if response.status_code == 200:
        if blog:
            blog.cover_image = shortened_url
            blog.image_key = response_data["resp_data"][1]
            blog.save()
        if poll:
            poll.snapshot_location = shortened_url
            poll.snapshot_key = response_data["resp_data"][1]
            poll.save()

    return True


def create_other_blog_documents(files, blog, user):
    try:
        for img in files:
            file_name = str(img.name).lower()
            new_filename = file_name.replace(" ", "_")
            blog_title = str(blog.title).replace(" ", "_")
            user_name = f"{user.first_name}-{user.last_name}".lower()
            base_directory = f"{LOCAL_FILE_PATH}{user_name}"
            full_directory = f"{base_directory}/Blog_Documents/{blog_title}"

            container_client = blob_service_client.get_container_client(user_name)
            if not container_client.exists():
                container_client.create_container(public_access="blob")

            fs = FileSystemStorage(location=full_directory)
            fs.save(new_filename, img)
            file_path = f"{full_directory}/{new_filename}"
            blob_name = f"Blog_Documents/{blog_title}/{new_filename}"

            # Upload a file to the container
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data)

            # Return blob url
            file_url = f"{BLOB_BASE_URL}/{user_name}/{blob_name}"
            shortened_url = shorten_url(file_url)
            new_blog_doc = {
                "owner_id": user.user_key,
                "blog_id": blog.id,
                "document_location": shortened_url,
                "document_key": blob_name,
            }

            BlogDocuments.objects.create(**new_blog_doc)

            if path.exists(f"media/{user_name}"):
                shutil.rmtree(f"media/{user_name}")
    except ResourceExistsError:
        print("File already exists")
        if path.exists(f"media/{user_name}"):
            shutil.rmtree(f"media/{user_name}")
        pass


def delete_blob(container_name, blob_name):
    if blob_name:
        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)
        try:
            # Delete the blob
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
        except ResourceNotFoundError:
            pass
    else:
        return False


def upload_profile_image(file, user):
    file_name = str(file.name).lower()
    new_filename = file_name.replace(" ", "_")
    user_name = f"{user.first_name}-{user.last_name}".lower()
    base_directory = f"{LOCAL_FILE_PATH}{user_name}"
    full_directory = f"{base_directory}/Profile_Image"
    file_url = ""

    container_name = user_name

    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container(public_access="blob")

    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)
    file_path = f"{full_directory}/{new_filename}"
    blob_name = f"Profile_Image/{new_filename}"
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
    shortened_url = shorten_url(file_url)

    if path.exists(f"media/{user_name}"):
        shutil.rmtree(f"media/{user_name}")

    return shortened_url, blob_name
