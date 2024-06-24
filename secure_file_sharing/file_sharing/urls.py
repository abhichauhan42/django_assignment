from django.urls import path
from .views import UserLogin, FileUpload, UserSignUp, EmailVerify, FileDownload, ListFiles

urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('upload/', FileUpload.as_view(), name='upload'),
    path('signup/', UserSignUp.as_view(), name='signup'),
    path('verify-email/', EmailVerify.as_view(), name='verify_email'),
    path('download-file/<int:file_id>/', FileDownload.as_view(), name='download_file'),
    path('list-files/', ListFiles.as_view(), name='list_files'),
]
