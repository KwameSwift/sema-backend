from django.urls import path

from .views.forum_views import (
    GetSingleForum,
    CreateForum,
    DeleteForum,
    GetAllForums,
    LikeAForum,
    JoinForum,
    LeaveForum,
    UpdateForum,
    SearchForum,
    UploadForumFiles,
    DeleteVirtualMeeting,
    CreateVirtualMeeting,
    RegisterForMeeting,
    UpdateVirtualMeeting,
    CreateForumPoll,
    DeleteForumPoll,
    VoteOnAForumPoll,
    GetAllForumPollsByUser,
    CommentOnForum,
    DeleteCommentOnForum,
    LikeAForumComment,
    GetAllForumDiscussions,
    GetAllMeetingAttendees,
)

urlpatterns = [
    # Forums
    path(
        "create-forum/",
        CreateForum.as_view(),
        name="Create Forum",
    ),
    path(
        "get-forum/<int:forum_id>/",
        GetSingleForum.as_view(),
        name="Get Single Forum",
    ),
    path(
        "delete-forum/<int:forum_id>/",
        DeleteForum.as_view(),
        name="Delete Forum",
    ),
    path(
        "get-all-forums/<int:forum_type>/<int:page_number>/",
        GetAllForums.as_view(),
        name="Get All Forums",
    ),
    path(
        "like-a-forum/<int:forum_id>/",
        LikeAForum.as_view(),
        name="Like A Forum",
    ),
    path(
        "join-forum/<int:forum_id>/",
        JoinForum.as_view(),
        name="Join Forum",
    ),
    path(
        "leave-forum/<int:forum_id>/",
        LeaveForum.as_view(),
        name="Leave Forum",
    ),
    path(
        "update-forum/<int:forum_id>/",
        UpdateForum.as_view(),
        name="Update Forum",
    ),
    path(
        "search-forums/",
        SearchForum.as_view(),
        name="Search Forums",
    ),
    path(
        "upload-forum-files/<int:forum_id>/",
        UploadForumFiles.as_view(),
        name="Upload Forum Files",
    ),
    path(
        "create-virtual-meeting/<int:forum_id>/",
        CreateVirtualMeeting.as_view(),
        name="Create Virtual Meeting",
    ),
    path(
        "delete-virtual-meeting/<int:meeting_id>/",
        DeleteVirtualMeeting.as_view(),
        name="Delete Virtual Meeting",
    ),
    path(
        "update-virtual-meeting/<int:meeting_id>/",
        UpdateVirtualMeeting.as_view(),
        name="Update Virtual Meeting",
    ),
    path(
        "register-virtual-meeting/<int:meeting_id>/",
        RegisterForMeeting.as_view(),
        name="Register For Meeting",
    ),
    path(
        "get-meeting-attendants/<int:meeting_id>/<int:page_number>/",
        GetAllMeetingAttendees.as_view(),
        name="Get All Meeting Attendants",
    ),
    path(
        "create-forum-poll/<int:forum_id>/",
        CreateForumPoll.as_view(),
        name="Create Forum Poll",
    ),
    path(
        "delete-forum-poll/<int:forum_poll_id>/",
        DeleteForumPoll.as_view(),
        name="Delete Forum Poll",
    ),
    path(
        "vote-on-forum-poll/",
        VoteOnAForumPoll.as_view(),
        name="Vote On A Forum Poll",
    ),
    path(
        "get-all-forum-polls/<int:forum_id>/<int:page_number>/",
        GetAllForumPollsByUser.as_view(),
        name="Get All Forum Polls By User",
    ),
    path(
        "comment-on-forum/<int:forum_id>/",
        CommentOnForum.as_view(),
        name="Comment On Forum",
    ),
    path(
        "delete-forum-comment/<int:comment_id>/",
        DeleteCommentOnForum.as_view(),
        name="Delete Comment On Forum",
    ),
    path(
        "like-forum-comment/<int:forum_comment_id>/",
        LikeAForumComment.as_view(),
        name="Like A Forum Comment",
    ),
    path(
        "get-all-forum-discussions/<int:forum_id>/",
        GetAllForumDiscussions.as_view(),
        name="Get All Forum Discussions",
    ),
]
