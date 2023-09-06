from datetime import datetime

from Forum.models import ChatRoomMessages
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
        f"Dear {forum.author.first_name},{new_line}"
        f"We regret to inform you that your forum titled '{forum.topic}', which was created on {formatted_datetime}, "
        f"has not been approved due to violations of our policies.{new_line}"
        f"After conducting a thorough assessment of the forum content, we have identified the following reasons for "
        f"its declination:{double_new_line}"
        f"{comments}"
        f"{new_line}"
        f"We kindly request your attention to the provided feedback and ask you to take the necessary actions "
        f"accordingly."
        f"{new_line}"
        f"Thank you for your understanding and cooperation."
        f"{double_new_line}"
        f"Sincerely,{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def send_forum_join_request_to_admin(forum, admin_email, user):
    subject = "Request To Join Forum"
    recipient_email = admin_email
    user_name = f"{user.first_name} {user.last_name}"
    user_email = f"{user.email}"
    # Convert the string to a datetime object
    dt_object = datetime.fromisoformat(str(forum.created_on).replace("Z", "+00:00"))
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Dear {forum.author.first_name},{new_line}"
        f"We would like to inform you that a guest user has submitted a request to join your forum '{forum.topic}', "
        f"which was created on {formatted_datetime}.{new_line}"
        f"Below are the details of the user:{new_line}"
        f"Name: {user_name}{new_line}"
        f"Email: {user_email}{new_line}"
        f"We kindly request you to review this request on your dashboard for further information.{new_line}"
        f"Your attention to this matter is greatly appreciated.{new_line}"
        f"Thank you for being a part of Sema.{new_line}"
        f"{double_new_line}"
        f"Sincerely,{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def send_forum_join_request_decline_to_user(forum, user):
    subject = "Your Forum Membership Request: Declined"
    recipient_email = user.email
    user_name = f"{user.first_name} {user.last_name}"
    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Dear {user_name},{new_line}"
        f"We would like to thank you for your interest in joining the '{forum.topic}' forum.{new_line}"
        f"However, after careful consideration, we regret to inform you that your request to join the forum has been "
        f"declined.{new_line}"
        f"The decision was made based on alignment with our forum's focus and guidelines.{new_line}"
        f"We genuinely appreciate your understanding in this matter and encourage you to continue exploring other "
        f"avenues within our community."
        f"{double_new_line}"
        f"Thank you for your time and interest.{new_line}"
        f"Sincerely,{new_line}"
        f"The Sema Team"
    )
    send_email(recipient_email, subject, message)


def send_forum_request_response_to_user(forum, user):
    subject = f"Your Request to Join '{forum.topic}' Forum"
    recipient_email = user.email
    user_name = f"{user.first_name} {user.last_name}"

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Hello, {user_name}.{new_line}"
        f"Thank you for your interest in joining the '{forum.topic}' forum. We appreciate your enthusiasm to become a "
        f"member of our private community.{new_line}"
        f"We'd like to inform you that our administrative team is currently reviewing your request.{new_line}"
        f" As {forum.topic} is a private forum, we carefully evaluate each request to ensure the best experience for "
        f"all members.{new_line}"
        f"Please anticipate a response from us shortly regarding the status of your request."
        f"If you have any immediate questions, please contact us at {forum.author.email}."
        f"{double_new_line}"
        f"Best regards,"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def send_forum_join_request_approval_to_user(forum, user):
    subject = "Your Forum Membership Request: Approved"
    recipient_email = user.email
    user_name = f"{user.first_name} {user.last_name}"
    user_email = f"{user.email}"
    # Convert the string to a datetime object
    dt_object = datetime.fromisoformat(str(forum.created_on).replace("Z", "+00:00"))
    # Convert the datetime object to the desired format
    formatted_datetime = dt_object.strftime("%d-%b-%Y %H:%M:%S %Z")

    new_line = "\n"
    double_new_line = "\n\n"
    message = (
        f"Dear, {user.first_name}.{new_line}"
        f"We're pleased to inform you that your request to join the '{forum.topic}' forum has been "
        f"approved.{new_line}"
        f"Join in the discussions and interactions by visiting our website. We're excited to have you as a part of "
        f"our community."
        f"{double_new_line}"
        f"Thank you.{new_line}"
        f"The Sema Team"
    )

    send_email(recipient_email, subject, message)


def create_chat_room_message(data, sender_id):
    ChatRoomMessages.objects.create(
        chat_room_id=data["chat_room_id"],
        sender_id=sender_id,
        message=data["message"],
        is_media=True if data.get("media_files") else False,
        media_files=data["media_files"] if data.get("media_files") else None,
    )
