from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Friendship

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_email(self, email):
        user = User.objects.filter(email__iexact=email)
        if user:
            raise serializers.ValidationError("User already exists")

        return email

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = User.objects.filter(email__iexact=email)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        email = user[0].email
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        validated_data["user"] = user
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name"]


class FriendshipRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for friendship requests.
    """

    from_user = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ["id", "from_user", "to_user", "status"]
        read_only_fields = [
            "status",
        ]

    def validate(self, validate_data):
        to_user = validate_data["to_user"]
        from_user = self.context.get("request").user

        if Friendship.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError(
                {"request": "Friendship request already exists."}
            )

        if Friendship.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError(
                {"request": "Friendship request already received"}
            )
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        latest_objs = Friendship.objects.filter(
            from_user=from_user, created_at__gt=one_minute_ago
        ).order_by("-created_at")

        if len(latest_objs) > 2:
            raise serializers.ValidationError(
                {"request": "Exceeded the limit of sending friend requests."}
            )

        return validate_data

    def create(self, validated_data):
        to_user = validated_data["to_user"]
        from_user = self.context.get("request").user

        if to_user == from_user:
            raise serializers.ValidationError(
                {"request": "User can't send request to self"}
            )

        friendship_request = Friendship(from_user=from_user, to_user=to_user)
        friendship_request.save()
        return friendship_request


class UserfriendSerializer(serializers.ModelSerializer):
    """
    Serializer for user's friends.
    """

    friends = UserSerializer(many=True)

    class Meta:
        model = User
        fields = ["friends"]
