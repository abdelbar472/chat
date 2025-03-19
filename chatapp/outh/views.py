from django.shortcuts import redirect,render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.core.mail import EmailMessage

def home(request):
    return render(request, 'login.html')


class CompleteProfileAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            # Send Welcome Email
            send_mail(
                subject="Welcome to the App!",
                message=f"Hi {user.username},\nWelcome to the app! Your profile setup is pending.",
                from_email='your_email',
                recipient_list=[user.email],
            )

            # Construct the redirect URL to the Complete Profile page
            redirect_url = f"http://127.0.0.1:8000/profile/"
            return Response({"redirect_url": redirect_url}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = validated_data['user']
            remember_me = validated_data.get('remember_me', False)

            # Login the user
            login(request, user)

            # Generate JWT token
            tokens = validated_data['tokens']

            # Optionally set the session expiry
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            redirect_url = f"http://127.0.0.1:8000/teams/"
            return Response(
                {
                    "message": "Login successful!",
                    "access_token": tokens['access'],
                    "refresh_token": tokens['refresh'],
                     "redirect_url": redirect_url
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)  # Use request.data, not URL token
        if serializer.is_valid():
            serializer.save()
            logout(request)
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
