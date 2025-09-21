from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_profile, name="edit_profile"),
    path("view_profile/", views.profile_view, name="profile"),
]