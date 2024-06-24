from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import File
from .serializers import UserSerializer, FileSerializer
from urllib.parse import urlencode
import hashlib
import hmac
import base64

class UserLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class FileUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if not request.user.is_ops_user:
            return Response({'detail': 'Only Ops Users can upload files.'}, status=status.HTTP_403_FORBIDDEN)

        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(uploaded_by=request.user)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        if user.is_client_user:
            token, _ = Token.objects.get_or_create(user=user)
            verification_link = f"http://example.com/verify-email/?token={token.key}"
            send_mail(
                'Verify your email',
                f'Please verify your email using the following link: {verification_link}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
        else:
            raise serializers.ValidationError("Only Client Users can sign up.")

class EmailVerify(APIView):
    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        try:
            token = Token.objects.get(key=token)
            user = token.user
            user.is_active = True
            user.save()
            return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class FileDownload(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        if not request.user.is_client_user:
            return Response({'detail': 'Only Client Users can download files.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            file = File.objects.get(id=file_id)
            download_link = generate_secure_link(file)
            return Response({'download-link': download_link, 'message': 'success'})
        except File.DoesNotExist:
            return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

def generate_secure_link(file):
    secret_key = b'your_secret_key'
    url = f"http://example.com/download-file/{file.id}/"
    signature = hmac.new(secret_key, url.encode('utf-8'), hashlib.sha256).hexdigest()
    secure_link = f"{url}?signature={signature}"
    return secure_link

class ListFiles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_client_user:
            return Response({'detail': 'Only Client Users can list files.'}, status=status.HTTP_403_FORBIDDEN)
        
        files = File.objects.filter(uploaded_by__is_ops_user=True)
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)
