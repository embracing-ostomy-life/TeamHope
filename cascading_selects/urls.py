from django.urls import path

from components.cascading_selects.select import SelectCascadingSelectsComponent


urlpatterns = [
    path(
        "states/",
        SelectCascadingSelectsComponent.as_view(),
        name="select_cascading_selects",
    ),
]