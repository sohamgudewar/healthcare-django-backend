from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for exposing basic user profile information."""

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'is_staff', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='User password (at least 6 characters).',
    )
    email = serializers.EmailField(
        required=True,
        help_text='Valid unique email address.',
    )
    name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=255,
        help_text='Full name of the user.',
    )
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default=User.ROLE_PATIENT,
        required=False,
        help_text='User role (admin, doctor, patient, staff). Defaults to patient.',
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError('A user with this email address already exists.')
        return normalized_email

    def validate_name(self, value):
        trimmed_name = value.strip()
        if not trimmed_name:
            raise serializers.ValidationError('Name cannot be blank or contain only spaces.')
        return trimmed_name

    def create(self, validated_data):
        role = validated_data.get('role', User.ROLE_PATIENT)
        is_staff = role in [User.ROLE_ADMIN, User.ROLE_STAFF]
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=role,
            is_staff=is_staff,
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for validating user credentials and issuing JWT tokens."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password', '')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required.')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('This user account is currently inactive.')

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh['name'] = user.name
        refresh['email'] = user.email

        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
