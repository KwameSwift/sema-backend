"""
URL configuration for _project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sentry-debug/", trigger_error),
    path("auth/", include("Auth.urls")),
    path("users/", include("Users.urls")),
    path("utilities/", include("Utilities.urls")),
    path("blog/", include("Blog.urls")),
    path("super-admin/", include("Admin.urls")),
    path("events/", include("Events.urls")),
    path("polls/", include("Polls.urls")),
    path("forum/", include("Forum.forum_urls")),
    path("chats/", include("Forum.chat_urls")),
    path("document-vault/", include("DocumentVault.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
