import datetime

from helpers.email_sender import send_email


def send_blog_declination_mail(blog, comments):
    subject = "Blog Declined"
    # Convert the string to a datetime object
    dt_object = datetime.datetime.fromisoformat(str(blog.created_on).replace("Z", "+00:00"))
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Hi, {blog.author.first_name}.{new_line}"
        f"Your blog with the title: {blog.title}, created on {formatted_datetime} "
        f"has been declined.{new_line}"
        f"After a careful review of the blog, we realized it was in breach of our policies.{new_line}"
        f"Please find the reason for the declination below and act accordingly: {double_new_line}"
        f"{comments}"
        f"{double_new_line}"
        f"Thank you.{new_line}"
        f"The Sema Team"
    )

    send_email(blog.author.email, subject, message)
