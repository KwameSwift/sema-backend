from django.urls import path

from .views.utilities_view import AddCountries, DropDowns

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
]
