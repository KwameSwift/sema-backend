import random
import string

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.timezone import make_aware

from _project import settings


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
