from django.urls import path

from .views.utilities_view import AddCountries, DropDowns, GetFeed

urlpatterns = [
    # Dropdowns
    path(
        "dropdowns/<int:drop_type>/",
        DropDowns.as_view(),
        name="All Dropdowns",
    ),
    # Seed Countries into DB
    path(
        "add-countries/",
        AddCountries.as_view(),
        name="Add Countries",
    ),
    
    # Feed
    path(
        "get-feed/<int:page_number>/",
        GetFeed.as_view(),
        name="Get Feed",
    ),
]
