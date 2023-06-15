import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .serializers import RegisterSerializer

User = get_user_model()


@pytest.fixture(scope="class")
def api_client():
    """
    Fixture for creating an instance of the APIClient.
    """
    client = APIClient()
    return client


@pytest.fixture
def register_data():
    """
    Fixture for providing register data.
    """
    return {
        "username": "testuser",
        "password": "testpassword",
        "password2": "testpassword",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }


@pytest.fixture
@pytest.mark.django_db
def register_user(api_client, register_data):
    """
    Fixture for registering a user.
    """
    api_client.credentials()
    if User.objects.filter(username="testuser").exists():
        return User.objects.get(username="testuser")

    response = api_client.post("/register/", data=register_data)
    user = User.objects.first()
    assert response.status_code == 201
    user = User.objects.first()
    assert user is not None
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    return user


@pytest.fixture
@pytest.mark.django_db
def auth_client(api_client, register_user):
    """
    Fixture for creating an authenticated client.
    """
    user = User.objects.first()
    token = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token[0].key)
    return api_client


@pytest.fixture
@pytest.mark.django_db
def client_second(api_client, register_user):
    """
    Fixture for creating a second client.
    """
    payload = {
        "username": "test_super",
        "password": "testpassword",
        "password2": "testpassword",
        "email": "test_super@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }
    response = api_client.post("/register/", data=payload)
    return response.json()


@pytest.fixture
@pytest.mark.django_db
def send_request_to_auth_client(client_second, register_user):
    """
    Fixture for sending a friend request to the authenticated client.
    """
    user = User.objects.get(email=client_second["email"])
    data = {"to_user": register_user.id}
    token = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token[0].key)
    response = client.post("/friend_request/", data=data)
    return response


@pytest.mark.django_db
class TestUserSignupLogin:
    """
    Test class for user signup and login.
    """

    def test_register_api_same_data(self, api_client, register_data, register_user):
        """
        Test case for registering a user with the same data.
        """
        response = api_client.post("/register/", data=register_data)
        assert response.status_code == 400

    def test_register_serializer_create(self, register_data):
        """
        Test case for registering a user using the serializer.
        """
        register_serializer = RegisterSerializer(data=register_data)
        assert register_serializer.is_valid()
        user = register_serializer.save()
        assert user is not None
        assert user.username == "testuser"

    def test_register_serializer_invalid(self, register_data):
        """
        Test case for invalid registration data with the serializer.
        """
        register_serializer = RegisterSerializer(data=register_data)
        register_serializer.initial_data["password2"] = "super"
        assert not register_serializer.is_valid()

    @pytest.mark.parametrize(
        "email, password, code",
        [
            ("test@example.com", "testpassword", 200),  # Test with email
            ("Test@example.com", "testpassword", 200),  # Test case insensitive email
            ("te@example.com", "testpassword", 400),  # Test wrong email
        ],
    )
    def test_login_api(self, email, password, code, api_client, register_user):
        """
        Test case for user login.
        """
        response = api_client.post(
            "/login/", data={"email": email, "password": password}
        )
        assert response.status_code == code
        if code == 200:
            assert response.json()["token"]


@pytest.mark.django_db
class TestUserSearchApi:
    """
    Test class for user search API.
    """

    def test_search_api(self, auth_client, client_second):
        """
        Test case for searching users.
        """
        response = auth_client.get("/search_user/")
        result = response.json()
        assert len(result) == 2

    @pytest.mark.parametrize(
        "search_keyword, expected_results",
        [
            ("Joh", 2),  # search with username
            ("test@example.com", 1),  # search with email
            ("te@example.com", 0),  # expect 0 because exact match with email
        ],
    )
    def test_with_exact_email(
        self, auth_client, client_second, search_keyword, expected_results
    ):
        """
        Test case for searching users with an exact email match.
        """
        response = auth_client.get("/search_user/", {"search": search_keyword})
        assert response.status_code == 200
        results = response.json()
        assert len(results) == expected_results


@pytest.mark.django_db
class TestFriendRequestAPI:
    """
    Test class for friend request API.
    """

    def test_send_request_api(self, send_request_to_auth_client):
        """
        Test case for sending a friend request.
        """
        assert send_request_to_auth_client.status_code == 201
        result = send_request_to_auth_client.json()
        assert result

    def test_pending_list(self, send_request_to_auth_client, auth_client):
        """
        Test case for retrieving the pending friend requests list.
        """
        response = auth_client.get("/friend_request/")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["from_user"]["username"] == "test_super"

    def test_accept_request(self, send_request_to_auth_client, auth_client):
        """
        Test case for accepting a friend request.
        """
        request = send_request_to_auth_client.json()
        id = request["id"]
        response = auth_client.put(f"/friend_request/{id}/accept_request/")
        assert response.status_code == 200
        result = response.json()
        assert result == {"message": "Friendship request accepted."}

    def test_reject_request(self, send_request_to_auth_client, auth_client):
        """
        Test case for rejecting a friend request.
        """
        request = send_request_to_auth_client.json()
        id = request["id"]
        response = auth_client.put(f"/friend_request/{id}/reject_request/")
        assert response.status_code == 200
        result = response.json()
        assert result == {"message": "Friendship request rejected."}


@pytest.mark.django_db
class TestFriendListAPI:
    """
    Test class for friend list API.
    """

    def test_request_user_friend_list(self, send_request_to_auth_client, auth_client):
        """
        Test case for retrieving the friend list of the requesting user.
        """
        request = send_request_to_auth_client.json()
        id = request["id"]
        auth_client.put(f"/friend_request/{id}/accept_request/")
        response = auth_client.get("/user_friend_list/")
        result = response.json()
        friends = result[0]["friends"]
        assert len(friends) == 1
        assert friends[0]["username"] == "test_super"
