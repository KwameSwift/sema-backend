import ftplib
import os
import random
import string

from better_profanity import profanity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.timezone import make_aware

from _project import settings

FTP_HOSTNAME = os.getenv("FTP_HOSTNAME")
FTP_USERNAME = os.getenv("FTP_USERNAME")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")


# Function to return paginated data
def paginate_data(data, page_number, items_per_page):
    # Pass the data to the paginator module
    paginator = Paginator(data, items_per_page)
    try:
        # Get data specific to page number
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        # Return first page in any exception
        page = paginator.page(1)

    # Get data details after paginated
    try:
        total_data = data.count()
    except TypeError:
        total_data = len(data)

    total_pages = paginator.num_pages

    new_data = list(page)

    # Create an object to be returned
    response_data = {
        "status": "success",
        "detail": "Data fetched successfully",
        "current_page": page.number,
        "total_data": total_data,
        "total_pages": total_pages,
        "data": new_data,
    }

    # Return paginated data details
    return response_data


# Function to return aware datetime
def aware_datetime(datetime):
    settings.TIME_ZONE
    return make_aware(datetime)


# Generate random password
def generate_random_string(length):
    alphanumeric_chars = string.ascii_letters + string.digits
    random_string = "".join(random.choice(alphanumeric_chars) for _ in range(length))
    return random_string


def delete_file(file_name, subdirectory=None):
    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(FTP_HOSTNAME)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)

        if subdirectory:
            file_path = subdirectory + "/" + file_name
        else:
            file_path = file_name

        try:
            # Delete the file
            ftp.delete(file_path)
            # Close the FTP connection
            ftp.quit()
            print("File deleted successfully.")
            return True
        except ftplib.all_errors:
            print("File does not exist")
            return False

    except ftplib.all_errors as e:
        print("FTP error:", str(e))


def create_directory_recursively(ftp, path):
    dirs = path.split("/")
    for dir in dirs:
        if dir not in ftp.nlst():
            ftp.mkd(dir)
        ftp.cwd(dir)


def upload_files(file_path, subdirectory):
    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(FTP_HOSTNAME)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)

        # Create parent directories recursively if they don't exist
        create_directory_recursively(ftp, subdirectory)

        file_name = os.path.basename(file_path)

        try:
            ftp.delete(file_name)
        except ftplib.all_errors:
            pass

        # Open the local file in binary mode for uploading
        with open(file_path, "rb") as file:
            # Upload the file to the remote directory
            ftp.storbinary("STOR " + file_name, file)

        # Close the FTP connection
        ftp.quit()

        print("File uploaded successfully.")
        remote_filepath = "/" + subdirectory + "/" + file_name
        return remote_filepath
    except ftplib.all_errors as e:
        print("FTP error:", str(e))
        return False


def retrieve_file(remote_filepath, local_directory):
    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(FTP_HOSTNAME)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)

        # Extract the file name from the remote file path
        file_name = os.path.basename(remote_filepath)

        # Set the local file path where the retrieved file will be saved
        local_file_path = os.path.join(local_directory, file_name)

        # Open the local file in binary mode for writing
        with open(local_file_path, "wb") as file:
            # Retrieve the file from the remote directory
            ftp.retrbinary("RETR " + remote_filepath, file.write)

        # Close the FTP connection
        ftp.quit()

        print("File retrieved successfully.")
        return local_file_path
    except ftplib.all_errors as e:
        print("FTP error:", str(e))
        return False


# Upload files
def local_file_upload(full_directory, file):
    from django.core.files.storage import FileSystemStorage

    file_name = str(file.name)

    new_filename = file_name.replace(" ", "_")
    fs = FileSystemStorage(location=full_directory)
    fs.save(new_filename, file)

    return f"{full_directory}/{new_filename}"


# Delete files
def delete_local_file(full_directory):
    try:
        if os.path.exists(full_directory):
            os.remove(full_directory)
    except TypeError:
        pass

    return True


# Check Abusive words
def check_abusive_words(content):
    profanity.load_censor_words()
    censored_text = profanity.censor(content)
    is_abusive = profanity.contains_profanity(content)
    return censored_text, is_abusive
