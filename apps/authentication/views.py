from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """Register a new user account with name, email, and password."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description='User successfully registered.',
                response=UserSerializer,
            ),
            400: OpenApiResponse(description='Validation error or duplicate email.'),
        },
        tags=['Authentication'],
        summary='Register a new user',
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for convenient immediate use
        refresh = RefreshToken.for_user(user)
        refresh['name'] = user.name
        refresh['email'] = user.email

        return Response(
            {
                'success': True,
                'message': 'User registered successfully.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate an existing user and obtain JWT access and refresh tokens."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Login successful with JWT tokens.'),
            400: OpenApiResponse(description='Invalid credentials or missing fields.'),
        },
        tags=['Authentication'],
        summary='User login with JWT',
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        access_token = serializer.validated_data['access']
        refresh_token = serializer.validated_data['refresh']

        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    """Retrieve profile details of the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        tags=['Authentication'],
        summary='Get current user profile',
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
