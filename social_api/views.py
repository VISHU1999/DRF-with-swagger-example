from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Friendship
from .serializers import (
    FriendshipRequestSerializer,
    RegisterSerializer,
    UserfriendSerializer,
    UserLoginSerializer,
    UserSerializer,
)

User = get_user_model()


class BaseException(APIException):
    """
    Base exception class for custom exceptions.
    """

    status_code = 400
    default_detail = "Internal error"

    def __init__(self, details=None, status_code=None):
        if details is not None:
            self.default_detail = details
        if status_code is not None:
            self.status_code = status_code

        super().__init__()


@extend_schema(description="Register User,Email is case insensitive")
class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [
        AllowAny,
    ]


class UserLoginView(ObtainAuthToken):
    """
    View for user login.
    """

    @extend_schema(request=UserLoginSerializer, methods=["POST"])
    @extend_schema(description="Email is case insensitive", methods=["POST"])
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key})


@extend_schema(
    description="User Search by exact email or first/last name", methods=["GET"]
)
class UserSearchView(generics.ListAPIView):
    """
    View for searching users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["first_name", "last_name", "=email"]


@extend_schema(description="Get User friend list", methods=["GET"])
class UserFriendsList(generics.ListAPIView):
    """
    View for listing user's friends.
    """

    serializer_class = UserfriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


@extend_schema(description="Send Friend Request to User by User Id", methods=["POST"])
@extend_schema(description="Get Pending Friend Request", methods=["GET"])
class FriendshipRequestAPIView(viewsets.ModelViewSet):
    """
    ViewSet for managing friendship requests.
    """

    serializer_class = FriendshipRequestSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = [
        "get",
        "post",
        "put",
    ]

    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, status="pending")

    @extend_schema(request=None, methods=["PUT"])
    @extend_schema(description="Accept friend request", methods=["PUT"])
    @action(detail=True, methods=["put"])
    def accept_request(self, request, *args, **kwargs):
        """
        Accept a friendship request.
        """
        friendship_request = self.get_object()
        if request.user != friendship_request.to_user:
            raise BaseException(status_code=400, details="Unauthenticated request Id")
        else:
            if friendship_request.status != "pending":
                raise BaseException(
                    status_code=400,
                    details=f"its a {friendship_request.status} request",
                )

            friendship_request.status = "accepted"
            friendship_request.save()
            sender = friendship_request.from_user
            receiver = friendship_request.to_user

            sender.friends.add(receiver)
            receiver.friends.add(sender)

        return Response({"message": "Friendship request accepted."})

    @extend_schema(request=None, methods=["PUT"])
    @extend_schema(description="Reject friend request", methods=["PUT"])
    @action(detail=True, methods=["put"])
    def reject_request(self, request, *args, **kwargs):
        """
        Reject a friendship request.
        """
        friendship_request = self.get_object()
        if request.user != friendship_request.to_user:
            raise BaseException(status_code=400, details="Unauthenticated request Id")
        else:
            if friendship_request.status != "pending":
                raise BaseException(
                    status_code=400,
                    details=f"its a {friendship_request.status} request",
                )

            friendship_request.status = "rejected"
            friendship_request.save()

        return Response({"message": "Friendship request rejected."})

    def update(self, request, *args, **kwargs):
        """
        Handle updates for the viewset.
        Raises MethodNotAllowed exception for regular PUT requests.
        """
        raise MethodNotAllowed("PUT")
