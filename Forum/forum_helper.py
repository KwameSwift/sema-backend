from datetime import datetime

from helpers.email_sender import send_email


def send_forum_declination_mail(forum, comments):
    subject = "Forum Declined"
    recipient_email = forum.author.email
    # Convert the string to a datetime object
    dt_object = datetime.fromisoformat(str(forum.created_on).replace("Z", "+00:00"))
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Hi, {forum.author.first_name}.{new_line}"
        f"Your forum with the topic: {forum.topic}, created on {formatted_datetime} "
        f"has been declined.{new_line}"
        f"After a careful review of the forum, we realized it was in breach of our policies.{new_line}"
        f"Please find the reason for the declination below and act accordingly: {double_new_line}"
        f"{comments}"
        f"{double_new_line}"
        f"Thank you.{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)
