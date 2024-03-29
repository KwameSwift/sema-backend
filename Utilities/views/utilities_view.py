import datetime
from itertools import chain
import os

import requests
from django.db.models import Sum, Exists, Q
from django.http import JsonResponse
from rest_framework.views import APIView

from Auth.models.permissions_model import Module
from Auth.models.user_model import Country, UserRole
from Blog.models.blog_model import BlogComment, BlogPost
from Polls.models.poll_models import Poll, PollChoices
from Polls.poll_helper import retrieve_poll_with_choices, get_polls_by_logged_in_user
from Utilities.models.documents_model import BlogDocuments, UserDocuments
from helpers.functions import (
    aware_datetime,
    convert_quill_text_to_normal_text,
    paginate_data,
    truncate_text,
)
from helpers.status_codes import cannot_perform_action


class AddCountries(APIView):
    def post(self, request, *args, **kwargs):
        countries_data = []
        response = requests.get(url=os.environ.get("COUNTRIES_API"))
        data = response.json()
        for country in data:
            countries_data.append(
                Country(
                    name=country["name"],
                    abbreviation=country["alpha3Code"],
                    calling_code="+" + country["callingCodes"][0],
                    flag=country["flags"]["png"],
                )
            )
        Country.objects.bulk_create(
            countries_data, batch_size=10000, ignore_conflicts=True
        )
        log_msg = (
            "========= Uploading " + str(len(countries_data)) + " records ============"
        )
        print(log_msg)

        return JsonResponse({"detail": "Countries loaded successfully"}, safe=False)


class DropDowns(APIView):
    def get(self, request, *args, **kwargs):
        drop_type = self.kwargs["drop_type"]

        if drop_type == 1:
            data = (
                UserRole.objects.all()
                .values("id", "name", "created_on")
                .order_by("-created_on")
            )
        elif drop_type == 2:
            data = Country.objects.all().values("id", "name", "calling_code", "flag")
        elif drop_type == 3:
            data = (
                Module.objects.all().values("id", "name", "created_on").order_by("id")
            )
        else:
            raise cannot_perform_action("Invalid drop_type")
        return JsonResponse(
            {
                "status": "success",
                "detail": "Data fetched successfully",
                "data": list(data),
            },
            safe=False,
        )


class GetFeed(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.kwargs.get("page_number")
        user = self.request.user
        blog_posts = (
            BlogPost.objects.filter(is_approved=True, is_published=True)
            .values(
                "id",
                "title",
                "content",
                "description",
                "is_approved",
                "total_likes",
                "total_shares",
                "is_published",
                "approved_and_published_by__first_name",
                "approved_and_published_by__last_name",
                "cover_image",
                "links",
                "censored_content",
                "is_abusive",
                "reference",
                "author_id",
                "author__first_name",
                "author__last_name",
                "author__profile_image",
                "author__is_verified",
                "author__organization",
                "created_on",
            )
            .order_by("-created_on")
        )

        for blog_post in blog_posts:
            converted_text = convert_quill_text_to_normal_text(blog_post["content"])
            blog_post["preview_text"] = truncate_text(converted_text, 200)
            comments = (
                BlogComment.objects.filter(blog_id=blog_post["id"])
                .values(
                    "id",
                    "commentor__first_name",
                    "commentor__last_name",
                    "commentor__profile_image",
                    "comment",
                    "created_on",
                )
                .order_by("-created_on")
            )
            blog_post["total_comments"] = comments.count()
            blog_post["comments"] = list(comments)
            blog_post["documents"] = list(
                BlogDocuments.objects.filter(blog_id=blog_post["id"])
                .values()
                .order_by("-created_on")
            )
        if user.is_authenticated:
            for blog_post in blog_posts:
                exists = BlogPost.likers.through.objects.filter(
                    Q(blogpost_id=blog_post["id"]) & Q(user_id=user.user_key)
                )
                blog_post["has_liked"] = True if exists else False

            Poll.objects.filter(
                end_date__lt=aware_datetime(datetime.datetime.now()), is_ended=False
            ).update(is_ended=True)
            modified_polls = get_polls_by_logged_in_user(user)
        else:
            polls = (
                Poll.objects.filter(is_approved=True)
                .values(
                    "id",
                    "file_location",
                    "question",
                    "start_date",
                    "end_date",
                    "is_approved",
                    "is_ended",
                    "author_id",
                    "author__first_name",
                    "author__last_name",
                    "author__profile_image",
                    "author__is_verified",
                    "created_on",
                )
                .order_by("-created_on")
            )

            modified_polls = []
            for poll in polls:
                if poll["is_ended"]:
                    modified_poll = retrieve_poll_with_choices(poll["id"])
                    modified_poll["total_votes"] = PollChoices.objects.filter(
                        poll_id=poll["id"]
                    ).aggregate(total_votes=Sum("votes"))["total_votes"]
                    modified_polls.append(modified_poll)
                    # poll["stats"] = retrieve_poll_with_choices(poll["id"])

                else:
                    poll["total_votes"] = PollChoices.objects.filter(
                        poll_id=poll["id"]
                    ).aggregate(total_votes=Sum("votes"))["total_votes"]
                    poll["choices"] = list(
                        PollChoices.objects.filter(poll_id=poll["id"]).values(
                            "id", "choice"
                        )
                    )
                    modified_polls.append(poll)

        combined_results = sorted(
            chain(blog_posts, modified_polls),
            key=lambda x: x["created_on"],
            reverse=True,
        )
        data = paginate_data(combined_results, page_number, 10)
        return JsonResponse(
            # {"success": "Success"},
            data,
            safe=False,
        )
