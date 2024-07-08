from django.urls import path
from .views import (
    UserRetriewUpdateDestroyView,
    UserCeateView,
    MyDetailView,
    UserListView,
)

urlpatterns = [
    path("<int:pk>/", UserRetriewUpdateDestroyView.as_view(), name="user_detail"),
    path("", UserCeateView.as_view(), name="user_create"),
    path("me/", MyDetailView.as_view(), name="user_me"),
    path("all/", UserListView.as_view(), name="user_list"),
]
