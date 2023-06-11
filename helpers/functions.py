import ftplib
import os
import random
import string

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
            print(f"File '{file_path}' deleted successfully.")
            return True
        except ftplib.all_errors as e:
            print("File does not exist")
            return False
        
    except ftplib.all_errors as e:
        print("FTP error:", str(e))


def upload_images(file_path, subdirectory):
    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(FTP_HOSTNAME)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)

        # Check if the parent directory exists
        parent_directory = os.path.dirname(subdirectory)

        try:
            if parent_directory and parent_directory not in ftp.nlst():
                # Create the parent directory if it doesn't exist
                ftp.mkd(parent_directory)
        except ftplib.all_errors as e:
            pass

        try:
            # Check if the subdirectory exists
            if subdirectory not in ftp.nlst():
                # Create the subdirectory
                ftp.mkd(subdirectory)
        except ftplib.all_errors as e:
            pass

        # Change to the subdirectory
        ftp.cwd(subdirectory)

        file_name = os.path.basename(file_path)

        try:
            ftp.delete(file_name)
        except ftplib.all_errors as e:
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
