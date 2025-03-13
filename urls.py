from django.urls import path, include

#from components.inline_validation.form import FormInlineValidationComponent
from components.cascading_selects.parent_select import ParentSelectCascadingSelectsComponent
from components.cascading_selects.select import SelectCascadingSelectsComponent

urlpatterns = [
    #path(
    #    "",
    #    FormInlineValidationComponent.as_view(),
    #    name="form_inline_validation",
    #),
    #path(
    #    "cascading_selects/",
    #    ParentSelectCascadingSelectsComponent.as_view(),
    #    name="cascading_selects",
    #),
    path("cascading_selects/", include("components.cascading_selects.urls")),
    path("inline_validation/", include("components.inline_validation.urls")),
]
