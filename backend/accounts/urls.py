from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView, StudentEnrollmentRequestsView, UserProgressView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("progress/", UserProgressView.as_view(), name="progress"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('enrollment-requests/', StudentEnrollmentRequestsView.as_view(), name='student-requests'),
]
