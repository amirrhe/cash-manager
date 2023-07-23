from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializer import UserSerializer, UserLoginSerializer
from drf_yasg.utils import swagger_auto_schema


class RegisterUserView(APIView):
    @swagger_auto_schema(
        tags=['users'],
        request_body=UserSerializer,
        responses={
            201: 'User successfully registered.',
            400: 'Bad Request. The provided data is invalid or incomplete.'}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            response_data = {
                'user_id': user.id,
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        tags=['users'],
        request_body=UserLoginSerializer,
        responses={
            200: 'User successfully logged in. Returns user_id, username, refresh, and access tokens.',
            400: 'Bad Request. The provided data is invalid or incomplete.',
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            response_data = {
                'user_id': user.id,
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
