from django.urls import path
from .views import RegisterView, LoginView, ProfileView, UserProgressView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('progress/', UserProgressView.as_view(), name='progress'),
]
