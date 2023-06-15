from django.urls import path
from rest_framework.routers import DefaultRouter

from social_api.views import (
    FriendshipRequestAPIView,
    RegisterView,
    UserFriendsList,
    UserLoginView,
    UserSearchView,
)

router = DefaultRouter()
router.register(r"friend_request", FriendshipRequestAPIView, basename="send_request")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", UserLoginView.as_view(), name="auth_login"),
    path("search_user/", UserSearchView.as_view(), name="search"),
    path("user_friend_list/", UserFriendsList.as_view(), name="friend_list"),
]
urlpatterns += router.urls
